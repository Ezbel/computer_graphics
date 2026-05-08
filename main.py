import pygame
import random
from collections import deque

# Initialize Pygame
pygame.init()

# Constants
ROWS, COLS = 20, 20
CELL_SIZE = 30
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE
FPS = 60
MAX_SOLVE_STEPS_PER_FRAME = 1

# Create display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Generator & Solver")
clock = pygame.time.Clock()

# Colors
COLOR_BG = (20, 20, 20)
COLOR_WALL = (180, 180, 180) # Slightly darker walls
COLOR_HEAD = (255, 165, 0) # Orange for the current cell (generator/solver head)
COLOR_ACTIVE_PATH = (150, 0, 0) # Red for the current path being explored
COLOR_DEADLOCK = (0, 0, 150) # Blue for confirmed deadlocks
COLOR_FINAL_PATH = (255, 0, 0) # Bright red for the final solution path


class Cell:
    def __init__(self, r, c):
        self.r = r
        self.c = c
        self.walls = [True, True, True, True] # [top, right, bottom, left]
        self.visited_gen = False    # For generation (DFS)
        self.visited_solve = False  # For solving (DFS)
        self.on_current_path = False # For solver visualization (green path)
        self.is_deadlock = False    # For solver visualization (blue deadlock)
        self.parent = None

    def draw(self, screen):
        x = self.c * CELL_SIZE
        y = self.r * CELL_SIZE
        
        # Prioritize drawing the active path, then deadlocks
        if self.on_current_path:
            pygame.draw.rect(screen, COLOR_ACTIVE_PATH, (x, y, CELL_SIZE, CELL_SIZE))
        elif self.is_deadlock:
            pygame.draw.rect(screen, COLOR_DEADLOCK, (x, y, CELL_SIZE, CELL_SIZE))
        
        # Draw walls
        if self.walls[0]:  # Top
            pygame.draw.line(screen, COLOR_WALL, (x, y), (x + CELL_SIZE, y), 2)
        if self.walls[1]:  # Right
            pygame.draw.line(screen, COLOR_WALL, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 2)
        if self.walls[2]:  # Bottom
            pygame.draw.line(screen, COLOR_WALL, (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE), 2)
        if self.walls[3]:  # Left
            pygame.draw.line(screen, COLOR_WALL, (x, y), (x, y + CELL_SIZE), 2)

    def get_neighbors(self, grid):
        neighbors = []
        # Up, Right, Down, Left
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        for i, (dr, dc) in enumerate(directions):
            nr, nc = self.r + dr, self.c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                neighbors.append((grid[nr][nc], i))
        return neighbors


def remove_walls(current, next_cell, direction):
    """Remove walls between current and next_cell"""
    current.walls[direction] = False
    next_cell.walls[(direction + 2) % 4] = False


def print_text(text, x, y):
    font = pygame.font.SysFont("Arial", 18, bold=True)
    surface = font.render(text, True, (255, 255, 255))
    rect = surface.get_rect(center=(x, y))
    pygame.draw.rect(screen, COLOR_BG, rect.inflate(10, 6))
    screen.blit(surface, rect)


# Initialize grid
grid = [[Cell(r, c) for c in range(COLS)] for r in range(ROWS)] # Re-initialize grid on reset

# Generation variables
gen_stack = [grid[0][0]]
grid[0][0].visited_gen = True # Use visited_gen for generation
current_gen = grid[0][0]

# Solving variables
solve_stack = [] # Use a list as a stack for DFS
path = []
start_cell = grid[0][0]
end_cell = grid[ROWS-1][COLS-1]
current_solving = None

# State machine: 'GENERATING' -> 'SOLVING' -> 'DONE'
state = 'GENERATING'

# Main loop
running = True
while running:
    screen.fill(COLOR_BG)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                grid = [[Cell(r, c) for c in range(COLS)] for r in range(ROWS)]
                gen_stack = [grid[0][0]]
                grid[0][0].visited_gen = True # Reset visited_gen
                current_gen = grid[0][0]
                
                solve_stack = [] # Reset solve stack
                path = []
                current_solving = None
                start_cell = grid[0][0]
                end_cell = grid[ROWS-1][COLS-1]
                state = 'GENERATING'
                # No need to explicitly reset cell flags here, new grid is created

    # === GENERATION PHASE ===
    if state == 'GENERATING':
        unvisited = [n for n in current_gen.get_neighbors(grid) if not n[0].visited_gen]
        if unvisited:
            next_cell, direction = random.choice(unvisited)
            next_cell.visited_gen = True
            gen_stack.append(current_gen)
            remove_walls(current_gen, next_cell, direction)
            current_gen = next_cell
        elif gen_stack:
            current_gen = gen_stack.pop()
        else:
            state = 'SOLVING' # Transition to solving
            # Initialize DFS solver
            solve_stack.append(start_cell)
            start_cell.visited_solve = True
            start_cell.on_current_path = True

    # === SOLVING PHASE (BFS) ===
    elif state == 'SOLVING':
        current_solving = None
        steps_taken = 0
        while steps_taken < MAX_SOLVE_STEPS_PER_FRAME:
            if not solve_stack:
                state = 'DONE' # Stack empty, no path found
                break

            current = solve_stack[-1] # Peek at the top of the stack
            current_solving = current

            if current == end_cell:
                # Path found!
                path.clear()
                cell = end_cell
                while cell:
                    path.append(cell)
                    cell = cell.parent
                path.reverse()
                state = 'DONE'
                break
            
            # Find unvisited neighbors (that are accessible through a broken wall)
            unvisited_neighbors = []
            for neighbor, direction in current.get_neighbors(grid):
                if not current.walls[direction] and not neighbor.visited_solve:
                    unvisited_neighbors.append((neighbor, direction))

            if unvisited_neighbors:
                # Pick one neighbor to explore
                next_cell, _ = random.choice(unvisited_neighbors)
                
                next_cell.visited_solve = True
                next_cell.parent = current
                next_cell.on_current_path = True
                next_cell.is_deadlock = False 
                solve_stack.append(next_cell)
            else:
                # No neighbors left - this cell is part of a deadlock
                popped_cell = solve_stack.pop()
                popped_cell.on_current_path = False
                popped_cell.is_deadlock = True 
                # If stack becomes empty, no path found (shouldn't happen in a perfect maze)
                if not solve_stack:
                    state = 'DONE' # No path found
                    break
            steps_taken += 1 # Increment step counter
    
    # === RENDERING ===
    # Draw all cells (walls and backgrounds)
    for row in grid:
        for cell in row:
            cell.draw(screen)
    
    # Draw solution path (red) - only show when solved (overlays other colors)
    if state == 'DONE' and path:
        for cell in path:
            x = cell.c * CELL_SIZE
            y = cell.r * CELL_SIZE
            pygame.draw.rect(screen, COLOR_FINAL_PATH, (x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4))
    
    # Draw current solving cell during solving phase
    if state == 'SOLVING' and current_solving:
        x = current_solving.c * CELL_SIZE
        y = current_solving.r * CELL_SIZE
        pygame.draw.rect(screen, COLOR_HEAD, (x + 3, y + 3, CELL_SIZE - 6, CELL_SIZE - 6))

    # Draw current generation cell during generation phase
    if state == 'GENERATING':
        x = current_gen.c * CELL_SIZE
        y = current_gen.r * CELL_SIZE
        pygame.draw.rect(screen, COLOR_HEAD, (x + 3, y + 3, CELL_SIZE - 6, CELL_SIZE - 6))
    
    # Draw start (green) and end (red) markers (always on top)
    pygame.draw.rect(screen, (0, 255, 0), (0, 0, CELL_SIZE, CELL_SIZE), 6)  # Start - Green
    pygame.draw.rect(screen, (255, 0, 0), ((COLS-1)*CELL_SIZE, (ROWS-1)*CELL_SIZE, CELL_SIZE, CELL_SIZE), 6)  # End - Red

    # Display status text
    if state == 'GENERATING':
        print_text("GENERATING MAZE...", WIDTH // 2, HEIGHT - 20)
    elif state == 'SOLVING':
        print_text("SOLVING MAZE (DFS)...", WIDTH // 2, HEIGHT - 20)
    elif state == 'DONE':
        print_text("MAZE SOLVED! (R to Reset)", WIDTH // 2, HEIGHT - 20)
    
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
