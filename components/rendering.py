"""Basic rendering system for snake game."""

from typing import Any
import pygame
from config import config


def render_checkered_background(screen: pygame.Surface) -> None:
    """Draw checkered background pattern for the game map.

    Args:
        screen: Pygame surface to render on.
    """
    cell_size = config.grid_cell_size
    offset_x = config.map_offset_x
    offset_y = config.map_offset_y

    base_color = config.color_background
    light_color = (
        min(base_color[0] + 10, 255),
        min(base_color[1] + 10, 255),
        min(base_color[2] + 10, 255)
    )

    for y in range(config.map_size_height):
        for x in range(config.map_size_width):
            pixel_x = offset_x + x * cell_size
            pixel_y = offset_y + y * cell_size

            color = light_color if (x + y) % 2 == 0 else base_color

            rect = pygame.Rect(pixel_x, pixel_y, cell_size, cell_size)
            pygame.draw.rect(screen, color, rect)


def render_snake_basic(state: dict[str, Any], screen: pygame.Surface) -> None:
    """Draw snake using rectangular grid cells.

    Args:
        state: Game state containing snake data.
        screen: Pygame surface to render on.
    """
    snake = state.get('snake')
    if not snake:
        return

    cell_size = config.grid_cell_size
    offset_x = config.map_offset_x
    offset_y = config.map_offset_y
    segments = snake['segments']

    for i, (grid_x, grid_y) in enumerate(segments):
        pixel_x = offset_x + grid_x * cell_size
        pixel_y = offset_y + grid_y * cell_size

        color = config.color_snake_head if i == 0 else config.color_snake_body

        rect = pygame.Rect(pixel_x, pixel_y, cell_size, cell_size)
        pygame.draw.rect(screen, color, rect)


def render_food_basic(state: dict[str, Any], screen: pygame.Surface) -> None:
    """Draw food items as colored circles.

    Args:
        state: Game state containing food_items list.
        screen: Pygame surface to render on.
    """
    food_items = state.get('food_items', [])
    cell_size = config.grid_cell_size
    offset_x = config.map_offset_x
    offset_y = config.map_offset_y

    for food in food_items:
        grid_x, grid_y = food['position']

        center_x = offset_x + grid_x * cell_size + cell_size // 2
        center_y = offset_y + grid_y * cell_size + cell_size // 2
        radius = cell_size // 2

        pygame.draw.circle(screen, config.color_food, (center_x, center_y), radius)


def render_ui(state: dict[str, Any], screen: pygame.Surface) -> None:
    """Draw score and game state information.

    Args:
        state: Game state containing score.
        screen: Pygame surface to render on.
    """
    score = state.get('score', 0)

    font = pygame.font.Font(None, 36)
    score_text = font.render(f'Score: {score}', True, config.color_text)

    screen.blit(score_text, (10, 10))


def render_game_over(state: dict[str, Any], screen: pygame.Surface) -> None:
    """Display game over screen with final score and restart prompt.

    Args:
        state: Game state containing final score.
        screen: Pygame surface to render on.
    """
    score = state.get('score', 0)

    font_large = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 36)

    game_over_text = font_large.render('GAME OVER', True, config.color_text)
    score_text = font_medium.render(f'Final Score: {score}', True, config.color_text)
    restart_text = font_small.render('Press SPACE to restart or ESC to exit', True, config.color_ui)

    screen_width = config.window_width
    screen_height = config.window_height

    game_over_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 2 - 60))
    score_rect = score_text.get_rect(center=(screen_width // 2, screen_height // 2 + 20))
    restart_rect = restart_text.get_rect(center=(screen_width // 2, screen_height // 2 + 80))

    screen.blit(game_over_text, game_over_rect)
    screen.blit(score_text, score_rect)
    screen.blit(restart_text, restart_rect)
