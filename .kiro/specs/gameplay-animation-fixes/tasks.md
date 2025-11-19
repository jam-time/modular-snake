# Implementation Plan

- [ ] 1. Implement sine wave animation system for snake slithering




  - [x] 1.1 Add visual_state with wave_phase and wave_speed to Snake model


    - Create SnakeVisualState TypedDict in components/snake.py
    - Initialize visual_state in create_snake() with wave_phase=0.0 and wave_speed=4.0
    - _Requirements: 1.1, 1.6_

  - [x] 1.2 Implement wave phase update function


    - Create update_wave_phase() in components/enhanced_visuals.py
    - Update phase by wave_speed * delta_time each frame
    - Wrap phase to stay within 0 to 2π using modulo
    - _Requirements: 1.6_

  - [x] 1.3 Implement direction vector calculation functions


    - Create calculate_segment_direction_vector() to get direction from segment positions
    - Create calculate_perpendicular_vector() to rotate direction 90 degrees
    - Handle edge cases for head and tail segments
    - _Requirements: 1.7_

  - [x] 1.4 Implement sine wave offset calculation


    - Create calculate_sine_wave_offset() in components/enhanced_visuals.py
    - Head (segment 0): return offset of 0
    - Segment 1: ramp amplitude from 0 to full based on position in segment
    - Segments 2+: apply full amplitude sine wave with phase offset
    - Use base_amplitude of 8 pixels and wave_spacing of π/2 per segment
    - _Requirements: 1.2, 1.3, 1.4, 1.5_

  - [x] 1.5 Update render_snake() to apply sine wave pattern


    - For each segment, calculate base pixel position from grid position
    - Calculate direction and perpendicular vectors
    - Calculate sine wave offset for the segment
    - Apply offset perpendicular to direction: position + perpendicular * offset
    - Render circles at calculated positions with appropriate radius and color
    - _Requirements: 1.1, 1.2, 1.7_

  - [x] 1.6 Call update_wave_phase() in main game loop


    - Add call in main.py update section before rendering
    - Pass delta_time from game clock
    - _Requirements: 1.6_
- [ ] 2. Enhance debug output for snake visual components







- [ ] 2. Enhance debug output for snake visual components

  - [x] 2.1 Implement debug logging for wave state


    - Add debug_log_visual_state() function in components/enhanced_visuals.py
    - Log frame number, timestamp, grid segments
    - Log wave_phase and wave_speed
    - Log sample of visual circles with positions, radii, and offsets
    - Format output to be concise and readable
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8_

  - [x] 2.2 Integrate debug logging into render loop


    - Call debug_log_visual_state() when config.debug_mode is True
    - Call once per frame before rendering
    - _Requirements: 2.7_

- [x] 3. Fix food movement speed and timing





  - [x] 3.1 Update food movement to use snake speed instead of length


    - Modify update_movement() in components/food.py
    - Calculate max_flee_speed as snake_speed * 0.75
    - Calculate wander_speed as snake_speed * 0.2
    - Remove any references to snake_length in speed calculations
    - _Requirements: 3.1, 3.2, 3.5_


  - [x] 3.2 Implement proper delta time integration for food movement

    - Update position calculation to use velocity * delta_time
    - Ensure velocity is in cells per second (not cells per frame)
    - Clamp velocity magnitude to max_flee_speed or wander_speed
    - _Requirements: 3.3, 3.6_

  - [x] 3.3 Add dynamic speed updates when snake speeds up


    - Recalculate max food speeds based on current snake speed each frame
    - Ensure food never exceeds 90% of snake speed (using 75% for flee, 20% for wander)
    - _Requirements: 3.4, 3.5_

- [x] 4. Implement food stacking prevention




  - [x] 4.1 Create collision detection for food items


    - Implement detect_food_collisions() in components/food.py
    - Return dictionary mapping positions to list of food indices
    - _Requirements: 4.1_

  - [x] 4.2 Implement food repositioning logic


    - Create find_adjacent_empty_cell() to find empty cells near a position
    - Prefer cells away from snake when possible
    - Use expanding radius search up to max_radius of 3
    - _Requirements: 4.2_

  - [x] 4.3 Implement resolve_food_stacking() function


    - For each collision, keep first food at position
    - Reposition other food items to adjacent empty cells
    - Call after food movement and during spawning
    - _Requirements: 4.2, 4.3_

  - [x] 4.4 Integrate stacking prevention into food update


    - Call detect_food_collisions() after update_movement()
    - Call resolve_food_stacking() if collisions detected
    - Also check during spawn_food_items()
    - _Requirements: 4.4_

- [x] 5. Add spawn deadlock prevention




  - [x] 5.1 Implement pre-spawn validation


    - Calculate total cells, occupied cells, and available cells
    - Return early if available_cells <= 0
    - Log warning when no space available
    - _Requirements: 5.1, 5.2_

  - [x] 5.2 Add iteration limit to spawn attempts

    - Set max_attempts to 100 in spawn_food_items()
    - Track attempts in spawn loop
    - Break and log warning if limit reached
    - _Requirements: 5.3, 5.4_

-

- [x] 6. Enhance tongue animation



  - [x] 6.1 Create TongueState data structure


    - Add TongueState TypedDict to components/enhanced_visuals.py
    - Include fields: extended, extension_progress, timer, cooldown_timer
    - Initialize in create_tongue_state() function
    - _Requirements: 6.2, 6.3_


  - [x] 6.2 Implement tongue animation state machine

    - Create update_tongue_animation() with three phases: extension, hold, retraction
    - Extension duration: 0.4s, hold duration: 0.8s, retraction duration: 0.4s
    - Cooldown duration: 3.0s between flicks
    - Pause tongue during bite animation
    - _Requirements: 6.2, 6.3_

  - [x] 6.3 Implement forked tongue rendering


    - Create render_forked_tongue() in components/enhanced_visuals.py
    - Draw main tongue line extending 3/4 of total length
    - Draw two prongs at 20-degree angles for remaining 1/4 length
    - Use extension_progress to animate smoothly
    - _Requirements: 6.1, 6.4, 6.5_

  - [x] 6.4 Integrate tongue animation into game loop


    - Call update_tongue_animation() in main update loop
    - Call render_forked_tongue() during snake rendering
    - Pass delta_time for smooth animation
    - _Requirements: 6.5_

- [x] 7. Implement dramatic bite animation




  - [x] 7.1 Create BiteState data structure


    - Add BiteState TypedDict to components/enhanced_visuals.py
    - Include fields: active, progress, bite_position, wave_count, duration
    - _Requirements: 7.1_

  - [x] 7.2 Implement bite animation trigger


    - Create trigger_bite_animation() function
    - Initialize bite state when food is eaten
    - Store bite position for wave rendering
    - _Requirements: 7.1_

  - [x] 7.3 Implement bite animation update


    - Create update_bite_animation() to advance progress
    - Increment progress by delta_time / duration
    - Deactivate when progress >= 1.0
    - _Requirements: 7.5_

  - [x] 7.4 Implement bite rendering with enlarged head and C-shaped mouth


    - Scale head by 1.5x during bite (visual only, not collision)
    - Draw C-shaped mouth arc opening 108 degrees
    - Use progress to animate mouth opening
    - _Requirements: 7.2_

  - [x] 7.5 Implement squiggly line effects around mouth


    - Draw 5 squiggly lines radiating from mouth
    - Each line is 20 pixels with 4 sine waves (5 pixels per wave)
    - Lines shoot out simultaneously and fade based on progress
    - Use 20 segments per line for smooth curves
    - _Requirements: 7.3, 7.4_

  - [x] 7.6 Integrate bite animation with collision system


    - Call trigger_bite_animation() in components/collision.py when food eaten
    - Calculate pixel position of food for bite location
    - Pause normal mouth animation during bite
    - _Requirements: 7.1, 7.6_

- [ ] 8. Implement improved turn timing based on head position
  - [ ] 8.1 Modify set_direction() to apply turns immediately when enhanced visuals enabled
    - Check config.enable_enhanced_visuals flag in set_direction()
    - If True, apply direction change immediately (while entering next cell) and start turn animation
    - If False, use original behavior (queue next_direction for cell boundary)
    - Store old_direction before changing direction
    - Initialize turn_progress to 0.0 when turn starts
    - Add debug logging showing interpolation value when turn happens
    - _Requirements: 8.1, 8.2, 8.3_

  - [ ] 8.2 Update update_movement() to respect enhanced visuals mode
    - Keep original turn timing when config.enable_enhanced_visuals is False
    - When enhanced visuals enabled, direction is already applied in set_direction()
    - Ensure grid cell advancement still happens at move_timer >= time_per_cell
    - Add debug logging for turn timing differences
    - _Requirements: 8.3, 8.4, 8.5_

- [ ] 9. Implement smooth turn animation
  - [ ] 9.1 Add turn animation state to Snake model
    - Add turn_progress field (0.0 to 1.0) to Snake TypedDict
    - Add old_direction field to track direction before turn
    - Initialize turn_progress to 1.0 in create_snake()
    - _Requirements: 9.1, 9.2_

  - [ ] 9.2 Implement turn animation progress tracking
    - Start turn animation when direction changes (set turn_progress to 0.0)
    - Store old_direction before applying new direction
    - Update turn_progress based on remaining time in current cell
    - Reset turn_progress to 1.0 when moving to next grid cell
    - _Requirements: 9.1, 9.3, 9.5_

  - [ ] 9.3 Implement smooth head position calculation during turns
    - Create get_interpolated_head_position() function
    - Check if config.enhanced_animations is enabled
    - If enabled and turn_progress < 1.0, blend between old_direction and direction
    - Calculate intermediate direction vector for smooth arc
    - Use blended direction for head pixel position
    - Fall back to normal interpolation when turn_progress >= 1.0 or enhanced animations disabled
    - _Requirements: 9.2, 9.3, 9.4, 9.6_

  - [ ] 9.4 Integrate smooth turn rendering
    - Update render_snake() to use get_interpolated_head_position() when enhanced animations enabled
    - Ensure turn animation works with sine wave slithering
    - Use original interpolation when enhanced animations disabled
    - Test visual appearance of turns at different speeds
    - _Requirements: 9.4, 9.5, 9.6_
