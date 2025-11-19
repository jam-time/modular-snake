# Design Document

## Overview

The Snake Game Demo is a modular, presentation-friendly Python application built with Pygame. The architecture prioritizes live configurability, feature independence, and visual clarity for middle school audiences. The system uses a component-based design where each feature can be toggled via configuration flags, allowing presenters to progressively reveal functionality during demonstrations.

The game runs at a constant 60 FPS with two distinct rendering modes: a simple grid-based mode for basic gameplay, and an enhanced visual mode featuring circle-based rendering with sine wave slithering animations. All features are controlled through a centralized configuration section using clear, self-documenting variable names.

## Architecture

### High-Level Structure

```
snake_game/
├── main.py                 # Entry point and game loop
├── config.py               # Configuration class with validation
├── requirements.txt        # Dependencies (pygame)
├── PRESENTATION_GUIDE.md   # Quick reference for presenters
└── components/            # Feature modules
    ├── __init__.py
    ├── snake.py           # Snake entity and movement
    ├── food.py            # Food spawning and behavior
    ├── collision.py       # Collision detection
    ├── rendering.py       # Visual rendering systems
    ├── enhanced_visuals.py    # All visual enhancements combined
    └── secrets.py         # Hidden features: multiplayer and tournament
```

### Core Design Principles

1. **Configuration-Driven**: All features controlled by boolean flags and numeric parameters in a single config section
2. **Component Independence**: Each component operates without dependencies on other components
3. **Graceful Degradation**: Disabled components don't break the game
4. **60 FPS Constant**: Frame rate remains fixed; visual complexity varies by feature flags
5. **Grid-Based Logic**: Game logic operates on discrete grid cells with visual interpolation for smoothness
6. **Progressive Enhancement**: Features can be enabled incrementally to create multiple demonstration moments

### Feature Flag System

The game uses independent boolean flags for each major feature, allowing fine-grained control during presentations:

**Core Visual Enhancements**:
- `enable_enhanced_visuals`: Circle-based rendering with slithering animation

**Interactive Animations**:
- `enable_mouth_animation`: Mouth opens when near food
- `enable_tongue_animation`: Tongue flicks periodically
- `enable_animated_food`: Mouse sprite for food items
- `enable_food_movement`: Food wanders and flees

**Hidden Features**:
- `secret_mode_alpha`: Two-player multiplayer mode
- `secret_mode_omega`: Tournament bracket system

**Design Rationale**: Independent flags allow presenters to reveal features one at a time, creating multiple "wow moments" and demonstrating how complex features are built from simpler components. Each flag can be toggled without affecting other features, making the demo resilient to configuration changes.

## Components and Interfaces

### Configuration Module (config.py)

The configuration module provides a Config class with property-based validation and automatic value adjustment to ensure valid game state.

**Config Class Structure**
```python
class Config:
    def __init__(self):
        self._window_width = 800
        self._window_height = 600
        self._fullscreen_mode = False
        self._grid_cell_size = 20
        self._frame_rate = 60
        self._map_size_width = 40
        self._map_size_height = 30
        self._initial_speed = 10
        self._speed_factor = 1.5
        self._food_count = 1
        self._speed_calculation = None
        
        self.enable_enhanced_visuals = False
        self.enable_mouth_animation = False
        self.enable_tongue_animation = False
        self.enable_animated_food = False
        self.enable_food_movement = False
        
        self.secret_mode_alpha = False
        self.secret_mode_omega = False
        
        self.color_background = (20, 20, 30)
        self.color_snake_body = (50, 200, 50)
        self.color_snake_head = (70, 220, 70)
        self.color_food = (220, 50, 50)
        self.color_text = (255, 255, 255)
        self.color_ui = (100, 100, 120)
    
    @property
    def window_width(self):
        return self._window_width
    
    @window_width.setter
    def window_width(self, value):
        self._window_width = max(400, value)
    
    @property
    def window_height(self):
        return self._window_height
    
    @window_height.setter
    def window_height(self, value):
        self._window_height = max(300, value)
    
    @property
    def grid_cell_size(self):
        return self._grid_cell_size
    
    @grid_cell_size.setter
    def grid_cell_size(self, value):
        self._grid_cell_size = max(10, min(50, value))
    
    @property
    def map_size_width(self):
        max_cells = self._window_width // self._grid_cell_size
        return min(self._map_size_width, max_cells)
    
    @map_size_width.setter
    def map_size_width(self, value):
        self._map_size_width = max(10, value)
    
    @property
    def map_size_height(self):
        max_cells = self._window_height // self._grid_cell_size
        return min(self._map_size_height, max_cells)
    
    @map_size_height.setter
    def map_size_height(self, value):
        self._map_size_height = max(10, value)
    
    @property
    def initial_speed(self):
        return self._initial_speed
    
    @initial_speed.setter
    def initial_speed(self, value):
        self._initial_speed = max(1, value)
    
    @property
    def speed_factor(self):
        return self._speed_factor
    
    @speed_factor.setter
    def speed_factor(self, value):
        self._speed_factor = max(1.0, min(5.0, value))
    
    @property
    def frame_rate(self):
        return 60
    
    @property
    def food_count(self):
        if callable(self._food_count):
            return self._food_count
        return max(1, self._food_count)
    
    @food_count.setter
    def food_count(self, value):
        if callable(value):
            self._food_count = value
        else:
            self._food_count = max(1, value)
    
    @property
    def speed_calculation(self):
        if callable(self._speed_calculation):
            return self._speed_calculation
        return lambda current_speed, score: current_speed + self._speed_factor
    
    @speed_calculation.setter
    def speed_calculation(self, value):
        if callable(value):
            self._speed_calculation = value
        else:
            self._speed_calculation = None

config = Config()
```

**Validation Rules**
- `window_width`: Minimum 400 pixels
- `window_height`: Minimum 300 pixels
- `grid_cell_size`: Between 10 and 50 pixels
- `map_size_width`: Minimum 10 cells, automatically capped to fit window
- `map_size_height`: Minimum 10 cells, automatically capped to fit window
- `initial_speed`: Minimum 1 cell per second
- `speed_factor`: Between 1.0 and 5.0
- `frame_rate`: Fixed at 60 (read-only property)
- `food_count`: Can be an integer (minimum 1) or a callable function that takes score and returns food count
- `speed_calculation`: Can be a callable function that takes (current_speed, score) and returns new speed, defaults to additive

**Configurable Functions**

The config supports lambda functions for dynamic behavior:

```python
# Example: Food count doubles with each food eaten
config.food_count = lambda score: max(1, score * 2)

# Example: Exponential speed increase
config.speed_calculation = lambda speed, score: speed * 1.2

# Example: Speed caps at 50
config.speed_calculation = lambda speed, score: min(speed + 2, 50)
```

### Main Game Loop (main.py)

**Game Loop Structure**
```python
from config import config

def main():
    initialize_pygame()
    game_state = create_game_state()
    clock = pygame.time.Clock()
    
    while game_state.running:
        handle_input(game_state)
        update_game_state(game_state)
        render_frame(game_state)
        clock.tick(config.frame_rate)
```

**Component Integration Pattern**
```python
from config import config

def handle_input(state):
    """Process keyboard input for all players"""
    keys = pygame.key.get_pressed()
    
    # Player 1 accepts both arrow keys and WASD
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        snake.set_direction(state.snake, (0, -1))
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        snake.set_direction(state.snake, (0, 1))
    elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
        snake.set_direction(state.snake, (-1, 0))
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        snake.set_direction(state.snake, (1, 0))
    
    if config.secret_mode_alpha and state.player_two:
        secrets.handle_player_two_input(state, keys)

def update_game_state(state):
    snake.update_movement(state)
    
    if config.enable_food_movement:
        food.update_movement(state)
    
    collision.check_collisions(state)
    
    if config.secret_mode_alpha:
        secrets.update_player_two(state)

def render_frame(state):
    screen.fill(config.color_background)
    
    # Tournament mode overrides normal rendering
    if config.secret_mode_omega and state.tournament:
        secrets.render_tournament_phase(state, screen)
    else:
        # Normal game rendering
        if config.enable_enhanced_visuals:
            enhanced_visuals.render_snake(state, screen)
        else:
            rendering.render_snake_basic(state, screen)
        
        # Food rendering with optional sprite
        if config.enable_animated_food:
            enhanced_visuals.render_food_sprite(state, screen)
        else:
            rendering.render_food_basic(state, screen)
        
        rendering.render_ui(state, screen)
        
        if config.secret_mode_alpha:
            secrets.render_multiplayer_ui(state, screen)
    
    pygame.display.flip()
```

### Snake Component (components/snake.py)

**Responsibilities**
- Snake entity state management
- Movement logic and speed progression
- Grid position updates with frame interpolation
- Segment management (growth, tail following)

**Key Functions**
```python
def create_snake(start_pos, direction):
    """Initialize snake with 4 segments"""
    
def update_movement(state):
    """Update snake position based on speed and direction"""
    
def update_speed(snake, score):
    """Calculate new speed using config.speed_calculation"""
    
def interpolate_position(grid_pos, next_grid_pos, progress):
    """Calculate smooth position between grid cells"""
    
def add_segment(snake):
    """Add new segment when food is eaten"""
    
def get_head_position(snake):
    """Return current head grid coordinates"""
```

**Speed Calculation Logic**
```python
def update_speed(snake, score):
    """Update snake speed based on configuration"""
    speed_calc = config.speed_calculation
    new_speed = speed_calc(snake.speed, score)
    snake.speed = new_speed
```

**Data Structure**
```python
Snake = {
    'segments': [(x, y), ...],  # Grid positions
    'direction': (dx, dy),
    'next_direction': (dx, dy),
    'speed': float,  # Cells per second
    'move_timer': float,  # Time until next grid move
    'interpolation': float,  # 0.0 to 1.0 for smooth rendering
}
```

### Food Component (components/food.py)

**Responsibilities**
- Multiple food spawning at valid positions
- Food count management based on score
- Food movement behavior (when enabled)
- Distance calculations to snake

**Key Functions**
```python
def spawn_food_items(state):
    """Spawn food items based on config.food_count"""
    
def get_required_food_count(score):
    """Calculate how many food items should exist based on score"""
    
def update_movement(state):
    """Move all food items based on snake proximity"""
    
def calculate_flee_direction(food_pos, snake_head):
    """Determine direction away from snake"""
    
def is_valid_spawn_position(pos, state):
    """Check if position is not occupied by snake or other food"""
```

**Food Management Logic**
```python
# When food is eaten, check if more food should spawn
def on_food_eaten(state):
    state.score += 1
    
    # Get required count (may be function or int)
    if callable(config.food_count):
        required_count = config.food_count(state.score)
    else:
        required_count = config.food_count
    
    # Spawn additional food if needed
    while len(state.food_items) < required_count:
        spawn_food_items(state)
```

### Collision Component (components/collision.py)

**Responsibilities**
- Wall collision detection
- Self-collision detection
- Food consumption detection
- Multiplayer collision handling

**Key Functions**
```python
def check_wall_collision(snake, map_size):
    """Return True if snake head is outside bounds"""
    
def check_self_collision(snake):
    """Return True if head overlaps body"""
    
def check_food_collision(snake, food):
    """Return True if snake head reaches food"""
    
def check_player_collision(snake1, snake2):
    """Check if two snakes collide"""
```

### Rendering Component (components/rendering.py)

**Responsibilities**
- Basic grid-based snake rendering
- Basic food rendering
- UI elements (score, game over, restart prompt)
- Grid visualization

**Key Functions**
```python
def render_snake_basic(state, screen):
    """Draw snake as rectangular grid cells"""
    
def render_food_basic(state, screen):
    """Draw food as colored circle"""
    
def render_ui(state, screen):
    """Draw score and game state text"""
    
def render_game_over(state, screen):
    """Display game over screen with restart option"""
```

### Enhanced Visuals Component (components/enhanced_visuals.py)

**Responsibilities**
- Circle-based snake rendering with slithering animation
- Sine wave slithering animation
- Tapered body appearance
- Head shape with eyes
- Mouth opening animation based on food proximity (when enabled)
- Tongue flicking animation (when enabled)
- Mouse sprite rendering for food (when enabled)

**Key Functions**
```python
def render_snake(state, screen):
    """Draw snake with circles and slithering animation"""
    
def calculate_sine_wave_offset(segment_index, snake_speed, time):
    """Calculate perpendicular offset for slithering"""
    
def calculate_segment_radius(segment_index, total_segments):
    """Calculate radius for tapering effect"""
    
def render_head_details(head_pos, direction, state, screen):
    """Draw eyes and head shape"""
    
def render_mouth_animation(snake, food_items, screen):
    """Draw open mouth when near any food (if enabled)"""
    
def update_tongue_animation(snake, distance_moved):
    """Toggle tongue state periodically (if enabled)"""
    
def render_food_sprite(food, screen):
    """Draw mouse sprite instead of circle (if enabled)"""
```

**Design Rationale**: The enhanced visuals component provides the core visual upgrade (circles + slithering), while mouth, tongue, and food sprite animations are independently toggleable. This allows presenters to progressively reveal features: first show the slithering snake, then add mouth animation, then tongue, then animated food sprites.

**Slithering Animation Algorithm**
```python
# Sine wave frequency proportional to speed
frequency = snake.speed * 0.1
amplitude = GRID_CELL_SIZE * 0.3

for i, segment in enumerate(snake.segments):
    # Calculate phase based on segment position in body
    phase = i * 0.5 + time * frequency
    
    # Calculate perpendicular offset
    offset = sin(phase) * amplitude
    
    # Apply offset perpendicular to movement direction
    perpendicular = get_perpendicular(snake.direction)
    render_pos = segment + perpendicular * offset
    
    # Draw circle with tapered radius
    radius = calculate_segment_radius(i, len(snake.segments))
    pygame.draw.circle(screen, color, render_pos, radius)
```

### Input Handling Design

**Single Player Mode**: Both arrow keys and WASD control Player 1's snake. This provides flexibility for different keyboard layouts and allows students to choose their preferred control scheme.

**Multiplayer Mode** (`secret_mode_alpha = True`): Player 1 uses arrow keys, Player 2 uses WASD. This prevents control conflicts and allows two players to share one keyboard comfortably.

**Design Rationale**: Supporting both control schemes in single-player mode makes the game more accessible and demonstrates how games can accommodate different player preferences. The automatic separation in multiplayer mode shows thoughtful UX design.



### Secrets Component (components/secrets.py)

**Responsibilities**
- Hidden multiplayer mode (SECRET_MODE_ALPHA)
- Hidden tournament mode (SECRET_MODE_OMEGA)
- Second player snake management
- WASD input handling
- Dual score tracking
- Tournament bracket generation and visualization
- Match progression and winner tracking

**Multiplayer Functions**
```python
def create_player_two(state):
    """Initialize second snake at different position"""
    
def handle_player_two_input(state, keys):
    """Process WASD controls"""
    
def update_player_two(state):
    """Update second snake movement"""
    
def render_scores(state, screen):
    """Display both player scores"""
```

**Tournament Functions**
```python
def create_tournament(player_names):
    """Generate bracket structure for up to 8 players"""
    
def advance_winner(tournament, winner):
    """Move winner to next round"""
    
def render_bracket(tournament, screen):
    """Display bracket with next match highlighted"""
    
def render_pre_match_splash(match, screen):
    """Display contestant names with animations"""
    
def render_post_match_splash(winner, screen):
    """Display winner with celebration animations"""
    
def render_champion_screen(winner, screen):
    """Display tournament champion with animations"""
    
def get_current_match(tournament):
    """Return current player matchup"""
```

**Tournament Flow States**
```python
TournamentState = {
    'phase': str,  # 'name_entry', 'bracket', 'pre_match', 'playing', 'post_match', 'champion'
    'rounds': [[matches], ...],
    'current_round': int,
    'current_match': int,
    'winner': str | None,
    'animation_timer': float,
}

Match = {
    'player1': str,
    'player2': str,
    'winner': str | None,
}
```

**Tournament Flow Sequence**

1. **Name Entry Phase** (`phase='name_entry'`)
   - Display input screen for up to 8 unique player names
   - Validate uniqueness and non-empty names
   - Transition to bracket phase when complete

2. **Bracket Phase** (`phase='bracket'`)
   - Display full tournament bracket
   - Highlight next match to be played
   - Wait for presenter input to start match
   - Transition to pre-match phase

3. **Pre-Match Splash** (`phase='pre_match'`)
   - Display both contestant names with animations
   - Show fun visual effects (particle systems, text animations)
   - Auto-transition to playing phase after 3 seconds

4. **Playing Phase** (`phase='playing'`)
   - Run normal game with two players
   - Track which player wins
   - Transition to post-match phase on game over

5. **Post-Match Splash** (`phase='post_match'`)
   - Display winner name with celebration animations
   - Show fun visual effects (confetti, fireworks)
   - Auto-transition to bracket phase after 3 seconds

6. **Repeat Steps 2-5** until all matches complete

7. **Champion Phase** (`phase='champion'`)
   - Display tournament winner with grand animations
   - Show final bracket results
   - Option to restart tournament or exit

## Data Models

### Game State

```python
GameState = {
    'running': bool,
    'game_over': bool,
    'score': int,
    'snake': Snake,
    'food_items': list[Food],  # Multiple food items
    'time': float,  # Elapsed game time
    'frame_count': int,
    
    # Multiplayer
    'player_two': Snake | None,
    'score_two': int,
    
    # Tournament
    'tournament': TournamentState | None,
}
```

### Snake

```python
Snake = {
    'segments': list[tuple[int, int]],  # Grid coordinates
    'direction': tuple[int, int],  # (dx, dy)
    'next_direction': tuple[int, int],
    'speed': float,  # Grid cells per second
    'move_timer': float,  # Countdown to next grid move
    'interpolation': float,  # Visual position between cells
    'distance_moved': float,  # For tongue animation
    'tongue_extended': bool,  # Tongue animation state
}
```

### Food

```python
Food = {
    'position': tuple[int, int],  # Grid coordinates
    'velocity': tuple[float, float],  # For movement (when enabled)
    'wander_timer': float,  # Time until direction change
}
```

### Tournament State

```python
TournamentState = {
    'phase': str,  # Current tournament phase
    'rounds': list[list[Match]],  # Bracket structure
    'current_round': int,
    'current_match': int,
    'winner': str | None,
    'animation_timer': float,
    'player_names': list[str],  # All participant names
}

Match = {
    'player1': str,
    'player2': str,
    'winner': str | None,
}
```

## Error Handling

### Graceful Degradation Strategy

1. **Missing Dependencies**: Display clear error message with installation instructions
2. **Invalid Configuration**: Clamp values to valid ranges with console warnings
3. **Component Failures**: Log error and continue with feature disabled
4. **Window Close**: Clean shutdown without exceptions

### Validation

Configuration validation is handled automatically through property setters in the Config class. Invalid values are automatically adjusted to valid ranges:

- Values too small are clamped to minimum thresholds
- Values too large are clamped to maximum thresholds
- Map dimensions are automatically adjusted to fit within window bounds
- Frame rate is read-only and always returns 60

This ensures the game never enters an invalid state regardless of configuration changes during presentation.

## Testing Strategy

### Manual Testing Approach

Since the game is highly visual and interactive, testing will be primarily manual with the developer providing feedback on observed behavior. To facilitate this:

**Debug Logging System**:
- All animation calculations should log key values to console
- Movement updates should log position, speed, and interpolation values
- Feature toggles should log when features activate/deactivate
- Collision events should log what collided and resulting state changes

**Console Output Format**:
```python
# Example debug output
print(f'[SNAKE] pos={head_pos}, speed={speed:.2f}, interp={interpolation:.2f}')
print(f'[SLITHER] segment={i}, phase={phase:.2f}, offset={offset:.2f}')
print(f'[MOUTH] distance={dist:.1f}, threshold={threshold}, open={is_open}')
print(f'[FOOD] spawned at {pos}, total_count={len(food_items)}')
print(f'[COLLISION] type={collision_type}, game_over={game_over}')
```

**Testing Workflow**:
1. Developer implements feature with debug logging
2. Developer runs game and observes visual behavior
3. Developer provides console output and description of visual results
4. Agent analyzes output and suggests fixes if needed
5. Repeat until feature works correctly

### Core Functionality Tests

1. **Snake Movement**: Verify grid-based movement and interpolation via console logs
2. **Collision Detection**: Test wall, self, and food collisions with logged events
3. **Speed Progression**: Confirm speed increases with food consumption via speed logs
4. **Component Isolation**: Ensure disabled components don't affect gameplay

### Visual Feature Tests

1. **Enhanced Visuals Toggle**: Verify rendering switches correctly (visual observation)
2. **Slithering Animation**: Confirm sine wave frequency scales with speed (console logs + visual)
3. **Interactive Animations**: Test mouth/tongue based on proximity (console logs + visual)

### Integration Tests

1. **Multiplayer Mode**: Test two-player collision and scoring
2. **Tournament Flow**: Verify bracket progression and winner tracking
3. **Configuration Changes**: Test live parameter modifications

### Presentation Tests

1. **Feature Reveal Flow**: Test enabling features in sequence
2. **Performance**: Ensure 60 FPS maintained with all features enabled
3. **Quick Restart**: Verify game resets properly

### Debug Mode Configuration

Add a debug flag to config for verbose logging:

```python
class Config:
    def __init__(self):
        # ... other config ...
        self.debug_mode = True  # Set to False for presentations
```

When `debug_mode = True`, all components should output detailed console logs. When `False`, suppress all debug output for clean presentations.

## Performance Considerations

### Optimization Strategies

1. **Constant Frame Rate**: 60 FPS regardless of visual complexity
2. **Minimal Allocations**: Reuse data structures, avoid creating objects in game loop
3. **Efficient Rendering**: Only redraw changed elements when possible
4. **Grid-Based Logic**: Keep collision detection O(1) using grid coordinates

### Resource Management

- **Sprites**: Load food sprite once at initialization
- **Fonts**: Cache font objects for UI rendering
- **Colors**: Use tuples defined in config (no runtime color calculations)

## Implementation Notes

### Configurable Food Count

Food count can be static or dynamic:

```python
# Static: Always 3 food items
config.food_count = 3

# Dynamic: Doubles with each food eaten (1, 2, 4, 8, 16...)
config.food_count = lambda score: max(1, 2 ** score)

# Dynamic: Linear growth (1, 2, 3, 4, 5...)
config.food_count = lambda score: score + 1
```

When food is eaten, the system checks if additional food should spawn based on the current score.

### Configurable Speed Calculation

Speed progression can be customized:

```python
# Default: Additive increase
config.speed_calculation = lambda speed, score: speed + config.speed_factor

# Multiplicative increase
config.speed_calculation = lambda speed, score: speed * 1.15

# Capped growth
config.speed_calculation = lambda speed, score: min(speed + 2, 50)

# Score-based jumps
config.speed_calculation = lambda speed, score: 10 + (score * 0.5)
```

The function receives current speed and score, returns new speed value.

### Sine Wave Slithering Details

The slithering effect uses a sine wave applied perpendicular to the snake's movement direction:

- **Frequency**: Proportional to snake speed (faster = more waves)
- **Amplitude**: Fixed at 30% of grid cell size
- **Phase**: Each segment offset by 0.5 radians for wave propagation
- **Direction**: Perpendicular to current movement vector

### Progressive Visual Enhancement System

The visual system is designed for incremental feature reveals during presentations:

**Base Enhanced Visuals** (`enable_enhanced_visuals = True`):
- Circle-based rendering with packed segments
- Sine wave slithering animation
- Tapered body from head to tail
- Head shape with eyes

**Additional Toggleable Features**:
- `enable_mouth_animation`: Mouth opens when snake is near food
- `enable_tongue_animation`: Tongue flicks in and out periodically
- `enable_animated_food`: Food rendered as mouse sprite instead of circle
- `enable_food_movement`: Food wanders and flees from snake

**Design Rationale**: This modular approach allows presenters to create multiple "wow moments" by enabling features one at a time. Students can see each enhancement independently and understand how features combine to create the final polished game.

### Tournament Flow Implementation

Tournament mode completely overrides normal game flow:

1. **Name Entry**: Text input screen, validates 2-8 unique names
2. **Bracket Display**: Shows full bracket, highlights next match
3. **Pre-Match Splash**: 3-second animated intro with player names
4. **Match Play**: Standard two-player game
5. **Post-Match Splash**: 3-second animated outro with winner
6. **Repeat**: Continue until champion determined
7. **Champion Screen**: Final celebration with tournament results

Each phase has its own rendering and input handling logic.

### Tournament Bracket Logic

- **8 Players**: 3 rounds (quarterfinals, semifinals, finals)
- **4 Players**: 2 rounds (semifinals, finals)
- **2 Players**: 1 round (finals)
- **Odd Numbers**: Bye rounds for advancement

### Multiplayer Spawn Positions

- **Player 1**: Starts at (MAP_SIZE_WIDTH // 3, MAP_SIZE_HEIGHT // 2)
- **Player 2**: Starts at (2 * MAP_SIZE_WIDTH // 3, MAP_SIZE_HEIGHT // 2)
- **Opposite Directions**: Player 1 faces right, Player 2 faces left

## Future Extensibility

The component-based architecture supports easy addition of:

- Additional visual effects (particle systems, trails)
- New game modes (time attack, survival)
- AI opponents
- Power-ups and special food types
- Sound effects and music
- Replay system
- Leaderboards

Each new feature can be added as an independent component with its own configuration flag.
