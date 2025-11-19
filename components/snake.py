"""Snake entity and movement system."""

from typing import Any, TypedDict
from config import config


class SnakeVisualState(TypedDict):
    """Visual animation state for snake rendering."""
    wave_phase: float
    wave_speed: float


class Snake(TypedDict):
    """Snake data structure with movement state."""
    segments: list[tuple[int, int]]
    direction: tuple[int, int]
    next_direction: tuple[int, int]
    speed: float
    move_timer: float
    interpolation: float
    distance_moved: float
    tongue_extended: bool
    visual_state: SnakeVisualState
    tongue_state: dict[str, Any]


def create_snake(start_pos: tuple[int, int], direction: tuple[int, int]) -> Snake:
    """Initialize snake with 4 segments at starting position.

    Args:
        start_pos: Initial head position (x, y) in grid coordinates.
        direction: Initial movement direction (dx, dy).

    Returns:
        Snake data structure with 4 segments.
    """
    x, y = start_pos
    dx, dy = direction

    segments = [
        (x, y),
        (x - dx, y - dy),
        (x - 2 * dx, y - 2 * dy),
        (x - 3 * dx, y - 3 * dy),
    ]

    from components.enhanced_visuals import create_tongue_state

    snake: Snake = {
        'segments': segments,
        'direction': direction,
        'next_direction': direction,
        'speed': config.initial_speed,
        'move_timer': 0.0,
        'interpolation': 0.0,
        'distance_moved': 0.0,
        'tongue_extended': False,
        'visual_state': {
            'wave_phase': 0.0,
            'wave_speed': 8.0,
        },
        'tongue_state': create_tongue_state(),
    }

    if config.debug_mode:
        print(f'[SNAKE] Created at {start_pos} facing {direction}')
        print(f'[SNAKE] Initial segments: {segments}')
        print(f'[SNAKE] Initial speed: {snake["speed"]:.2f} cells/sec')

    return snake


def set_direction(snake: Snake, new_direction: tuple[int, int]) -> None:
    """Set snake's next direction with reversal prevention.

    Args:
        snake: Snake to update.
        new_direction: Desired direction (dx, dy).
    """
    current_dir = snake['direction']

    is_reversal = (
        new_direction[0] == -current_dir[0] and
        new_direction[1] == -current_dir[1]
    )

    if not is_reversal and new_direction != (0, 0):
        snake['next_direction'] = new_direction

        if config.debug_mode:
            print(f'[SNAKE] Direction queued: {new_direction}')


def update_movement(snake: Snake, delta_time: float) -> None:
    """Update snake movement with grid-based logic and frame interpolation.

    Args:
        snake: Snake to update.
        delta_time: Time elapsed since last frame in seconds.
    """
    snake['move_timer'] += delta_time

    time_per_cell = 1.0 / snake['speed']

    if snake['move_timer'] >= time_per_cell:
        snake['move_timer'] -= time_per_cell

        snake['direction'] = snake['next_direction']

        head_x, head_y = snake['segments'][0]
        dx, dy = snake['direction']
        new_head = (head_x + dx, head_y + dy)

        snake['segments'] = [new_head] + snake['segments'][:-1]

        snake['distance_moved'] += 1.0

        if config.debug_mode:
            print(f'[SNAKE] Moved to {new_head}, speed={snake["speed"]:.2f}, dir={snake["direction"]}')

    snake['interpolation'] = min(snake['move_timer'] / time_per_cell, 1.0)

    if config.debug_mode and snake['interpolation'] < 0.1:
        head = snake['segments'][0]
        print(f'[SNAKE] pos={head}, speed={snake["speed"]:.2f}, interp={snake["interpolation"]:.2f}')


def get_head_position(snake: Snake) -> tuple[int, int]:
    """Get current head grid coordinates.

    Args:
        snake: Snake to query.

    Returns:
        Head position (x, y) in grid coordinates.
    """
    return snake['segments'][0]


def interpolate_position(
    grid_pos: tuple[int, int],
    next_grid_pos: tuple[int, int],
    progress: float
) -> tuple[float, float]:
    """Calculate smooth position between grid cells for rendering.

    Args:
        grid_pos: Current grid cell (x, y).
        next_grid_pos: Next grid cell (x, y).
        progress: Interpolation progress from 0.0 to 1.0.

    Returns:
        Interpolated position (x, y) as floats.
    """
    x = grid_pos[0] + (next_grid_pos[0] - grid_pos[0]) * progress
    y = grid_pos[1] + (next_grid_pos[1] - grid_pos[1]) * progress
    return (x, y)


def update_speed(snake: Snake, score: int) -> None:
    """Update snake speed based on configuration and score.

    Args:
        snake: Snake to update.
        score: Current game score.
    """
    speed_calc = config.speed_calculation
    old_speed = snake['speed']
    new_speed = speed_calc(old_speed, score)
    snake['speed'] = new_speed

    if config.debug_mode:
        print(f'[SNAKE] Speed updated: {old_speed:.2f} -> {new_speed:.2f} (score={score})')


def add_segment(snake: Snake) -> None:
    """Add new segment to snake's tail for growth.

    Args:
        snake: Snake to grow.
    """
    tail = snake['segments'][-1]
    snake['segments'].append(tail)

    if config.debug_mode:
        print(f'[SNAKE] Segment added, new length: {len(snake["segments"])}')
