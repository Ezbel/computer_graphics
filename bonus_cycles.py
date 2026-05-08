"""
BONUS FEATURE: Cycle Generation for Maze Assignment
This is a STANDALONE version that demonstrates how cycles break 
the 'shoulder-to-the-wall' rule.
"""
import pygame
import random
from collections import deque

# Initialize Pygame
pygame.init()

# Colors
COLOR_BG = (20, 20, 20)
COLOR_WALL = (180, 180, 180)
COLOR_HEAD = (255, 165, 0)
COLOR_ACTIVE_PATH = (150, 0, 0)
COLOR_DEADLOCK = (0, 0, 150)
COLOR_FINAL_PATH = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Constants
ROWS, COLS = 20, 20
CELL_SIZE = 30
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE
FPS = 60
MAX_SOLVE_STEPS_PER_FRAME = 1

# Create display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Bonus: Cycle Generation")
clock = pygame.time.Clock()

class Cell:
    def __init__(self, r, c):
        self.r = r
        self.c = c
        # Mapping to assignment requirements:
        # index 0: northWall (Top)
        # index 1: eastWall  (Right)
        # index 2: southWall (Bottom)
        # index 3: westWall  (Left)
        self.walls = [True, True, True, True] 
        
        self.visited_gen = False
        self.visited_solve = False
        self.on_current_path = False
        self.is_deadlock = False
        self.parent = None

    def draw(self, screen):
        x = self.c * CELL_SIZE
        y = self.r * CELL_SIZE
        
        if self.on_current_path:
            pygame.draw.rect(screen, COLOR_ACTIVE_PATH, (x, y, CELL_SIZE, CELL_SIZE))
        elif self.is_deadlock:
            pygame.draw.rect(screen, COLOR_DEADLOCK, (x, y, CELL_SIZE, CELL_SIZE))
        
        # Draw walls
        if self.walls[0]: pygame.draw.line(screen, COLOR_WALL, (x, y), (x + CELL_SIZE, y), 2)
        if self.walls[1]: pygame.draw.line(screen, COLOR_WALL, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 2)
        if self.walls[2]: pygame.draw.line(screen, COLOR_WALL, (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE), 2)
        if self.walls[3]: pygame.draw.line(screen, COLOR_WALL, (x, y), (x, y + CELL_SIZE), 2)

    def get_neighbors(self, grid):
        neighbors = []
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        for i, (dr, dc) in enumerate(directions):
            nr, nc = self.r + dr, self.c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                neighbors.append((grid[nr][nc], i))
        return neighbors

def remove_walls(current, next_cell, direction):
    current.walls[direction] = False
    next_cell.walls[(direction + 2) % 4] = False

def add_cycles(grid, probability=20):
    """
    The 'Extra Mile' Bonus: Eats extra walls to create cycles.
    Applying a 1-in-20 (5%) probability to all remaining internal walls.
    """
    ROWS = len(grid)
    COLS = len(grid[0])
    walls_removed = 0
    for r in range(ROWS):
        for c in range(COLS):
            # Check Right wall (equivalent to eastWall) independently
            if c < COLS - 1 and grid[r][c].walls[1]:
                if random.randint(1, probability) == 1:
                    grid[r][c].walls[1] = False
                    grid[r][c+1].walls[3] = False
                    walls_removed += 1
            
            # Check Bottom wall (equivalent to southWall) independently
            if r < ROWS - 1 and grid[r][c].walls[2]:
                if random.randint(1, probability) == 1:
                    grid[r][c].walls[2] = False
                    grid[r+1][c].walls[0] = False
                    walls_removed += 1

    return walls_removed

def print_text(text, x, y):
    font = pygame.font.SysFont("Arial", 16, bold=True)
    surface = font.render(text, True, (255, 255, 255))
    rect = surface.get_rect(center=(x, y))
    pygame.draw.rect(screen, COLOR_BG, rect.inflate(10, 6))
    screen.blit(surface, rect)

if __name__ == "__main__":
    grid = [[Cell(r, c) for c in range(COLS)] for r in range(ROWS)]
    # Start and End in the interior (not on boundaries) as per Addendum
    start_cell = grid[ROWS // 5][COLS // 5]
    end_cell = grid[ROWS - ROWS // 5][COLS - COLS // 5]
    
    gen_stack = [start_cell]
    start_cell.visited_gen = True
    current_gen = start_cell

    solve_stack = []
    path = []
    state = 'GENERATING'
    extra_walls = 0

    running = True
    while running:
        screen.fill(COLOR_BG)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: # Reset
                    grid = [[Cell(r, c) for c in range(COLS)] for r in range(ROWS)]
                    start_cell = grid[ROWS // 4][COLS // 4]
                    end_cell = grid[3 * ROWS // 4][3 * COLS // 4]
                    gen_stack, solve_stack, path = [start_cell], [], []
                    start_cell.visited_gen = True
                    current_gen = start_cell
                    state = 'GENERATING'

        # GENERATION
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
                # THE BONUS MOMENT
                extra_walls = add_cycles(grid, probability=20)
                print(f"Bonus: Removed {extra_walls} extra walls to create cycles.")
                
                state = 'SOLVING'
                solve_stack.append(start_cell)
                start_cell.visited_solve = True
                start_cell.on_current_path = True

        # SOLVING (DFS)
        elif state == 'SOLVING':
            steps = 0
            while steps < MAX_SOLVE_STEPS_PER_FRAME:
                if not solve_stack:
                    state = 'DONE'
                    break
                current = solve_stack[-1]
                if current == end_cell:
                    temp = end_cell
                    while temp:
                        path.append(temp)
                        temp = temp.parent
                    state = 'DONE'
                    break
                
                accessible = []
                for neighbor, direction in current.get_neighbors(grid):
                    if not current.walls[direction] and not neighbor.visited_solve:
                        accessible.append(neighbor)

                if accessible:
                    next_cell = random.choice(accessible)
                    next_cell.visited_solve = True
                    next_cell.parent = current
                    next_cell.on_current_path = True
                    solve_stack.append(next_cell)
                else:
                    popped = solve_stack.pop()
                    popped.on_current_path = False
                    popped.is_deadlock = True
                steps += 1

        # DRAWING
        for row in grid:
            for cell in row:
                cell.draw(screen)

        if state == 'DONE' and path:
            for cell in path:
                x, y = cell.c * CELL_SIZE, cell.r * CELL_SIZE
                pygame.draw.rect(screen, COLOR_FINAL_PATH, (x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4))

        # Draw head and markers
        if state == 'GENERATING':
            pygame.draw.rect(screen, COLOR_HEAD, (current_gen.c * CELL_SIZE + 3, current_gen.r * CELL_SIZE + 3, CELL_SIZE - 6, CELL_SIZE - 6))
        elif state == 'SOLVING' and solve_stack:
            curr = solve_stack[-1]
            pygame.draw.rect(screen, COLOR_HEAD, (curr.c * CELL_SIZE + 3, curr.r * CELL_SIZE + 3, CELL_SIZE - 6, CELL_SIZE - 6))

        pygame.draw.rect(screen, (0, 255, 0), (start_cell.c * CELL_SIZE, start_cell.r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 6)
        pygame.draw.rect(screen, (255, 0, 0), (end_cell.c * CELL_SIZE, end_cell.r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 6)

        # Status text explaining the bonus
        if state == 'GENERATING':
            print_text("GENERATING PERFECT MAZE...", WIDTH // 2, HEIGHT - 25)
        elif state == 'SOLVING':
            print_text(f"CYCLES ADDED! ({extra_walls} extra walls eaten)", WIDTH // 2, HEIGHT - 35)
            print_text("Wall-following rule would FAIL here.", WIDTH // 2, HEIGHT - 15)
        elif state == 'DONE':
            print_text("MAZE SOLVED (R to Restart)", WIDTH // 2, HEIGHT - 25)

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()