"""Hidden multiplayer and tournament features."""

from typing import Any
import random
from config import config
from components import snake


def create_player_two(state: dict[str, Any]) -> None:
    """Initialize second player snake at distinct spawn position.

    Args:
        state: Game state to add player two to.
    """
    spawn_x = config.map_size_width - 2
    spawn_y = 1
    initial_direction = (-1, 0)

    state['player_two'] = snake.create_snake((spawn_x, spawn_y), initial_direction)
    state['score_two'] = 0

    player_one_spawn_x = 1
    player_one_spawn_y = config.map_size_height - 2
    player_one_direction = (1, 0)

    state['snake'] = snake.create_snake((player_one_spawn_x, player_one_spawn_y), player_one_direction)
    state['score'] = 0

    if config.debug_mode:
        print(f'[SECRETS] Player 1 spawned at ({player_one_spawn_x}, {player_one_spawn_y}) facing {player_one_direction}')
        print(f'[SECRETS] Player 2 spawned at ({spawn_x}, {spawn_y}) facing {initial_direction}')


def start_tournament_match(state: dict[str, Any]) -> None:
    """Start tournament match countdown from pre-match splash.
    
    Args:
        state: Game state containing tournament data.
    """
    tournament = state.get('tournament')
    if not tournament:
        return
    
    tournament['phase'] = 'countdown'
    tournament['animation_timer'] = 3.0
    
    state['game_over'] = False
    state['score'] = 0
    state['score_two'] = 0
    
    match = get_current_match(tournament)
    if match:
        create_player_two(state)
        tournament['current_player1_name'] = match['player1']
        tournament['current_player2_name'] = match['player2']
        
        if config.debug_mode:
            print(f'[TOURNAMENT] Starting countdown for: {match["player1"]} vs {match["player2"]}')


def handle_player_two_input(state: dict[str, Any], keys: Any) -> None:
    """Process arrow key controls for player two.

    Args:
        state: Game state containing player two snake.
        keys: Pygame key state array.
    """
    import pygame

    player_two = state.get('player_two')
    if not player_two:
        return

    if keys[pygame.K_UP]:
        snake.set_direction(player_two, (0, -1))
    elif keys[pygame.K_DOWN]:
        snake.set_direction(player_two, (0, 1))
    elif keys[pygame.K_LEFT]:
        snake.set_direction(player_two, (-1, 0))
    elif keys[pygame.K_RIGHT]:
        snake.set_direction(player_two, (1, 0))


def update_player_two(state: dict[str, Any], delta_time: float) -> None:
    """Update second snake movement.

    Args:
        state: Game state containing player two snake.
        delta_time: Time elapsed since last frame in seconds.
    """
    player_two = state.get('player_two')
    if not player_two:
        return

    snake.update_movement(player_two, delta_time)

    if config.enable_tongue_animation:
        from components import enhanced_visuals
        enhanced_visuals.update_tongue_animation(player_two, delta_time, state)


def render_scores(state: dict[str, Any], screen: Any) -> None:
    """Display both player scores in a dedicated top bar.

    Args:
        state: Game state with both player scores.
        screen: Pygame surface to render on.
    """
    import pygame

    bar_height = 50
    bar_color = (30, 30, 40)
    
    pygame.draw.rect(screen, bar_color, (0, 0, config.window_width, bar_height))
    pygame.draw.line(screen, config.color_ui, (0, bar_height), (config.window_width, bar_height), 2)

    font = pygame.font.Font(None, 36)

    tournament = state.get('tournament')
    if tournament and tournament.get('phase') == 'playing':
        player1_name = tournament.get('current_player1_name', 'Player 1')
        player2_name = tournament.get('current_player2_name', 'Player 2')
    else:
        player1_name = 'Player 1'
        player2_name = 'Player 2'

    score_text = f'{player1_name}: {state["score"]}'
    score_surface = font.render(score_text, True, config.color_snake_head)
    screen.blit(score_surface, (20, 10))

    score_two_text = f'{player2_name}: {state["score_two"]}'
    score_two_surface = font.render(score_two_text, True, (220, 70, 220))
    text_width = score_two_surface.get_width()
    screen.blit(score_two_surface, (config.window_width - text_width - 20, 10))

    if config.debug_mode and state['frame_count'] % 60 == 0:
        print(f'[SECRETS] {player1_name} Score: {state["score"]}, {player2_name} Score: {state["score_two"]}')


def render_player_two_basic(state: dict[str, Any], screen: Any) -> None:
    """Draw player two snake using rectangular grid cells.

    Args:
        state: Game state containing player two snake.
        screen: Pygame surface to render on.
    """
    import pygame

    player_two = state.get('player_two')
    if not player_two:
        return

    cell_size = config.grid_cell_size
    offset_x = config.map_offset_x
    offset_y = config.map_offset_y
    segments = player_two['segments']

    player_two_body_color = (200, 50, 200)
    player_two_head_color = (220, 70, 220)

    for i, (grid_x, grid_y) in enumerate(segments):
        pixel_x = offset_x + grid_x * cell_size
        pixel_y = offset_y + grid_y * cell_size

        color = player_two_head_color if i == 0 else player_two_body_color

        rect = pygame.Rect(pixel_x, pixel_y, cell_size, cell_size)
        pygame.draw.rect(screen, color, rect)


def render_player_two_enhanced(state: dict[str, Any], screen: Any) -> None:
    """Draw player two snake with enhanced visuals.

    Args:
        state: Game state containing player two snake.
        screen: Pygame surface to render on.
    """
    from components import enhanced_visuals

    player_two = state.get('player_two')
    if not player_two:
        return

    player_two_body_color = (200, 50, 200)
    player_two_head_color = (220, 70, 220)

    enhanced_visuals.render_snake_with_colors(
        player_two,
        screen,
        state['time'],
        player_two_body_color,
        player_two_head_color
    )
    enhanced_visuals.render_head_details_for_snake(
        player_two,
        screen,
        state,
        player_two_head_color
    )


def render_game_over_multiplayer(state: dict[str, Any], screen: Any) -> None:
    """Display game over screen with both player scores.

    Args:
        state: Game state containing both player scores.
        screen: Pygame surface to render on.
    """
    import pygame

    score = state.get('score', 0)
    score_two = state.get('score_two', 0)

    font_large = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 36)

    game_over_text = font_large.render('GAME OVER', True, config.color_text)

    if score > score_two:
        winner_text = font_medium.render('Player 1 Wins!', True, config.color_snake_head)
    elif score_two > score:
        winner_text = font_medium.render('Player 2 Wins!', True, (220, 70, 220))
    else:
        winner_text = font_medium.render('Tie Game!', True, config.color_text)

    score_text = font_small.render(f'P1: {score}  |  P2: {score_two}', True, config.color_text)
    restart_text = font_small.render('Press SPACE to restart or ESC to exit', True, config.color_ui)

    screen_width = config.window_width
    screen_height = config.window_height

    game_over_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 2 - 80))
    winner_rect = winner_text.get_rect(center=(screen_width // 2, screen_height // 2 - 20))
    score_rect = score_text.get_rect(center=(screen_width // 2, screen_height // 2 + 40))
    restart_rect = restart_text.get_rect(center=(screen_width // 2, screen_height // 2 + 100))

    screen.blit(game_over_text, game_over_rect)
    screen.blit(winner_text, winner_rect)
    screen.blit(score_text, score_rect)
    screen.blit(restart_text, restart_rect)


def create_tournament(player_names: list[str]) -> dict[str, Any]:
    """Generate tournament bracket structure for up to 8 players.
    
    Args:
        player_names: List of 2-8 unique player names.
        
    Returns:
        Tournament state dictionary with bracket structure.
    """
    if len(player_names) < 2 or len(player_names) > 8:
        raise ValueError('Tournament requires 2-8 players')
    
    if len(set(player_names)) != len(player_names):
        raise ValueError('Player names must be unique')
    
    num_players = len(player_names)
    
    if num_players <= 2:
        num_rounds = 1
    elif num_players <= 4:
        num_rounds = 2
    else:
        num_rounds = 3
    
    shuffled_names = player_names.copy()
    random.shuffle(shuffled_names)
    
    rounds: list[list[dict[str, Any]]] = []
    
    if num_players == 2:
        rounds.append([{
            'player1': shuffled_names[0],
            'player2': shuffled_names[1],
            'winner': None
        }])
    elif num_players == 3:
        rounds.append([
            {'player1': shuffled_names[0], 'player2': shuffled_names[1], 'winner': None},
            {'player1': shuffled_names[2], 'player2': 'BYE', 'winner': shuffled_names[2]}
        ])
        rounds.append([{'player1': None, 'player2': None, 'winner': None}])
    elif num_players == 4:
        rounds.append([
            {'player1': shuffled_names[0], 'player2': shuffled_names[1], 'winner': None},
            {'player1': shuffled_names[2], 'player2': shuffled_names[3], 'winner': None}
        ])
        rounds.append([{'player1': None, 'player2': None, 'winner': None}])
    elif num_players == 5:
        rounds.append([
            {'player1': shuffled_names[0], 'player2': shuffled_names[1], 'winner': None},
            {'player1': shuffled_names[2], 'player2': shuffled_names[3], 'winner': None},
            {'player1': shuffled_names[4], 'player2': 'BYE', 'winner': shuffled_names[4]}
        ])
        rounds.append([
            {'player1': None, 'player2': None, 'winner': None},
            {'player1': None, 'player2': 'BYE', 'winner': None}
        ])
        rounds.append([{'player1': None, 'player2': None, 'winner': None}])
    elif num_players == 6:
        rounds.append([
            {'player1': shuffled_names[0], 'player2': shuffled_names[1], 'winner': None},
            {'player1': shuffled_names[2], 'player2': shuffled_names[3], 'winner': None},
            {'player1': shuffled_names[4], 'player2': shuffled_names[5], 'winner': None}
        ])
        rounds.append([
            {'player1': None, 'player2': None, 'winner': None},
            {'player1': None, 'player2': 'BYE', 'winner': None}
        ])
        rounds.append([{'player1': None, 'player2': None, 'winner': None}])
    elif num_players == 7:
        rounds.append([
            {'player1': shuffled_names[0], 'player2': shuffled_names[1], 'winner': None},
            {'player1': shuffled_names[2], 'player2': shuffled_names[3], 'winner': None},
            {'player1': shuffled_names[4], 'player2': shuffled_names[5], 'winner': None},
            {'player1': shuffled_names[6], 'player2': 'BYE', 'winner': shuffled_names[6]}
        ])
        rounds.append([
            {'player1': None, 'player2': None, 'winner': None},
            {'player1': None, 'player2': None, 'winner': None}
        ])
        rounds.append([{'player1': None, 'player2': None, 'winner': None}])
    else:
        rounds.append([
            {'player1': shuffled_names[0], 'player2': shuffled_names[1], 'winner': None},
            {'player1': shuffled_names[2], 'player2': shuffled_names[3], 'winner': None},
            {'player1': shuffled_names[4], 'player2': shuffled_names[5], 'winner': None},
            {'player1': shuffled_names[6], 'player2': shuffled_names[7], 'winner': None}
        ])
        rounds.append([
            {'player1': None, 'player2': None, 'winner': None},
            {'player1': None, 'player2': None, 'winner': None}
        ])
        rounds.append([{'player1': None, 'player2': None, 'winner': None}])
    
    tournament_state = {
        'phase': 'bracket',
        'rounds': rounds,
        'current_round': 0,
        'current_match': 0,
        'winner': None,
        'animation_timer': 0.0,
        'player_names': player_names.copy()
    }
    
    if config.debug_mode:
        print(f'[TOURNAMENT] Created bracket for {num_players} players')
        print(f'[TOURNAMENT] {num_rounds} rounds, first round has {len(rounds[0])} matches')
    
    return tournament_state



def render_name_entry(state: dict[str, Any], screen: Any) -> None:
    """Display name entry screen with text input.
    
    Args:
        state: Game state containing tournament data.
        screen: Pygame surface to render on.
    """
    import pygame
    
    tournament = state.get('tournament')
    if not tournament:
        return
    
    screen.fill(config.color_background)
    
    font_large = pygame.font.Font(None, 64)
    font_medium = pygame.font.Font(None, 42)
    font_small = pygame.font.Font(None, 32)
    
    title_text = font_large.render('Tournament Setup', True, config.color_text)
    title_rect = title_text.get_rect(center=(config.window_width // 2, 60))
    screen.blit(title_text, title_rect)
    
    player_names = tournament.get('player_names', [])
    current_input = tournament.get('current_input', '')
    
    instruction_text = font_medium.render(f'Enter Player {len(player_names) + 1} Name:', True, config.color_text)
    instruction_rect = instruction_text.get_rect(center=(config.window_width // 2, 140))
    screen.blit(instruction_text, instruction_rect)
    
    input_box_width = 400
    input_box_height = 50
    input_box_x = (config.window_width - input_box_width) // 2
    input_box_y = 200
    
    pygame.draw.rect(screen, config.color_ui, (input_box_x, input_box_y, input_box_width, input_box_height), 2)
    
    input_text = font_medium.render(current_input, True, config.color_text)
    screen.blit(input_text, (input_box_x + 10, input_box_y + 10))
    
    y_offset = 280
    for i, name in enumerate(player_names):
        player_text = font_small.render(f'{i + 1}. {name}', True, config.color_snake_head)
        screen.blit(player_text, (config.window_width // 2 - 100, y_offset + i * 35))
    
    help_text = font_small.render('Press ENTER to add player (2-8 players)', True, config.color_ui)
    help_rect = help_text.get_rect(center=(config.window_width // 2, config.window_height - 100))
    screen.blit(help_text, help_rect)
    
    if len(player_names) >= 2:
        start_text = font_small.render('Press SPACE to start tournament', True, config.color_snake_head)
        start_rect = start_text.get_rect(center=(config.window_width // 2, config.window_height - 60))
        screen.blit(start_text, start_rect)


def handle_name_entry_input(state: dict[str, Any], event: Any) -> None:
    """Process keyboard input for name entry phase.
    
    Args:
        state: Game state containing tournament data.
        event: Pygame event to process.
    """
    import pygame
    
    tournament = state.get('tournament')
    if not tournament:
        return
    
    if event.type == pygame.KEYDOWN:
        current_input = tournament.get('current_input', '')
        player_names = tournament.get('player_names', [])
        
        if event.key == pygame.K_RETURN and current_input.strip():
            if current_input.strip() not in player_names and len(player_names) < 8:
                player_names.append(current_input.strip())
                tournament['current_input'] = ''
                
                if config.debug_mode:
                    print(f'[TOURNAMENT] Added player: {current_input.strip()}')
        
        elif event.key == pygame.K_BACKSPACE:
            tournament['current_input'] = current_input[:-1]
        
        elif event.key == pygame.K_SPACE and len(player_names) >= 2:
            tournament_bracket = create_tournament(player_names)
            state['tournament'] = tournament_bracket
            
            if config.debug_mode:
                print(f'[TOURNAMENT] Starting tournament with {len(player_names)} players')
        
        elif event.unicode and len(current_input) < 20:
            if event.unicode.isprintable() and event.unicode != ' ':
                tournament['current_input'] = current_input + event.unicode



def render_bracket(tournament: dict[str, Any], screen: Any) -> None:
    """Display tournament bracket showing all matchups.
    
    Args:
        tournament: Tournament state with bracket structure.
        screen: Pygame surface to render on.
    """
    import pygame
    
    screen.fill(config.color_background)
    
    font_large = pygame.font.Font(None, 56)
    font_medium = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 28)
    
    title_text = font_large.render('Tournament Bracket', True, config.color_text)
    title_rect = title_text.get_rect(center=(config.window_width // 2, 40))
    screen.blit(title_text, title_rect)
    
    rounds = tournament['rounds']
    current_round = tournament['current_round']
    current_match = tournament['current_match']
    
    round_width = config.window_width // (len(rounds) + 1)
    
    match_positions = []
    
    for round_idx, round_matches in enumerate(rounds):
        x_pos = round_width * (round_idx + 1)
        
        if round_idx == 0:
            round_label = 'Round 1'
        elif round_idx == len(rounds) - 1:
            round_label = 'Finals'
        else:
            round_label = f'Round {round_idx + 1}'
        
        label_text = font_small.render(round_label, True, config.color_ui)
        label_rect = label_text.get_rect(center=(x_pos, 100))
        screen.blit(label_text, label_rect)
        
        match_spacing = (config.window_height - 200) // (len(round_matches) + 1)
        round_positions = []
        
        for match_idx, match in enumerate(round_matches):
            y_pos = 150 + match_spacing * (match_idx + 1)
            
            is_current = (round_idx == current_round and match_idx == current_match)
            
            box_color = config.color_snake_head if is_current else config.color_ui
            box_width = 180
            box_height = 80
            box_x = x_pos - box_width // 2
            box_y = y_pos - box_height // 2
            
            pygame.draw.rect(screen, box_color, (box_x, box_y, box_width, box_height), 3)
            
            round_positions.append((x_pos, y_pos, box_x, box_y, box_width, box_height))
            
            player1 = match.get('player1')
            player2 = match.get('player2')
            winner = match.get('winner')
            
            if player1 is None:
                player1 = '???'
            if player2 is None:
                player2 = '???'
            
            if player1 == 'BYE' or player2 == 'BYE':
                bye_text = font_small.render('BYE', True, config.color_ui)
                bye_rect = bye_text.get_rect(center=(x_pos, y_pos))
                screen.blit(bye_text, bye_rect)
            elif player1 == '???' or player2 == '???':
                p1_text = font_small.render(str(player1)[:12], True, config.color_ui)
                p2_text = font_small.render(str(player2)[:12], True, config.color_ui)
                
                p1_rect = p1_text.get_rect(center=(x_pos, y_pos - 15))
                p2_rect = p2_text.get_rect(center=(x_pos, y_pos + 15))
                
                screen.blit(p1_text, p1_rect)
                screen.blit(p2_text, p2_rect)
            else:
                if winner:
                    p1_color = config.color_snake_head if winner == player1 else config.color_ui
                    p2_color = config.color_snake_head if winner == player2 else config.color_ui
                else:
                    p1_color = config.color_text
                    p2_color = config.color_text
                
                p1_text = font_small.render(str(player1)[:12], True, p1_color)
                p2_text = font_small.render(str(player2)[:12], True, p2_color)
                
                p1_rect = p1_text.get_rect(center=(x_pos, y_pos - 15))
                p2_rect = p2_text.get_rect(center=(x_pos, y_pos + 15))
                
                screen.blit(p1_text, p1_rect)
                screen.blit(p2_text, p2_rect)
        
        match_positions.append(round_positions)
    
    for round_idx in range(len(match_positions) - 1):
        current_round_positions = match_positions[round_idx]
        next_round_positions = match_positions[round_idx + 1]
        
        for next_match_idx, next_pos in enumerate(next_round_positions):
            match1_idx = next_match_idx * 2
            match2_idx = next_match_idx * 2 + 1
            
            if match1_idx < len(current_round_positions):
                x1, y1, bx1, by1, bw1, bh1 = current_round_positions[match1_idx]
                x2, y2, bx2, by2, bw2, bh2 = next_pos
                
                start_x = bx1 + bw1
                start_y = y1
                mid_x = (start_x + bx2) // 2
                end_x = bx2
                end_y = y2
                
                pygame.draw.line(screen, config.color_ui, (start_x, start_y), (mid_x, start_y), 2)
                pygame.draw.line(screen, config.color_ui, (mid_x, start_y), (mid_x, end_y), 2)
                pygame.draw.line(screen, config.color_ui, (mid_x, end_y), (end_x, end_y), 2)
            
            if match2_idx < len(current_round_positions):
                x1, y1, bx1, by1, bw1, bh1 = current_round_positions[match2_idx]
                x2, y2, bx2, by2, bw2, bh2 = next_pos
                
                start_x = bx1 + bw1
                start_y = y1
                mid_x = (start_x + bx2) // 2
                end_x = bx2
                end_y = y2
                
                pygame.draw.line(screen, config.color_ui, (start_x, start_y), (mid_x, start_y), 2)
                pygame.draw.line(screen, config.color_ui, (mid_x, start_y), (mid_x, end_y), 2)
                pygame.draw.line(screen, config.color_ui, (mid_x, end_y), (end_x, end_y), 2)
    
    next_match = get_current_match(tournament)
    if next_match and next_match.get('player1') and next_match.get('player2'):
        if next_match['player2'] != 'BYE':
            prompt_text = font_medium.render('Press ENTER to start next match', True, config.color_snake_head)
            prompt_rect = prompt_text.get_rect(center=(config.window_width // 2, config.window_height - 50))
            screen.blit(prompt_text, prompt_rect)


def handle_bracket_input(state: dict[str, Any], keys: Any) -> None:
    """Process presenter key input to start next match.
    
    Args:
        state: Game state containing tournament data.
        keys: Pygame key state array.
    """
    tournament = state.get('tournament')
    if not tournament:
        return
    
    next_match = get_current_match(tournament)
    if next_match and next_match.get('player1') and next_match.get('player2'):
        if next_match['player2'] == 'BYE':
            advance_winner(tournament, next_match['player1'])
            
            if config.debug_mode:
                print(f'[TOURNAMENT] {next_match["player1"]} advances via BYE')
        else:
            tournament['phase'] = 'pre_match'
            tournament['animation_timer'] = 3.0
            
            if config.debug_mode:
                print(f'[TOURNAMENT] Starting match: {next_match["player1"]} vs {next_match["player2"]}')



def _render_starburst(screen: Any, center_x: int, center_y: int, timer: float, color: tuple[int, int, int], base_size: int = 200, inner_ratio: float = 0.7) -> None:
    """Render animated starburst with rotation and pulsing.
    
    Args:
        screen: Pygame surface to render on.
        center_x: X coordinate of starburst center.
        center_y: Y coordinate of starburst center.
        timer: Animation timer for rotation and pulsing.
        color: RGB color tuple for the starburst.
        base_size: Base radius of the starburst.
        inner_ratio: Ratio of inner points to outer points (shorter = more dramatic rays).
    """
    import pygame
    import math
    
    rotation = math.sin(timer * 2) * 0.3
    scale = 1.0 + math.sin(timer * 3) * 0.15
    
    size = int(base_size * scale)
    num_points = 16
    
    points = []
    for i in range(num_points):
        angle = (i * 2 * math.pi / num_points) + rotation
        if i % 2 == 0:
            radius = size
        else:
            radius = size * inner_ratio
        
        x = center_x + int(radius * math.cos(angle))
        y = center_y + int(radius * math.sin(angle))
        points.append((x, y))
    
    if len(points) >= 3:
        pygame.draw.polygon(screen, color, points)


def _render_pulsing_oval(screen: Any, center_x: int, center_y: int, timer: float) -> None:
    """Render pulsing oval behind player name that oscillates between white and light yellow.
    
    Args:
        screen: Pygame surface to render on.
        center_x: X coordinate of oval center.
        center_y: Y coordinate of oval center.
        timer: Animation timer for color pulsing.
    """
    import pygame
    import math
    
    pulse = (math.sin(timer * 2) + 1) / 2
    
    r = int(255)
    g = int(255)
    b = int(255 - pulse * 100)
    color = (r, g, b)
    
    width = 300
    height = 100
    
    rect = pygame.Rect(
        center_x - width // 2,
        center_y - height // 2,
        width,
        height
    )
    pygame.draw.ellipse(screen, color, rect)


def render_countdown(tournament: dict[str, Any], screen: Any) -> None:
    """Display countdown before match starts.
    
    Args:
        tournament: Tournament state with countdown timer.
        screen: Pygame surface to render on.
    """
    import pygame
    
    screen.fill((0, 0, 0))
    
    timer = tournament.get('animation_timer', 0)
    countdown = int(timer) + 1
    
    if countdown > 0:
        font_huge = pygame.font.Font(None, 300)
        countdown_text = font_huge.render(str(countdown), True, (255, 255, 255))
        countdown_rect = countdown_text.get_rect(center=(config.window_width // 2, config.window_height // 2))
        screen.blit(countdown_text, countdown_rect)


def render_pre_match_splash(tournament: dict[str, Any], screen: Any) -> None:
    """Display pre-match splash with contestant names and animations.
    
    Args:
        tournament: Tournament state with current match info.
        screen: Pygame surface to render on.
    """
    import pygame
    
    screen.fill((0, 0, 0))
    
    match = get_current_match(tournament)
    if not match:
        return
    
    timer = tournament.get('animation_timer', 0)
    
    font_vs = pygame.font.SysFont(None, 120, bold=True, italic=True)
    font_names = pygame.font.Font(None, 120)
    font_countdown = pygame.font.Font(None, 48)
    
    vs_text = font_vs.render('VS', True, (0, 0, 0))
    vs_rect = vs_text.get_rect(center=(config.window_width // 2, config.window_height // 2))
    
    actual_bounds = vs_text.get_bounding_rect()
    stripe_height = actual_bounds.height - 10
    stripe_y = vs_rect.top + actual_bounds.top + 5
    pygame.draw.rect(screen, (220, 20, 20), (0, stripe_y, config.window_width, stripe_height))
    
    screen.blit(vs_text, vs_rect)
    
    player1_text = font_names.render(match['player1'], True, (255, 255, 255))
    player1_rect = player1_text.get_rect(center=(config.window_width // 2, config.window_height // 2 - 150))
    screen.blit(player1_text, player1_rect)
    
    player2_text = font_names.render(match['player2'], True, (255, 255, 255))
    player2_rect = player2_text.get_rect(center=(config.window_width // 2, config.window_height // 2 + 150))
    screen.blit(player2_text, player2_rect)
    
    prompt_text = font_countdown.render('Press SPACE or ENTER to start', True, (255, 255, 255))
    prompt_rect = prompt_text.get_rect(center=(config.window_width // 2, config.window_height - 80))
    screen.blit(prompt_text, prompt_rect)


def render_post_match_splash(tournament: dict[str, Any], screen: Any, winner_name: str) -> None:
    """Display post-match splash with winner celebration.
    
    Args:
        tournament: Tournament state.
        screen: Pygame surface to render on.
        winner_name: Name of the match winner.
    """
    import pygame
    import math
    
    screen.fill(config.color_background)
    
    timer = tournament.get('animation_timer', 0)
    
    font_huge = pygame.font.Font(None, 96)
    font_large = pygame.font.Font(None, 64)
    
    center_x = config.window_width // 2
    center_y = config.window_height // 2
    
    _render_starburst(screen, center_x, center_y, timer, (255, 255, 255), base_size=250, inner_ratio=0.75)
    _render_starburst(screen, center_x, center_y, timer + 0.5, (255, 215, 0), base_size=220, inner_ratio=0.75)
    
    pulse = abs(math.sin(timer * 4))
    
    winner_label = font_large.render('WINNER', True, config.color_ui)
    winner_label_rect = winner_label.get_rect(center=(center_x, center_y - 80))
    screen.blit(winner_label, winner_label_rect)
    
    winner_text = font_huge.render(winner_name, True, config.color_snake_head)
    winner_rect = winner_text.get_rect(center=(center_x, center_y + 20))
    
    scale = 1.0 + pulse * 0.15
    scaled_winner = pygame.transform.scale(
        winner_text,
        (int(winner_rect.width * scale), int(winner_rect.height * scale))
    )
    scaled_rect = scaled_winner.get_rect(center=(center_x, center_y + 20))
    screen.blit(scaled_winner, scaled_rect)



def get_current_match(tournament: dict[str, Any]) -> dict[str, Any] | None:
    """Retrieve the current active matchup.
    
    Args:
        tournament: Tournament state with bracket structure.
        
    Returns:
        Current match dictionary or None if tournament complete.
    """
    rounds = tournament['rounds']
    current_round = tournament['current_round']
    current_match = tournament['current_match']
    
    if current_round >= len(rounds):
        return None
    
    round_matches = rounds[current_round]
    
    if current_match >= len(round_matches):
        return None
    
    match = round_matches[current_match]
    
    if match['player1'] is None or match['player2'] is None:
        if current_round > 0:
            prev_round = rounds[current_round - 1]
            
            match_pair_idx = current_match * 2
            if match_pair_idx < len(prev_round):
                match1 = prev_round[match_pair_idx]
                if match1.get('winner'):
                    match['player1'] = match1['winner']
            
            if match_pair_idx + 1 < len(prev_round):
                match2 = prev_round[match_pair_idx + 1]
                if match2.get('winner'):
                    match['player2'] = match2['winner']
    
    return match


def advance_winner(tournament: dict[str, Any], winner_name: str) -> None:
    """Update bracket with match winner and progress to next match.
    
    Args:
        tournament: Tournament state to update.
        winner_name: Name of the player who won the match.
    """
    rounds = tournament['rounds']
    current_round = tournament['current_round']
    current_match = tournament['current_match']
    
    if current_round >= len(rounds):
        return
    
    round_matches = rounds[current_round]
    if current_match >= len(round_matches):
        return
    
    match = round_matches[current_match]
    match['winner'] = winner_name
    
    if config.debug_mode:
        print(f'[TOURNAMENT] Winner recorded: {winner_name}')
    
    tournament['current_match'] += 1
    
    if tournament['current_match'] >= len(round_matches):
        tournament['current_round'] += 1
        tournament['current_match'] = 0
        
        if config.debug_mode:
            print(f'[TOURNAMENT] Advancing to round {tournament["current_round"] + 1}')
    
    if tournament['current_round'] >= len(rounds):
        tournament['winner'] = winner_name
        tournament['phase'] = 'champion'
        
        if config.debug_mode:
            print(f'[TOURNAMENT] Tournament complete! Champion: {winner_name}')


def record_match_winner(state: dict[str, Any]) -> None:
    """Record winner when match ends and transition to post-match splash.
    
    Winner is determined by:
    1. Who survived longest (if one player is still alive, they win)
    2. If both died simultaneously, higher score wins
    3. If tied on score, player 1 wins
    
    Args:
        state: Game state containing tournament and player scores.
    """
    tournament = state.get('tournament')
    if not tournament or tournament['phase'] != 'playing':
        return
    
    player1_name = tournament.get('current_player1_name')
    player2_name = tournament.get('current_player2_name')
    
    if not player1_name or not player2_name:
        return
    
    player1_alive = state.get('player1_alive', True)
    player2_alive = state.get('player2_alive', True)
    score = state.get('score', 0)
    score_two = state.get('score_two', 0)
    
    if player1_alive and not player2_alive:
        winner = player1_name
        if config.debug_mode:
            print(f'[TOURNAMENT] {player1_name} wins by survival (P1:{score} vs P2:{score_two})')
    elif player2_alive and not player1_alive:
        winner = player2_name
        if config.debug_mode:
            print(f'[TOURNAMENT] {player2_name} wins by survival (P1:{score} vs P2:{score_two})')
    else:
        if score > score_two:
            winner = player1_name
            if config.debug_mode:
                print(f'[TOURNAMENT] {player1_name} wins by score ({score} vs {score_two})')
        elif score_two > score:
            winner = player2_name
            if config.debug_mode:
                print(f'[TOURNAMENT] {player2_name} wins by score ({score_two} vs {score})')
        else:
            winner = player1_name
            if config.debug_mode:
                print(f'[TOURNAMENT] {player1_name} wins by tiebreaker (both {score})')
    
    tournament['match_winner'] = winner
    
    rounds = tournament['rounds']
    current_round = tournament['current_round']
    current_match = tournament['current_match']
    
    is_final_match = (
        current_round == len(rounds) - 1 and
        current_match == len(rounds[current_round]) - 1
    )
    
    if is_final_match:
        tournament['winner'] = winner
        tournament['phase'] = 'champion'
        tournament['animation_timer'] = 0.0
        
        if config.debug_mode:
            print(f'[TOURNAMENT] Final match complete! Champion: {winner}')
    else:
        tournament['phase'] = 'post_match'
        tournament['animation_timer'] = 3.0



def render_champion_screen(tournament: dict[str, Any], screen: Any) -> None:
    """Display tournament champion with grand animations.
    
    Args:
        tournament: Tournament state with winner information.
        screen: Pygame surface to render on.
    """
    import pygame
    import math
    
    screen.fill(config.color_background)
    
    winner = tournament.get('winner', 'Unknown')
    timer = tournament.get('animation_timer', 0)
    
    font_huge = pygame.font.Font(None, 140)
    font_large = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 36)
    
    pulse = abs(math.sin(timer * 2))
    
    center_x = config.window_width // 2
    center_y = config.window_height // 2
    
    if '_confetti' not in tournament:
        tournament['_confetti'] = []
        for i in range(150):
            tournament['_confetti'].append({
                'x': random.uniform(0, config.window_width),
                'y': random.uniform(-100, config.window_height),
                'speed': random.uniform(40, 80),
                'drift_speed': random.uniform(0.5, 1.2),
                'drift_offset': random.uniform(0, math.pi * 2),
                'size': random.randint(3, 7),
                'color': random.choice([
                    (255, 0, 0),
                    (255, 165, 0),
                    (255, 255, 0),
                    (0, 255, 0),
                    (0, 150, 255),
                    (138, 43, 226),
                    (255, 105, 180)
                ])
            })
    
    confetti = tournament.get('_confetti', [])
    for particle in confetti:
        particle['y'] += particle['speed'] * 0.016
        drift = math.sin(timer * particle['drift_speed'] + particle['drift_offset']) * 20
        particle['x'] += drift * 0.016
        
        if particle['x'] < 0:
            particle['x'] = config.window_width
        elif particle['x'] > config.window_width:
            particle['x'] = 0
        
        if particle['y'] > config.window_height + 20:
            particle['y'] = -20
            particle['x'] = random.uniform(0, config.window_width)
        
        pygame.draw.circle(
            screen,
            particle['color'],
            (int(particle['x']), int(particle['y'])),
            particle['size']
        )
    
    for i in range(17):
        progress = i / 16.0
        
        if progress < 0.5:
            blend = progress * 2
            r = int(0 + blend * 255)
            g = int(0 + blend * 255)
            b = int(0 + blend * 255)
        else:
            blend = (progress - 0.5) * 2
            r = int(255)
            g = int(255 - blend * 40)
            b = int(255 - blend * 255)
        
        color = (r, g, b)
        
        size_base = int((280 - i * 12) * 1.5)
        rotation_offset = i * 0.3
        inner_ratio = 0.7 + (i % 3) * 0.05
        
        _render_starburst(
            screen,
            center_x,
            center_y - 50,
            timer + rotation_offset,
            color,
            base_size=size_base,
            inner_ratio=inner_ratio
        )
    
    trophy_y = 80
    pygame.draw.rect(screen, (255, 215, 0), (center_x - 25, trophy_y, 50, 60), 0)
    pygame.draw.rect(screen, (255, 215, 0), (center_x - 35, trophy_y - 15, 70, 20), 0)
    pygame.draw.rect(screen, (255, 215, 0), (center_x - 15, trophy_y + 60, 30, 15), 0)
    pygame.draw.circle(screen, (255, 215, 0), (center_x - 40, trophy_y + 20), 12)
    pygame.draw.circle(screen, (255, 215, 0), (center_x + 40, trophy_y + 20), 12)
    
    trophy_scale = 1.0 + pulse * 0.15
    if trophy_scale > 1.0:
        offset = int((trophy_scale - 1.0) * 40)
        pygame.draw.rect(screen, (255, 215, 0), (center_x - 25 - offset, trophy_y - offset, 50 + offset * 2, 60 + offset * 2), 0)
    
    shadow_offset = 3
    champion_shadow = font_large.render('TOURNAMENT CHAMPION', True, (0, 0, 0))
    champion_shadow_rect = champion_shadow.get_rect(center=(center_x + shadow_offset, center_y - 180 + shadow_offset))
    screen.blit(champion_shadow, champion_shadow_rect)
    
    champion_glow_colors = [
        (255, 255, 200, 30),
        (255, 255, 150, 50),
        (255, 255, 100, 70)
    ]
    
    for idx, glow_color in enumerate(champion_glow_colors):
        glow_size = int(6 + pulse * 4 - idx * 1.5)
        glow_surface = pygame.Surface((config.window_width, config.window_height), pygame.SRCALPHA)
        glow_text = font_large.render('TOURNAMENT CHAMPION', True, glow_color[:3])
        glow_rect = glow_text.get_rect(center=(center_x, center_y - 180))
        
        for dx in range(-glow_size, glow_size + 1, 2):
            for dy in range(-glow_size, glow_size + 1, 2):
                if dx * dx + dy * dy <= glow_size * glow_size:
                    glow_surface.blit(glow_text, (glow_rect.x + dx, glow_rect.y + dy))
        
        glow_surface.set_alpha(glow_color[3] if len(glow_color) > 3 else 255)
        screen.blit(glow_surface, (0, 0))
    
    champion_label = font_large.render('TOURNAMENT CHAMPION', True, (255, 255, 255))
    champion_label_rect = champion_label.get_rect(center=(center_x, center_y - 180))
    screen.blit(champion_label, champion_label_rect)
    
    shadow_offset = 4
    winner_shadow = font_huge.render(winner, True, (0, 0, 0))
    shadow_rect = winner_shadow.get_rect(center=(center_x + shadow_offset, center_y - 50 + shadow_offset))
    screen.blit(winner_shadow, shadow_rect)
    
    glow_colors = [
        (255, 255, 200, 30),
        (255, 255, 150, 50),
        (255, 255, 100, 70)
    ]
    
    for idx, glow_color in enumerate(glow_colors):
        glow_size = int(8 + pulse * 6 - idx * 2)
        glow_surface = pygame.Surface((config.window_width, config.window_height), pygame.SRCALPHA)
        glow_text = font_huge.render(winner, True, glow_color[:3])
        glow_rect = glow_text.get_rect(center=(center_x, center_y - 50))
        
        for dx in range(-glow_size, glow_size + 1, 2):
            for dy in range(-glow_size, glow_size + 1, 2):
                if dx * dx + dy * dy <= glow_size * glow_size:
                    glow_surface.blit(glow_text, (glow_rect.x + dx, glow_rect.y + dy))
        
        glow_surface.set_alpha(glow_color[3] if len(glow_color) > 3 else 255)
        screen.blit(glow_surface, (0, 0))
    
    winner_text = font_huge.render(winner, True, (255, 255, 255))
    winner_rect = winner_text.get_rect(center=(center_x, center_y - 50))
    screen.blit(winner_text, winner_rect)
    
    rounds = tournament.get('rounds', [])
    bracket_label = font_medium.render('Final Bracket:', True, config.color_text)
    screen.blit(bracket_label, (50, center_y + 100))
    
    y_offset = center_y + 150
    for round_idx, round_matches in enumerate(rounds):
        if round_idx == len(rounds) - 1:
            round_name = 'Finals'
        else:
            round_name = f'Round {round_idx + 1}'
        
        round_text = font_small.render(round_name, True, config.color_text)
        screen.blit(round_text, (70, y_offset))
        y_offset += 30
        
        for match in round_matches:
            if match.get('winner') and match['player2'] != 'BYE':
                match_text = font_small.render(
                    f'  {match["player1"]} vs {match["player2"]} > {match["winner"]}',
                    True,
                    config.color_ui
                )
                screen.blit(match_text, (90, y_offset))
                y_offset += 25
    
    restart_text = font_medium.render('Press SPACE to restart or ESC to exit', True, config.color_snake_head)
    restart_rect = restart_text.get_rect(center=(config.window_width // 2, config.window_height - 50))
    screen.blit(restart_text, restart_rect)



def update_tournament_timers(state: dict[str, Any], delta_time: float) -> None:
    """Update tournament animation timers and handle phase transitions.
    
    Args:
        state: Game state containing tournament data.
        delta_time: Time elapsed since last frame in seconds.
    """
    tournament = state.get('tournament')
    if not tournament:
        return
    
    phase = tournament.get('phase')
    
    if phase == 'pre_match':
        pass
    
    elif phase == 'countdown':
        tournament['animation_timer'] -= delta_time
        
        if tournament['animation_timer'] <= 0:
            tournament['phase'] = 'playing'
            
            if config.debug_mode:
                print('[TOURNAMENT] Countdown complete, match starting!')
    
    elif phase == 'post_match':
        tournament['animation_timer'] -= delta_time
        
        if tournament['animation_timer'] <= 0:
            winner = tournament.get('match_winner')
            if winner:
                advance_winner(tournament, winner)
            
            if tournament.get('phase') != 'champion':
                tournament['phase'] = 'bracket'
                
                if config.debug_mode:
                    print('[TOURNAMENT] Returning to bracket view')
            else:
                if config.debug_mode:
                    print('[TOURNAMENT] Tournament complete, showing champion screen')
    
    elif phase == 'champion':
        tournament['animation_timer'] += delta_time
