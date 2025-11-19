"""Test eye positioning logic to debug placement issues."""

import math
import pygame
from config import config


def calculate_eye_positions(pixel_x: float, pixel_y: float, direction: tuple[int, int], look_at: tuple[float, float] | None = None):
    """Calculate eye positions based on direction.
    
    Returns:
        dict with eye1_pos, eye2_pos, backing1_pos, backing2_pos
    """
    cell_size = config.grid_cell_size
    eye_radius = cell_size // 9
    
    if look_at:
        angle_to_target = math.atan2(look_at[1] - pixel_y, look_at[0] - pixel_x)
    else:
        angle_to_target = math.atan2(direction[1], direction[0])
    
    top_offset = cell_size * 0.52
    eye_spacing = cell_size * 0.08
    backing_offset = eye_radius * 0.6
    
    perp_angle = angle_to_target + math.pi / 2
    spacing_angle = angle_to_target
    
    if not look_at and direction[0] != 0:
        perp_angle = -math.pi / 2
        spacing_angle = 0
    
    top_x = pixel_x + math.cos(perp_angle) * top_offset
    top_y = pixel_y + math.sin(perp_angle) * top_offset
    
    eye1_x = top_x - math.cos(spacing_angle) * eye_spacing
    eye1_y = top_y - math.sin(spacing_angle) * eye_spacing
    eye2_x = top_x + math.cos(spacing_angle) * eye_spacing
    eye2_y = top_y + math.sin(spacing_angle) * eye_spacing
    
    backing1_x = eye1_x - math.cos(spacing_angle) * backing_offset
    backing1_y = eye1_y - math.sin(spacing_angle) * backing_offset
    backing2_x = eye2_x - math.cos(spacing_angle) * backing_offset
    backing2_y = eye2_y - math.sin(spacing_angle) * backing_offset
    
    return {
        'angle_to_target': math.degrees(angle_to_target),
        'perp_angle': math.degrees(perp_angle),
        'spacing_angle': math.degrees(spacing_angle),
        'top': (top_x, top_y),
        'eye1': (eye1_x, eye1_y),
        'eye2': (eye2_x, eye2_y),
        'backing1': (backing1_x, backing1_y),
        'backing2': (backing2_x, backing2_y),
    }


def test_eye_positions():
    """Test eye positions for all four directions."""
    head_x, head_y = 400.0, 300.0
    
    print('\\n=== EYE POSITION TESTS ===\\n')
    
    # Test moving right
    print('Moving RIGHT (1, 0):')
    result = calculate_eye_positions(head_x, head_y, (1, 0))
    print(f'  angle_to_target: {result["angle_to_target"]:.1f}°')
    print(f'  perp_angle: {result["perp_angle"]:.1f}°')
    print(f'  spacing_angle: {result["spacing_angle"]:.1f}°')
    print(f'  top: ({result["top"][0]:.1f}, {result["top"][1]:.1f})')
    print(f'  eye1: ({result["eye1"][0]:.1f}, {result["eye1"][1]:.1f})')
    print(f'  eye2: ({result["eye2"][0]:.1f}, {result["eye2"][1]:.1f})')
    print(f'  Eye1 relative to head: ({result["eye1"][0] - head_x:.1f}, {result["eye1"][1] - head_y:.1f})')
    print(f'  Eye2 relative to head: ({result["eye2"][0] - head_x:.1f}, {result["eye2"][1] - head_y:.1f})')
    print()
    
    # Test moving left
    print('Moving LEFT (-1, 0):')
    result = calculate_eye_positions(head_x, head_y, (-1, 0))
    print(f'  angle_to_target: {result["angle_to_target"]:.1f}°')
    print(f'  perp_angle: {result["perp_angle"]:.1f}°')
    print(f'  spacing_angle: {result["spacing_angle"]:.1f}°')
    print(f'  top: ({result["top"][0]:.1f}, {result["top"][1]:.1f})')
    print(f'  eye1: ({result["eye1"][0]:.1f}, {result["eye1"][1]:.1f})')
    print(f'  eye2: ({result["eye2"][0]:.1f}, {result["eye2"][1]:.1f})')
    print(f'  Eye1 relative to head: ({result["eye1"][0] - head_x:.1f}, {result["eye1"][1] - head_y:.1f})')
    print(f'  Eye2 relative to head: ({result["eye2"][0] - head_x:.1f}, {result["eye2"][1] - head_y:.1f})')
    print()
    
    # Test moving down
    print('Moving DOWN (0, 1):')
    result = calculate_eye_positions(head_x, head_y, (0, 1))
    print(f'  angle_to_target: {result["angle_to_target"]:.1f}°')
    print(f'  perp_angle: {result["perp_angle"]:.1f}°')
    print(f'  spacing_angle: {result["spacing_angle"]:.1f}°')
    print(f'  top: ({result["top"][0]:.1f}, {result["top"][1]:.1f})')
    print(f'  eye1: ({result["eye1"][0]:.1f}, {result["eye1"][1]:.1f})')
    print(f'  eye2: ({result["eye2"][0]:.1f}, {result["eye2"][1]:.1f})')
    print(f'  Eye1 relative to head: ({result["eye1"][0] - head_x:.1f}, {result["eye1"][1] - head_y:.1f})')
    print(f'  Eye2 relative to head: ({result["eye2"][0] - head_x:.1f}, {result["eye2"][1] - head_y:.1f})')
    print()
    
    # Test moving up
    print('Moving UP (0, -1):')
    result = calculate_eye_positions(head_x, head_y, (0, -1))
    print(f'  angle_to_target: {result["angle_to_target"]:.1f}°')
    print(f'  perp_angle: {result["perp_angle"]:.1f}°')
    print(f'  spacing_angle: {result["spacing_angle"]:.1f}°')
    print(f'  top: ({result["top"][0]:.1f}, {result["top"][1]:.1f})')
    print(f'  eye1: ({result["eye1"][0]:.1f}, {result["eye1"][1]:.1f})')
    print(f'  eye2: ({result["eye2"][0]:.1f}, {result["eye2"][1]:.1f})')
    print(f'  Eye1 relative to head: ({result["eye1"][0] - head_x:.1f}, {result["eye1"][1] - head_y:.1f})')
    print(f'  Eye2 relative to head: ({result["eye2"][0] - head_x:.1f}, {result["eye2"][1] - head_y:.1f})')
    print()
    
    print('\\n=== EXPECTED RESULTS ===')
    print('Moving LEFT/RIGHT: Both eyes should have same Y (on top), different X')
    print('Moving UP/DOWN: Both eyes should have same X (on side), different Y')
    print()


if __name__ == '__main__':
    test_eye_positions()
