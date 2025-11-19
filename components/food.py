"""Food spawning and management system."""

from typing import TypedDict, Any
import random
import math
from config import config
from components.utils import calculate_distance


class Food(TypedDict):
    """Food data structure with position and movement state."""
    position: tuple[float, float]
    velocity: tuple[float, float]
    wander_timer: float


def create_food(position: tuple[int, int]) -> Food:
    """Create a food item at specified position.

    Args:
        position: Grid position (x, y) for the food.

    Returns:
        Food data structure.
    """
    food: Food = {
        'position': (float(position[0]), float(position[1])),
        'velocity': (0.0, 0.0),
        'wander_timer': 0.0,
    }
    return food


def is_valid_spawn_position(
    pos: tuple[float, float],
    state: dict[str, Any]
) -> bool:
    """Check if position is valid for food spawning using hitbox collision.

    Args:
        pos: Continuous position (x, y) in grid coordinates.
        state: Game state containing snake and food_items.

    Returns:
        True if position doesn't overlap with snake or other mice.
    """
    from components.collision import get_snake_head_hitbox, check_circle_overlap

    cell_size = config.grid_cell_size
    mouse_radius = cell_size // 2 * config.mouse_hitbox_scale

    # Convert to pixel position for hitbox check
    offset_x = config.map_offset_x
    offset_y = config.map_offset_y
    pixel_x = offset_x + pos[0] * cell_size + cell_size // 2
    pixel_y = offset_y + pos[1] * cell_size + cell_size // 2
    spawn_center = (pixel_x, pixel_y)

    # Check against snake head
    snake = state.get('snake')
    if snake:
        head_center, head_radius = get_snake_head_hitbox(snake)
        if check_circle_overlap(spawn_center, mouse_radius, head_center, head_radius):
            return False

        # Check against all snake body segments
        for segment in snake['segments']:
            seg_pixel_x = offset_x + segment[0] * cell_size + cell_size // 2
            seg_pixel_y = offset_y + segment[1] * cell_size + cell_size // 2
            seg_center = (seg_pixel_x, seg_pixel_y)
            seg_radius = cell_size // 2 * 0.75  # Body segments slightly smaller

            if check_circle_overlap(spawn_center, mouse_radius, seg_center, seg_radius):
                return False

    # Check against player two if exists
    player_two = state.get('player_two')
    if player_two:
        # Check player two head
        head_grid = player_two['segments'][0]
        head_pixel_x = offset_x + head_grid[0] * cell_size + cell_size // 2
        head_pixel_y = offset_y + head_grid[1] * cell_size + cell_size // 2
        head_center = (head_pixel_x, head_pixel_y)
        head_radius = cell_size // 2 * config.snake_head_hitbox_scale

        if check_circle_overlap(spawn_center, mouse_radius, head_center, head_radius):
            return False

        # Check player two body segments
        for segment in player_two['segments']:
            seg_pixel_x = offset_x + segment[0] * cell_size + cell_size // 2
            seg_pixel_y = offset_y + segment[1] * cell_size + cell_size // 2
            seg_center = (seg_pixel_x, seg_pixel_y)
            seg_radius = cell_size // 2 * 0.75

            if check_circle_overlap(spawn_center, mouse_radius, seg_center, seg_radius):
                return False

    # Check against existing mice
    food_items = state.get('food_items', [])
    for food_item in food_items:
        # Create temporary food dict to use get_mouse_hitbox
        from components.collision import get_mouse_hitbox
        mouse_center, existing_radius = get_mouse_hitbox(food_item)
        if check_circle_overlap(spawn_center, mouse_radius, mouse_center, existing_radius):
            return False

    return True


def spawn_food_items(state: dict[str, Any]) -> None:
    """Spawn a single food item at a valid random position.

    Args:
        state: Game state to update with new food item.
    """
    max_attempts = 100
    map_width = config.map_size_width
    map_height = config.map_size_height

    # Pre-spawn validation: calculate available cells
    total_cells = map_width * map_height
    
    # Count occupied cells
    occupied_cells = 0
    snake = state.get('snake')
    if snake:
        occupied_cells += len(snake['segments'])
    
    player_two = state.get('player_two')
    if player_two:
        occupied_cells += len(player_two['segments'])
    
    food_items = state.get('food_items', [])
    occupied_cells += len(food_items)
    
    available_cells = total_cells - occupied_cells
    
    # Early exit if no space available
    if available_cells <= 0:
        if config.debug_mode:
            print(f'[FOOD] WARNING: No empty cells available (total={total_cells}, occupied={occupied_cells}), skipping spawn')
        return

    for attempt in range(max_attempts):
        x = float(random.randint(0, map_width - 1))
        y = float(random.randint(0, map_height - 1))
        pos = (x, y)

        if is_valid_spawn_position(pos, state):
            food = create_food((int(x), int(y)))
            if 'food_items' not in state:
                state['food_items'] = []
            state['food_items'].append(food)

            if config.debug_mode:
                print(f'[FOOD] Spawned at {pos}, total_count={len(state["food_items"])}')

            # Check for stacking after spawn and resolve if needed
            food_items = state.get('food_items', [])
            collisions = detect_food_collisions(food_items)
            if collisions:
                resolve_food_stacking(state, collisions)

            return

    # Deadlock prevention: log warning and skip spawning
    if config.debug_mode:
        print(f'[FOOD] WARNING: Failed to spawn after {max_attempts} attempts ({available_cells} cells theoretically available) - skipping spawn')


def get_required_food_count(score: int) -> int:
    """Calculate required food count based on configuration and score.

    Args:
        score: Current game score.

    Returns:
        Number of food items that should exist.
    """
    food_count_config = config.food_count

    if callable(food_count_config):
        required = food_count_config(score)
    else:
        required = food_count_config

    return max(1, required)


def update_movement(state: dict[str, Any], delta_time: float) -> None:
    """Update food movement with wander and flee behaviors.

    Args:
        state: Game state containing food items and snake.
        delta_time: Time elapsed since last frame in seconds.
    """
    if not config.enable_food_movement:
        return

    food_items = state.get('food_items', [])
    snake = state.get('snake')

    if not snake:
        return

    snake_head = snake['segments'][0]
    snake_speed = snake['speed']

    # Calculate max speeds based on current snake speed (dynamically updated each frame)
    # Using much lower multipliers because food moves continuously while snake moves discretely
    max_flee_speed = snake_speed * 0.3
    wander_speed = snake_speed * 0.1

    flee_distance = 8.0
    wander_change_interval = 2.0

    if config.debug_mode and len(food_items) > 0:
        print(f'[FOOD] snake_speed={snake_speed:.2f}, max_flee={max_flee_speed:.2f}, wander={wander_speed:.2f}, delta_time={delta_time:.4f}')

    map_width = config.map_size_width
    map_height = config.map_size_height

    for food_item in food_items:
        food_x, food_y = food_item['position']
        distance_to_snake = calculate_distance((food_x, food_y), snake_head)

        if distance_to_snake < flee_distance:
            # Calculate flee direction away from snake
            dx = food_x - snake_head[0]
            dy = food_y - snake_head[1]
            dist = max(distance_to_snake, 0.1)
            flee_dir_x = dx / dist
            flee_dir_y = dy / dist

            # Set velocity in cells per second
            vel_x = flee_dir_x * max_flee_speed
            vel_y = flee_dir_y * max_flee_speed

            # Clamp velocity magnitude to max_flee_speed
            velocity_magnitude = (vel_x * vel_x + vel_y * vel_y) ** 0.5
            if velocity_magnitude > max_flee_speed:
                vel_x = (vel_x / velocity_magnitude) * max_flee_speed
                vel_y = (vel_y / velocity_magnitude) * max_flee_speed

            food_item['velocity'] = (vel_x, vel_y)
            behavior = 'flee'
        else:
            food_item['wander_timer'] += delta_time

            if food_item['wander_timer'] >= wander_change_interval:
                food_item['wander_timer'] = 0.0

                # Generate random wander direction
                angle = random.uniform(0, 2 * 3.14159)
                wander_dir_x = (angle * 1000 % 1000 - 500) / 500
                wander_dir_y = ((angle * 1234 + 567) % 1000 - 500) / 500
                length = (wander_dir_x * wander_dir_x + wander_dir_y * wander_dir_y) ** 0.5
                if length > 0:
                    wander_dir_x /= length
                    wander_dir_y /= length

                # Set velocity in cells per second
                vel_x = wander_dir_x * wander_speed
                vel_y = wander_dir_y * wander_speed

                # Clamp velocity magnitude to wander_speed
                velocity_magnitude = (vel_x * vel_x + vel_y * vel_y) ** 0.5
                if velocity_magnitude > wander_speed:
                    vel_x = (vel_x / velocity_magnitude) * wander_speed
                    vel_y = (vel_y / velocity_magnitude) * wander_speed

                food_item['velocity'] = (vel_x, vel_y)

            behavior = 'wander'

        # Update position using velocity * delta_time (proper delta time integration)
        vel_x, vel_y = food_item['velocity']
        old_x, old_y = food_x, food_y
        new_x = food_x + vel_x * delta_time
        new_y = food_y + vel_y * delta_time

        # Clamp to map boundaries
        new_x = max(0.0, min(float(map_width - 1), new_x))
        new_y = max(0.0, min(float(map_height - 1), new_y))

        # Store as float to maintain sub-pixel precision
        food_item['position'] = (new_x, new_y)

        if config.debug_mode and behavior == 'flee' and random.random() < 0.05:
            delta_x = new_x - old_x
            delta_y = new_y - old_y
            print(f'[FOOD] FLEE: old=({old_x:.2f},{old_y:.2f}) new=({new_x:.2f},{new_y:.2f}) delta=({delta_x:.3f},{delta_y:.3f}) vel=({vel_x:.2f},{vel_y:.2f})')

    # After all movement, resolve overlaps
    resolve_mouse_overlaps(state, delta_time)

    # Check for grid-based stacking and resolve
    collisions = detect_food_collisions(food_items)
    if collisions:
        resolve_food_stacking(state, collisions)


def detect_food_collisions(food_items: list[Food]) -> dict[tuple[int, int], list[int]]:
    """Find all grid positions with multiple food items.

    Args:
        food_items: List of food items to check for collisions.

    Returns:
        Dictionary mapping position -> list of food indices at that position.
    """
    position_map: dict[tuple[int, int], list[int]] = {}

    for idx, food_item in enumerate(food_items):
        # Convert float position to grid cell
        grid_x = int(food_item['position'][0])
        grid_y = int(food_item['position'][1])
        grid_pos = (grid_x, grid_y)

        if grid_pos not in position_map:
            position_map[grid_pos] = []
        position_map[grid_pos].append(idx)

    # Filter to only positions with multiple food items
    collisions = {pos: indices for pos, indices in position_map.items() if len(indices) > 1}

    return collisions


def find_adjacent_empty_cell(
    position: tuple[int, int],
    state: dict[str, Any],
    prefer_away_from_snake: bool = True,
    max_radius: int = 3
) -> tuple[int, int] | None:
    """Find nearest empty cell, preferring cells away from snake if possible.

    Args:
        position: Current food position.
        state: Game state with snake position.
        prefer_away_from_snake: If True, prioritize cells away from snake.
        max_radius: Maximum search radius.

    Returns:
        Empty cell position, or None if no cells available.
    """
    snake = state.get('snake')
    food_items = state.get('food_items', [])
    map_width = config.map_size_width
    map_height = config.map_size_height

    # Get snake head position for distance calculation
    snake_head = snake['segments'][0] if snake else None

    # Build set of occupied positions
    occupied: set[tuple[int, int]] = set()
    if snake:
        occupied.update(snake['segments'])

    player_two = state.get('player_two')
    if player_two:
        occupied.update(player_two['segments'])

    # Add food positions
    for food_item in food_items:
        grid_x = int(food_item['position'][0])
        grid_y = int(food_item['position'][1])
        occupied.add((grid_x, grid_y))

    # Search in expanding radius
    for radius in range(1, max_radius + 1):
        candidates: list[tuple[int, int, float]] = []

        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                # Only check cells at current radius (manhattan distance)
                if abs(dx) + abs(dy) != radius:
                    continue

                check_x = position[0] + dx
                check_y = position[1] + dy

                # Check bounds
                if check_x < 0 or check_x >= map_width or check_y < 0 or check_y >= map_height:
                    continue

                check_pos = (check_x, check_y)

                # Check if occupied
                if check_pos in occupied:
                    continue

                # Calculate distance from snake head
                if prefer_away_from_snake and snake_head:
                    dist_to_snake = calculate_distance(check_pos, snake_head)
                    candidates.append((check_x, check_y, dist_to_snake))
                else:
                    candidates.append((check_x, check_y, 0.0))

        # If we found candidates, return the best one
        if candidates:
            if prefer_away_from_snake and snake_head:
                # Sort by distance from snake (descending)
                candidates.sort(key=lambda c: c[2], reverse=True)
            return (candidates[0][0], candidates[0][1])

    return None


def resolve_food_stacking(
    state: dict[str, Any],
    collisions: dict[tuple[int, int], list[int]]
) -> None:
    """Reposition stacked food items to adjacent empty cells.

    For each collision:
    1. Keep first food item at current position
    2. For other food items, attempt to flee from snake to adjacent cells
    3. If no empty cells away from snake, find any adjacent empty cell
    4. Food items can cluster near each other, just not in same cell
    5. If no empty cells, try expanding search radius

    Args:
        state: Game state containing food items.
        collisions: Dictionary mapping positions to list of food indices.
    """
    food_items = state.get('food_items', [])

    for position, indices in collisions.items():
        # Keep first food at position, reposition others
        for idx in indices[1:]:
            food_item = food_items[idx]

            # Try to find adjacent empty cell away from snake
            new_pos = find_adjacent_empty_cell(position, state, prefer_away_from_snake=True)

            if new_pos:
                food_item['position'] = (float(new_pos[0]), float(new_pos[1]))
                if config.debug_mode:
                    print(f'[FOOD] Repositioned food {idx} from {position} to {new_pos}')
            else:
                # No empty cells found, log warning
                if config.debug_mode:
                    print(f'[FOOD] WARNING: Could not reposition food {idx} at {position} - no empty cells')

    if config.debug_mode and collisions:
        print(f'[FOOD] Resolved {len(collisions)} stacking collisions')


def detect_mouse_overlaps(food_items: list[Food]) -> list[tuple[int, int]]:
    """Find all pairs of overlapping mice.

    Args:
        food_items: List of food items to check for overlaps.

    Returns:
        List of (index1, index2) tuples for overlapping mice.
    """
    from components.collision import get_mouse_hitbox, check_circle_overlap

    overlaps: list[tuple[int, int]] = []

    for i in range(len(food_items)):
        for j in range(i + 1, len(food_items)):
            center1, radius1 = get_mouse_hitbox(food_items[i])
            center2, radius2 = get_mouse_hitbox(food_items[j])

            if check_circle_overlap(center1, radius1, center2, radius2):
                overlaps.append((i, j))

    return overlaps


def apply_separation_force(
    food_item1: Food,
    food_item2: Food,
    delta_time: float
) -> None:
    """Push two overlapping mice apart.

    Applies a separation force that pushes mice away from each other
    while trying to maintain their current movement direction.

    Args:
        food_item1: First food item to separate.
        food_item2: Second food item to separate.
        delta_time: Time elapsed since last frame in seconds.
    """
    pos1 = food_item1['position']
    pos2 = food_item2['position']

    # Calculate separation direction (from 2 to 1)
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    distance = math.sqrt(dx * dx + dy * dy)

    # Avoid division by zero
    if distance < 0.01:
        # Random separation if exactly overlapping
        angle = random.uniform(0, 2 * math.pi)
        dx = math.cos(angle)
        dy = math.sin(angle)
        distance = 1.0

    # Normalize separation direction
    sep_x = dx / distance
    sep_y = dy / distance

    # Calculate separation force magnitude
    # Stronger force when mice are closer
    cell_size = config.grid_cell_size
    min_distance = cell_size * 0.8  # Mice should stay at least 80% of cell apart
    overlap = max(0, min_distance - distance)

    separation_speed = 2.0  # cells per second
    force_magnitude = separation_speed * (overlap / min_distance)

    # Apply force to both mice (equal and opposite)
    force_x = sep_x * force_magnitude * delta_time
    force_y = sep_y * force_magnitude * delta_time

    # Update positions
    new_pos1 = (pos1[0] + force_x, pos1[1] + force_y)
    new_pos2 = (pos2[0] - force_x, pos2[1] - force_y)

    # Clamp to map boundaries
    map_width = config.map_size_width
    map_height = config.map_size_height

    food_item1['position'] = (
        max(0.0, min(float(map_width - 1), new_pos1[0])),
        max(0.0, min(float(map_height - 1), new_pos1[1]))
    )

    food_item2['position'] = (
        max(0.0, min(float(map_width - 1), new_pos2[0])),
        max(0.0, min(float(map_height - 1), new_pos2[1]))
    )

    if config.debug_mode:
        print(f'[FOOD] Separation applied: distance={distance:.2f}, force={force_magnitude:.2f}')


def resolve_mouse_overlaps(state: dict[str, Any], delta_time: float) -> None:
    """Separate all overlapping mice.

    Args:
        state: Game state containing food items.
        delta_time: Time elapsed since last frame in seconds.
    """
    food_items = state.get('food_items', [])
    overlaps = detect_mouse_overlaps(food_items)

    for i, j in overlaps:
        apply_separation_force(food_items[i], food_items[j], delta_time)

    if config.debug_mode and overlaps:
        print(f'[FOOD] Resolved {len(overlaps)} mouse overlaps')


def on_food_eaten(state: dict[str, Any]) -> None:
    """Handle food consumption and spawn additional food if needed.

    Args:
        state: Game state to update.
    """
    state['score'] = state.get('score', 0) + 1
    score = state['score']

    required_count = get_required_food_count(score)
    current_count = len(state.get('food_items', []))

    if config.debug_mode:
        print(f'[FOOD] Food eaten! Score={score}, required={required_count}, current={current_count}')

    while len(state.get('food_items', [])) < required_count:
        spawn_food_items(state)

    if config.debug_mode:
        final_count = len(state.get('food_items', []))
        print(f'[FOOD] After spawning: total_count={final_count}')
