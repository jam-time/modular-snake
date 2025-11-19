# Requirements Document

## Introduction

This document specifies the requirements for an interactive Snake game demo designed for middle school career day presentations. The game will be built in Python with a focus on modularity, easy configuration, and the ability to demonstrate features incrementally through configuration flags. The primary goal is to engage students by allowing them to suggest changes to game parameters and see immediate results.

## Glossary

- **Snake Game**: A classic arcade game where the player controls a snake that grows longer when eating food
- **Game Window**: The visual display area where the game is rendered
- **Snake**: The player-controlled entity that moves continuously and grows when eating food
- **Food**: A collectible item that appears randomly on the game grid
- **Grid System**: The coordinate system that divides the game window into discrete cells
- **Configuration Section**: A clearly marked code block containing adjustable parameters
- **Feature Module**: A self-contained, independently importable code component that implements a specific game feature
- **Component**: A modular Python module that encapsulates a single game feature and can be imported and called independently
- **Game Loop**: The continuous cycle that updates game state and renders graphics
- **Collision Detection**: The system that determines when the snake hits walls, itself, or food
- **Tournament Mode**: A competitive mode that manages bracket-style matches between up to 8 players
- **Tournament Bracket**: A visual display showing player matchups and progression through tournament rounds
- **Presentation Guide**: A reference document listing code sections and line numbers for activating features during the demo
- **Map Size**: The dimensions of the playable grid area measured in grid cells
- **Speed Factor**: A multiplier that controls how rapidly the snake's movement speed increases as it grows


## Requirements

### Requirement 1

**User Story:** As a presenter, I want a centralized configuration section at the top of the code, so that students can easily see and modify game parameters during the demo.

#### Acceptance Criteria

1. THE Snake Game SHALL contain a configuration section with all adjustable parameters grouped at the top of the main file
2. THE Configuration Section SHALL include parameters for window width, window height, fullscreen mode, grid cell size, frame rate, map size, speed factor, and all color values
3. THE Configuration Section SHALL use clear, self-documenting variable names that indicate each parameter's purpose
4. WHEN a student suggests a parameter change, THE Snake Game SHALL allow the presenter to modify only the configuration section to implement the change
5. THE Configuration Section SHALL use Python constants (UPPER_CASE naming) to indicate these are configuration values

### Requirement 2

**User Story:** As a presenter, I want the game to have a modular architecture with separate component files, so that each feature is independently maintainable and can be enabled or disabled through configuration.

#### Acceptance Criteria

1. THE Snake Game SHALL organize each feature as a separate Component in a components directory
2. THE Snake Game SHALL import all Components at the top of the main file
3. THE Game Loop SHALL call each Component function based on configuration flags
4. EACH Component SHALL function independently without dependencies on other Components
5. THE Configuration Section SHALL include boolean flags for enabling or disabling each Component
6. WHEN a Component is disabled via configuration, THE Snake Game SHALL continue to run without errors

### Requirement 3

**User Story:** As a presenter, I want the game to have clear visual feedback, so that students can immediately see the results of their suggested changes.

#### Acceptance Criteria

1. THE Snake SHALL be rendered with a distinct color that contrasts with the background
2. THE Food SHALL be rendered with a distinct color different from the snake and background
3. THE Game Window SHALL display the current score in a readable font size
4. WHEN the snake eats food, THE Game Window SHALL provide immediate visual feedback by growing the snake
5. THE Game Window SHALL use a grid-based rendering system where each cell is clearly defined

### Requirement 4

**User Story:** As a presenter, I want the game to have simple, intuitive controls, so that students can quickly understand and potentially test the game.

#### Acceptance Criteria

1. THE Snake Game SHALL accept arrow key inputs for directional control (up, down, left, right)
2. THE Snake Game SHALL accept WASD key inputs as alternative directional controls
3. THE Snake Game SHALL prevent the snake from reversing direction into itself
4. THE Snake Game SHALL accept ESC key input to exit the game
5. WHEN no valid input is received, THE Snake SHALL continue moving in its current direction

### Requirement 5

**User Story:** As a presenter, I want the game to handle edge cases gracefully, so that the demo doesn't crash during the presentation.

#### Acceptance Criteria

1. WHEN the snake collides with a wall, THE Snake Game SHALL end the game and display a game over message
2. WHEN the snake collides with itself, THE Snake Game SHALL end the game and display a game over message
3. WHEN the game ends, THE Snake Game SHALL display the final score
4. WHEN the game ends, THE Snake Game SHALL provide an option to restart by pressing SPACE or exit by pressing ESC
5. THE Snake Game SHALL handle window close events gracefully without throwing errors

### Requirement 6

**User Story:** As a presenter, I want the code to be well-organized and clean, so that I can reference it during the presentation without confusion.

#### Acceptance Criteria

1. THE Snake Game SHALL use clear function names that describe their purpose
2. THE Snake Game SHALL organize code into logical sections: configuration, initialization, game logic, rendering, and main loop
3. THE Snake Game SHALL use consistent indentation and spacing following Python conventions
4. THE Snake Game SHALL limit each function to a single, well-defined responsibility
5. THE Snake Game SHALL NOT include code comments as per Python best practices for clean, self-documenting code

### Requirement 7

**User Story:** As a presenter, I want the game to support multiplayer mode that can be hidden and revealed, so that I can surprise students with a tournament at the end of the session.

#### Acceptance Criteria

1. THE Snake Game SHALL support up to 2 players simultaneously on the same keyboard
2. THE Feature Module for multiplayer mode SHALL be independently toggleable via configuration
3. WHEN multiplayer mode is enabled, THE Game Window SHALL render a second snake with a distinct color
4. THE Snake Game SHALL assign Player 1 controls to arrow keys and Player 2 controls to WASD keys
5. WHEN multiplayer mode is enabled, THE Snake Game SHALL track and display separate scores for each player
6. WHEN one snake collides in multiplayer mode, THE Snake Game SHALL end the game for both players and display both final scores
7. THE Snake Game SHALL spawn food that either player can collect

### Requirement 8

**User Story:** As a presenter, I want the game to start quickly and reliably, so that I don't waste presentation time troubleshooting.

#### Acceptance Criteria

1. THE Snake Game SHALL use only standard Python libraries or widely-available packages (pygame)
2. THE Snake Game SHALL initialize within 2 seconds of execution
3. THE Snake Game SHALL display clear error messages if required dependencies are missing
4. THE Snake Game SHALL include a requirements.txt file listing all dependencies
5. WHEN executed, THE Snake Game SHALL start immediately in the game state without requiring menu navigation

### Requirement 9

**User Story:** As a presenter, I want a tournament mode that manages bracket-style competition between students, so that I can end the presentation with an exciting surprise tournament.

#### Acceptance Criteria

1. THE Feature Module for tournament mode SHALL be independently toggleable via configuration
2. WHEN tournament mode is enabled, THE Snake Game SHALL accept up to 8 student names as input
3. THE Snake Game SHALL generate a Tournament Bracket displaying all matchups for the tournament
4. THE Game Window SHALL display the Tournament Bracket showing current match and remaining matches
5. WHEN a match ends, THE Snake Game SHALL record the winner and advance them in the Tournament Bracket
6. THE Snake Game SHALL automatically proceed to the next match when the presenter presses a designated key
7. WHEN the tournament completes, THE Snake Game SHALL display the tournament winner and final bracket results

### Requirement 10

**User Story:** As a presenter, I want the snake to move smoothly through the grid with configurable speed progression, so that students can see how game mechanics affect difficulty and challenge.

#### Acceptance Criteria

1. THE Snake Game SHALL run at 60 frames per second regardless of visual enhancement settings
2. THE Snake Game SHALL initialize each snake with 4 segments at game start
3. THE Snake SHALL move continuously in its current direction at a rate determined by the current speed setting
4. THE Snake Game SHALL update the snake's grid position at regular intervals based on the current movement speed
5. WHEN the snake eats food, THE Snake Game SHALL increase the snake's movement speed by an amount determined by the speed factor configuration
6. THE Snake Game SHALL maintain smooth visual movement between grid cells by interpolating the snake's position across frames
7. THE Snake Game SHALL ensure the snake's head reaches the next grid cell before processing the next movement input
8. THE Snake Game SHALL add a new segment to the snake's tail when food is consumed

### Requirement 11

**User Story:** As a presenter, I want enhanced snake visuals with smooth slithering animation, so that students can see a dramatic visual upgrade when the feature is enabled.

#### Acceptance Criteria

1. THE Configuration Section SHALL include color parameters for background, food, snake body, snake head, text, and UI elements
2. THE Feature Module for enhanced snake visuals SHALL be independently toggleable via configuration
3. WHEN enhanced snake visuals are disabled, THE Snake Game SHALL render the snake using the standard grid-based rectangular segments with basic frame-by-frame updates
4. WHEN enhanced snake visuals are enabled, THE Snake Game SHALL render the snake using a series of circles packed closely together to create a smooth, organic appearance
5. WHEN enhanced snake visuals are enabled, THE Snake Game SHALL apply a sine wave pattern to the snake's body segments that creates a slithering animation
6. WHEN enhanced snake visuals are enabled, THE Snake Game SHALL set the sine wave frequency proportional to the snake's current speed to create natural-looking slithering motion
7. WHEN enhanced snake visuals are enabled, THE Snake Game SHALL utilize all available frames to exhibit smooth animation
8. WHEN enhanced snake visuals are enabled, THE Snake Game SHALL render the snake with a tapered appearance from head to tail, distinct head shape, eyes, and tongue

### Requirement 12

**User Story:** As a presenter, I want interactive visual animations for the snake and food, so that students can see advanced game features that respond to gameplay.

#### Acceptance Criteria

1. THE Feature Module for mouth animation SHALL be independently toggleable via configuration
2. WHEN mouth animation is enabled, THE Snake Game SHALL display the snake's mouth opening when within a configurable distance from food
3. THE Feature Module for tongue animation SHALL be independently toggleable via configuration
4. WHEN tongue animation is enabled, THE Snake Game SHALL flick the tongue in and out periodically every few grid cells of movement rather than keeping it extended continuously
5. THE Feature Module for animated food SHALL be independently toggleable via configuration
6. WHEN animated food is enabled, THE Snake Game SHALL render the food as a mouse sprite
7. THE Feature Module for food movement SHALL be independently toggleable via configuration
8. WHEN food movement is enabled, THE Snake Game SHALL make the food wander at half the snake's speed until the snake is within a configurable distance
9. WHEN food movement is enabled and the snake is within the configured distance, THE Snake Game SHALL make the food flee at a speed proportional to the snake's length but never exceeding the snake's speed

### Requirement 13

**User Story:** As a presenter, I want a concise presentation guide document, so that I can quickly reference what to change during the live demo.

#### Acceptance Criteria

1. THE Snake Game SHALL include a Presentation Guide document named PRESENTATION_GUIDE.md in the root directory
2. THE Presentation Guide SHALL list each feature with the corresponding configuration flag to modify
3. THE Presentation Guide SHALL include a suggested presentation flow showing the order to reveal features
4. THE Presentation Guide SHALL include example parameter values for common student suggestions
5. THE Presentation Guide SHALL include troubleshooting tips for common issues during live demos

### Requirement 14

**User Story:** As a presenter, I want configurable gameplay parameters that affect difficulty, so that students can experiment with different challenge levels.

#### Acceptance Criteria

1. THE Configuration Section SHALL include a map size parameter that controls the playable grid dimensions
2. THE Configuration Section SHALL include a speed factor parameter that controls how quickly the snake accelerates
3. WHEN the speed factor is increased, THE Snake Game SHALL increase the snake's movement speed more rapidly as it grows
4. WHEN the map size is changed, THE Snake Game SHALL adjust the playable area dimensions accordingly
5. THE Snake Game SHALL validate that map size and speed factor values are within reasonable ranges


