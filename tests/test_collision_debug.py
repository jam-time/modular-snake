"""Test collision detection debug logging."""

from components.snake import create_snake
from components.food import create_food
from components.collision import (
    check_wall_collision,
    check_self_collision,
    check_food_collision,
    check_player_collision,
    check_collisions
)
from config import config


def main():
    """Test debug logging for collision detection."""
    print('=== Testing Collision Debug Logging ===\n')
    
    config.debug_mode = True
    
    print('1. Wall collision:')
    snake = create_snake((5, 5), (1, 0))
    snake['segments'][0] = (-1, 5)
    check_wall_collision(snake)
    
    print('\n2. Self collision:')
    snake = create_snake((5, 5), (1, 0))
    snake['segments'][0] = snake['segments'][2]
    check_self_collision(snake)
    
    print('\n3. Food collision:')
    snake = create_snake((5, 5), (1, 0))
    food_items = [create_food((5, 5))]
    check_food_collision(snake, food_items)
    
    print('\n4. Player collision:')
    snake1 = create_snake((5, 5), (1, 0))
    snake2 = create_snake((10, 10), (-1, 0))
    snake1['segments'][0] = snake2['segments'][1]
    check_player_collision(snake1, snake2)
    
    print('\n5. Integrated collision check (wall):')
    state = {
        'snake': create_snake((5, 5), (1, 0)),
        'food_items': [],
        'game_over': False,
        'score': 0
    }
    state['snake']['segments'][0] = (-1, 5)
    check_collisions(state)
    
    print('\n6. Integrated collision check (food eaten):')
    state = {
        'snake': create_snake((5, 5), (1, 0)),
        'food_items': [create_food((5, 5))],
        'game_over': False,
        'score': 0
    }
    check_collisions(state)
    
    print('\n✅ Debug logging test complete!')


if __name__ == '__main__':
    main()
