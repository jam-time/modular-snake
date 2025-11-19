"""Test bite animation functionality."""

from components.enhanced_visuals import trigger_bite_animation, update_bite_animation, BiteState
from components.snake import create_snake


def test_bite_state_creation():
    """Test that BiteState is created correctly."""
    snake = create_snake((10, 10), (1, 0))
    bite_pos = (100.0, 100.0)

    trigger_bite_animation(snake, bite_pos)

    assert 'bite_state' in snake
    bite_state = snake['bite_state']
    assert bite_state['active'] is True
    assert bite_state['progress'] == 0.0
    assert bite_state['bite_position'] == bite_pos
    assert bite_state['wave_count'] == 5
    assert bite_state['duration'] == 0.5

    print('[TEST] Bite state creation: PASSED')


def test_bite_animation_progress():
    """Test that bite animation progresses correctly."""
    snake = create_snake((10, 10), (1, 0))
    trigger_bite_animation(snake, (100.0, 100.0))

    bite_state = snake['bite_state']
    assert bite_state['active'] is True
    assert bite_state['progress'] == 0.0

    update_bite_animation(snake, 0.25)
    assert bite_state['progress'] == 0.5
    assert bite_state['active'] is True

    update_bite_animation(snake, 0.25)
    assert bite_state['active'] is False
    assert bite_state['progress'] == 0.0

    print('[TEST] Bite animation progress: PASSED')


def test_bite_animation_deactivation():
    """Test that bite animation deactivates after completion."""
    snake = create_snake((10, 10), (1, 0))
    trigger_bite_animation(snake, (100.0, 100.0))

    update_bite_animation(snake, 0.6)

    bite_state = snake['bite_state']
    assert bite_state['active'] is False
    assert bite_state['progress'] == 0.0

    print('[TEST] Bite animation deactivation: PASSED')


if __name__ == '__main__':
    test_bite_state_creation()
    test_bite_animation_progress()
    test_bite_animation_deactivation()
    print('\n[TEST] All bite animation tests passed! ✨')
