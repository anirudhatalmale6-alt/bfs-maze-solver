#!/usr/bin/env python3
"""
maze_solver.py
==============

Command-line, zero-interaction Breadth-First Search (BFS) maze solver for
ordinary 2D grid mazes.

BFS is used because, on an unweighted grid (every step costs the same), it is
guaranteed to find the *shortest* path in terms of number of steps. It explores
the grid in expanding "rings" from the start cell, so the first time it reaches
the goal it has necessarily done so via a minimum-length route.

Maze file format (plain text, one row per line):
    #  wall        (impassable)
    .  open cell   (passable)
    S  start
    E  end / goal

Example (sample_maze.txt):
    #########
    #S..#...#
    #.#.#.#.#
    #.#...#.#
    #.#####.#
    #......E#
    #########

Usage:
    python maze_solver.py <maze_file> [--diagonal] [--no-animate] [--quiet]

    <maze_file>     Path to the maze text file.
    --diagonal      Allow 8-directional movement (default: 4-directional).
    --no-animate    Skip the step-by-step animation, just print the solution.
    --quiet         Print only the path coordinates and length (machine-friendly).

Exit codes:
    0  maze solved (path found)
    1  no path exists between S and E
    2  bad input (file missing, no S/E, malformed maze)

Everything runs hands-off from the command line with no prompts at any stage.
"""

import argparse
import sys
import time
from collections import deque


# --------------------------------------------------------------------------- #
# Maze loading / validation
# --------------------------------------------------------------------------- #
def load_maze(path):
    """
    Read the maze file into a list-of-lists grid and locate S and E.

    Returns (grid, start, end) where start/end are (row, col) tuples.
    Raises ValueError on any structural problem so the caller can exit cleanly.
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            # Strip the trailing newline only; keep interior spacing intact.
            raw_lines = [line.rstrip("\n") for line in fh]
    except OSError as exc:
        raise ValueError("cannot read maze file: %s" % exc)

    # Drop blank trailing lines that editors often leave behind.
    while raw_lines and raw_lines[-1].strip() == "":
        raw_lines.pop()

    if not raw_lines:
        raise ValueError("maze file is empty")

    # Normalise all rows to the same width by padding with walls, so a ragged
    # file (rows of unequal length) still forms a rectangular grid.
    width = max(len(line) for line in raw_lines)
    grid = [list(line.ljust(width, "#")) for line in raw_lines]

    start = end = None
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch == "S":
                if start is not None:
                    raise ValueError("maze has more than one start (S)")
                start = (r, c)
            elif ch == "E":
                if end is not None:
                    raise ValueError("maze has more than one end (E)")
                end = (r, c)
            elif ch not in ("#", ".", " "):
                # Treat any other character as an open cell but warn once by
                # normalising it, so stray glyphs never break the solve.
                grid[r][c] = "."

    if start is None:
        raise ValueError("maze has no start cell (S)")
    if end is None:
        raise ValueError("maze has no end cell (E)")

    return grid, start, end


# --------------------------------------------------------------------------- #
# The BFS core
# --------------------------------------------------------------------------- #
def solve_bfs(grid, start, end, diagonal=False):
    """
    Breadth-First Search for the shortest path from `start` to `end`.

    How it works:
      * A FIFO queue holds the frontier of cells to explore, nearest-first.
      * `came_from` remembers, for each visited cell, which cell we reached it
        from. That lets us reconstruct the path once we hit the goal.
      * Because BFS dequeues cells in non-decreasing distance order, the first
        time `end` is popped we have found a shortest path.

    Returns the path as a list of (row, col) tuples from start to end, or
    None if the goal is unreachable.
    """
    rows, cols = len(grid), len(grid[0])

    # 4-directional moves (up, down, left, right). Diagonals added on request.
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if diagonal:
        moves += [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    def passable(r, c):
        return 0 <= r < rows and 0 <= c < cols and grid[r][c] != "#"

    frontier = deque([start])
    came_from = {start: None}  # doubles as the "visited" set

    while frontier:
        current = frontier.popleft()
        if current == end:
            return _reconstruct_path(came_from, end)

        cr, cc = current
        for dr, dc in moves:
            nxt = (cr + dr, cc + dc)
            if nxt not in came_from and passable(*nxt):
                came_from[nxt] = current
                frontier.append(nxt)

    return None  # frontier exhausted without reaching the goal


def _reconstruct_path(came_from, end):
    """Walk the came_from links backwards from end to start, then reverse."""
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = came_from[node]
    path.reverse()
    return path


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
def render(grid, path_set, start, end):
    """Return the maze as a string with the path marked by '*'."""
    out = []
    for r, row in enumerate(grid):
        line = []
        for c, ch in enumerate(row):
            if (r, c) == start:
                line.append("S")
            elif (r, c) == end:
                line.append("E")
            elif (r, c) in path_set:
                line.append("*")
            else:
                line.append(ch)
        out.append("".join(line))
    return "\n".join(out)


def animate(grid, path, start, end, delay=0.05):
    """
    Redraw the maze as the path is traced out, one cell at a time, to give a
    visible demo of the solve. Still fully hands-off — no input required.
    """
    for i in range(1, len(path) + 1):
        partial = set(path[:i])
        # Clear the screen (ANSI) then draw the current frame.
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.write(render(grid, partial, start, end))
        sys.stdout.write("\n")
        sys.stdout.flush()
        time.sleep(delay)


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Solve a 2D grid maze with BFS (shortest path)."
    )
    parser.add_argument("maze_file", help="path to the maze text file")
    parser.add_argument(
        "--diagonal", action="store_true",
        help="allow 8-directional (diagonal) movement",
    )
    parser.add_argument(
        "--no-animate", action="store_true",
        help="print the solved maze once instead of animating the trace",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="print only path length and coordinates (machine-friendly)",
    )
    args = parser.parse_args(argv)

    try:
        grid, start, end = load_maze(args.maze_file)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2

    path = solve_bfs(grid, start, end, diagonal=args.diagonal)

    if path is None:
        print("No path exists between S and E.", file=sys.stderr)
        return 1

    if args.quiet:
        # Length is edges = cells - 1.
        print("length=%d" % (len(path) - 1))
        print(" ".join("%d,%d" % (r, c) for r, c in path))
        return 0

    if args.no_animate:
        print(render(grid, set(path), start, end))
    else:
        animate(grid, path, start, end)

    print("\nSolved. Shortest path length: %d steps." % (len(path) - 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
