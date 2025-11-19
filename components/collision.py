"""Collision detection system for snake game."""

import math
from typing import Any
from config import config
from components.snake import Snake, get_head_position, interpolate_position
from components.food import Food


def calculate_distance(pos1: tuple[float, float], pos2: tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points.
    
    Args:
        pos1: First position (x, y).
        pos2: Second position (x, y).
        
    Returns:
        Distance between the two points.
    """
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    return math.sqrt(dx * dx + dy * dy)


def check_circle_overlap(
    center1: tuple[float, float],
    radius1: float,
    center2: tuple[float, float],
    radius2: float
) -> bool:
    """Check if two circles overlap.
    
    Args:
        center1: Center of first circle (x, y).
        radius1: Radius of first circle.
        center2: Center of second circle (x, y).
        radius2: Radius of second circle.
        
    Returns:
        True if circles overlap (distance < sum of radii).
    """
    distance = calculate_distance(center1, center2)
    return distance < (radius1 + radius2)


def get_snake_head_hitbox(snake: Snake) -> tuple[tuple[float, float], float]:
    """Get snake head hitbox as (center, radius).
    
    Uses interpolated position for smooth collision detection.
    
    Args:
        snake: Snake to get hitbox for.
        
    Returns:
        Tuple of ((x, y), radius) where center is interpolated pixel position.
    """
    head_grid = snake['segments'][0]
    direction = snake['direction']
    next_head = (head_grid[0] + direction[0], head_grid[1] + direction[1])
    interp_progress = snake['interpolation']
    
    interp_grid = interpolate_position(head_grid, next_head, interp_progress)
    
    cell_size = config.grid_cell_size
    offset_x = config.map_offset_x
    offset_y = config.map_offset_y
    
    pixel_x = offset_x + interp_grid[0] * cell_size + cell_size // 2
    pixel_y = offset_y + interp_grid[1] * cell_size + cell_size // 2
    
    base_radius = cell_size // 2
    hitbox_scale = config.snake_head_hitbox_scale
    radius = base_radius * hitbox_scale
    
    return ((pixel_x, pixel_y), radius)


def get_mouse_hitbox(food_item: Food) -> tuple[tuple[float, float], float]:
    """Get mouse hitbox as (center, radius).
    
    Args:
        food_item: Food item to get hitbox for.
        
    Returns:
        Tuple of ((x, y), radius) where center is continuous pixel position.
    """
    grid_x, grid_y = food_item['position']
    cell_size = config.grid_cell_size
    offset_x = config.map_offset_x
    offset_y = config.map_offset_y
    
    pixel_x = offset_x + grid_x * cell_size + cell_size // 2
    pixel_y = offset_y + grid_y * cell_size + cell_size // 2
    
    base_radius = cell_size // 2
    hitbox_scale = config.mouse_hitbox_scale
    radius = base_radius * hitbox_scale
    
    return ((pixel_x, pixel_y), radius)


def check_wall_collision(snake: Snake) -> bool:
    """Check if snake head collides with map boundaries.

    Args:
        snake: Snake to check for wall collision.

    Returns:
        True if snake head is outside map bounds.
    """
    head_x, head_y = get_head_position(snake)
    map_width = config.map_size_width
    map_height = config.map_size_height

    collision = (
        head_x < 0 or
        head_x >= map_width or
        head_y < 0 or
        head_y >= map_height
    )

    if collision and config.debug_mode:
        print(f'[COLLISION] Wall collision at ({head_x}, {head_y}), bounds=({map_width}, {map_height})')

    return collision


def check_self_collision(snake: Snake) -> bool:
    """Check if snake head overlaps with its own body.

    Args:
        snake: Snake to check for self-collision.

    Returns:
        True if head position matches any body segment.
    """
    head = get_head_position(snake)
    body = snake['segments'][1:]

    collision = head in body

    if collision and config.debug_mode:
        print(f'[COLLISION] Self collision at {head}, body_length={len(body)}')

    return collision


def check_food_collision(snake: Snake, food_items: list[Food]) -> Food | None:
    """Check if snake head reaches any food item using hitbox collision.

    Args:
        snake: Snake to check.
        food_items: List of food items to check against.

    Returns:
        Food item that was eaten, or None if no collision.
    """
    head_center, head_radius = get_snake_head_hitbox(snake)

    for food in food_items:
        mouse_center, mouse_radius = get_mouse_hitbox(food)
        
        if check_circle_overlap(head_center, head_radius, mouse_center, mouse_radius):
            if config.debug_mode:
                distance = calculate_distance(head_center, mouse_center)
                threshold = head_radius + mouse_radius
                print(f'[COLLISION] Food eaten: distance={distance:.2f}, threshold={threshold:.2f}')
            return food

    return None


def check_player_collision(snake1: Snake, snake2: Snake) -> bool:
    """Check if two snakes collide with each other.

    Args:
        snake1: First snake to check.
        snake2: Second snake to check.

    Returns:
        True if either snake's head collides with the other snake's body.
    """
    head1 = get_head_position(snake1)
    head2 = get_head_position(snake2)

    collision_1_into_2 = head1 in snake2['segments']
    collision_2_into_1 = head2 in snake1['segments']

    collision = collision_1_into_2 or collision_2_into_1

    if collision and config.debug_mode:
        if collision_1_into_2:
            print(f'[COLLISION] Player 1 head at {head1} collided with Player 2')
        if collision_2_into_1:
            print(f'[COLLISION] Player 2 head at {head2} collided with Player 1')

    return collision


def check_collisions(state: dict[str, Any]) -> None:
    """Check all collision types and update game state accordingly.

    Args:
        state: Game state containing snake, food_items, and game_over flag.
    """
    if state.get('game_over', False):
        return

    snake = state.get('snake')
    if not snake:
        return

    player1_alive = True
    player2_alive = True

    if check_wall_collision(snake):
        player1_alive = False
        if config.debug_mode:
            print('[COLLISION] Player 1 wall collision')

    if check_self_collision(snake):
        player1_alive = False
        if config.debug_mode:
            print('[COLLISION] Player 1 self collision')

    food_items = state.get('food_items', [])
    eaten_food = check_food_collision(snake, food_items)
    if eaten_food and not eaten_food.get('being_eaten', False):
        from components.snake import add_segment, update_speed
        from components.food import on_food_eaten
        from components.enhanced_visuals import trigger_bite_animation

        food_grid_x, food_grid_y = eaten_food['position']
        cell_size = config.grid_cell_size
        offset_x = config.map_offset_x
        offset_y = config.map_offset_y

        food_pixel_x = offset_x + food_grid_x * cell_size + cell_size // 2
        food_pixel_y = offset_y + food_grid_y * cell_size + cell_size // 2

        eaten_food['being_eaten'] = True
        eaten_food['eaten_by'] = id(snake)

        trigger_bite_animation(snake, (food_pixel_x, food_pixel_y))

        add_segment(snake)
        on_food_eaten(state)
        update_speed(snake, state.get('score', 0))

        if config.debug_mode:
            print(f'[COLLISION] Food eaten, score={state.get("score", 0)}')

    tournament = state.get('tournament')
    is_multiplayer = config.secret_mode_alpha or (config.secret_mode_omega and tournament and tournament.get('phase') == 'playing')
    
    if is_multiplayer:
        player_two = state.get('player_two')
        if player_two:
            if check_wall_collision(player_two):
                player2_alive = False
                if config.debug_mode:
                    print('[COLLISION] Player 2 wall collision')

            if check_self_collision(player_two):
                player2_alive = False
                if config.debug_mode:
                    print('[COLLISION] Player 2 self collision')

            eaten_food_p2 = check_food_collision(player_two, food_items)
            if eaten_food_p2 and not eaten_food_p2.get('being_eaten', False):
                from components.snake import add_segment, update_speed
                from components.food import on_food_eaten
                from components.enhanced_visuals import trigger_bite_animation

                food_grid_x, food_grid_y = eaten_food_p2['position']
                cell_size = config.grid_cell_size
                offset_x = config.map_offset_x
                offset_y = config.map_offset_y

                food_pixel_x = offset_x + food_grid_x * cell_size + cell_size // 2
                food_pixel_y = offset_y + food_grid_y * cell_size + cell_size // 2

                eaten_food_p2['being_eaten'] = True
                eaten_food_p2['eaten_by'] = id(player_two)

                trigger_bite_animation(player_two, (food_pixel_x, food_pixel_y))

                add_segment(player_two)
                state['score_two'] = state.get('score_two', 0) + 1
                on_food_eaten(state)
                update_speed(player_two, state.get('score_two', 0))

                if config.debug_mode:
                    print(f'[COLLISION] Player 2 food eaten, score={state.get("score_two", 0)}')

            if check_player_collision(snake, player_two):
                head1 = get_head_position(snake)
                head2 = get_head_position(player_two)
                
                collision_1_into_2 = head1 in player_two['segments']
                collision_2_into_1 = head2 in snake['segments']
                
                if collision_1_into_2:
                    player1_alive = False
                    if config.debug_mode:
                        print('[COLLISION] Player 1 collided with Player 2')
                
                if collision_2_into_1:
                    player2_alive = False
                    if config.debug_mode:
                        print('[COLLISION] Player 2 collided with Player 1')
    
    if is_multiplayer:
        if not player1_alive or not player2_alive:
            state['game_over'] = True
            state['player1_alive'] = player1_alive
            state['player2_alive'] = player2_alive
            
            if config.debug_mode:
                print(f'[COLLISION] Game over: P1 alive={player1_alive}, P2 alive={player2_alive}')
    else:
        if not player1_alive:
            state['game_over'] = True
            if config.debug_mode:
                print('[COLLISION] Game over: single player death')
