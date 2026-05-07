import pygame

pygame.init()

ROWS = 20
COLS = 20
CELL = 30

WIDTH = COLS * CELL
HEIGHT = ROWS * CELL

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Grid")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def draw_grid():
    screen.fill(BLACK)

    for i in range(ROWS):
        for j in range(COLS):
            x = j * CELL
            y = i * CELL

            pygame.draw.rect(screen, WHITE, (x, y, CELL, CELL), 1)


running = True

while running:
    draw_grid()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

pygame.quit()