"""Configuration system with property-based validation."""

from typing import Callable


class Config:
    """Game configuration with automatic validation and value clamping."""

    def __init__(self) -> None:
        """Initialize configuration with default values."""
        self._window_width: int = 0
        self._window_height: int = 0
        self._fullscreen_mode: bool = False
        self._frame_rate: int = 60
        self._map_size: int = 30
        self._initial_speed: float = 10.0
        self._speed_factor: float = 1.5
        self._food_count: int | Callable[[int], int] = 1
        self._speed_calculation: Callable[[float, int], float] | None = None

        self.snake_head_hitbox_scale: float = 1.0
        self.mouse_hitbox_scale: float = 1.0

        self.enable_enhanced_visuals: bool = False
        self.enable_mouth_animation: bool = False
        self.enable_tongue_animation: bool = False
        self.enable_animated_food: bool = False
        self.enable_food_movement: bool = False

        self.secret_mode_alpha: bool = False
        self.secret_mode_omega: bool = False

        self.debug_mode: bool = True

        self.color_background: tuple[int, int, int] = (20, 20, 30)
        self.color_snake_body: tuple[int, int, int] = (50, 200, 50)
        self.color_snake_head: tuple[int, int, int] = (70, 220, 70)
        self.color_food: tuple[int, int, int] = (220, 50, 50)
        self.color_text: tuple[int, int, int] = (255, 255, 255)
        self.color_ui: tuple[int, int, int] = (100, 100, 120)

    @property
    def window_width(self) -> int:
        """Get window width in pixels."""
        return self._window_width

    @window_width.setter
    def window_width(self, value: int) -> None:
        """Set window width with minimum validation."""
        if value == 0:
            self._window_width = 0
        elif value < 400:
            if self.debug_mode:
                print(f'[CONFIG] Window width {value} clamped to minimum 400')
            self._window_width = 400
        else:
            self._window_width = value

    @property
    def window_height(self) -> int:
        """Get window height in pixels."""
        return self._window_height

    @window_height.setter
    def window_height(self, value: int) -> None:
        """Set window height with minimum validation."""
        if value == 0:
            self._window_height = 0
        elif value < 300:
            if self.debug_mode:
                print(f'[CONFIG] Window height {value} clamped to minimum 300')
            self._window_height = 300
        else:
            self._window_height = value

    @property
    def fullscreen_mode(self) -> bool:
        """Get fullscreen mode setting."""
        return self._fullscreen_mode

    @fullscreen_mode.setter
    def fullscreen_mode(self, value: bool) -> None:
        """Set fullscreen mode."""
        self._fullscreen_mode = value

    @property
    def map_size(self) -> int:
        """Get map size (grid squares on shorter side)."""
        return self._map_size

    @map_size.setter
    def map_size(self, value: int) -> None:
        """Set map size with minimum validation."""
        if value < 10:
            if self.debug_mode:
                print(f'[CONFIG] Map size {value} clamped to minimum 10')
            self._map_size = 10
        else:
            self._map_size = value

    @property
    def grid_cell_size(self) -> int:
        """Get grid cell size calculated from window and map size."""
        width = self._window_width if self._window_width > 0 else 800
        height = self._window_height if self._window_height > 0 else 600
        shorter_side = min(width, height)
        return shorter_side // self._map_size

    @property
    def map_size_width(self) -> int:
        """Get map width in grid cells."""
        width = self._window_width if self._window_width > 0 else 800
        return width // self.grid_cell_size

    @property
    def map_size_height(self) -> int:
        """Get map height in grid cells."""
        height = self._window_height if self._window_height > 0 else 600
        return height // self.grid_cell_size

    @property
    def frame_rate(self) -> int:
        """Get frame rate (fixed at 60 FPS)."""
        return 60

    @property
    def map_offset_x(self) -> int:
        """Get X offset to center map in window."""
        width = self._window_width if self._window_width > 0 else 800
        map_pixel_width = self.map_size_width * self.grid_cell_size
        return (width - map_pixel_width) // 2

    @property
    def map_offset_y(self) -> int:
        """Get Y offset to center map in window, accounting for score bar."""
        height = self._window_height if self._window_height > 0 else 600
        map_pixel_height = self.map_size_height * self.grid_cell_size
        score_bar_height = 50 if (self.secret_mode_alpha or self.secret_mode_omega) else 0
        available_height = height - score_bar_height
        return score_bar_height + (available_height - map_pixel_height) // 2

    @property
    def initial_speed(self) -> float:
        """Get initial snake speed in cells per second."""
        return self._initial_speed

    @initial_speed.setter
    def initial_speed(self, value: float) -> None:
        """Set initial speed with minimum validation."""
        if value < 1.0:
            if self.debug_mode:
                print(f"[CONFIG] Initial speed {value} clamped to minimum 1.0")
            self._initial_speed = 1.0
        else:
            self._initial_speed = value

    @property
    def speed_factor(self) -> float:
        """Get speed increase factor."""
        return self._speed_factor

    @speed_factor.setter
    def speed_factor(self, value: float) -> None:
        """Set speed factor with range validation."""
        if value < 1.0:
            if self.debug_mode:
                print(f"[CONFIG] Speed factor {value} clamped to minimum 1.0")
            self._speed_factor = 1.0
        elif value > 5.0:
            if self.debug_mode:
                print(f"[CONFIG] Speed factor {value} clamped to maximum 5.0")
            self._speed_factor = 5.0
        else:
            self._speed_factor = value

    @property
    def food_count(self) -> int | Callable[[int], int]:
        """Get food count (can be int or callable)."""
        if callable(self._food_count):
            return self._food_count
        return max(1, self._food_count)

    @food_count.setter
    def food_count(self, value: int | Callable[[int], int]) -> None:
        """Set food count (int or callable function)."""
        if callable(value):
            self._food_count = value
        else:
            if value < 1:
                if self.debug_mode:
                    print(f"[CONFIG] Food count {value} clamped to minimum 1")
                self._food_count = 1
            else:
                self._food_count = value

    @property
    def speed_calculation(self) -> Callable[[float, int], float]:
        """Get speed calculation function."""
        if callable(self._speed_calculation):
            return self._speed_calculation
        return lambda current_speed, score: current_speed + self._speed_factor

    @speed_calculation.setter
    def speed_calculation(self, value: Callable[[float, int], float] | None) -> None:
        """Set custom speed calculation function."""
        if callable(value):
            self._speed_calculation = value
        else:
            self._speed_calculation = None


config = Config()
