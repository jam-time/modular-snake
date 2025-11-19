"""Test wavelength scaling with snake length."""

import math
from components.enhanced_visuals import calculate_sine_wave_offset_for_segment


def test_wavelength_scales_with_length():
    """Test that wavelength adjusts based on snake length."""
    wave_phase = 0.0

    print('\n=== Short Snake (5 segments) ===')
    short_segments = 5
    for i in range(short_segments):
        offset = calculate_sine_wave_offset_for_segment(i, short_segments, wave_phase)
        print(f'Segment {i}: offset = {offset:.2f}')

    print('\n=== Medium Snake (10 segments) ===')
    medium_segments = 10
    for i in range(medium_segments):
        offset = calculate_sine_wave_offset_for_segment(i, medium_segments, wave_phase)
        print(f'Segment {i}: offset = {offset:.2f}')

    print('\n=== Long Snake (20 segments) ===')
    long_segments = 20
    for i in range(long_segments):
        offset = calculate_sine_wave_offset_for_segment(i, long_segments, wave_phase)
        print(f'Segment {i}: offset = {offset:.2f}')


if __name__ == '__main__':
    test_wavelength_scales_with_length()
