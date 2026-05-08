# computer_graphics
# Maze Project README

This project contains two Python files for generating and solving mazes using Pygame: [main.py](main.py) and [bonus_cycles.py](bonus_cycles.py). Below is an explanation of the key functions and classes in each file.

## main.py

This file implements a maze generator using Depth-First Search (DFS) and a maze solver using DFS. It visualizes the process in real-time.

### Classes and Functions

#### Cell Class
- `__init__(self, r, c)`: Initializes a cell at row `r`, column `c` with all walls intact and flags for generation and solving.
- `draw(self, screen)`: Draws the cell on the Pygame screen, including walls and color overlays for paths and deadlocks.
- `get_neighbors(self, grid)`: Returns a list of neighboring cells and their directions.

#### Functions
- `remove_walls(current, next_cell, direction)`: Removes the walls between two adjacent cells in the specified direction.
- `print_text(text, x, y)`: Renders and displays text on the screen at the given coordinates.

#### Main Logic
- **Generation Phase**: Uses DFS to create a perfect maze by carving paths and removing walls.
- **Solving Phase**: Uses DFS to find a path from start to end, marking the current path and deadlocks.
- **Rendering**: Draws the maze, highlights the solution path, and shows status text.
- **Event Handling**: Allows resetting the maze with the 'R' key.

## bonus_cycles.py

This file is a bonus feature that generates a perfect maze and then adds cycles by removing extra walls, demonstrating how cycles can break the "wall-following" rule for maze solving.

### Classes and Functions

#### Cell Class
- Same as in [main.py](main.py).

#### Functions
- `remove_walls(current, next_cell, direction)`: Same as in [main.py](main.py).
- `add_cycles(grid, probability=20)`: Removes extra walls randomly to create cycles in the maze. Takes a probability (default 20, meaning 5% chance) to decide which walls to remove.
- `print_text(text, x, y)`: Same as in [main.py](main.py).

#### Main Logic
- **Generation Phase**: Generates a perfect maze using DFS.
- **Cycle Addition**: Calls `add_cycles` to remove extra walls, creating cycles.
- **Solving Phase**: Attempts to solve the maze with cycles using DFS, showing that wall-following may fail.
- **Rendering**: Similar to [main.py](main.py), with additional text explaining the bonus feature.

## Usage

1. Run [main.py](main.py) to see a perfect maze generation and solving.
2. Run [bonus_cycles.py](bonus_cycles.py) to see how cycles affect maze solving.
3. Press 'R' to reset the maze in either file.
4. Close the window to exit.

## Dependencies

- Pygame: Install with `pip install pygame`.
- Python 3.x

## Notes

- The maze is 20x20 cells by default.
- Colors: Orange for current cell, red for active path, blue for deadlocks, bright red for solution path.
- Start is top-left (green), end is bottom-right (red).</content>
<parameter name="filePath">c:\Users\Ezbeal\Desktop\maze_project\README.md

Name - Ezbel Tsegezeab
ID - UGR/9827/16
Section - 1
