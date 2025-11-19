"""Common utility functions for snake game."""

from config import config


def grid_to_pixel(grid_x: int, grid_y: int) -> tuple[int, int]:
    """Convert grid coordinates to pixel coordinates.

    Args:
        grid_x: Grid x coordinate.
        grid_y: Grid y coordinate.

    Returns:
        Pixel (x, y) coordinates at cell center.
    """
    cell_size = config.grid_cell_size
    offset_x = config.map_offset_x
    offset_y = config.map_offset_y

    pixel_x = offset_x + grid_x * cell_size + cell_size // 2
    pixel_y = offset_y + grid_y * cell_size + cell_size // 2

    return (pixel_x, pixel_y)


def grid_to_pixel_corner(grid_x: int, grid_y: int) -> tuple[int, int]:
    """Convert grid coordinates to pixel coordinates at top-left corner.

    Args:
        grid_x: Grid x coordinate.
        grid_y: Grid y coordinate.

    Returns:
        Pixel (x, y) coordinates at cell corner.
    """
    cell_size = config.grid_cell_size
    offset_x = config.map_offset_x
    offset_y = config.map_offset_y

    pixel_x = offset_x + grid_x * cell_size
    pixel_y = offset_y + grid_y * cell_size

    return (pixel_x, pixel_y)


def calculate_distance(pos1: tuple[int, int], pos2: tuple[int, int]) -> float:
    """Calculate Euclidean distance between two positions.

    Args:
        pos1: First position (x, y).
        pos2: Second position (x, y).

    Returns:
        Distance in grid cells.
    """
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    return (dx * dx + dy * dy) ** 0.5
