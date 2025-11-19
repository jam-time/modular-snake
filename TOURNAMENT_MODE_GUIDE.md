# Tournament Mode Guide (secret_mode_omega)

## Overview

Tournament mode is a hidden feature that transforms the Snake Game into a bracket-style competition system supporting 2-8 players. It includes name entry, bracket visualization, animated splash screens, and a grand champion celebration.

## Activation

Enable tournament mode in `config.py`:

```python
config.secret_mode_omega = True
```

## Tournament Flow

### 1. Name Entry Phase
- Enter player names one at a time
- Press ENTER to add each player
- Minimum 2 players, maximum 8 players
- Names must be unique and non-empty
- Press SPACE when ready to start (requires at least 2 players)

### 2. Bracket Phase
- Displays full tournament bracket with all matchups
- Current match is highlighted in green
- Shows player names and match progression
- Press ENTER to start the highlighted match

### 3. Pre-Match Splash (3 seconds)
- Animated "VS" screen with player names
- Pulsing text effects
- Particle animations
- Countdown timer
- Auto-transitions to match

### 4. Playing Phase
- Standard two-player Snake game
- Player 1: Arrow keys
- Player 2: WASD keys
- Both players compete for highest score
- Match ends when either player collides

### 5. Post-Match Splash (3 seconds)
- Winner announcement with celebration
- Confetti falling animation
- Firework explosions
- Star particle effects
- Auto-transitions back to bracket

### 6. Champion Phase
- Grand celebration for tournament winner
- Animated trophy
- Pulsing champion name
- Rainbow fireworks
- Complete bracket results displayed
- Press SPACE to restart or ESC to exit

## Bracket Generation

The system automatically generates appropriate brackets based on player count:

- **2 players**: 1 round (finals)
- **3 players**: 2 rounds with 1 bye
- **4 players**: 2 rounds (semifinals + finals)
- **5 players**: 3 rounds with byes
- **6 players**: 3 rounds with byes
- **7 players**: 3 rounds with 1 bye
- **8 players**: 3 rounds (quarterfinals + semifinals + finals)

Players are randomly shuffled at bracket creation for fairness.

## Visual Effects

### Pre-Match Splash
- Pulsing "VS" text (scales 1.0-1.2x)
- Random particle system (20 particles)
- Countdown display
- Player names in large font

### Post-Match Splash
- Falling confetti (30 pieces, 5 colors)
- Pulsing winner name (scales 1.0-1.15x)
- Animated star particles (10 stars)

### Champion Screen
- Animated trophy emoji (scales 1.0-1.3x)
- Pulsing champion name (scales 1.0-1.2x)
- Firework explosions (50 particles, 7 colors)
- Expanding particle effects
- Complete bracket history

## Debug Output

When `config.debug_mode = True`, tournament mode logs:

```
[TOURNAMENT] Created bracket for X players
[TOURNAMENT] X rounds, first round has X matches
[TOURNAMENT] Added player: PlayerName
[TOURNAMENT] Starting tournament with X players
[TOURNAMENT] Starting match: Player1 vs Player2
[TOURNAMENT] Match ended: Winner wins (score1 vs score2)
[TOURNAMENT] Winner recorded: Winner
[TOURNAMENT] Advancing to round X
[TOURNAMENT] Tournament complete! Champion: Winner
[TOURNAMENT] PlayerName advances via BYE
[TOURNAMENT] Returning to bracket view
```

## Integration with Main Game

Tournament mode completely overrides normal game flow when enabled:

1. **Game State**: Adds `tournament` dictionary to state
2. **Input Handling**: Routes input based on tournament phase
3. **Update Logic**: Manages phase transitions and timers
4. **Rendering**: Displays appropriate screen for each phase

Tournament mode is mutually exclusive with `secret_mode_alpha` (multiplayer). If both are enabled, tournament mode takes precedence.

## Testing

Run the visual test:

```bash
python test_tournament_visual.py
```

Or run unit tests:

```bash
python test_tournament.py
```

## Presentation Tips

1. Keep tournament mode hidden until the end of the demo
2. Have student names ready to enter quickly
3. Let students play their own matches
4. The celebration screens create great photo opportunities
5. Tournament typically takes 5-10 minutes for 4-8 players

## Technical Details

### Data Structures

```python
TournamentState = {
    'phase': str,  # 'name_entry', 'bracket', 'pre_match', 'playing', 'post_match', 'champion'
    'rounds': list[list[Match]],  # Bracket structure
    'current_round': int,
    'current_match': int,
    'winner': str | None,
    'animation_timer': float,
    'player_names': list[str],
    'current_input': str,  # For name entry
    'match_winner': str  # Temporary storage during post-match
}

Match = {
    'player1': str,
    'player2': str,
    'winner': str | None
}
```

### Key Functions

- `create_tournament(player_names)`: Generate bracket structure
- `get_current_match(tournament)`: Retrieve active matchup
- `advance_winner(tournament, winner)`: Progress bracket
- `record_match_winner(state)`: Capture match result
- `update_tournament_timers(state, delta_time)`: Handle phase transitions
- `render_*()`: Phase-specific rendering functions

## Requirements Satisfied

This implementation satisfies all requirements from Requirement 9:

- ✅ 9.1: Tournament mode toggleable via configuration
- ✅ 9.2: Accepts up to 8 student names with validation
- ✅ 9.3: Generates tournament bracket with proper structure
- ✅ 9.4: Displays bracket showing current and remaining matches
- ✅ 9.5: Records winners and advances them in bracket
- ✅ 9.6: Presenter key to proceed, splash screens with animations
- ✅ 9.7: Displays tournament winner and final bracket results
