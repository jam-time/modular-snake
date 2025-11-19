"""Test food spawning and management."""

from components.food import (
    create_food,
    is_valid_spawn_position,
    spawn_food_items,
    get_required_food_count,
    on_food_eaten,
)
from components.snake import create_snake
from config import config


def test_food_creation():
    """Test basic food creation."""
    food = create_food((5, 5))
    assert food['position'] == (5, 5)
    assert food['velocity'] == (0.0, 0.0)
    assert food['wander_timer'] == 0.0
    print('✓ Food creation works')


def test_valid_spawn_position():
    """Test spawn position validation."""
    snake = create_snake((10, 10), (1, 0))
    state = {'snake': snake, 'food_items': []}

    assert not is_valid_spawn_position((10, 10), state)
    assert not is_valid_spawn_position((9, 10), state)
    assert is_valid_spawn_position((5, 5), state)
    print('✓ Spawn position validation works')


def test_spawn_food():
    """Test food spawning."""
    snake = create_snake((10, 10), (1, 0))
    state = {'snake': snake, 'food_items': []}

    spawn_food_items(state)
    assert len(state['food_items']) == 1
    assert state['food_items'][0]['position'] not in snake['segments']
    print('✓ Food spawning works')


def test_required_food_count():
    """Test food count calculation."""
    config.food_count = 3
    assert get_required_food_count(0) == 3
    assert get_required_food_count(5) == 3

    config.food_count = lambda score: score + 1
    assert get_required_food_count(0) == 1
    assert get_required_food_count(5) == 6

    config.food_count = 1
    print('✓ Food count calculation works')


def test_on_food_eaten():
    """Test food eaten handler."""
    config.food_count = 2
    snake = create_snake((10, 10), (1, 0))
    state = {'snake': snake, 'food_items': [], 'score': 0}

    spawn_food_items(state)
    assert len(state['food_items']) == 1

    state['food_items'].pop()
    on_food_eaten(state)

    assert state['score'] == 1
    assert len(state['food_items']) == 2
    print('✓ Food eaten handler works')


if __name__ == '__main__':
    config.debug_mode = False

    test_food_creation()
    test_valid_spawn_position()
    test_spawn_food()
    test_required_food_count()
    test_on_food_eaten()

    print('\n🎉 All food tests passed!')
