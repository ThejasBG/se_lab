"""
renderer: all pygame drawing lives here, kept separate from game logic.
"""

import pygame

WIDTH, HEIGHT = 700, 500
WINDOW_SIZE = (WIDTH, HEIGHT)

COLOR_BG = (35, 45, 35)
COLOR_PLAYER = (80, 180, 255)
COLOR_OBSTACLE = (150, 70, 70)
COLOR_TEXT = (255, 255, 255)


def draw_scene(surface, player, coins, obstacles=None):
    surface.fill(COLOR_BG)

    if obstacles:
        for obstacle in obstacles:
            pygame.draw.rect(surface, COLOR_OBSTACLE, obstacle, border_radius=5)

    for coin in coins:
        pygame.draw.circle(
            surface,
            coin.color,
            (int(coin.x), int(coin.y)),
            coin.radius,
        )

    pygame.draw.rect(
        surface,
        COLOR_PLAYER,
        player.get_rect(),
        border_radius=4,
    )


def draw_text(surface, font, text, pos, color=COLOR_TEXT):
    surface.blit(font.render(text, True, color), pos)


def draw_banner(surface, font, text):
    surf = font.render(text, True, (255, 220, 80))
    rect = surf.get_rect(
        center=(surface.get_width() // 2, surface.get_height() // 2)
    )
    surface.blit(surf, rect)


def draw_game_over(surface, font, score, final_score, elapsed_time, reason):
    """Dim the play area and show the final score and restart instruction."""
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surface.blit(overlay, (0, 0))

    title = font.render(reason, True, (255, 220, 80))
    score_text = font.render(f"Coins: {score}", True, COLOR_TEXT)
    time_text = font.render(f"Time: {elapsed_time:.2f}s", True, COLOR_TEXT)
    final_text = font.render(f"Final Score: {final_score:.2f}", True, COLOR_TEXT)
    restart_text = font.render("Press R to start a new round", True, COLOR_TEXT)

    center_x = surface.get_width() // 2
    surface.blit(title, title.get_rect(center=(center_x, 190)))
    surface.blit(score_text, score_text.get_rect(center=(center_x, 230)))
    surface.blit(time_text, time_text.get_rect(center=(center_x, 265)))
    surface.blit(final_text, final_text.get_rect(center=(center_x, 305)))
    surface.blit(restart_text, restart_text.get_rect(center=(center_x, 350)))
