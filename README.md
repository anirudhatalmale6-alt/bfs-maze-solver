# BFS Maze Solver

A compact, zero-interaction command-line tool that solves ordinary 2D grid
mazes and returns the **shortest path** using Breadth-First Search (BFS).

BFS is the right algorithm here: on an unweighted grid every step costs the
same, so BFS is *guaranteed* to find a minimum-length path. It explores the
maze in expanding rings from the start, so the first time it reaches the goal
it has done so via a shortest route.

Runs from the command line with no prompts at any stage — give it a maze file
and it prints (or animates) the solution and the path length.

## Requirements

- Python 3.6+ (no third-party packages — standard library only)

Runs the same on Windows, macOS and Linux. On Windows:

```
python maze_solver.py sample_maze.txt
```

## Maze file format

Plain text, one row per line:

| Char | Meaning              |
|------|----------------------|
| `#`  | wall (impassable)    |
| `.`  | open cell (passable) |
| `S`  | start                |
| `E`  | end / goal           |

Example (`sample_maze.txt`):

```
#########
#S..#...#
#.#.#.#.#
#.#...#.#
#.#####.#
#......E#
#########
```

## Usage

```
python maze_solver.py <maze_file> [--diagonal] [--no-animate] [--quiet]
```

| Flag           | Effect                                                        |
|----------------|--------------------------------------------------------------|
| `--diagonal`   | Allow 8-directional movement (default is 4-directional).     |
| `--no-animate` | Print the solved maze once instead of animating the trace.   |
| `--quiet`      | Print only path length + coordinates (machine-friendly).     |

### Examples

Animate the solve (default):

```
python maze_solver.py sample_maze.txt
```

Print the solved maze with the path marked by `*`:

```
python maze_solver.py sample_maze.txt --no-animate
```

```
#########
#S..#...#
#*#.#.#.#
#*#...#.#
#*#####.#
#******E#
#########

Solved. Shortest path length: 10 steps.
```

Machine-friendly output (easy to pipe into another program):

```
python maze_solver.py sample_maze.txt --quiet
```

```
length=10
1,1 2,1 3,1 4,1 5,1 5,2 5,3 5,4 5,5 5,6 5,7
```

## Exit codes

| Code | Meaning                                   |
|------|-------------------------------------------|
| `0`  | Maze solved (path found)                  |
| `1`  | No path exists between `S` and `E`        |
| `2`  | Bad input (missing file, no S/E, etc.)    |

These make it easy to chain the solver into a larger automated flow.

## How the BFS works (source walkthrough)

See `maze_solver.py` — the `solve_bfs()` function is the heart of it:

1. A FIFO queue (`collections.deque`) holds the frontier of cells to explore,
   nearest-first.
2. A `came_from` dictionary records which cell we reached each cell *from*.
   It doubles as the visited-set.
3. Cells are dequeued in non-decreasing distance order, so the first time the
   goal is popped we have a shortest path.
4. `_reconstruct_path()` walks the `came_from` links backwards from the goal to
   the start and reverses them to produce the final route.
