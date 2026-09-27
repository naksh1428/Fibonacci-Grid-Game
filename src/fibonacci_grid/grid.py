"""The game board and its rules. No pygame, so it is easy to test."""

from fibonacci_grid.config import (
    FIB_RUN_LENGTH,
    CHECK_DIAGONALS,
    CLICKED_CELL_DOUBLE,
    MAX_GRID_SIZE,
)
from fibonacci_grid.fibonacci import is_consecutive_fibonacci_run


class Grid:
    """A square board of numbers. Every cell starts empty (0)."""

    def __init__(self, size):
        """Make an empty board.

        Args:
            size (int): Rows and columns, kept in 1..MAX_GRID_SIZE.
        """
        self.size = max(1, min(size, MAX_GRID_SIZE))
        self.cells = [[0] * self.size for _ in range(self.size)]

    # -- basic helpers -----------------------------------------------------
    def in_bounds(self, row, col):
        """Check if a cell is on the board.

        Args:
            row (int): Row index.
            col (int): Column index.

        Returns:
            bool: True if inside.
        """
        return 0 <= row < self.size and 0 <= col < self.size

    def clear(self):
        """Set every cell back to 0. The board keeps its size."""
        for row in self.cells:
            for col in range(self.size):
                row[col] = 0

    # -- the click rule ----------------------------------------------------
    def increment_cross(self, row, col):
        """Add 1 to the clicked row and column (clicked cell gets +2).

        Args:
            row (int): Clicked row.
            col (int): Clicked column.
        """
        for c in range(self.size):
            self.cells[row][c] += 1
        for r in range(self.size):
            self.cells[r][col] += 1
        if not CLICKED_CELL_DOUBLE:
            self.cells[row][col] -= 1

    # -- the clearing rule -------------------------------------------------
    def _lines(self):
        """Yield each row, column and (if on) diagonal.

        Yields:
            list[tuple[int, int]]: The (row, col) cells of one line.
        """
        for r in range(self.size):
            yield [(r, c) for c in range(self.size)]          # rows
        for c in range(self.size):
            yield [(r, c) for r in range(self.size)]          # columns

        if CHECK_DIAGONALS:
            down, up = {}, {}
            for r in range(self.size):
                for c in range(self.size):
                    down.setdefault(r - c, []).append((r, c))  # "\" diagonals
                    up.setdefault(r + c, []).append((r, c))    # "/" diagonals
            for key in sorted(down):
                yield down[key]
            for key in sorted(up):
                yield up[key]

    def find_run_cells(self):
        """Find all cells that are in a Fibonacci run.

        Returns:
            set[tuple[int, int]]: The (row, col) cells to clear.
        """
        marked = set()
        for line in self._lines():
            values = [self.cells[r][c] for (r, c) in line]
            for i in range(len(line) - FIB_RUN_LENGTH + 1):
                if is_consecutive_fibonacci_run(values[i:i + FIB_RUN_LENGTH]):
                    marked.update(line[i:i + FIB_RUN_LENGTH])
        return marked

    def clear_cells(self, cells):
        """Set the given cells to 0.

        Args:
            cells (Iterable[tuple[int, int]]): The (row, col) cells to empty.
        """
        for (r, c) in cells:
            self.cells[r][c] = 0
