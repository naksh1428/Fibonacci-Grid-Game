"""All game settings: rules, window size, layout and colours."""

# --------------------------------------------------------------------------
# Gameplay options
# --------------------------------------------------------------------------
MAX_GRID_SIZE = 50            # Hard cap (50 x 50).
DEFAULT_GRID_SIZE = 20        # Grid the game starts on.
GRID_SIZE_OPTIONS = (10, 20, 30, 50)   # Selectable sizes (all <= MAX).

FIB_RUN_LENGTH = 5            # How many neighbours form a clearable run.
CHECK_DIAGONALS = False       # Also scan the two diagonal directions?
CLICKED_CELL_DOUBLE = True    # Clicked cell sits on its row AND column.
#                               True  -> it rises by 2 (natural overlap).
#                               False -> it rises by only 1.

NUMBER_MIN_CELL = 16          # Draw the numeric value only when a cell is
#                               at least this many pixels wide (else the
#                               board is shown purely as a heat-map).
HEAT_CAP = 13                 # Value at which the heat-map colour maxes out.

WIN_CLEARED_CELLS = 10        # Win: clear this many cells in total...
MAX_CLICKS = 60               # ...within this many clicks (else lose).

# --------------------------------------------------------------------------
# Window / layout (all in pixels)
# --------------------------------------------------------------------------
WINDOW_WIDTH = 900            # Starting size when FIT_TO_SCREEN is False
WINDOW_HEIGHT = 780           # (and the smallest size it will start at).
FIT_TO_SCREEN = True          # Start the window as big as the screen allows,
#                               so a 50 x 50 board is still readable.
SCREEN_PADDING = 100          # Room left for the taskbar and title bar.
TOOLBAR_HEIGHT = 96
MARGIN = 20
FPS = 60
FLASH_FRAMES = 20             # How long cleared cells flash, in frames.

# --------------------------------------------------------------------------
# Sound
# --------------------------------------------------------------------------
SOUND_ENABLED = True          # Play a sound when a grid cell is clicked.
CLICK_SOUND_FILE = "click.wav"    # File inside the package's assets/ folder.
CLICK_SOUND_VOLUME = 0.5      # 0.0 (silent) .. 1.0 (full volume).

# --------------------------------------------------------------------------
# Colours (R, G, B) unless noted
# --------------------------------------------------------------------------
COLOR_BG = (22, 24, 30)
COLOR_TOOLBAR = (32, 35, 44)
COLOR_PANEL_BORDER = (55, 60, 72)
COLOR_GRID_LINE = (40, 44, 54)

COLOR_EMPTY = (30, 33, 42)          # A value-0 cell.
COLOR_HEAT_LOW = (46, 84, 120)      # A cell with value 1.
COLOR_HEAT_HIGH = (94, 214, 255)    # A cell at (or above) HEAT_CAP.

COLOR_TEXT = (232, 236, 242)
COLOR_TEXT_DIM = (150, 158, 172)

COLOR_BUTTON = (52, 57, 70)
COLOR_BUTTON_HOVER = (66, 72, 88)
COLOR_BUTTON_ACTIVE = (94, 214, 255)
COLOR_BUTTON_TEXT = (226, 231, 238)
COLOR_BUTTON_ACTIVE_TEXT = (16, 20, 28)

COLOR_HOVER_OVERLAY = (94, 214, 255, 38)   # RGBA -- highlights the "+".
COLOR_FLASH = (255, 238, 120)              # Border on freshly cleared cells.
COLOR_WIN = (120, 230, 140)
COLOR_LOSE = (255, 110, 110)
COLOR_BANNER_BG = (0, 0, 0, 170)           # RGBA -- dims board behind result.
