"""Plays turns and keeps score. No pygame, so it is easy to test."""

from fibonacci_grid.config import (
    DEFAULT_GRID_SIZE,
    MAX_GRID_SIZE,
    MAX_CLICKS,
    WIN_CLEARED_CELLS,
)
from fibonacci_grid.grid import Grid


class Game:
    """Holds the board and the score, and plays one turn at a time."""

    def __init__(self, size=DEFAULT_GRID_SIZE):
        """Start a new game.

        Args:
            size (int): Rows and columns, kept in 1..MAX_GRID_SIZE.
        """
        self.grid = Grid(size)
        self.clicks = 0
        self.cells_cleared = 0
        self.last_cleared = set()

    @property
    def size(self):
        """int: How many rows (and columns) the board has."""
        return self.grid.size

    @property
    def status(self):
        """str: "won", "lost" or "playing"."""
        if self.cells_cleared >= WIN_CLEARED_CELLS:
            return "won"
        if self.clicks >= MAX_CLICKS:
            return "lost"
        return "playing"

    # -- the main interaction ---------------------------------------------
    def play(self, row, col):
        """Play one click: grow the row and column, then clear any runs.

        Args:
            row (int): Clicked row.
            col (int): Clicked column.

        Returns:
            set[tuple[int, int]]: Cells cleared this turn (may be empty).
        """
        if self.status != "playing" or not self.grid.in_bounds(row, col):
            return set()

        self.clicks += 1
        self.grid.increment_cross(row, col)

        cleared = self.grid.find_run_cells()
        self.grid.clear_cells(cleared)

        self.cells_cleared += len(cleared)
        self.last_cleared = cleared
        return cleared

    # -- menu commands -----------------------------------------------------
    def clear_board(self):
        """Empty every cell, but keep the board size and the score."""
        self.grid.clear()
        self.last_cleared = set()

    def reset(self):
        """Start over: empty the board and set the score back to zero."""
        self.grid = Grid(self.grid.size)
        self.clicks = 0
        self.cells_cleared = 0
        self.last_cleared = set()

    def resize(self, size):
        """Start a new game on a new board size. The score resets.

        Args:
            size (int): Rows and columns, kept in 1..MAX_GRID_SIZE.
        """
        size = max(1, min(size, MAX_GRID_SIZE))
        self.grid = Grid(size)
        self.clicks = 0
        self.cells_cleared = 0
        self.last_cleared = set()
