# Snake Visual System Debug Tasks

## Phase 1: Diagnostic and Understanding

- [x] 1. Add comprehensive debug logging


  - Log circle count on every frame
  - Log first 3 and last 3 circle positions
  - Log when circles are added/removed
  - Log head position and interpolation value

- [ ] 2. Verify initialization
  - Check that create_visual_state creates exactly the right number of circles
  - Verify initial positions form a continuous line
  - Print out all initial positions to verify correctness

- [ ] 3. Trace update_visual_positions execution
  - Add print statement at start of function
  - Log old circle count vs new circle count
  - Verify the shift operation is working correctly

## Phase 2: Fix Core Issues

- [ ] 4. Fix circle count management
  - Ensure list size never exceeds num_segments × circles_per_segment
  - Remove any code that appends without removing
  - Verify list is replaced, not extended

- [ ] 5. Fix follow-the-leader logic
  - Verify we're using old_positions[i-1] for new_positions[i]
  - Ensure we're not accidentally duplicating positions
  - Test that tail positions are properly discarded

- [ ] 6. Fix update frequency
  - Verify update_visual_positions is called every frame
  - Remove any distance thresholds or conditional updates
  - Ensure smooth continuous updates

## Phase 3: Rendering

- [ ] 7. Simplify rendering first
  - Temporarily remove sine wave
  - Just render circles at their stored positions
  - Verify basic follow-the-leader works

- [ ] 8. Add sine wave back
  - Apply sine wave offset during rendering only
  - Only to first segment
  - Verify wavelength and amplitude are correct

- [ ] 9. Add radius tapering
  - Neck effect at segment 1
  - Tail taper at last segment
  - Verify smooth transitions

## Phase 4: Validation

- [ ] 10. Run all test cases
  - Initial state test
  - Straight movement test
  - Turning test
  - Growth test
  - Sine wave test

- [ ] 11. Performance check
  - Verify no memory leaks
  - Check frame rate is stable
  - Ensure no lag when snake is long

- [ ] 12. Visual polish
  - Adjust sine wave parameters if needed
  - Fine-tune radius tapering
  - Verify colors are correct
