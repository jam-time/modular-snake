# Design Document

## Overview

This design addresses seven critical issues in the Snake Game Demo's gameplay mechanics and visual animations. The solution involves restructuring the snake's visual representation to use a traveling sine wave pattern for realistic slithering, enhancing debug output for all visual components, implementing frame-rate independent food movement with speed caps, preventing food stacking through collision detection, adding safeguards against spawn deadlocks, and creating more dramatic and realistic animations for the snake's tongue and bite effects.

## Architecture

### Current System Analysis

The current implementation has several architectural issues:

1. **Slithering Animation**: Head oscillates side-to-side, which looks unnatural; needs a traveling wave pattern where head stays centered
2. **Visual Representation**: Conflates grid segments with visual circles, making it difficult to achieve smooth animations
3. **Food Movement**: Calculates velocity based on snake length rather than snake speed, and doesn't respect delta time properly
4. **Food Spawning**: Has no maximum iteration safeguard, causing potential infinite loops
5. **Tongue Animation**: Triggers too frequently (every 3 cells) and displays for too short (0.5 seconds)
6. **Mouth Animation**: Simple triangle with no bite effect or visual impact
7. **Turn Timing**: Direction changes happen when `move_timer >= time_per_cell`, causing the head to appear to back up before turning
8. **Turn Animation**: Direction changes are instant snaps rather than smooth transitions

### Proposed Architecture Changes

#### 1. Snake Visual System Refactoring

Separate mechanical grid segments from visual representation:

```
Snake (Mechanical)
├── segments: list[tuple[int, int]]  # Grid positions
├── direction, speed, etc.
└── visual_state: SnakeVisualState

SnakeVisualState (Visual)
├── wave_phase: float  # Current phase of traveling wave (radians)
├── wave_speed: float  # How fast wave travels (radians per second)
├── tongue_state: TongueState
└── bite_state: BiteState
```

#### 2. Food System Enhancement

Add collision detection and speed management:

```
Food
├── position: tuple[int, int]
├── velocity: tuple[float, float]
├── wander_timer: float
└── max_speed: float  # NEW: Capped by snake speed

FoodSystem
├── spawn_food_items() -> with max iteration limit
├── update_movement() -> respects delta time and speed cap
├── detect_stacking() -> NEW: Prevents overlapping food
└── resolve_collisions() -> NEW: Repositions stacked food
```

#### 3. Animation State Management

Centralize animation timing and state:

```
TongueState
├── extended: bool
├── extension_progress: float  # 0.0 to 1.0
├── timer: float
└── cooldown_timer: float

BiteState
├── active: bool
├── progress: float  # 0.0 to 1.0
├── wave_radii: list[float]
└── duration: float
```

## Components and Interfaces

### Component 1: Snake Sine Wave Animation System

**Location**: `components/snake.py` and `components/enhanced_visuals.py`

**New Data Structures**:

```python
class SnakeVisualState(TypedDict):
    wave_phase: float  # Current phase of traveling wave (radians)
    wave_speed: float  # How fast wave travels (radians per second)
```

**Key Functions**:

```python
def create_visual_state(snake: Snake) -> SnakeVisualState:
    '''Initialize visual state with wave parameters.'''
    return {
        'wave_phase': 0.0,
        'wave_speed': 4.0  # radians per second
    }

def update_wave_phase(
    visual_state: SnakeVisualState,
    delta_time: float
) -> None:
    '''Update wave phase to create traveling wave effect.
    
    - Increment phase by wave_speed * delta_time
    - Wrap phase to stay within 0 to 2π
    '''
    visual_state['wave_phase'] += visual_state['wave_speed'] * delta_time
    visual_state['wave_phase'] %= (2 * math.pi)

def calculate_segment_direction_vector(
    segment_index: int,
    segments: list[tuple[int, int]]
) -> tuple[float, float]:
    '''Calculate normalized direction vector for a segment.
    
    For each segment, look at the vector from next segment to current segment.
    This gives the direction the snake is traveling at that point.
    
    Returns:
        Normalized (x, y) direction vector
    '''

def calculate_perpendicular_vector(
    direction: tuple[float, float]
) -> tuple[float, float]:
    '''Calculate perpendicular vector (rotated 90 degrees).
    
    For direction (dx, dy), perpendicular is (-dy, dx)
    '''

def calculate_sine_wave_offset(
    segment_index: int,
    total_segments: int,
    wave_phase: float,
    base_amplitude: float
) -> float:
    '''Calculate sine wave offset for a segment.
    
    Args:
        segment_index: Index of segment (0 = head)
        total_segments: Total number of segments
        wave_phase: Current wave phase (radians)
        base_amplitude: Maximum amplitude in pixels
    
    Returns:
        Offset distance in pixels (positive or negative)
    
    Algorithm:
    - Head (segment 0): offset = 0 (no oscillation)
    - Segment 1: amplitude ramps from 0 to full over the segment
    - Segments 2+: full amplitude sine wave
    - Wave phase increases along body to create traveling effect
    '''

def calculate_circle_radius(
    circle_index: int,
    total_circles: int,
    circles_per_segment: int,
    base_radius: int
) -> int:
    '''Calculate radius for a circle based on position in snake.
    
    Tapering rules:
    - Segment 0 (head): full radius
    - Segment 1 (neck): 60% radius
    - Segment 2: full radius
    - Middle segments: full radius
    - Last 3 segments: taper from 100% to 20%
    '''

def calculate_circle_color(
    circle_index: int,
    total_circles: int,
    base_color: tuple[int, int, int]
) -> tuple[int, int, int]:
    '''Calculate color for a circle to create 3D gradient effect.
    
    Creates a gradient perpendicular to snake body for 3D appearance.
    Head color is slightly lighter than body color.
    '''

def get_circle_positions_for_rendering(
    visual_state: SnakeVisualState,
    snake: Snake
) -> list[tuple[float, float, int, tuple[int, int, int]]]:
    '''Return all circles with positions, radii, and gradient colors.
    
    For each segment:
    1. Calculate base pixel position (grid position + interpolation)
    2. Calculate direction vector for this segment
    3. Calculate perpendicular vector
    4. Calculate sine wave offset
    5. Apply offset perpendicular to direction
    6. Calculate radius and color
    7. Return (x, y, radius, color) tuple
    '''
```

**Algorithm for Sine Wave Slithering**:

1. **Head Position (Segment 0)**:
   - Calculate pixel position from grid position + interpolation
   - No sine wave offset applied (stays centered on path)

2. **First Body Segment (Segment 1)**:
   - Calculate direction vector from segment 2 to segment 1
   - Calculate perpendicular vector
   - For each circle in this segment:
     - Calculate position along segment (0.0 to 1.0)
     - Amplitude ramps from 0 at head to full at end: `amp = base_amplitude * position_in_segment`
     - Calculate sine: `offset = amp * sin(wave_phase + segment_index * wave_spacing)`
     - Apply offset perpendicular to direction

3. **Remaining Segments (Segment 2+)**:
   - Calculate direction vector from next segment to current segment
   - Calculate perpendicular vector
   - Full amplitude sine wave: `offset = base_amplitude * sin(wave_phase + segment_index * wave_spacing)`
   - Apply offset perpendicular to direction

4. **Wave Parameters**:
   - `base_amplitude`: 8 pixels (how far circles move side-to-side)
   - `wave_spacing`: π/2 radians per segment (creates smooth wave along body)
   - `wave_speed`: 4 radians per second (how fast wave travels toward tail)
   - `wave_phase`: Updated each frame by `wave_speed * delta_time`

5. **Circle Spacing**:
   - 3-4 circles per segment for smooth appearance
   - Circles evenly distributed along each segment
   - Total circles = `num_segments * circles_per_segment`

**Circle Radius Tapering**:
- Head segment (segment 0): Full radius
- First body segment (segment 1): Tapers down to smaller radius (neck effect)
- Second body segment (segment 2): Tapers back up to full radius
- Middle segments: Constant full radius
- Last 3 segments: Taper down from full radius to 20% of max radius (tail tip)

Example for 20px cell size (base radius = 10px):
- Segment 0 (head): radius = 10px
- Segment 1 (neck): radius = 6px (60% of max)
- Segment 2: radius = 10px (back to full)
- Segments 3 to N-4: radius = 10px (constant)
- Segment N-3: radius = 8px (80% of max)
- Segment N-2: radius = 5px (50% of max)
- Segment N-1 (tail): radius = 2px (20% of max)

**Circle Color Gradient (3D Effect)**:
- Apply a gradient perpendicular to the snake's body to create 3D appearance
- Head color is slightly lighter than body color (e.g., if body is RGB(50,200,50), head is RGB(70,220,70))
- Gradient runs across the width of each circle to simulate lighting/shading
- This creates depth and makes the snake appear cylindrical rather than flat

### Component 2: Enhanced Debug Output

**Location**: `components/snake.py`, `components/enhanced_visuals.py`

**Debug Output Format**:

```
[SNAKE] Frame 120, t=2.00s
[SNAKE] Grid Segments (4): [(20,15), (19,15), (18,15), (17,15)]
[SNAKE] Wave State: phase=2.45rad, speed=4.0rad/s
[SNAKE] Visual Circles (12 total):
  Seg 0 (head): (640.0,480.0,r=10,offset=0.0)
  Seg 1: (620.0,481.2,r=6,offset=1.2), (615.0,482.8,r=6,offset=2.8), (610.0,483.5,r=6,offset=3.5)
  Seg 2: (600.0,487.2,r=10,offset=7.2), (595.0,488.0,r=10,offset=8.0), (590.0,486.5,r=10,offset=6.5)
  Seg 3 (tail): (580.0,483.1,r=2,offset=3.1)
[SNAKE] Movement: dir=(1,0), speed=10.5, interp=0.35
[TONGUE] State: extended=True, progress=0.6, cooldown=1.2s
[BITE] Active: False
```

**Note**: Shows wave phase and offset values to help debug the sine wave animation. Output logged every frame as wave phase constantly updates.

**Implementation**:
- Add `debug_log_visual_state()` function
- Call once per frame when `config.debug_mode` is True
- Log only first 10 and last 10 circles to keep output manageable
- Show total count and sample positions with radii

### Component 3: Food Movement System Redesign

**Location**: `components/food.py`

**Changes to `update_movement()`**:

```python
def update_movement(state: dict[str, Any], delta_time: float) -> None:
    '''Update food movement with proper speed capping and delta time.'''
    
    # Get snake speed and calculate max food speed
    snake_speed = snake['speed']  # cells per second
    max_flee_speed = snake_speed * 0.75  # 75% of snake speed when fleeing
    wander_speed = snake_speed * 0.2  # 20% of snake speed when wandering (slow)
    
    # For each food item:
    # 1. Determine behavior (flee if snake nearby, otherwise wander)
    # 2. Calculate desired velocity based on behavior
    # 3. Clamp velocity magnitude to appropriate max speed
    # 4. Update position using: new_pos = old_pos + velocity * delta_time
    # 5. Clamp to map boundaries
```

**Key Changes**:
- Remove `snake_length` from speed calculation
- Use `snake_speed * 0.75` as maximum flee speed
- Use `snake_speed * 0.2` as wander speed (slow, random movement)
- Wander direction is completely random
- Ensure velocity is in cells/second (not cells/frame)
- Multiply by `delta_time` when updating position

**Velocity Clamping**:
```python
# After calculating flee_dir or wander_dir
# Cap at 75% of snake speed
max_food_speed = snake_speed * 0.75

velocity_magnitude = math.sqrt(vel_x**2 + vel_y**2)
if velocity_magnitude > max_food_speed:
    vel_x = (vel_x / velocity_magnitude) * max_food_speed
    vel_y = (vel_y / velocity_magnitude) * max_food_speed
```

### Component 4: Food Stacking Prevention

**Location**: `components/food.py`

**New Functions**:

```python
def detect_food_collisions(food_items: list[Food]) -> dict[tuple[int, int], list[int]]:
    '''Find all grid positions with multiple food items.
    
    Returns:
        Dictionary mapping position -> list of food indices at that position
    '''

def resolve_food_stacking(
    state: dict[str, Any],
    collisions: dict[tuple[int, int], list[int]]
) -> None:
    '''Reposition stacked food items to adjacent empty cells.
    
    For each collision:
    1. Keep first food item at current position
    2. For other food items, attempt to flee from snake to adjacent cells
    3. If no empty cells away from snake, find any adjacent empty cell
    4. Food items can cluster near each other, just not in same cell
    5. If no empty cells, try expanding search radius
    '''

def find_adjacent_empty_cell(
    position: tuple[int, int],
    state: dict[str, Any],
    prefer_away_from_snake: bool = True,
    max_radius: int = 3
) -> tuple[int, int] | None:
    '''Find nearest empty cell, preferring cells away from snake if possible.
    
    Args:
        position: Current food position
        state: Game state with snake position
        prefer_away_from_snake: If True, prioritize cells away from snake
        max_radius: Maximum search radius
    
    Returns:
        Empty cell position, or None if no cells available
    '''
```

**Integration**:
- Call `detect_food_collisions()` after all food movement
- Call `resolve_food_stacking()` if collisions detected
- Also check during food spawning in `spawn_food_items()`

### Component 5: Spawn Deadlock Prevention

**Location**: `components/food.py`

**Changes to `spawn_food_items()`**:

```python
def spawn_food_items(state: dict[str, Any]) -> None:
    '''Spawn a single food item with deadlock prevention.'''
    
    max_attempts = 100
    
    # Calculate available empty cells
    total_cells = config.map_size_width * config.map_size_height
    occupied_cells = len(snake_segments) + len(food_items)
    available_cells = total_cells - occupied_cells
    
    # Early exit if no space
    if available_cells <= 0:
        if config.debug_mode:
            print('[FOOD] No empty cells available, skipping spawn')
        return
    
    # Try to spawn with iteration limit
    for attempt in range(max_attempts):
        # ... existing spawn logic ...
    
    # Log warning if failed
    if config.debug_mode:
        print(f'[FOOD] Failed to spawn after {max_attempts} attempts, '
              f'{available_cells} cells theoretically available')
```

**Additional Safety**:
- Add check in `on_food_eaten()` to limit spawning attempts
- Never spawn more food than available empty cells
- Log warnings when approaching capacity

### Component 6: Tongue Animation Enhancement

**Location**: `components/enhanced_visuals.py`

**New Tongue State**:

```python
class TongueState(TypedDict):
    extended: bool
    extension_progress: float  # 0.0 (retracted) to 1.0 (fully extended)
    timer: float  # Time in current state
    cooldown_timer: float  # Time until next flick allowed
```

**Updated Animation Logic**:

```python
def update_tongue_animation(snake: dict[str, Any], delta_time: float) -> None:
    '''Update tongue with proper timing and forked shape.'''
    
    EXTENSION_DURATION = 0.4  # Seconds to extend
    HOLD_DURATION = 0.8  # Seconds to hold extended
    RETRACTION_DURATION = 0.4  # Seconds to retract
    COOLDOWN_DURATION = 3.0  # Seconds between flicks
    
    tongue_state = snake.get('tongue_state')
    if not tongue_state:
        snake['tongue_state'] = create_tongue_state()
        tongue_state = snake['tongue_state']
    
    # Pause tongue animation during bite
    bite_state = snake.get('bite_state')
    if bite_state and bite_state.get('active', False):
        return
    
    # Update cooldown
    if tongue_state['cooldown_timer'] > 0:
        tongue_state['cooldown_timer'] -= delta_time
        return
    
    # Update animation phases
    tongue_state['timer'] += delta_time
    
    if tongue_state['timer'] < EXTENSION_DURATION:
        # Extending phase
        tongue_state['extension_progress'] = tongue_state['timer'] / EXTENSION_DURATION
        tongue_state['extended'] = True
    elif tongue_state['timer'] < EXTENSION_DURATION + HOLD_DURATION:
        # Holding phase
        tongue_state['extension_progress'] = 1.0
        tongue_state['extended'] = True
    elif tongue_state['timer'] < EXTENSION_DURATION + HOLD_DURATION + RETRACTION_DURATION:
        # Retracting phase
        retract_time = tongue_state['timer'] - EXTENSION_DURATION - HOLD_DURATION
        tongue_state['extension_progress'] = 1.0 - (retract_time / RETRACTION_DURATION)
        tongue_state['extended'] = True
    else:
        # Complete, start cooldown
        tongue_state['extended'] = False
        tongue_state['extension_progress'] = 0.0
        tongue_state['timer'] = 0.0
        tongue_state['cooldown_timer'] = COOLDOWN_DURATION
```

**Forked Tongue Rendering**:

```python
def render_forked_tongue(
    screen: pygame.Surface,
    base_pos: tuple[float, float],
    direction: tuple[int, int],
    extension_progress: float
) -> None:
    '''Draw forked tongue with two subtle prongs.'''
    
    cell_size = config.grid_cell_size
    tongue_length = cell_size * 0.6 * extension_progress
    tongue_width = 2
    tongue_color = (200, 50, 50)
    
    # Calculate base angle from direction
    base_angle = math.atan2(direction[1], direction[0])
    
    # Main tongue extends 3/4 of total length
    main_length = tongue_length * 0.75
    main_tip_x = base_pos[0] + math.cos(base_angle) * main_length
    main_tip_y = base_pos[1] + math.sin(base_angle) * main_length
    
    # Draw main tongue line
    pygame.draw.line(screen, tongue_color, 
                    (int(base_pos[0]), int(base_pos[1])),
                    (int(main_tip_x), int(main_tip_y)), 
                    tongue_width)
    
    # Fork splits at 1/4 of remaining length
    fork_length = tongue_length * 0.25
    fork_angle_rad = math.radians(20)  # 20 degrees
    
    # Left prong
    left_angle = base_angle - fork_angle_rad
    left_tip_x = main_tip_x + math.cos(left_angle) * fork_length
    left_tip_y = main_tip_y + math.sin(left_angle) * fork_length
    pygame.draw.line(screen, tongue_color,
                    (int(main_tip_x), int(main_tip_y)),
                    (int(left_tip_x), int(left_tip_y)),
                    tongue_width)
    
    # Right prong
    right_angle = base_angle + fork_angle_rad
    right_tip_x = main_tip_x + math.cos(right_angle) * fork_length
    right_tip_y = main_tip_y + math.sin(right_angle) * fork_length
    pygame.draw.line(screen, tongue_color,
                    (int(main_tip_x), int(main_tip_y)),
                    (int(right_tip_x), int(right_tip_y)),
                    tongue_width)
```

### Component 7: Bite Animation System

**Location**: `components/enhanced_visuals.py`

**New Bite State**:

```python
class BiteState(TypedDict):
    active: bool
    progress: float  # 0.0 to 1.0
    bite_position: tuple[float, float]  # Where bite occurred
    wave_count: int
    duration: float
```

**Bite Trigger**:

```python
def trigger_bite_animation(snake: dict[str, Any], bite_pos: tuple[float, float]) -> None:
    '''Start bite animation at food consumption.'''
    
    snake['bite_state'] = {
        'active': True,
        'progress': 0.0,
        'bite_position': bite_pos,
        'wave_count': 3,
        'duration': 0.5
    }
```

**Bite Animation Update**:

```python
def update_bite_animation(snake: dict[str, Any], delta_time: float) -> None:
    '''Update bite animation progress.'''
    
    bite_state = snake.get('bite_state')
    if not bite_state or not bite_state['active']:
        return
    
    bite_state['progress'] += delta_time / bite_state['duration']
    
    if bite_state['progress'] >= 1.0:
        bite_state['active'] = False
        bite_state['progress'] = 0.0
```

**Bite Rendering**:

```python
def render_bite_animation(
    screen: pygame.Surface,
    bite_state: BiteState,
    direction: tuple[int, int],
    head_pos: tuple[float, float]
) -> None:
    '''Draw dramatic bite with enlarged head, C-shaped mouth, and squiggly lines.'''
    
    if not bite_state['active']:
        return
    
    progress = bite_state['progress']
    pos = bite_state['bite_position']
    
    # Enlarge entire head (scale up by 1.5x during bite) - VISUAL ONLY
    # Note: This does not affect collision detection, only rendering
    head_scale = 1.0 + (0.5 * min(progress * 2, 1.0))
    enlarged_radius = int(config.grid_cell_size // 2 * head_scale)
    
    # Draw enlarged head circle
    pygame.draw.circle(screen, config.color_snake_head, 
                      (int(head_pos[0]), int(head_pos[1])), enlarged_radius)
    
    # Draw C-shaped mouth opening
    # Calculate mouth arc based on direction
    base_angle = math.atan2(direction[1], direction[0])
    mouth_opening_angle = math.pi * 0.6  # 108 degrees of opening
    
    # Draw arc for C-shape (use pygame.draw.arc)
    mouth_rect = pygame.Rect(
        int(head_pos[0] - enlarged_radius),
        int(head_pos[1] - enlarged_radius),
        enlarged_radius * 2,
        enlarged_radius * 2
    )
    start_angle = base_angle - mouth_opening_angle / 2
    end_angle = base_angle + mouth_opening_angle / 2
    pygame.draw.arc(screen, (50, 50, 50), mouth_rect, start_angle, end_angle, 3)
    
    # Draw 5 squiggly lines around mouth
    num_lines = 5
    line_length = 20  # 20 pixels
    wave_frequency = 5  # 5 pixels per wave (4 waves total)
    
    for i in range(num_lines):
        # Calculate angle around mouth (spread around 180 degrees in front)
        angle_offset = (i / (num_lines - 1) - 0.5) * math.pi  # -90 to +90 degrees
        angle = base_angle + angle_offset
        
        # All lines shoot out at once
        current_length = line_length * min(progress * 2, 1.0)
        
        # Fade out as animation progresses
        alpha = int(255 * (1.0 - progress))
        
        # Create squiggly effect with sine wave
        # 4 waves over 20 pixels = wavelength of 5 pixels
        num_segments = 20  # 1 segment per pixel for smooth curve
        prev_pos = None
        for seg in range(num_segments + 1):
            t = seg / num_segments
            distance = current_length * t
            
            # Base position along angle
            x = pos[0] + math.cos(angle) * distance
            y = pos[1] + math.sin(angle) * distance
            
            # Add perpendicular wiggle (4 complete waves over line_length)
            wave_progress = (distance / wave_frequency) * math.pi * 2
            wiggle_amplitude = 3  # pixels
            wiggle = math.sin(wave_progress) * wiggle_amplitude
            x += math.cos(angle + math.pi/2) * wiggle
            y += math.sin(angle + math.pi/2) * wiggle
            
            if prev_pos is not None:
                # Draw with fade (use temporary surface for alpha if needed)
                pygame.draw.line(screen, (255, 255, 255), prev_pos, (int(x), int(y)), 2)
            prev_pos = (int(x), int(y))
```

**Integration with Collision System**:

In `components/collision.py`, when food is eaten:

```python
# After detecting food collision
from components.enhanced_visuals import trigger_bite_animation

# Get pixel position of food
food_pixel_pos = calculate_pixel_position(food_item['position'])
trigger_bite_animation(snake, food_pixel_pos)
```

### Component 8: Improved Turn Timing System

**Location**: `components/snake.py`

**Problem Analysis**:

Currently, the direction change happens when `move_timer >= time_per_cell`, meaning the snake waits until it's *fully* in the next grid cell before turning. This causes the head to visually appear to back up when it finally turns.

**Solution**:

Apply direction changes as soon as the player presses a turn key, which will be while the head is in the process of entering the next cell (interpolation between 0.0 and 1.0). This only applies when enhanced visuals are enabled.

**Conceptual Flow**:
1. Snake head is at grid position (5, 5), moving right toward (6, 5)
2. Interpolation is at 0.3 (30% of the way into cell (6, 5))
3. Player presses down arrow
4. Direction immediately changes to down
5. Head continues smoothly into (6, 5) but now curves downward
6. When head reaches (6, 5) fully, next move will be to (6, 6)

```python
def update_movement(snake: Snake, delta_time: float) -> None:
    '''Update snake movement with early turn timing for enhanced visuals.'''
    
    snake['move_timer'] += delta_time
    time_per_cell = 1.0 / snake['speed']
    
    # Calculate interpolation first
    snake['interpolation'] = min(snake['move_timer'] / time_per_cell, 1.0)
    
    # For non-enhanced mode, apply direction change at cell boundary
    if not config.enable_enhanced_visuals:
        if snake['move_timer'] >= time_per_cell and snake['direction'] != snake['next_direction']:
            snake['direction'] = snake['next_direction']
    
    # Move to next grid cell when timer expires
    if snake['move_timer'] >= time_per_cell:
        snake['move_timer'] -= time_per_cell
        
        head_x, head_y = snake['segments'][0]
        dx, dy = snake['direction']
        new_head = (head_x + dx, head_y + dy)
        
        snake['segments'] = [new_head] + snake['segments'][:-1]
        snake['distance_moved'] += 1.0
```

**Updated set_direction()**:

```python
def set_direction(snake: Snake, new_direction: tuple[int, int]) -> None:
    '''Set snake's next direction with immediate application for enhanced visuals.'''
    
    current_dir = snake['direction']
    
    is_reversal = (
        new_direction[0] == -current_dir[0] and
        new_direction[1] == -current_dir[1]
    )
    
    if not is_reversal and new_direction != (0, 0):
        if config.enable_enhanced_visuals:
            # Apply turn immediately - head is entering next cell
            snake['old_direction'] = snake['direction']
            snake['direction'] = new_direction
            snake['next_direction'] = new_direction
            snake['turn_progress'] = 0.0
            
            if config.debug_mode:
                interp = snake.get('interpolation', 0.0)
                print(f'[SNAKE] Turn applied at interp={interp:.2f}: {snake["old_direction"]} -> {new_direction}')
        else:
            # Queue for next cell boundary (original behavior)
            snake['next_direction'] = new_direction
            
            if config.debug_mode:
                print(f'[SNAKE] Direction queued: {new_direction}')
```

**Key Changes**:
- When `config.enable_enhanced_visuals` is True, direction changes happen immediately in `set_direction()`
- The turn happens while the head is entering the next cell (interpolation 0.0-1.0)
- When False, use original behavior (queue direction for cell boundary at interpolation = 1.0)
- This prevents the "backing up" visual because the turn happens into the cell being entered
- Uses existing config flag rather than adding a new one

### Component 9: Smooth Turn Animation

**Location**: `components/snake.py` and `components/enhanced_visuals.py`

**Problem Analysis**:

When direction changes, the head instantly snaps to moving in the new direction. We want smooth animation into the turn.

**Solution**:

Track when direction changes occur and smoothly interpolate the head's movement direction:

```python
class Snake(TypedDict):
    # ... existing fields ...
    turn_progress: float  # NEW: 0.0 to 1.0, tracks turn animation
    old_direction: tuple[int, int]  # NEW: Direction before turn
```

**Turn Animation Logic**:

```python
def update_movement(snake: Snake, delta_time: float) -> None:
    '''Update snake movement with smooth turn animation.'''
    
    snake['move_timer'] += delta_time
    time_per_cell = 1.0 / snake['speed']
    
    # Calculate interpolation
    snake['interpolation'] = min(snake['move_timer'] / time_per_cell, 1.0)
    
    # Apply direction change when head is mostly in next cell
    if snake['interpolation'] >= 0.5 and snake['direction'] != snake['next_direction']:
        # Start turn animation
        snake['old_direction'] = snake['direction']
        snake['direction'] = snake['next_direction']
        snake['turn_progress'] = 0.0
        
        if config.debug_mode:
            print(f'[SNAKE] Turn started: {snake["old_direction"]} -> {snake["direction"]}')
    
    # Update turn animation progress
    if snake.get('turn_progress', 1.0) < 1.0:
        # Turn completes over remaining time in current cell
        remaining_time = time_per_cell - snake['move_timer']
        turn_speed = 1.0 / max(remaining_time, 0.1)  # Prevent division by zero
        snake['turn_progress'] = min(snake['turn_progress'] + turn_speed * delta_time, 1.0)
    
    # Move to next grid cell when timer expires
    if snake['move_timer'] >= time_per_cell:
        snake['move_timer'] -= time_per_cell
        
        head_x, head_y = snake['segments'][0]
        dx, dy = snake['direction']
        new_head = (head_x + dx, head_y + dy)
        
        snake['segments'] = [new_head] + snake['segments'][:-1]
        snake['distance_moved'] += 1.0
        
        # Reset turn animation
        snake['turn_progress'] = 1.0
```

**Rendering with Smooth Turns**:

```python
def get_interpolated_head_position(snake: Snake) -> tuple[float, float]:
    '''Calculate head position with smooth turn animation.
    
    When turning, blend between old and new directions based on turn_progress.
    '''
    head = snake['segments'][0]
    next_head_x = head[0] + snake['direction'][0]
    next_head_y = head[1] + snake['direction'][1]
    
    # Check if we're mid-turn
    turn_progress = snake.get('turn_progress', 1.0)
    if turn_progress < 1.0:
        # Blend between old and new directions
        old_dir = snake.get('old_direction', snake['direction'])
        new_dir = snake['direction']
        
        # Calculate intermediate direction
        blend_x = old_dir[0] * (1.0 - turn_progress) + new_dir[0] * turn_progress
        blend_y = old_dir[1] * (1.0 - turn_progress) + new_dir[1] * turn_progress
        
        # Use blended direction for interpolation
        interp = snake['interpolation']
        pixel_x = head[0] + blend_x * interp
        pixel_y = head[1] + blend_y * interp
        
        return (pixel_x, pixel_y)
    else:
        # Normal interpolation
        return interpolate_position(head, (next_head_x, next_head_y), snake['interpolation'])
```

**Algorithm Summary**:

1. **Turn Trigger**: When `interpolation >= 0.5` and player has queued a new direction
2. **Turn Animation**: `turn_progress` goes from 0.0 to 1.0 over the remaining time in the current cell
3. **Head Position**: Blend between `old_direction` and `direction` based on `turn_progress`
4. **Result**: Head smoothly curves into the new direction instead of snapping

**Visual Effect**:
- At turn_progress = 0.0: Head moving in old direction
- At turn_progress = 0.5: Head moving diagonally between old and new directions
- At turn_progress = 1.0: Head fully moving in new direction
- Creates a smooth arc rather than a sharp corner

## Data Models

### Snake Extended Model

```python
class Snake(TypedDict):
    # Existing fields
    segments: list[tuple[int, int]]
    direction: tuple[int, int]
    next_direction: tuple[int, int]
    speed: float
    move_timer: float
    interpolation: float
    distance_moved: float
    
    # New fields
    visual_state: SnakeVisualState
    tongue_state: TongueState
    bite_state: BiteState

class SnakeVisualState(TypedDict):
    wave_phase: float  # Current phase of traveling wave (radians)
    wave_speed: float  # How fast wave travels (radians per second)

class TongueState(TypedDict):
    extended: bool
    extension_progress: float
    timer: float
    cooldown_timer: float

class BiteState(TypedDict):
    active: bool
    progress: float
    bite_position: tuple[float, float]
    wave_count: int
    duration: float
```

### Food Extended Model

```python
class Food(TypedDict):
    position: tuple[int, int]
    velocity: tuple[float, float]
    wander_timer: float
    max_speed: float  # NEW: Dynamically set based on snake speed
```

## Error Handling

### Food Spawning Errors

**Issue**: Infinite loop when no empty cells available

**Solution**:
- Pre-calculate available cells before attempting spawn
- Return early if no cells available
- Add iteration limit (100 attempts)
- Log warnings when spawn fails

### Food Stacking Errors

**Issue**: Multiple food items at same position

**Solution**:
- Detect collisions after movement
- Resolve by repositioning to adjacent cells
- Use expanding radius search if nearby cells occupied
- Log warnings if resolution fails

### Animation State Errors

**Issue**: Missing or invalid animation state

**Solution**:
- Initialize states lazily on first access
- Provide default values for all state fields
- Validate state before rendering
- Reset state on errors

## Testing Strategy

### Unit Tests

1. **Sine Wave Calculations**
   - Test wave phase updates correctly with delta time
   - Test wave phase wraps at 2π
   - Test head has zero offset
   - Test first segment has ramping amplitude
   - Test subsequent segments have full amplitude
   - Test perpendicular vector calculation

2. **Food Speed Capping**
   - Test velocity never exceeds snake speed * 0.9
   - Test delta time integration
   - Test speed updates when snake speeds up

3. **Food Collision Detection**
   - Test detects multiple food at same position
   - Test resolution finds adjacent cells
   - Test handles no available cells gracefully

4. **Spawn Deadlock Prevention**
   - Test early exit when no cells available
   - Test iteration limit prevents infinite loops
   - Test correct cell counting

5. **Animation Timing**
   - Test tongue extends for 0.8+ seconds
   - Test tongue cooldown is 3+ seconds
   - Test bite animation completes in 0.5 seconds

### Integration Tests

1. **Slithering Animation**
   - Visual test: Snake body shows smooth sine wave pattern
   - Verify head stays centered on path
   - Verify wave appears to travel toward tail
   - Check first segment has smooth amplitude ramp
   - Verify wave works correctly when changing directions

2. **Food Movement**
   - Verify food never moves faster than snake
   - Check food doesn't stack in corners
   - Verify movement is frame-rate independent

3. **Tongue Animation**
   - Visual test: Forked tongue shape visible
   - Verify timing feels natural
   - Check cooldown prevents rapid flicking

4. **Bite Animation**
   - Visual test: Dramatic mouth opening
   - Verify waves expand smoothly
   - Check animation doesn't block gameplay

### Debug Output Validation

1. **Completeness**
   - Verify all grid segments logged
   - Verify all visual circles logged
   - Verify all connecting circles logged

2. **Readability**
   - Check output is concise
   - Verify grouping makes sense
   - Ensure timestamps are accurate

## Performance Considerations

### Sine Wave Calculations

- Pre-calculate direction and perpendicular vectors per segment
- Cache sine values if calculating multiple circles per segment
- Use simple math operations (no complex transformations)

### Food Collision Detection

- Only check after movement (not every frame)
- Use dictionary for O(1) position lookup
- Limit resolution search radius

### Animation Rendering

- Skip bite animation rendering if not active
- Use simple shapes (circles, lines) for performance
- Avoid creating new surfaces each frame

### Debug Output

- Only log when `debug_mode` is True
- Limit logging frequency (e.g., every 10 frames for some data)
- Use string formatting efficiently

## Implementation Notes

### Phase 1: Visual System Refactoring
- Add visual_state with wave_phase to Snake
- Implement wave phase update logic
- Implement sine wave offset calculations
- Update render_snake() to apply sine wave
- Test slithering animation with traveling wave

### Phase 2: Debug Output
- Add debug logging functions
- Format output for readability
- Test with various snake lengths

### Phase 3: Food System Fixes
- Fix speed calculation
- Add collision detection
- Add spawn safeguards
- Test edge cases

### Phase 4: Animation Enhancements
- Implement tongue state machine
- Add forked tongue rendering
- Implement bite animation
- Integrate with collision system

### Code Style Notes

- Follow Python steering guide (single quotes, f-strings, type hints)
- Keep functions focused and small
- Use descriptive variable names
- Add docstrings for all public functions
- Remove trailing whitespace from blank lines
