# Snake Visual System Debug Requirements

## Problem Statement

The current snake visual system is completely broken:
1. Snake leaves permanent trails of circles everywhere
2. Body length is not fixed - grows infinitely
3. Circles don't follow the head properly
4. No proper slithering animation

## Root Cause Analysis

The fundamental issue is that `update_visual_positions()` is being called EVERY FRAME and creating new positions, but the list keeps growing instead of maintaining a fixed size.

## Core Requirements

### Requirement 1: Fixed Circle Count
**User Story:** As a player, I want the snake to have a consistent visual length that matches its actual segment count.

**Acceptance Criteria:**
1. Total circles = `num_segments × circles_per_segment`
2. For a 4-segment snake with 30px cells = 120 circles total
3. This count only changes when the snake eats food (adds segment)
4. Circle count NEVER exceeds this maximum

### Requirement 2: Follow-the-Leader Movement
**User Story:** As a player, I want each part of the snake body to follow the path of the part ahead of it.

**Acceptance Criteria:**
1. Circle at index 0 = current head position (with interpolation)
2. Circle at index N = position where circle N-1 was in the previous frame
3. This creates a "shift" effect where positions propagate down the body
4. Old positions at the tail end are discarded (not kept)

### Requirement 3: Update Frequency
**User Story:** As a developer, I need to understand when positions should update.

**Acceptance Criteria:**
1. Positions update EVERY frame (not just when moving to new grid cell)
2. Head position uses interpolation for smooth movement
3. Body positions shift on every update
4. No distance threshold - always update

### Requirement 4: Sine Wave Slithering
**User Story:** As a player, I want the snake's head segment to slither naturally.

**Acceptance Criteria:**
1. Sine wave applied ONLY during rendering (not stored in positions)
2. Only affects first segment (circles 0 to circles_per_segment-1)
3. Wavelength = 2 × cell_size
4. Amplitude = cell_size × 0.15
5. Offset multiplier decreases from 1.0 at head to 0.0 at end of first segment

## Test Cases

### Test 1: Initial State
- Create 4-segment snake
- Verify exactly 120 circles exist (30 per segment)
- Verify all circles have valid positions
- Verify no circles are at (0, 0) unless that's the actual position

### Test 2: Straight Movement
- Move snake forward 5 cells in straight line
- Verify circle count remains 120
- Verify head circles move forward
- Verify tail circles follow the path
- Verify no trail is left behind

### Test 3: Turning
- Move snake forward, then turn 90 degrees
- Verify circles smoothly follow the curved path around the corner
- Verify no "jumping" or "teleporting"
- Verify the turn creates a smooth curve, not a sharp angle

### Test 4: Growth
- Snake eats food and grows by 1 segment
- Verify circle count increases to 150 (5 segments × 30)
- Verify new circles are added at the tail
- Verify existing circles continue following properly

### Test 5: Sine Wave
- Observe first segment while moving
- Verify slight side-to-side oscillation
- Verify oscillation completes 2 full cycles per grid cell
- Verify other segments don't oscillate
