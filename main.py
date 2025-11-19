"""Snake Game Demo - Interactive presentation game for career day."""

from typing import Any
import pygame
from config import config
from components import snake, food, collision, rendering, enhanced_visuals, secrets


def initialize_pygame() -> pygame.Surface:
    """Initialize pygame and create display window.

    Returns:
        Pygame display surface for rendering.
    """
    pygame.init()

    width = config.window_width
    height = config.window_height

    if width == 0 or height == 0:
        info = pygame.display.Info()
        if width == 0:
            width = info.current_w
            config.window_width = width
        if height == 0:
            height = info.current_h
            config.window_height = height

        if config.debug_mode:
            print(f'[MAIN] Auto-detected screen size: {width}x{height}')

    if config.fullscreen_mode:
        screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((width, height))

    pygame.display.set_caption('Snake Game Demo')

    if config.debug_mode:
        print('[MAIN] Pygame initialized')
        print(f'[MAIN] Window: {width}x{height}')
        print(f'[MAIN] Fullscreen: {config.fullscreen_mode}')

    return screen


def create_game_state() -> dict[str, Any]:
    """Create initial game state with all required fields.

    Returns:
        Game state dictionary with snake, food, scores, and flags.
    """
    start_x = config.map_size_width // 2
    start_y = config.map_size_height // 2
    initial_direction = (1, 0)

    state: dict[str, Any] = {
        "running": True,
        "game_over": False,
        "score": 0,
        "snake": snake.create_snake((start_x, start_y), initial_direction),
        "food_items": [],
        "time": 0.0,
        "frame_count": 0,
        "player_two": None,
        "score_two": 0,
        "tournament": None,
    }

    if config.secret_mode_omega:
        state["tournament"] = {
            "phase": "name_entry",
            "player_names": [],
            "current_input": "",
            "rounds": [],
            "current_round": 0,
            "current_match": 0,
            "winner": None,
            "animation_timer": 0.0,
        }
        if config.debug_mode:
            print("[MAIN] Tournament mode initialized")
    elif config.secret_mode_alpha:
        secrets.create_player_two(state)

    required_food = food.get_required_food_count(0)
    for _ in range(required_food):
        food.spawn_food_items(state)

    if config.debug_mode:
        print("[MAIN] Game state created")
        print(f"[MAIN] Map: {config.map_size_width}x{config.map_size_height} cells")
        print(f"[MAIN] Grid cell size: {config.grid_cell_size}px")
        print(f"[MAIN] Initial speed: {config.initial_speed} cells/sec")
        print(f"[MAIN] Speed factor: {config.speed_factor}")
        print(f"[MAIN] Frame rate: {config.frame_rate} FPS")
        print(f"[MAIN] Food items: {len(state['food_items'])}")
        print(f"[MAIN] Enhanced visuals: {config.enable_enhanced_visuals}")
        print(f"[MAIN] Multiplayer mode: {config.secret_mode_alpha}")
        print(f"[MAIN] Tournament mode: {config.secret_mode_omega}")

    return state


def handle_input(state: dict[str, Any]) -> None:
    """Process keyboard input for game control.

    Args:
        state: Game state to update based on input.
    """
    tournament = state.get("tournament")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state["running"] = False
            if config.debug_mode:
                print("[INPUT] Window close requested")

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                state["running"] = False
                if config.debug_mode:
                    print("[INPUT] ESC pressed, exiting")

            if config.secret_mode_omega and tournament:
                if tournament["phase"] == "name_entry":
                    secrets.handle_name_entry_input(state, event)
                    continue
                elif tournament["phase"] == "bracket":
                    # Block all key input during bracket display except RETURN (handled separately)
                    continue
                elif tournament["phase"] == "pre_match":
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        secrets.start_tournament_match(state)
                        if config.debug_mode:
                            print("[INPUT] Starting match from pre-match splash")
                    continue
                elif tournament["phase"] == "post_match":
                    # Block all key input during post-match winner splash
                    continue
                elif tournament["phase"] == "champion":
                    if event.key == pygame.K_SPACE:
                        if config.debug_mode:
                            print("[INPUT] SPACE pressed, restarting tournament")
                        new_state = create_game_state()
                        state.update(new_state)
                    continue

            if event.key == pygame.K_SPACE and state.get("game_over", False):
                if config.debug_mode:
                    print("[INPUT] SPACE pressed, restarting game")
                new_state = create_game_state()
                state.update(new_state)

    if config.secret_mode_omega and tournament:
        if tournament["phase"] == "bracket":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]:
                secrets.handle_bracket_input(state, keys)
            return
        elif tournament["phase"] in [
            "name_entry",
            "pre_match",
            "countdown",
            "post_match",
            "champion",
        ]:
            return

    if state.get("game_over", False):
        return

    keys = pygame.key.get_pressed()

    player_snake = state.get("snake")
    if player_snake:
        if config.secret_mode_alpha or (
            tournament and tournament["phase"] == "playing"
        ):
            if keys[pygame.K_w]:
                snake.set_direction(player_snake, (0, -1))
            elif keys[pygame.K_s]:
                snake.set_direction(player_snake, (0, 1))
            elif keys[pygame.K_a]:
                snake.set_direction(player_snake, (-1, 0))
            elif keys[pygame.K_d]:
                snake.set_direction(player_snake, (1, 0))
        else:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                snake.set_direction(player_snake, (0, -1))
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                snake.set_direction(player_snake, (0, 1))
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                snake.set_direction(player_snake, (-1, 0))
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                snake.set_direction(player_snake, (1, 0))

    if config.secret_mode_alpha or (tournament and tournament["phase"] == "playing"):
        secrets.handle_player_two_input(state, keys)


def update_game_state(state: dict[str, Any], delta_time: float) -> None:
    """Update game state for current frame.

    Args:
        state: Game state to update.
        delta_time: Time elapsed since last frame in seconds.
    """
    tournament = state.get("tournament")

    if config.secret_mode_omega and tournament:
        secrets.update_tournament_timers(state, delta_time)

        if tournament["phase"] != "playing":
            state["time"] += delta_time
            state["frame_count"] += 1
            return

        if state.get("game_over", False):
            secrets.record_match_winner(state)
            return

    if state.get("game_over", False):
        return

    player_snake = state.get("snake")
    if player_snake:
        snake.update_movement(player_snake, delta_time)

        if config.enable_enhanced_visuals:
            visual_state = player_snake.get("visual_state")
            if visual_state:
                enhanced_visuals.update_wave_phase(visual_state, delta_time)

        if config.enable_tongue_animation:
            enhanced_visuals.update_tongue_animation(player_snake, delta_time, state)

        enhanced_visuals.update_bite_animation(player_snake, delta_time, state)
        enhanced_visuals.update_blink_animation(player_snake, delta_time)

    if config.enable_food_movement:
        food.update_movement(state, delta_time)

    if config.secret_mode_alpha or (tournament and tournament["phase"] == "playing"):
        secrets.update_player_two(state, delta_time)

        player_two = state.get("player_two")
        if player_two:
            if config.enable_enhanced_visuals:
                visual_state_two = player_two.get("visual_state")
                if visual_state_two:
                    enhanced_visuals.update_wave_phase(visual_state_two, delta_time)

            enhanced_visuals.update_bite_animation(player_two, delta_time, state)
            enhanced_visuals.update_blink_animation(player_two, delta_time)

    collision.check_collisions(state)

    state["time"] += delta_time
    state["frame_count"] += 1


def render_frame(state: dict[str, Any], screen: pygame.Surface) -> None:
    """Render current game frame.

    Args:
        state: Game state to render.
        screen: Pygame surface to render on.
    """
    tournament = state.get("tournament")

    if config.secret_mode_omega and tournament:
        phase = tournament.get("phase")

        if phase == "name_entry":
            secrets.render_name_entry(state, screen)
            pygame.display.flip()
            return
        elif phase == "bracket":
            secrets.render_bracket(tournament, screen)
            pygame.display.flip()
            return
        elif phase == "pre_match":
            secrets.render_pre_match_splash(tournament, screen)
            pygame.display.flip()
            return
        elif phase == "countdown":
            secrets.render_countdown(tournament, screen)
            pygame.display.flip()
            return
        elif phase == "post_match":
            winner = tournament.get("match_winner", "Unknown")
            secrets.render_post_match_splash(tournament, screen, winner)
            pygame.display.flip()
            return
        elif phase == "champion":
            secrets.render_champion_screen(tournament, screen)
            pygame.display.flip()
            return

    screen.fill(config.color_background)
    rendering.render_checkered_background(screen)

    if config.enable_enhanced_visuals:
        if config.enable_tongue_animation:
            enhanced_visuals.render_tongue_before_head(state, screen)
        right_eye_data = enhanced_visuals.get_right_eye_data(state)
        if right_eye_data:
            eye_pos, eye_radius, backing_pos, backing_radius, eye_closed = right_eye_data
            enhanced_visuals._render_single_eye(screen, eye_pos, eye_radius, backing_pos, backing_radius, eye_closed, config.color_snake_head)
        enhanced_visuals.render_snake(state, screen)
        enhanced_visuals.render_head_details(state, screen)
        if config.secret_mode_alpha or (
            tournament and tournament["phase"] == "playing"
        ):
            secrets.render_player_two_enhanced(state, screen)
    else:
        rendering.render_snake_basic(state, screen)
        if config.secret_mode_alpha or (
            tournament and tournament["phase"] == "playing"
        ):
            secrets.render_player_two_basic(state, screen)

    if config.enable_animated_food:
        enhanced_visuals.render_food_sprite(state, screen)
    else:
        rendering.render_food_basic(state, screen)

    if config.secret_mode_alpha or (tournament and tournament["phase"] == "playing"):
        secrets.render_scores(state, screen)
    else:
        rendering.render_ui(state, screen)

    if state.get("game_over", False):
        if config.secret_mode_alpha or (
            tournament and tournament["phase"] == "playing"
        ):
            secrets.render_game_over_multiplayer(state, screen)
        else:
            rendering.render_game_over(state, screen)

    pygame.display.flip()


def main() -> None:
    """Main entry point for the snake game."""
    if config.debug_mode:
        print("[MAIN] Snake Game Demo starting...")

    screen = initialize_pygame()
    game_state = create_game_state()
    clock = pygame.time.Clock()

    if config.debug_mode:
        print("[MAIN] Entering main game loop at 60 FPS")

    while game_state["running"]:
        delta_time = clock.tick(config.frame_rate) / 1000.0

        handle_input(game_state)
        update_game_state(game_state, delta_time)
        render_frame(game_state, screen)

        if config.debug_mode and game_state["frame_count"] % 60 == 0:
            fps = clock.get_fps()
            print(
                f"[MAIN] Frame {game_state['frame_count']}, FPS={fps:.1f}, time={game_state['time']:.1f}s"
            )

    pygame.quit()

    if config.debug_mode:
        print("[MAIN] Game exited cleanly")


if __name__ == "__main__":
    # Configuration - Modify these values to customize the game
    # Window settings
    config.window_width = 1200
    config.window_height = 900
    config.fullscreen_mode = False

    # Map settings
    config.map_size = 40

    # Game mechanics
    config.initial_speed = 5
    config.speed_calculation = lambda x, y: x + 1
    config.food_count = 5

    # Visual enhancements
    config.enable_enhanced_visuals = False
    config.enable_mouth_animation = False
    config.enable_tongue_animation = False
    config.enable_animated_food = False
    config.enable_food_movement = False

    # Secret modes
    config.secret_mode_alpha = False
    config.secret_mode_omega = False

    # Color scheme (RGB tuples)
    config.color_background = (20, 20, 30)
    config.color_snake_body = (50, 200, 50)
    config.color_snake_head = (70, 220, 70)
    config.color_food = (220, 50, 50)
    config.color_text = (255, 255, 255)
    config.color_ui = (100, 100, 120)

    main()
