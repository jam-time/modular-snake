"""Enhanced visual rendering with circle-based snake and slithering animation."""

from typing import Any, TypedDict
import math
import pygame
from config import config


_mouse_sprite_cache: pygame.Surface | None = None


class SegmentRenderData(TypedDict):
    """Rendering data for a single snake segment."""
    base_x: float
    base_y: float
    render_x: float
    render_y: float
    sine_offset: float
    perpendicular: tuple[float, float]
    radius: int
    color: tuple[int, int, int]


class TongueState(TypedDict):
    """Tongue animation state for realistic flicking behavior."""
    phase: str
    timer: float
    extension_progress: float
    cooldown_timer: float


class BiteState(TypedDict):
    """Bite animation state for dramatic eating effect."""
    active: bool
    progress: float
    bite_position: tuple[float, float]
    wave_count: int
    duration: float


def create_tongue_state() -> TongueState:
    """Initialize tongue state with default values.

    Returns:
        TongueState with animation ready to start.
    """
    return {
        'phase': 'retracted',
        'timer': 0.0,
        'extension_progress': 0.0,
        'cooldown_timer': 0.0,
    }


def update_blink_animation(snake: dict[str, Any], delta_time: float) -> None:
    """Update eye blinking animation.

    Args:
        snake: Snake data structure.
        delta_time: Time elapsed since last frame in seconds.
    """
    if 'blink_state' not in snake:
        snake['blink_state'] = {
            'timer': 0.0,
            'eye1_closed': 0.0,
            'eye2_closed': 0.0
        }
    
    blink_state = snake['blink_state']
    blink_state['timer'] += delta_time
    
    blink_interval = 3.0
    blink_duration = 0.2
    eye2_offset = 0.1
    
    cycle_time = blink_state['timer'] % blink_interval
    
    if cycle_time < blink_duration:
        blink_state['eye1_closed'] = 1.0 - abs(cycle_time - blink_duration / 2) / (blink_duration / 2)
    else:
        blink_state['eye1_closed'] = 0.0
    
    cycle_time_eye2 = (blink_state['timer'] + eye2_offset) % blink_interval
    if cycle_time_eye2 < blink_duration:
        blink_state['eye2_closed'] = 1.0 - abs(cycle_time_eye2 - blink_duration / 2) / (blink_duration / 2)
    else:
        blink_state['eye2_closed'] = 0.0


def trigger_bite_animation(snake: dict[str, Any], bite_pos: tuple[float, float]) -> None:
    """Start bite animation at food consumption.

    Args:
        snake: Snake data structure to update.
        bite_pos: Pixel position where bite occurred (x, y).
    """
    base_duration = 0.5
    speed_factor = snake['speed'] / config.initial_speed
    duration = base_duration / max(speed_factor, 1.0)
    
    snake['bite_state'] = {
        'active': True,
        'progress': 0.0,
        'bite_position': bite_pos,
        'wave_count': 5,
        'duration': duration,
        'food_hidden': False
    }

    if config.debug_mode:
        print(f'[BITE] Animation triggered at {bite_pos}, duration={duration:.2f}s')


def update_wave_phase(visual_state: dict[str, float], delta_time: float) -> None:
    """Update wave phase to create traveling wave effect.

    Args:
        visual_state: Visual state dictionary with wave_phase and wave_speed.
        delta_time: Time elapsed since last frame in seconds.
    """
    visual_state['wave_phase'] += visual_state['wave_speed'] * delta_time
    visual_state['wave_phase'] %= (2 * math.pi)


def calculate_segment_direction_vector(
    segment_index: int,
    segments: list[tuple[int, int]]
) -> tuple[float, float]:
    """Calculate normalized direction vector for a segment.

    Args:
        segment_index: Index of segment (0 = head).
        segments: List of all segment positions.

    Returns:
        Normalized (x, y) direction vector.
    """
    if segment_index >= len(segments):
        return (1.0, 0.0)

    if segment_index == len(segments) - 1:
        if len(segments) > 1:
            prev_seg = segments[segment_index - 1]
            curr_seg = segments[segment_index]
            dx = prev_seg[0] - curr_seg[0]
            dy = prev_seg[1] - curr_seg[1]
        else:
            return (1.0, 0.0)
    else:
        curr_seg = segments[segment_index]
        next_seg = segments[segment_index + 1]
        dx = curr_seg[0] - next_seg[0]
        dy = curr_seg[1] - next_seg[1]

    length = math.sqrt(dx * dx + dy * dy)
    if length > 0:
        return (dx / length, dy / length)
    return (1.0, 0.0)


def calculate_perpendicular_vector(direction: tuple[float, float]) -> tuple[float, float]:
    """Calculate perpendicular vector (rotated 90 degrees).

    Args:
        direction: Direction vector (dx, dy).

    Returns:
        Perpendicular vector (-dy, dx).
    """
    dx, dy = direction
    return (-dy, dx)


def calculate_sine_wave_offset_for_segment(
    segment_index: int,
    total_segments: int,
    wave_phase: float,
    circle_index_in_segment: int = 0,
    circles_per_segment: int = 1
) -> float:
    """Calculate sine wave offset for a segment.

    Args:
        segment_index: Index of segment (0 = head).
        total_segments: Total number of segments.
        wave_phase: Current wave phase (radians).
        circle_index_in_segment: Index of circle within segment.
        circles_per_segment: Number of circles per segment.

    Returns:
        Offset distance in pixels (positive or negative).
    """
    base_amplitude = 8.0
    # Cap the effective segment count to prevent wavelength from getting too long
    effective_segments = min(total_segments, 12)
    wave_spacing = (2 * math.pi) / max(effective_segments, 3)

    if segment_index == 0:
        return 0.0

    phase_offset = segment_index * wave_spacing
    offset = base_amplitude * math.sin(wave_phase - phase_offset)
    return offset


def calculate_segment_radius(segment_index: int, total_segments: int) -> int:
    """Calculate radius for tapered body effect with tail tapering.

    Args:
        segment_index: Position of segment in snake body (0 = head).
        total_segments: Total number of segments in snake.

    Returns:
        Radius in pixels for this segment.
    """
    base_radius = config.grid_cell_size // 2
    
    if segment_index == 0:
        return base_radius
    
    scale_factor = 0.75
    
    if segment_index == total_segments - 1:
        scale_factor = 0.25
    
    radius = int(base_radius * scale_factor)
    return max(radius, config.grid_cell_size // 4)


def _darken_color(color: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    """Darken a color by a given factor.

    Args:
        color: RGB color tuple.
        factor: Darkening factor (0.0 = black, 1.0 = original).

    Returns:
        Darkened RGB color tuple.
    """
    return (
        int(color[0] * factor),
        int(color[1] * factor),
        int(color[2] * factor)
    )


def _draw_gradient_circle(
    screen: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    color: tuple[int, int, int],
    perpendicular: tuple[float, float] = (0.0, 1.0)
) -> None:
    """Draw a circle with simple shading for performance.

    Args:
        screen: Pygame surface to render on.
        center: Center position (x, y).
        radius: Circle radius in pixels.
        color: Base RGB color for the center.
        perpendicular: Direction perpendicular to snake (for gradient direction).
    """
    if radius <= 0:
        return

    cx, cy = center
    perp_x, perp_y = perpendicular

    layers = [
        (1.0, 0.4),
        (0.92, 0.5),
        (0.84, 0.6),
        (0.76, 0.8),
        (0.68, 1.0),
        (0.60, 1.15),
        (0.52, 1.25),
        (0.44, 1.35),
        (0.36, 1.45)
    ]

    for size_factor, brightness in layers:
        layer_radius = int(radius * size_factor)
        if layer_radius < 1:
            continue

        if brightness > 1.0:
            layer_color = (
                min(255, int(color[0] * brightness)),
                min(255, int(color[1] * brightness)),
                min(255, int(color[2] * brightness))
            )
        else:
            layer_color = _darken_color(color, brightness)
        offset = radius - layer_radius
        layer_x = cx - int(perp_x * offset)
        layer_y = cy - int(perp_y * offset)
        pygame.draw.circle(screen, layer_color, (layer_x, layer_y), layer_radius)


def _calculate_head_pixel_position(snake: dict[str, Any]) -> tuple[float, float]:
    """Calculate interpolated head position in pixels.

    Args:
        snake: Snake data structure.

    Returns:
        Interpolated (x, y) pixel position of head.
    """
    segments = snake['segments']
    direction = snake['direction']
    interpolation = snake['interpolation']

    grid_x, grid_y = segments[0]
    cell_size = config.grid_cell_size
    offset_x = config.map_offset_x
    offset_y = config.map_offset_y

    pixel_x = offset_x + grid_x * cell_size + cell_size // 2
    pixel_y = offset_y + grid_y * cell_size + cell_size // 2

    next_x = offset_x + (grid_x + direction[0]) * cell_size + cell_size // 2
    next_y = offset_y + (grid_y + direction[1]) * cell_size + cell_size // 2

    pixel_x = pixel_x + (next_x - pixel_x) * interpolation
    pixel_y = pixel_y + (next_y - pixel_y) * interpolation

    return (pixel_x, pixel_y)


def _render_single_eye(screen: pygame.Surface, eye_pos: tuple[int, int], eye_radius: int, backing_pos: tuple[int, int], backing_radius: int, eye_closed: float, head_color: tuple[int, int, int]) -> None:
    """Render a single eye with green backing circle.

    Args:
        screen: Pygame surface to render on.
        eye_pos: Eye center position.
        eye_radius: Eye radius.
        backing_pos: Backing circle position.
        backing_radius: Backing circle radius.
        eye_closed: Blink progress 0.0 to 1.0.
        head_color: RGB color for backing circle.
    """
    pygame.draw.circle(screen, head_color, backing_pos, backing_radius)

    if eye_closed < 0.9:
        eye_height = int(eye_radius * 2 * (1.0 - eye_closed))
        pygame.draw.ellipse(screen, (255, 255, 255), (eye_pos[0] - eye_radius, eye_pos[1] - eye_height // 2, eye_radius * 2, eye_height))
        pygame.draw.circle(screen, (255, 255, 255), eye_pos, eye_radius, 2)
        pupil_height = int(eye_radius * 0.8 * (1.0 - eye_closed))
        pupil_width = int(eye_radius * 0.8)
        pygame.draw.ellipse(screen, (0, 0, 0), (eye_pos[0] - pupil_width // 2, eye_pos[1] - pupil_height // 2, pupil_width, pupil_height))
    else:
        pygame.draw.line(screen, (0, 0, 0), (eye_pos[0] - eye_radius, eye_pos[1]), (eye_pos[0] + eye_radius, eye_pos[1]), 2)


def _render_eyes(screen: pygame.Surface, pixel_x: float, pixel_y: float, direction: tuple[int, int], look_at: tuple[float, float] | None = None, blink_state: dict[str, float] | None = None, head_color: tuple[int, int, int] | None = None) -> tuple[tuple[int, int], int, tuple[int, int], int, float, float]:
    """Render snake eyes that track nearest food and blink.

    Args:
        screen: Pygame surface to render on.
        pixel_x: Head x position in pixels.
        pixel_y: Head y position in pixels.
        direction: Snake movement direction.
        look_at: Optional position to look at (food position).
        blink_state: Optional blink animation state.
        head_color: Optional head color for backing circles.

    Returns:
        Tuple of (right_eye_pos, right_eye_radius, right_backing_pos, right_backing_radius, eye1_closed, eye2_closed).
    """
    cell_size = config.grid_cell_size
    eye_radius = cell_size // 9
    backing_radius = int(eye_radius * 1.3)

    if head_color is None:
        head_color = config.color_snake_head

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

    backing1_x = eye1_x - math.cos(angle_to_target) * backing_offset
    backing1_y = eye1_y - math.sin(angle_to_target) * backing_offset
    backing2_x = eye2_x - math.cos(angle_to_target) * backing_offset
    backing2_y = eye2_y - math.sin(angle_to_target) * backing_offset

    eye1_pos = (int(eye1_x), int(eye1_y))
    eye2_pos = (int(eye2_x), int(eye2_y))
    backing1_pos = (int(backing1_x), int(backing1_y))
    backing2_pos = (int(backing2_x), int(backing2_y))

    eye1_closed = blink_state.get('eye1_closed', 0.0) if blink_state else 0.0
    eye2_closed = blink_state.get('eye2_closed', 0.0) if blink_state else 0.0

    if not look_at and direction[0] < 0:
        _render_single_eye(screen, eye2_pos, eye_radius, backing2_pos, backing_radius, eye2_closed, head_color)
    else:
        _render_single_eye(screen, eye1_pos, eye_radius, backing1_pos, backing_radius, eye1_closed, head_color)

    return (eye2_pos, eye_radius, backing2_pos, backing_radius, eye1_closed, eye2_closed)


def render_forked_tongue(
    screen: pygame.Surface,
    base_pos: tuple[float, float],
    direction: tuple[int, int],
    extension_progress: float,
    time: float = 0.0
) -> None:
    """Draw curvy forked tongue with waving tip animation.

    Args:
        screen: Pygame surface to render on.
        base_pos: Base position of tongue (head position).
        direction: Snake movement direction.
        extension_progress: Animation progress from 0.0 to 1.0.
        time: Current time for wave animation.
    """
    cell_size = config.grid_cell_size
    tongue_color = (220, 80, 80)

    base_angle = math.atan2(direction[1], direction[0])

    tongue_length = cell_size * 0.7 * extension_progress

    stable_length = tongue_length * 0.4
    stable_end_x = base_pos[0] + math.cos(base_angle) * stable_length
    stable_end_y = base_pos[1] + math.sin(base_angle) * stable_length

    pygame.draw.line(screen, tongue_color, (int(base_pos[0]), int(base_pos[1])), (int(stable_end_x), int(stable_end_y)), 2)

    wave_length = tongue_length * 0.6
    wave_frequency = 25.0
    wave_amplitude = cell_size * 0.25

    perp_x = -math.sin(base_angle)
    perp_y = math.cos(base_angle)

    wave_phase = math.sin(time * wave_frequency)

    num_wave_segments = 12
    wave_points = [(int(stable_end_x), int(stable_end_y))]

    actual_end_x = stable_end_x
    actual_end_y = stable_end_y

    for i in range(1, num_wave_segments + 1):
        t = i / num_wave_segments

        base_x = stable_end_x + math.cos(base_angle) * wave_length * t
        base_y = stable_end_y + math.sin(base_angle) * wave_length * t

        sine_progress = t * 0.25 * math.pi
        sine_value = math.sin(sine_progress) * wave_phase
        offset = sine_value * wave_amplitude * extension_progress

        x = base_x + perp_x * offset
        y = base_y + perp_y * offset

        wave_points.append((int(x), int(y)))

        if i == num_wave_segments:
            actual_end_x = x
            actual_end_y = y

    if len(wave_points) > 1:
        pygame.draw.lines(screen, tongue_color, False, wave_points, 2)

    fork_length = cell_size * 0.15 * extension_progress
    fork_angle = 0.5

    tangent_x = actual_end_x - wave_points[-2][0]
    tangent_y = actual_end_y - wave_points[-2][1]
    tangent_length = math.sqrt(tangent_x * tangent_x + tangent_y * tangent_y)
    if tangent_length > 0:
        tangent_x /= tangent_length
        tangent_y /= tangent_length
    else:
        tangent_x = math.cos(base_angle)
        tangent_y = math.sin(base_angle)

    fork1_x = actual_end_x + (tangent_x * math.cos(-fork_angle) - tangent_y * math.sin(-fork_angle)) * fork_length
    fork1_y = actual_end_y + (tangent_x * math.sin(-fork_angle) + tangent_y * math.cos(-fork_angle)) * fork_length
    pygame.draw.line(screen, tongue_color, (int(actual_end_x), int(actual_end_y)), (int(fork1_x), int(fork1_y)), 2)

    fork2_x = actual_end_x + (tangent_x * math.cos(fork_angle) - tangent_y * math.sin(fork_angle)) * fork_length
    fork2_y = actual_end_y + (tangent_x * math.sin(fork_angle) + tangent_y * math.cos(fork_angle)) * fork_length
    pygame.draw.line(screen, tongue_color, (int(actual_end_x), int(actual_end_y)), (int(fork2_x), int(fork2_y)), 2)


def _render_tongue(screen: pygame.Surface, snake: dict[str, Any], pixel_x: float, pixel_y: float, direction: tuple[int, int], time: float = 0.0) -> None:
    """Render snake tongue if extended.

    Args:
        screen: Pygame surface to render on.
        snake: Snake data structure.
        pixel_x: Head x position in pixels.
        pixel_y: Head y position in pixels.
        direction: Snake movement direction.
        time: Current time for wave animation.
    """
    if not config.enable_tongue_animation:
        return

    tongue_state = snake.get('tongue_state')
    if not tongue_state or tongue_state.get('phase') == 'retracted':
        return

    extension_progress = tongue_state.get('extension_progress', 0.0)
    if extension_progress > 0:
        render_forked_tongue(screen, (pixel_x, pixel_y), direction, extension_progress, time)


def _draw_interpolation_circles(screen: pygame.Surface, data: SegmentRenderData, next_data: SegmentRenderData) -> None:
    """Draw interpolation circles between two segments."""
    dx = next_data['render_x'] - data['render_x']
    dy = next_data['render_y'] - data['render_y']
    distance = math.sqrt(dx * dx + dy * dy)

    avg_radius = (data['radius'] + next_data['radius']) / 2
    if distance > avg_radius * 1.5:
        steps = max(1, int(distance / avg_radius) + 1)
        for step in range(steps):
            t = (step + 1) / (steps + 1)
            base_x = data['base_x'] + (next_data['base_x'] - data['base_x']) * t
            base_y = data['base_y'] + (next_data['base_y'] - data['base_y']) * t
            interp_sine_offset = data['sine_offset'] + (next_data['sine_offset'] - data['sine_offset']) * t
            perp_x = data['perpendicular'][0] + (next_data['perpendicular'][0] - data['perpendicular'][0]) * t
            perp_y = data['perpendicular'][1] + (next_data['perpendicular'][1] - data['perpendicular'][1]) * t
            interp_x = base_x + perp_x * interp_sine_offset
            interp_y = base_y + perp_y * interp_sine_offset
            interp_radius = int(data['radius'] + (next_data['radius'] - data['radius']) * t)
            interp_color = (
                int(data['color'][0] + (next_data['color'][0] - data['color'][0]) * t),
                int(data['color'][1] + (next_data['color'][1] - data['color'][1]) * t),
                int(data['color'][2] + (next_data['color'][2] - data['color'][2]) * t)
            )
            _draw_gradient_circle(screen, (int(interp_x), int(interp_y)), interp_radius, interp_color, (perp_x, perp_y))


def _draw_interpolation_circles_offset(screen: pygame.Surface, data: SegmentRenderData, next_data: SegmentRenderData, offset_x: float, offset_y: float) -> None:
    """Draw interpolation circles with position offset."""
    dx = next_data['render_x'] - data['render_x']
    dy = next_data['render_y'] - data['render_y']
    distance = math.sqrt(dx * dx + dy * dy)

    avg_radius = (data['radius'] + next_data['radius']) / 2
    if distance > avg_radius * 1.5:
        steps = max(1, int(distance / avg_radius) + 1)
        for step in range(steps):
            t = (step + 1) / (steps + 1)
            base_x = data['base_x'] + (next_data['base_x'] - data['base_x']) * t
            base_y = data['base_y'] + (next_data['base_y'] - data['base_y']) * t
            interp_sine_offset = data['sine_offset'] + (next_data['sine_offset'] - data['sine_offset']) * t
            perp_x = data['perpendicular'][0] + (next_data['perpendicular'][0] - data['perpendicular'][0]) * t
            perp_y = data['perpendicular'][1] + (next_data['perpendicular'][1] - data['perpendicular'][1]) * t
            interp_x = base_x + perp_x * interp_sine_offset + offset_x
            interp_y = base_y + perp_y * interp_sine_offset + offset_y
            interp_radius = int(data['radius'] + (next_data['radius'] - data['radius']) * t)
            interp_color = (
                int(data['color'][0] + (next_data['color'][0] - data['color'][0]) * t),
                int(data['color'][1] + (next_data['color'][1] - data['color'][1]) * t),
                int(data['color'][2] + (next_data['color'][2] - data['color'][2]) * t)
            )
            _draw_gradient_circle(screen, (int(interp_x), int(interp_y)), interp_radius, interp_color, (perp_x, perp_y))


def calculate_distance_to_nearest_food(snake_head: tuple[int, int], food_items: list[dict[str, Any]]) -> float:
    """Calculate distance from snake head to nearest food item.

    Args:
        snake_head: Snake head grid position (x, y).
        food_items: List of food items with position data.

    Returns:
        Distance in grid cells to nearest food, or infinity if no food.
    """
    if not food_items:
        return float('inf')

    head_x, head_y = snake_head
    min_distance = float('inf')

    for food_item in food_items:
        food_x, food_y = food_item['position']
        distance = math.sqrt((head_x - food_x) ** 2 + (head_y - food_y) ** 2)
        min_distance = min(min_distance, distance)

    return min_distance


def draw_head_with_mouth(
    screen: pygame.Surface,
    head_pos: tuple[float, float],
    radius: int,
    bite_pos: tuple[float, float],
    mouth_width: float,
    mouth_depth: float,
    head_color: tuple[int, int, int],
    perpendicular: tuple[float, float],
    segment_data: list[SegmentRenderData],
    next_segment_data: SegmentRenderData | None
) -> None:
    """Draw head with C-shaped mouth cutout using mask technique.

    Args:
        screen: Pygame surface to render on.
        head_pos: Head center position.
        radius: Head radius.
        bite_pos: Position of food being bitten.
        mouth_width: Width of mouth opening.
        mouth_depth: How deep the mouth cuts into the head.
        head_color: RGB color for head.
        perpendicular: Perpendicular vector for gradient.
        segment_data: Head segment render data.
        next_segment_data: Next segment data for interpolation.
    """
    _draw_gradient_circle(screen, (int(head_pos[0]), int(head_pos[1])), radius, head_color, perpendicular)
    
    if mouth_width < 0.5 or mouth_depth < 0.5:
        return
    
    angle_to_food = math.atan2(bite_pos[1] - head_pos[1], bite_pos[0] - head_pos[0])
    
    dir_x = math.cos(angle_to_food)
    dir_y = math.sin(angle_to_food)
    perp_x = -dir_y
    perp_y = dir_x
    
    mouth_center_dist = radius * 0.6
    mouth_center_x = head_pos[0] + dir_x * mouth_center_dist
    mouth_center_y = head_pos[1] + dir_y * mouth_center_dist
    
    mouth_width_actual = min(mouth_width, radius * 1.2)
    mouth_height = min(mouth_depth * 0.8, radius * 0.8)
    
    mouth_points = []
    num_points = 16
    for i in range(num_points):
        angle = (i / num_points) * 2 * math.pi
        
        local_x = math.cos(angle) * mouth_width_actual / 2
        local_y = math.sin(angle) * mouth_height / 2
        
        world_x = mouth_center_x + local_x * perp_x + local_y * dir_x
        world_y = mouth_center_y + local_x * perp_y + local_y * dir_y
        
        mouth_points.append((int(world_x), int(world_y)))
    
    mouth_color = (25, 25, 25)
    pygame.draw.polygon(screen, mouth_color, mouth_points)
    pygame.draw.aalines(screen, (0, 0, 0), True, mouth_points, 1)


def render_bite_mouth(
    screen: pygame.Surface,
    head_pos: tuple[float, float],
    direction: tuple[int, int],
    progress: float
) -> None:
    """Draw C-shaped mouth during bite animation.

    Args:
        screen: Pygame surface to render on.
        head_pos: Head position.
        direction: Snake movement direction.
        progress: Animation progress 0.0 to 1.0.
    """
    cell_size = config.grid_cell_size

    if progress < 0.3:
        scale_progress = progress / 0.3
    elif progress < 0.4:
        scale_progress = 1.0
    else:
        scale_progress = 1.0 - ((progress - 0.4) / 0.6)

    mouth_radius = cell_size * 0.6 * (1.0 + 0.5 * scale_progress)

    base_angle = math.atan2(direction[1], direction[0])

    if progress < 0.3:
        opening_progress = progress / 0.3
        mouth_opening_angle = math.radians(108) * opening_progress
    elif progress < 0.4:
        closing_progress = (progress - 0.3) / 0.1
        mouth_opening_angle = math.radians(108) * (1.0 - closing_progress)
    else:
        mouth_opening_angle = 0

    if mouth_opening_angle > 0.01:
        num_segments = 20
        points = []

        for i in range(num_segments + 1):
            t = i / num_segments
            angle = base_angle - mouth_opening_angle / 2 + mouth_opening_angle * t

            x = head_pos[0] + math.cos(angle) * mouth_radius
            y = head_pos[1] + math.sin(angle) * mouth_radius

            points.append((int(x), int(y)))

        if len(points) > 1:
            pygame.draw.lines(screen, (255, 0, 0), False, points, 6)
            
            if config.debug_mode:
                print(f'[BITE MOUTH] Drawing {len(points)} points at {head_pos}, angle={math.degrees(base_angle):.1f}, opening={math.degrees(mouth_opening_angle):.1f}, progress={progress:.2f}')


def render_mouth_animation(state: dict[str, Any], screen: pygame.Surface, head_pos: tuple[float, float], direction: tuple[int, int]) -> None:
    """Draw C-shaped mouth opening animation when near food.

    Args:
        state: Game state containing food items.
        screen: Pygame surface to render on.
        head_pos: Snake head pixel position (x, y).
        direction: Snake movement direction (dx, dy).
    """
    if not config.enable_mouth_animation:
        return

    player_snake = state.get('snake')
    if not player_snake:
        return

    bite_state = player_snake.get('bite_state')
    if bite_state and bite_state.get('active', False):
        return

    food_items = state.get('food_items', [])
    snake_head = player_snake['segments'][0]

    distance = calculate_distance_to_nearest_food(snake_head, food_items)
    threshold = 5.0

    if distance >= threshold:
        return

    cell_size = config.grid_cell_size
    mouth_radius = cell_size * 0.4

    base_angle = math.atan2(direction[1], direction[0])

    opening_factor = max(0, 1.0 - (distance / threshold))
    mouth_opening_angle = math.radians(60) * opening_factor

    if mouth_opening_angle > 0.01:
        num_segments = 15
        points = []

        for i in range(num_segments + 1):
            t = i / num_segments
            angle = base_angle - mouth_opening_angle / 2 + mouth_opening_angle * t

            x = head_pos[0] + math.cos(angle) * mouth_radius
            y = head_pos[1] + math.sin(angle) * mouth_radius

            points.append((int(x), int(y)))

        if len(points) > 1:
            pygame.draw.lines(screen, (255, 0, 0), False, points, 5)
            
            if config.debug_mode and opening_factor > 0.5:
                print(f'[MOUTH] Drawing {len(points)} points at {head_pos}, angle={math.degrees(base_angle):.1f}, opening={math.degrees(mouth_opening_angle):.1f}, distance={distance:.1f}')


def get_right_eye_data(state: dict[str, Any]) -> tuple[tuple[int, int], int, tuple[int, int], int, float] | None:
    """Get right eye rendering data to draw before head.

    Args:
        state: Game state containing snake data.

    Returns:
        Tuple of (eye_pos, eye_radius, backing_pos, backing_radius, eye_closed) or None.
    """
    player_snake = state.get('snake')
    if not player_snake or not player_snake['segments']:
        return None

    pixel_x, pixel_y = _calculate_head_pixel_position(player_snake)
    direction = player_snake['direction']

    bite_state = player_snake.get('bite_state')
    is_biting = bite_state and bite_state.get('active', False)

    nearest_food_pixel_pos = None
    food_items = state.get('food_items', [])
    head_grid = player_snake['segments'][0]
    min_distance = float('inf')

    for food_item in food_items:
        if food_item.get('being_eaten', False):
            continue
        food_x, food_y = food_item['position']
        distance = math.sqrt((head_grid[0] - food_x) ** 2 + (head_grid[1] - food_y) ** 2)
        if distance < min_distance and distance <= 3.0:
            min_distance = distance
            cell_size = config.grid_cell_size
            offset_x = config.map_offset_x
            offset_y = config.map_offset_y
            nearest_food_pixel_pos = (
                offset_x + food_x * cell_size + cell_size // 2,
                offset_y + food_y * cell_size + cell_size // 2
            )

    if is_biting:
        bite_pos = bite_state['bite_position']
        progress = bite_state['progress']

        if progress < 0.3:
            lunge_out = progress / 0.3
            eye_x = pixel_x + (bite_pos[0] - pixel_x) * lunge_out
            eye_y = pixel_y + (bite_pos[1] - pixel_y) * lunge_out
        elif progress < 0.4:
            eye_x = bite_pos[0]
            eye_y = bite_pos[1]
        else:
            lunge_back = (progress - 0.4) / 0.6
            eye_x = bite_pos[0] + (pixel_x - bite_pos[0]) * lunge_back
            eye_y = bite_pos[1] + (pixel_y - bite_pos[1]) * lunge_back

        look_at = bite_pos
    else:
        eye_x = pixel_x
        eye_y = pixel_y
        look_at = nearest_food_pixel_pos

    cell_size = config.grid_cell_size
    eye_radius = cell_size // 9
    backing_radius = int(eye_radius * 1.3)

    if look_at:
        angle_to_target = math.atan2(look_at[1] - eye_y, look_at[0] - eye_x)
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

    top_x = eye_x + math.cos(perp_angle) * top_offset
    top_y = eye_y + math.sin(perp_angle) * top_offset

    eye1_x = top_x - math.cos(spacing_angle) * eye_spacing
    eye1_y = top_y - math.sin(spacing_angle) * eye_spacing
    eye2_x = top_x + math.cos(spacing_angle) * eye_spacing
    eye2_y = top_y + math.sin(spacing_angle) * eye_spacing

    backing1_x = eye1_x - math.cos(angle_to_target) * backing_offset
    backing1_y = eye1_y - math.sin(angle_to_target) * backing_offset
    backing2_x = eye2_x - math.cos(angle_to_target) * backing_offset
    backing2_y = eye2_y - math.sin(angle_to_target) * backing_offset

    blink_state = player_snake.get('blink_state')
    eye1_closed = blink_state.get('eye1_closed', 0.0) if blink_state else 0.0
    eye2_closed = blink_state.get('eye2_closed', 0.0) if blink_state else 0.0

    if not look_at and direction[0] < 0:
        return ((int(eye1_x), int(eye1_y)), eye_radius, (int(backing1_x), int(backing1_y)), backing_radius, eye1_closed)
    else:
        return ((int(eye2_x), int(eye2_y)), eye_radius, (int(backing2_x), int(backing2_y)), backing_radius, eye2_closed)


def render_head_details(state: dict[str, Any], screen: pygame.Surface) -> None:
    """Draw eyes and distinct head shape for the snake.

    Args:
        state: Game state containing snake data.
        screen: Pygame surface to render on.
    """
    player_snake = state.get('snake')
    if not player_snake or not player_snake['segments']:
        return

    pixel_x, pixel_y = _calculate_head_pixel_position(player_snake)
    direction = player_snake['direction']

    bite_state = player_snake.get('bite_state')
    is_biting = bite_state and bite_state.get('active', False)

    nearest_food_pixel_pos = None
    food_items = state.get('food_items', [])
    head_grid = player_snake['segments'][0]
    min_distance = float('inf')

    for food_item in food_items:
        if food_item.get('being_eaten', False):
            continue
        food_x, food_y = food_item['position']
        distance = math.sqrt((head_grid[0] - food_x) ** 2 + (head_grid[1] - food_y) ** 2)
        if distance < min_distance and distance <= 3.0:
            min_distance = distance
            cell_size = config.grid_cell_size
            offset_x = config.map_offset_x
            offset_y = config.map_offset_y
            nearest_food_pixel_pos = (
                offset_x + food_x * cell_size + cell_size // 2,
                offset_y + food_y * cell_size + cell_size // 2
            )

    if is_biting:
        bite_pos = bite_state['bite_position']
        progress = bite_state['progress']

        if progress < 0.3:
            lunge_out = progress / 0.3
            eye_x = pixel_x + (bite_pos[0] - pixel_x) * lunge_out
            eye_y = pixel_y + (bite_pos[1] - pixel_y) * lunge_out
        elif progress < 0.4:
            eye_x = bite_pos[0]
            eye_y = bite_pos[1]
        else:
            lunge_back = (progress - 0.4) / 0.6
            eye_x = bite_pos[0] + (pixel_x - bite_pos[0]) * lunge_back
            eye_y = bite_pos[1] + (pixel_y - bite_pos[1]) * lunge_back

        _render_eyes(screen, eye_x, eye_y, direction, bite_pos, player_snake.get('blink_state'))
    else:
        _render_eyes(screen, pixel_x, pixel_y, direction, nearest_food_pixel_pos, player_snake.get('blink_state'))


def render_tongue_before_head(state: dict[str, Any], screen: pygame.Surface) -> None:
    """Draw tongue before head so it appears behind the head.

    Args:
        state: Game state containing snake data.
        screen: Pygame surface to render on.
    """
    player_snake = state.get('snake')
    if not player_snake or not player_snake['segments']:
        return

    bite_state = player_snake.get('bite_state')
    is_biting = bite_state and bite_state.get('active', False)

    if not is_biting:
        pixel_x, pixel_y = _calculate_head_pixel_position(player_snake)
        direction = player_snake['direction']
        time = state.get('time', 0.0)
        _render_tongue(screen, player_snake, pixel_x, pixel_y, direction, time)


def render_head_details_for_snake(
    snake: dict[str, Any],
    screen: pygame.Surface,
    state: dict[str, Any],
    head_color: tuple[int, int, int]
) -> None:
    """Draw eyes and head details for any snake.

    Args:
        snake: Snake data structure.
        screen: Pygame surface to render on.
        state: Game state for animations.
        head_color: RGB color for head.
    """
    if not snake or not snake['segments']:
        return

    pixel_x, pixel_y = _calculate_head_pixel_position(snake)
    direction = snake['direction']

    _render_eyes(screen, pixel_x, pixel_y, direction)


def render_snake(state: dict[str, Any], screen: pygame.Surface) -> None:
    """Draw snake with circle-based segments and slithering animation.

    Args:
        state: Game state containing snake data.
        screen: Pygame surface to render on.
    """
    player_snake = state.get('snake')
    if not player_snake:
        return

    render_snake_with_colors(
        player_snake,
        screen,
        state.get('time', 0.0),
        config.color_snake_body,
        config.color_snake_head,
        state
    )


def render_snake_with_colors(
    snake: dict[str, Any],
    screen: pygame.Surface,
    time: float,
    body_color: tuple[int, int, int],
    head_color: tuple[int, int, int],
    state: dict[str, Any] | None = None
) -> None:
    """Draw any snake with circle-based segments and custom colors.

    Args:
        snake: Snake data structure.
        screen: Pygame surface to render on.
        time: Current game time for animation.
        body_color: RGB color for body segments.
        head_color: RGB color for head segment.
        state: Game state for food proximity detection.
    """
    if not snake:
        return

    segments = snake['segments']
    direction = snake['direction']
    interpolation = snake['interpolation']
    visual_state = snake.get('visual_state', {'wave_phase': 0.0, 'wave_speed': 8.0})
    wave_phase = visual_state['wave_phase']

    cell_size = config.grid_cell_size
    offset_x = config.map_offset_x
    offset_y = config.map_offset_y
    total_segments = len(segments)

    bite_state = snake.get('bite_state')
    is_biting = bite_state and bite_state.get('active', False)

    global_direction = (direction[0], direction[1])
    if global_direction == (0, 0):
        global_direction = (1.0, 0.0)
    else:
        length = math.sqrt(global_direction[0] ** 2 + global_direction[1] ** 2)
        if length > 0:
            global_direction = (global_direction[0] / length, global_direction[1] / length)
    global_perpendicular = calculate_perpendicular_vector(global_direction)

    segment_data: list[SegmentRenderData] = []
    for i, (grid_x, grid_y) in enumerate(segments):
        pixel_x = offset_x + grid_x * cell_size + cell_size // 2
        pixel_y = offset_y + grid_y * cell_size + cell_size // 2

        if i == 0:
            next_x = offset_x + (grid_x + direction[0]) * cell_size + cell_size // 2
            next_y = offset_y + (grid_y + direction[1]) * cell_size + cell_size // 2
            pixel_x = pixel_x + (next_x - pixel_x) * interpolation
            pixel_y = pixel_y + (next_y - pixel_y) * interpolation

            if is_biting:
                bite_pos = bite_state['bite_position']
                bite_progress = bite_state['progress']

                if bite_progress < 0.3:
                    lunge_out = bite_progress / 0.3
                    pixel_x = pixel_x + (bite_pos[0] - pixel_x) * lunge_out
                    pixel_y = pixel_y + (bite_pos[1] - pixel_y) * lunge_out
                elif bite_progress < 0.4:
                    pixel_x = bite_pos[0]
                    pixel_y = bite_pos[1]
                else:
                    lunge_back = (bite_progress - 0.4) / 0.6
                    pixel_x = bite_pos[0] + (pixel_x - bite_pos[0]) * lunge_back
                    pixel_y = bite_pos[1] + (pixel_y - bite_pos[1]) * lunge_back
        else:
            prev_segment = segments[i - 1]
            prev_x = offset_x + prev_segment[0] * cell_size + cell_size // 2
            prev_y = offset_y + prev_segment[1] * cell_size + cell_size // 2
            pixel_x = pixel_x + (prev_x - pixel_x) * interpolation
            pixel_y = pixel_y + (prev_y - pixel_y) * interpolation

        perpendicular = global_perpendicular
        sine_offset = calculate_sine_wave_offset_for_segment(i, total_segments, wave_phase)

        render_x = pixel_x + perpendicular[0] * sine_offset
        render_y = pixel_y + perpendicular[1] * sine_offset

        radius = calculate_segment_radius(i, total_segments)

        if i == 0 and is_biting:
            bite_progress = bite_state['progress']
            if bite_progress < 0.3:
                scale_progress = bite_progress / 0.3
            elif bite_progress < 0.4:
                scale_progress = 1.0
            else:
                scale_progress = 1.0 - ((bite_progress - 0.4) / 0.6)
            radius = int(radius * (1.0 + 0.5 * scale_progress))

        color = head_color if i == 0 else body_color

        segment_data.append({
            'base_x': pixel_x,
            'base_y': pixel_y,
            'render_x': render_x,
            'render_y': render_y,
            'sine_offset': sine_offset,
            'perpendicular': perpendicular,
            'radius': radius,
            'color': color
        })

    for i in range(len(segment_data) - 1, 0, -1):
        data = segment_data[i]
        _draw_gradient_circle(
            screen,
            (int(data['render_x']), int(data['render_y'])),
            data['radius'],
            data['color'],
            data['perpendicular']
        )
        next_data = segment_data[i - 1]
        _draw_interpolation_circles(screen, data, next_data)

    if len(segment_data) > 1:
        head_data = segment_data[0]
        neck_data = segment_data[1]
        _draw_interpolation_circles(screen, neck_data, head_data)

    head_data = segment_data[0]
    mouth_width = 0
    mouth_depth = 0
    nearest_food_pos = None

    if is_biting:
        bite_progress = bite_state['progress']
        if bite_progress < 0.3:
            opening_progress = bite_progress / 0.3
            mouth_width = head_data['radius'] * 1.2 * opening_progress
            mouth_depth = head_data['radius'] * 0.8 * opening_progress
        elif bite_progress < 0.4:
            mouth_width = head_data['radius'] * 1.2
            mouth_depth = head_data['radius'] * 0.8
            closing_progress = (bite_progress - 0.3) / 0.1
            mouth_width *= (1.0 - closing_progress)
            mouth_depth *= (1.0 - closing_progress)

        if config.debug_mode and mouth_width > 0:
            print(f'[BITE] Mouth: width={mouth_width:.1f}, depth={mouth_depth:.1f}, progress={bite_progress:.2f}')
    elif state:
        head_grid = segments[0]
        food_items = state.get('food_items', [])

        min_distance = float('inf')
        for food_item in food_items:
            if food_item.get('being_eaten', False):
                continue
            food_x, food_y = food_item['position']
            distance = math.sqrt((head_grid[0] - food_x) ** 2 + (head_grid[1] - food_y) ** 2)
            if distance < min_distance:
                min_distance = distance
                nearest_food_pos = food_item['position']

        if min_distance <= 3.0:
            anticipation_factor = max(0, 1.0 - ((min_distance - 1.5) / 1.5))
            anticipation_factor = min(anticipation_factor, 1.0)
            mouth_width = head_data['radius'] * 1.5 * anticipation_factor
            mouth_depth = head_data['radius'] * 1.0 * anticipation_factor

    next_seg_data = segment_data[1] if len(segment_data) > 1 else None

    if nearest_food_pos and not is_biting:
        cell_size = config.grid_cell_size
        offset_x = config.map_offset_x
        offset_y = config.map_offset_y
        bite_position = (
            offset_x + nearest_food_pos[0] * cell_size + cell_size // 2,
            offset_y + nearest_food_pos[1] * cell_size + cell_size // 2
        )
    else:
        bite_position = bite_state['bite_position'] if bite_state else (head_data['render_x'], head_data['render_y'])

    draw_head_with_mouth(
        screen,
        (head_data['render_x'], head_data['render_y']),
        head_data['radius'],
        bite_position,
        mouth_width,
        mouth_depth,
        head_data['color'],
        head_data['perpendicular'],
        head_data,
        next_seg_data
    )


def create_mouse_sprite() -> pygame.Surface:
    """Create a procedural mouse sprite for food rendering.

    Returns:
        Pygame surface with mouse sprite drawn on it.
    """
    global _mouse_sprite_cache

    if _mouse_sprite_cache is not None:
        return _mouse_sprite_cache

    size = config.grid_cell_size
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)

    body_color = (150, 150, 150)
    ear_color = (180, 120, 120)
    eye_color = (0, 0, 0)
    nose_color = (200, 100, 100)

    center_x = size // 2
    center_y = size // 2
    body_radius = size // 3

    pygame.draw.circle(sprite, body_color, (center_x, center_y), body_radius)

    ear_radius = size // 6
    ear1_pos = (center_x - size // 4, center_y - size // 4)
    ear2_pos = (center_x + size // 4, center_y - size // 4)
    pygame.draw.circle(sprite, ear_color, ear1_pos, ear_radius)
    pygame.draw.circle(sprite, ear_color, ear2_pos, ear_radius)

    eye_radius = size // 12
    eye1_pos = (center_x - size // 6, center_y - size // 12)
    eye2_pos = (center_x + size // 6, center_y - size // 12)
    pygame.draw.circle(sprite, eye_color, eye1_pos, eye_radius)
    pygame.draw.circle(sprite, eye_color, eye2_pos, eye_radius)

    nose_radius = size // 10
    nose_pos = (center_x, center_y + size // 8)
    pygame.draw.circle(sprite, nose_color, nose_pos, nose_radius)

    tail_start = (center_x, center_y + body_radius)
    tail_end = (center_x + size // 3, center_y + size // 2)
    pygame.draw.line(sprite, body_color, tail_start, tail_end, 2)

    _mouse_sprite_cache = sprite
    return sprite


def render_food_sprite(state: dict[str, Any], screen: pygame.Surface) -> None:
    """Render food items as mouse sprites.

    Args:
        state: Game state containing food items.
        screen: Pygame surface to render on.
    """
    if not config.enable_animated_food:
        return

    food_items = state.get('food_items', [])
    sprite = create_mouse_sprite()
    cell_size = config.grid_cell_size
    offset_x = config.map_offset_x
    offset_y = config.map_offset_y

    for food_item in food_items:
        if food_item.get('being_eaten', False):
            continue
            
        grid_x, grid_y = food_item['position']
        pixel_x = offset_x + grid_x * cell_size
        pixel_y = offset_y + grid_y * cell_size

        screen.blit(sprite, (pixel_x, pixel_y))


def update_bite_animation(snake: dict[str, Any], delta_time: float, state: dict[str, Any]) -> None:
    """Update bite animation progress.

    Args:
        snake: Snake data structure.
        delta_time: Time elapsed since last frame in seconds.
        state: Game state for removing food.
    """
    bite_state = snake.get('bite_state')
    if not bite_state or not bite_state.get('active', False):
        return

    bite_state['progress'] += delta_time / bite_state['duration']

    if bite_state['progress'] >= 0.4 and not bite_state.get('food_hidden', False):
        bite_state['food_hidden'] = True
        food_items = state.get('food_items', [])
        snake_id = id(snake)
        for food in food_items[:]:
            if food.get('being_eaten', False) and food.get('eaten_by') == snake_id:
                food_items.remove(food)
                if config.debug_mode:
                    print('[BITE] Food removed (mouth closed)')

    if bite_state['progress'] >= 1.0:
        bite_state['active'] = False
        bite_state['progress'] = 0.0

        if config.debug_mode:
            print('[BITE] Animation complete')


def update_tongue_animation(snake: dict[str, Any], delta_time: float, state: dict[str, Any] | None = None) -> None:
    """Update tongue animation with four-phase state machine.

    Args:
        snake: Snake data structure.
        delta_time: Time elapsed since last frame in seconds.
        state: Game state for checking anticipation conditions.
    """
    if not config.enable_tongue_animation:
        return

    EXTENSION_DURATION = 0.4
    HOLD_DURATION = 0.8
    RETRACTION_DURATION = 0.4
    COOLDOWN_DURATION = 3.0

    tongue_state = snake.get('tongue_state')
    if not tongue_state:
        snake['tongue_state'] = create_tongue_state()
        tongue_state = snake['tongue_state']

    bite_state = snake.get('bite_state')
    if bite_state and bite_state.get('active', False):
        if tongue_state['phase'] != 'retracted':
            tongue_state['phase'] = 'retracted'
            tongue_state['extension_progress'] = 0.0
            tongue_state['cooldown_timer'] = COOLDOWN_DURATION
        return

    is_anticipating = False
    if state:
        segments = snake.get('segments', [])
        if segments:
            head_grid = segments[0]
            food_items = state.get('food_items', [])
            
            min_distance = float('inf')
            for food_item in food_items:
                if food_item.get('being_eaten', False):
                    continue
                food_x, food_y = food_item['position']
                distance = math.sqrt((head_grid[0] - food_x) ** 2 + (head_grid[1] - food_y) ** 2)
                min_distance = min(min_distance, distance)
            
            if min_distance <= 3.0:
                is_anticipating = True

    if is_anticipating:
        if tongue_state['phase'] != 'retracted':
            tongue_state['phase'] = 'retracted'
            tongue_state['extension_progress'] = 0.0
            tongue_state['cooldown_timer'] = COOLDOWN_DURATION
        return

    if tongue_state['phase'] == 'retracted':
        tongue_state['cooldown_timer'] -= delta_time
        if tongue_state['cooldown_timer'] <= 0:
            tongue_state['phase'] = 'extending'
            tongue_state['timer'] = 0.0
        return

    tongue_state['timer'] += delta_time

    if tongue_state['phase'] == 'extending':
        tongue_state['extension_progress'] = min(tongue_state['timer'] / EXTENSION_DURATION, 1.0)
        if tongue_state['timer'] >= EXTENSION_DURATION:
            tongue_state['phase'] = 'holding'
            tongue_state['timer'] = 0.0

    elif tongue_state['phase'] == 'holding':
        tongue_state['extension_progress'] = 1.0
        if tongue_state['timer'] >= HOLD_DURATION:
            tongue_state['phase'] = 'retracting'
            tongue_state['timer'] = 0.0

    elif tongue_state['phase'] == 'retracting':
        tongue_state['extension_progress'] = 1.0 - min(tongue_state['timer'] / RETRACTION_DURATION, 1.0)
        if tongue_state['timer'] >= RETRACTION_DURATION:
            tongue_state['phase'] = 'retracted'
            tongue_state['timer'] = 0.0
            tongue_state['extension_progress'] = 0.0
            tongue_state['cooldown_timer'] = COOLDOWN_DURATION
