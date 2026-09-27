"""Pygame drawing and input. Asks Game to change state, then draws it."""

from pathlib import Path

import pygame

from fibonacci_grid import config as cfg
from fibonacci_grid.game import Game

ASSETS_DIR = Path(__file__).resolve().parent / "assets"


class Button:
    """A labelled button that runs a function when clicked."""

    def __init__(self, rect, label, callback, is_active=None):
        """Create a button.

        Args:
            rect (tuple): (x, y, width, height).
            label (str): Button text.
            callback (function): Runs on click.
            is_active (function | None): Returns True to show as selected.
        """
        self.rect = pygame.Rect(rect)
        self.label = label
        self.callback = callback
        self.is_active = is_active

    def draw(self, surface, font):
        """Draw the button, highlighted if selected.

        Args:
            surface (pygame.Surface): Where to draw.
            font (pygame.font.Font): Label font.
        """
        active = bool(self.is_active and self.is_active())
        bg = cfg.COLOR_BUTTON_ACTIVE if active else cfg.COLOR_BUTTON
        fg = cfg.COLOR_BUTTON_ACTIVE_TEXT if active else cfg.COLOR_BUTTON_TEXT
        pygame.draw.rect(surface, bg, self.rect, border_radius=6)
        text = font.render(self.label, True, fg)
        surface.blit(text, text.get_rect(center=self.rect.center))

    def handle_click(self, pos):
        """Run the callback if pos is on the button.

        Args:
            pos (tuple[int, int]): Mouse position.

        Returns:
            bool: True if the button was hit.
        """
        if self.rect.collidepoint(pos):
            self.callback()
            return True
        return False


class GameUI:
    """Draws the game and sends input to Game."""

    def __init__(self):
        """Start pygame and set up the window, fonts, game and buttons."""
        pygame.init()
        self.screen = pygame.display.set_mode(
            self._start_size(), pygame.RESIZABLE
        )
        pygame.display.set_caption("Fibonacci Grid")
        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.SysFont("segoeui", 26, bold=True)
        self.ui_font = pygame.font.SysFont("segoeui", 16)
        self.button_font = pygame.font.SysFont("segoeui", 15, bold=True)
        self._cell_fonts = {}          # cache: cell size -> Font

        self.game = Game()
        self.buttons = []
        self._build_buttons()

        self.hover_cell = None         # (row, col) currently under the mouse
        self.flash_frames = 0          # counts down while cleared cells flash
        self.click_sound = self._load_click_sound()

    # ---------------------------------------------------------------- setup
    @staticmethod
    def _load_click_sound():
        """Load the click sound.

        Returns:
            pygame.mixer.Sound | None: The sound, or None if it can't play.
        """
        if not cfg.SOUND_ENABLED:
            return None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            sound = pygame.mixer.Sound(str(ASSETS_DIR / cfg.CLICK_SOUND_FILE))
        except (pygame.error, FileNotFoundError, NotImplementedError):
            return None
        sound.set_volume(cfg.CLICK_SOUND_VOLUME)
        return sound

    @staticmethod
    def _start_size():
        """Pick the starting window size (fills the screen if FIT_TO_SCREEN).

        Returns:
            tuple[int, int]: (width, height) in pixels.
        """
        width, height = cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT
        if not cfg.FIT_TO_SCREEN:
            return width, height
        try:
            screen_w, screen_h = pygame.display.get_desktop_sizes()[0]
        except (pygame.error, IndexError):
            return width, height
        height = max(height, screen_h - cfg.SCREEN_PADDING)
        width = max(width, height - cfg.TOOLBAR_HEIGHT)
        return min(width, screen_w), min(height, screen_h)

    def _build_buttons(self):
        """Create the size, Clear and Reset buttons."""
        x, y, h, gap = cfg.MARGIN + 46, 54, 30, 8

        for n in cfg.GRID_SIZE_OPTIONS:
            self.buttons.append(
                Button(
                    (x, y, 46, h),
                    str(n),
                    callback=lambda n=n: self.game.resize(n),
                    is_active=lambda n=n: self.game.size == n,
                )
            )
            x += 46 + gap

        x += 16  # a little breathing room before the action buttons
        self.buttons.append(
            Button((x, y, 74, h), "Clear", callback=self.game.clear_board)
        )
        x += 74 + gap
        self.buttons.append(
            Button((x, y, 74, h), "Reset", callback=self.game.reset)
        )

    # ----------------------------------------------------------- geometry
    def _grid_metrics(self):
        """Find the board position and cell size, centred below the toolbar.

        Returns:
            tuple[int, int, int]: (x, y, cell_size); x, y is the top-left.
        """
        size = self.game.size
        width, height = self.screen.get_size()
        avail_w = width - 2 * cfg.MARGIN
        avail_h = height - cfg.TOOLBAR_HEIGHT - 2 * cfg.MARGIN
        side = min(avail_w, avail_h)
        cell = max(1, side // size)
        grid_px = cell * size
        origin_x = cfg.MARGIN + (avail_w - grid_px) // 2
        origin_y = cfg.TOOLBAR_HEIGHT + cfg.MARGIN + (avail_h - grid_px) // 2
        return origin_x, origin_y, cell

    def _cell_at(self, pos):
        """Find the cell under a screen point.

        Args:
            pos (tuple[int, int]): Mouse position.

        Returns:
            tuple[int, int] | None: (row, col), or None if off the board.
        """
        x, y = pos
        ox, oy, cell = self._grid_metrics()
        size = self.game.size
        if ox <= x < ox + cell * size and oy <= y < oy + cell * size:
            return (y - oy) // cell, (x - ox) // cell
        return None

    def _cell_font(self, cell):
        """Return a cached font that fits numbers in a cell.

        Args:
            cell (int): Cell size in pixels.

        Returns:
            pygame.font.Font: The font.
        """
        if cell not in self._cell_fonts:
            self._cell_fonts[cell] = pygame.font.SysFont(
                "consolas", max(10, int(cell * 0.7))
            )
        return self._cell_fonts[cell]

    # --------------------------------------------------------------- colour
    @staticmethod
    def _value_color(value):
        """Pick a cell colour: brighter for bigger numbers, up to HEAT_CAP.

        Args:
            value (int): The cell's number.

        Returns:
            tuple[int, int, int]: (red, green, blue).
        """
        if value <= 0:
            return cfg.COLOR_EMPTY
        t = min(value, cfg.HEAT_CAP) / cfg.HEAT_CAP
        lo, hi = cfg.COLOR_HEAT_LOW, cfg.COLOR_HEAT_HIGH
        return tuple(int(lo[i] + (hi[i] - lo[i]) * t) for i in range(3))

    @staticmethod
    def _contrast_text(bg):
        """Pick dark or light text, whichever reads better on bg.

        Args:
            bg (tuple[int, int, int]): Background colour.

        Returns:
            tuple[int, int, int]: Text colour.
        """
        luminance = 0.299 * bg[0] + 0.587 * bg[1] + 0.114 * bg[2]
        return (16, 20, 28) if luminance > 140 else (232, 236, 242)

    # ----------------------------------------------------------- per-frame
    def update(self):
        """Step the clear flash forward one frame."""
        if self.flash_frames > 0:
            self.flash_frames -= 1

    def draw(self):
        """Draw one frame: background, toolbar and board."""
        self.screen.fill(cfg.COLOR_BG)
        self._draw_toolbar()
        self._draw_grid()

    def _draw_toolbar(self):
        """Draw the top bar: title, hint, score and buttons."""
        width = self.screen.get_width()
        bar = pygame.Rect(0, 0, width, cfg.TOOLBAR_HEIGHT)
        pygame.draw.rect(self.screen, cfg.COLOR_TOOLBAR, bar)
        pygame.draw.line(
            self.screen, cfg.COLOR_PANEL_BORDER,
            (0, cfg.TOOLBAR_HEIGHT), (width, cfg.TOOLBAR_HEIGHT),
        )

        title = self.title_font.render("Fibonacci Grid ", True, cfg.COLOR_TEXT)
        self.screen.blit(title, (cfg.MARGIN, 18))

        hint = self.ui_font.render(
            " Click to grow. Match 5 Fibonacci numbers to clear",
            True, cfg.COLOR_TEXT_DIM,
        )
        # Start the hint where the title actually ends: the title's width
        # depends on which font the system provides.
        hint_x = cfg.MARGIN + title.get_width() + 12
        hint_y = 18 + (title.get_height() - hint.get_height()) // 2
        self.screen.blit(hint, (hint_x, hint_y))

        stats = self.ui_font.render(
            f"Grid {self.game.size}x{self.game.size}     "
            f"Clicks {self.game.clicks}/{cfg.MAX_CLICKS}     "
            f"Cleared {self.game.cells_cleared}/{cfg.WIN_CLEARED_CELLS}",
            True, cfg.COLOR_TEXT,
        )
        self.screen.blit(
            stats, stats.get_rect(topright=(width - cfg.MARGIN, 60))
        )

        label = self.button_font.render("Size", True, cfg.COLOR_TEXT_DIM)
        self.screen.blit(label, (cfg.MARGIN, 62))
        for button in self.buttons:
            button.draw(self.screen, self.button_font)

    def _draw_grid(self):
        """Draw the board, hover "+", clear flash and end message."""
        ox, oy, cell = self._grid_metrics()
        size = self.game.size
        cells = self.game.grid.cells
        show_numbers = cell >= cfg.NUMBER_MIN_CELL
        draw_lines = cell >= 6

        # cells (and their numbers)
        for r in range(size):
            for c in range(size):
                value = cells[r][c]
                rect = pygame.Rect(ox + c * cell, oy + r * cell, cell, cell)
                pygame.draw.rect(self.screen, self._value_color(value), rect)
                if draw_lines:
                    pygame.draw.rect(self.screen, cfg.COLOR_GRID_LINE, rect, 1)
                if show_numbers and value > 0:
                    font = self._cell_font(cell)
                    txt = font.render(
                        str(value), True,
                        self._contrast_text(self._value_color(value)),
                    )
                    self.screen.blit(txt, txt.get_rect(center=rect.center))

        self._draw_hover(ox, oy, cell, size)
        self._draw_flash(ox, oy, cell)
        self._draw_result(ox, oy, cell * size)

    def _draw_result(self, ox, oy, grid_px):
        """Show "You win" or "You lose" when the game ends.

        Args:
            ox (int): Board left edge.
            oy (int): Board top edge.
            grid_px (int): Board width in pixels.
        """
        status = self.game.status
        if status == "playing":
            return
        if status == "won":
            text, color = "You win!", cfg.COLOR_WIN
        else:
            text, color = "Out of clicks - you lose", cfg.COLOR_LOSE

        shade = pygame.Surface((grid_px, grid_px), pygame.SRCALPHA)
        shade.fill(cfg.COLOR_BANNER_BG)
        self.screen.blit(shade, (ox, oy))

        center = (ox + grid_px // 2, oy + grid_px // 2)
        msg = self.title_font.render(text, True, color)
        self.screen.blit(msg, msg.get_rect(center=(center[0], center[1] - 16)))
        sub = self.ui_font.render(
            "Press R to play again", True, cfg.COLOR_TEXT
        )
        self.screen.blit(sub, sub.get_rect(center=(center[0], center[1] + 18)))

    def _draw_hover(self, ox, oy, cell, size):
        """Shade the row and column under the mouse.

        Args:
            ox (int): Board left edge.
            oy (int): Board top edge.
            cell (int): Cell size in pixels.
            size (int): Rows and columns on the board.
        """
        if self.hover_cell is None:
            return
        row, col = self.hover_cell
        if not (0 <= row < size and 0 <= col < size):
            return  # stale hover after a resize

        overlay = pygame.Surface((cell * size, cell * size), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 0))
        pygame.draw.rect(
            overlay, cfg.COLOR_HOVER_OVERLAY,
            (0, row * cell, cell * size, cell),
        )
        pygame.draw.rect(
            overlay, cfg.COLOR_HOVER_OVERLAY,
            (col * cell, 0, cell, cell * size),
        )
        self.screen.blit(overlay, (ox, oy))

    def _draw_flash(self, ox, oy, cell):
        """Briefly outline the cells cleared last turn.

        Args:
            ox (int): Board left edge.
            oy (int): Board top edge.
            cell (int): Cell size in pixels.
        """
        if self.flash_frames <= 0:
            return
        for (r, c) in self.game.last_cleared:
            rect = pygame.Rect(ox + c * cell, oy + r * cell, cell, cell)
            pygame.draw.rect(self.screen, cfg.COLOR_FLASH, rect,
                             max(2, cell // 8))

    # --------------------------------------------------------------- input
    def handle_event(self, event):
        """Handle mouse moves, clicks, C (clear), R (reset) and resizing.

        Args:
            event (pygame.event.Event): The event.
        """
        if event.type == pygame.VIDEORESIZE:
            self.screen = pygame.display.get_surface()

        elif event.type == pygame.MOUSEMOTION:
            self.hover_cell = self._cell_at(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.buttons:
                if button.handle_click(event.pos):
                    return
            cell = self._cell_at(event.pos)
            if cell is None:
                return
            clicks_before = self.game.clicks
            if self.game.play(*cell):
                self.flash_frames = cfg.FLASH_FRAMES
            # Only sound when the click really played a turn (not after
            # the game is over).
            if self.click_sound and self.game.clicks > clicks_before:
                self.click_sound.play()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                self.game.clear_board()
            elif event.key == pygame.K_r:
                self.game.reset()
