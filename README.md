# Fibonacci Grid

A small grid game built with **Python + pygame**, click a cell to raise its whole row and column; line up
five consecutive Fibonacci numbers to clear them.

## Run it

From the project root (the folder with `pyproject.toml`):

```bash
python -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -e .              # installs pygame and the fibonacci_grid package
python -m fibonacci_grid      # or just: fibonacci-grid
# or, without installing:
python src/fibonacci_grid/main.py
```

Backend tests need no display:

```bash
python -m unittest
```

## Run with Docker

pygame opens a real desktop window, so the container draws the game onto
computer's screen through X11 (Linux, or Wayland with XWayland).

### Prerequisites

- Docker with the Compose plugin (`docker --version`, `docker compose version`)
- A graphical desktop session (not a plain SSH shell)
- `xhost` (usually preinstalled; otherwise `sudo apt install x11-xserver-utils`)

### Steps

1. **Go to the project folder** (the one with the `Dockerfile`):

   ```bash
   cd Akshata-Papade
   ```

2. **Allow Docker to use your screen.** Do this once per login session:

   ```bash
   xhost +local:docker
   ```

3. **Build the image and start the game:**

   ```bash
   docker compose up --build
   ```

   The first build downloads the Python base image and pygame, so it takes a
   minute. The game window then opens. Later runs can skip the build step:
   `docker compose up`.

4. **Stop the game** by closing the window, or by pressing `Ctrl+C` in the
   terminal. To remove the stopped container:

   ```bash
   docker compose down
   ```

5. **Take back the screen access** when you're done (optional):

   ```bash
   xhost -local:docker
   ```

### Run the tests in Docker

The tests don't need a screen, so step 2 isn't needed:

```bash
docker compose --profile test run --rm test
```

### Win / lose

- **Win** – clear 10 cells in total.
- **Lose** – use up all 60 clicks first.

When the game ends, clicks on the board are ignored; press **Reset** (`R`) or
pick a size to play again. Both numbers are in `config.py`
(`WIN_CLEARED_CELLS`, `MAX_CLICKS`).

## Controls

- **Click a cell** – increments its entire row and column, then scans & clears. A short click sound plays (`assets/click.wav`; turn it off or change the volume with `SOUND_ENABLED` / `CLICK_SOUND_VOLUME` in `config.py`).
- **Size buttons (10 / 20 / 30 / 50)** – start a fresh game at that grid size (max 50×50).
- **Clear** – empty every cell, keep the running stats. (keyboard: `C`)
- **Reset** – empty the board *and* zero the stats. (keyboard: `R`)

While hovering, a translucent "＋" shows exactly which cells a click will hit.
Cleared cells flash briefly. When cells are large enough the value is printed;
otherwise the board is a heat-map (brighter = higher).

## Project structure — UI and logic fully separated

The backend modules import **nothing** from pygame, so every rule is unit-tested
on its own. Only `ui.py` touches the screen.

```
Akshata-Papade/
├── src/fibonacci_grid/    the game package (code below)
│   └── assets/click.wav   click sound
├── tests/                 unit tests
├── ASSIGNMENT.md          the original assignment brief
├── Analysis.txt           plain-language walkthrough of the game and code
├── pyproject.toml         package metadata + dependencies
├── requirements.txt       pinned pygame version (used by Docker)
├── Dockerfile, docker-compose.yml, .dockerignore, .gitignore
└── README.md
```

Inside `src/fibonacci_grid/`:

| File | Layer | Responsibility |
|------|-------|----------------|
| `__main__.py` | entry | Lets `python -m fibonacci_grid` start the game. |
| `config.py` | shared | All tunable constants: sizes, colours, gameplay flags. |
| `fibonacci.py` | backend | The Fibonacci sequence and the "consecutive run" test. |
| `grid.py` | backend | The board state: increment a cross, find runs, clear cells. |
| `game.py` | backend | Controller: runs one turn, tracks clicks/score, menu commands. |
| `ui.py` | frontend | pygame rendering, buttons, mouse/keyboard input. |
| `main.py` | frontend | Entry point + event loop only. |
| `tests` | tests | Unit tests for the backend (no pygame). |

Dependency direction: `main → ui → game → grid → fibonacci → config`.

## Design decisions (the parts the brief left open)

**1. The clicked cell goes up by 2.**
It sits at the crossing of its row and column, so the natural reading of "the
whole row +1 *and* the whole column +1" touches it twice. The implementation
simply adds 1 across the row and 1 down the column, which produces +2 for free.
It is one flag away from +1 if preferred: `CLICKED_CELL_DOUBLE = False` in
`config.py`.

**2. "Next to each other" = horizontal and vertical lines.**
Rows and columns are always scanned. Diagonals are implemented but off by
default; flip `CHECK_DIAGONALS = True` to include both diagonal directions.

**3. "Consecutive Fibonacci numbers" must be in order.**
Five cells qualify only when their values match five neighbouring entries of the
Fibonacci sequence, **in order — ascending or descending** (e.g. `1,2,3,5,8` or
`8,5,3,2,1`). Five Fibonacci values in a jumbled order do *not* count. I use the
**de-duplicated** sequence `1, 2, 3, 5, 8, 13, …` (a single leading 1). Because a
valid run is then strictly monotonic, the awkward `1, 1` pair can never start a
run — which resolves the ambiguity the brief flags. Empty cells (value 0) never
take part in a run.

**4. One scan-and-clear pass per click; overlaps cleared together.**
After the increment I scan the whole board, collect the union of every cell in
any run, and clear them all at once. This clears overlapping runs cleanly. I do
**not** cascade (re-scan after clearing) because the brief's loop is per click —
but it would be a one-line change in `Game.play` to loop until no runs remain.

**5. Clear vs Reset.**
`Clear` wipes the cells but keeps the size and stats (useful mid-game). `Reset`
wipes the board of the current size and zeroes the stats.
