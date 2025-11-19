"""Tests for sine wave interpolation in snake rendering."""

import math
import pytest
from components.enhanced_visuals import (
    calculate_sine_wave_offset_for_segment,
    calculate_segment_direction_vector,
    calculate_perpendicular_vector
)


def test_sine_wave_offset_head_is_zero():
    """Head segment should have zero sine offset."""
    offset = calculate_sine_wave_offset_for_segment(0, 10, 0.0)
    assert offset == 0.0


def test_sine_wave_offset_increases_along_body():
    """Sine offset should vary along the body."""
    wave_phase = 0.0
    total_segments = 10

    offset_1 = calculate_sine_wave_offset_for_segment(1, total_segments, wave_phase)
    offset_2 = calculate_sine_wave_offset_for_segment(2, total_segments, wave_phase)
    offset_5 = calculate_sine_wave_offset_for_segment(5, total_segments, wave_phase)

    print(f'Offset at segment 1: {offset_1:.2f}')
    print(f'Offset at segment 2: {offset_2:.2f}')
    print(f'Offset at segment 5: {offset_5:.2f}')

    assert offset_1 != 0.0


def test_sine_wave_changes_with_phase():
    """Sine offset should change as wave phase changes."""
    segment_index = 5
    total_segments = 10

    offset_phase_0 = calculate_sine_wave_offset_for_segment(segment_index, total_segments, 0.0)
    offset_phase_pi = calculate_sine_wave_offset_for_segment(segment_index, total_segments, math.pi)

    print(f'Offset at phase 0: {offset_phase_0:.2f}')
    print(f'Offset at phase π: {offset_phase_pi:.2f}')

    assert offset_phase_0 != offset_phase_pi


def test_direction_vector_horizontal():
    """Test direction vector for horizontal snake."""
    segments = [(5, 5), (4, 5), (3, 5), (2, 5)]

    dir_0 = calculate_segment_direction_vector(0, segments)
    dir_1 = calculate_segment_direction_vector(1, segments)

    print(f'Direction at segment 0: {dir_0}')
    print(f'Direction at segment 1: {dir_1}')

    assert dir_0 == (1.0, 0.0)
    assert dir_1 == (1.0, 0.0)


def test_direction_vector_vertical():
    """Test direction vector for vertical snake."""
    segments = [(5, 5), (5, 4), (5, 3), (5, 2)]

    dir_0 = calculate_segment_direction_vector(0, segments)
    dir_1 = calculate_segment_direction_vector(1, segments)

    print(f'Direction at segment 0: {dir_0}')
    print(f'Direction at segment 1: {dir_1}')

    assert dir_0 == (0.0, 1.0)
    assert dir_1 == (0.0, 1.0)


def test_direction_vector_at_corner():
    """Test direction vector when snake turns."""
    segments = [(5, 5), (4, 5), (3, 5), (3, 4), (3, 3)]

    dir_2 = calculate_segment_direction_vector(2, segments)
    dir_3 = calculate_segment_direction_vector(3, segments)

    print(f'Direction at segment 2 (before turn): {dir_2}')
    print(f'Direction at segment 3 (at turn): {dir_3}')


def test_perpendicular_vector():
    """Test perpendicular vector calculation."""
    perp_right = calculate_perpendicular_vector((1.0, 0.0))
    perp_down = calculate_perpendicular_vector((0.0, 1.0))
    perp_left = calculate_perpendicular_vector((-1.0, 0.0))
    perp_up = calculate_perpendicular_vector((0.0, -1.0))

    print(f'Perpendicular to right (1,0): {perp_right}')
    print(f'Perpendicular to down (0,1): {perp_down}')
    print(f'Perpendicular to left (-1,0): {perp_left}')
    print(f'Perpendicular to up (0,-1): {perp_up}')

    assert perp_right == (0.0, 1.0)
    assert perp_down == (-1.0, 0.0)
    assert perp_left == (0.0, -1.0)
    assert perp_up == (1.0, 0.0)


def test_interpolation_scenario():
    """Test a realistic interpolation scenario."""
    segments = [(10, 5), (9, 5), (8, 5), (7, 5), (6, 5)]
    wave_phase = 0.0
    total_segments = len(segments)

    print('\n=== Interpolation Test ===')
    for i in range(len(segments) - 1):
        direction = calculate_segment_direction_vector(i, segments)
        perpendicular = calculate_perpendicular_vector(direction)
        sine_offset_current = calculate_sine_wave_offset_for_segment(i, total_segments, wave_phase)
        sine_offset_next = calculate_sine_wave_offset_for_segment(i + 1, total_segments, wave_phase)

        print(f'\nSegment {i} -> {i+1}:')
        print(f'  Direction: {direction}')
        print(f'  Perpendicular: {perpendicular}')
        print(f'  Sine offset current: {sine_offset_current:.2f}')
        print(f'  Sine offset next: {sine_offset_next:.2f}')

        for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
            interp_offset = sine_offset_current + (sine_offset_next - sine_offset_current) * t
            print(f'    t={t:.2f}: interpolated offset = {interp_offset:.2f}')


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
