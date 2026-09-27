"""Starts the game loop. Run with "python -m fibonacci_grid"."""

import sys
from pathlib import Path

# When run as a plain script (``python main.py``, PyCharm's Run button)
# Python only sees this folder, not the package.  Put ``src/`` on the path
# so the ``fibonacci_grid`` imports below resolve either way.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pygame

from fibonacci_grid import config as cfg
from fibonacci_grid.ui import GameUI


def main():
    """Open the window and run the game until it is closed."""
    ui = GameUI()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                ui.handle_event(event)

        ui.update()
        ui.draw()
        pygame.display.flip()
        ui.clock.tick(cfg.FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
