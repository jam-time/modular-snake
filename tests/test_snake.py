"""Quick test for snake component functionality."""

from components.snake import create_snake, set_direction, update_movement, add_segment, update_speed, get_head_position
from config import config

config.debug_mode = True

print('=== Testing Snake Component ===\n')

print('Test 1: Create snake')
snake = create_snake((10, 10), (1, 0))
print(f'Snake created with {len(snake["segments"])} segments')
print(f'Head at: {get_head_position(snake)}')
print(f'Direction: {snake["direction"]}')
print()

print('Test 2: Set direction (valid)')
set_direction(snake, (0, 1))
print(f'Next direction: {snake["next_direction"]}')
print()

print('Test 3: Try to reverse (should be prevented)')
set_direction(snake, (-1, 0))
print(f'Next direction still: {snake["next_direction"]} (should be (0, 1))')
print()

print('Test 4: Update movement')
delta = 1.0 / 60.0
for i in range(10):
    update_movement(snake, delta)
    if i == 0 or i == 9:
        print(f'Frame {i}: head={get_head_position(snake)}, interp={snake["interpolation"]:.2f}')
print()

print('Test 5: Add segment')
initial_length = len(snake['segments'])
add_segment(snake)
print(f'Length: {initial_length} -> {len(snake["segments"])}')
print()

print('Test 6: Update speed')
initial_speed = snake['speed']
update_speed(snake, 1)
print(f'Speed: {initial_speed:.2f} -> {snake["speed"]:.2f}')
print()

print('Test 7: Custom speed calculation')
config.speed_calculation = lambda speed, score: speed * 1.2
update_speed(snake, 2)
print(f'Speed with custom calc: {snake["speed"]:.2f}')
print()

print('=== All Tests Complete ===')
