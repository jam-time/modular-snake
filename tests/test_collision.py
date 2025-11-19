"""Test collision detection system."""

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


def test_wall_collision():
    """Test wall collision detection."""
    print('\n=== Testing Wall Collision ===')
    
    snake = create_snake((5, 5), (1, 0))
    assert not check_wall_collision(snake), 'Snake at (5,5) should not collide with walls'
    
    snake['segments'][0] = (-1, 5)
    assert check_wall_collision(snake), 'Snake at (-1,5) should collide with left wall'
    
    snake['segments'][0] = (config.map_size_width, 5)
    assert check_wall_collision(snake), 'Snake at edge should collide with right wall'
    
    snake['segments'][0] = (5, -1)
    assert check_wall_collision(snake), 'Snake at (5,-1) should collide with top wall'
    
    snake['segments'][0] = (5, config.map_size_height)
    assert check_wall_collision(snake), 'Snake at bottom edge should collide with bottom wall'
    
    print('✓ Wall collision tests passed')


def test_self_collision():
    """Test self-collision detection."""
    print('\n=== Testing Self Collision ===')
    
    snake = create_snake((5, 5), (1, 0))
    assert not check_self_collision(snake), 'New snake should not self-collide'
    
    snake['segments'][0] = snake['segments'][2]
    assert check_self_collision(snake), 'Snake head at body position should self-collide'
    
    print('✓ Self collision tests passed')


def test_food_collision():
    """Test food collision detection."""
    print('\n=== Testing Food Collision ===')
    
    snake = create_snake((5, 5), (1, 0))
    food1 = create_food((10, 10))
    food2 = create_food((5, 5))
    food_items = [food1, food2]
    
    eaten = check_food_collision(snake, food_items)
    assert eaten is not None, 'Snake at (5,5) should collide with food at (5,5)'
    assert eaten == food2, 'Should return the correct food item'
    
    snake['segments'][0] = (3, 3)
    eaten = check_food_collision(snake, food_items)
    assert eaten is None, 'Snake at (3,3) should not collide with food'
    
    print('✓ Food collision tests passed')


def test_player_collision():
    """Test multiplayer collision detection."""
    print('\n=== Testing Player Collision ===')
    
    snake1 = create_snake((5, 5), (1, 0))
    snake2 = create_snake((10, 10), (-1, 0))
    
    assert not check_player_collision(snake1, snake2), 'Separated snakes should not collide'
    
    snake1['segments'][0] = snake2['segments'][1]
    assert check_player_collision(snake1, snake2), 'Snake1 head at Snake2 body should collide'
    
    snake1['segments'][0] = (5, 5)
    snake2['segments'][0] = snake1['segments'][2]
    assert check_player_collision(snake1, snake2), 'Snake2 head at Snake1 body should collide'
    
    print('✓ Player collision tests passed')


def test_check_collisions_integration():
    """Test integrated collision checking."""
    print('\n=== Testing Integrated Collision System ===')
    
    state = {
        'snake': create_snake((5, 5), (1, 0)),
        'food_items': [create_food((10, 10))],
        'game_over': False,
        'score': 0
    }
    
    check_collisions(state)
    assert not state['game_over'], 'Game should not be over initially'
    
    state['snake']['segments'][0] = (-1, 5)
    check_collisions(state)
    assert state['game_over'], 'Game should be over after wall collision'
    
    state = {
        'snake': create_snake((5, 5), (1, 0)),
        'food_items': [create_food((5, 5))],
        'game_over': False,
        'score': 0
    }
    
    initial_length = len(state['snake']['segments'])
    check_collisions(state)
    assert len(state['snake']['segments']) == initial_length + 1, 'Snake should grow after eating'
    assert state['score'] == 1, 'Score should increase after eating'
    assert len(state['food_items']) >= 1, 'New food should spawn'
    
    print('✓ Integrated collision tests passed')


def main():
    """Run all collision tests."""
    print('Starting collision detection tests...')
    
    config.debug_mode = False
    
    test_wall_collision()
    test_self_collision()
    test_food_collision()
    test_player_collision()
    test_check_collisions_integration()
    
    print('\n✅ All collision detection tests passed!')


if __name__ == '__main__':
    main()
