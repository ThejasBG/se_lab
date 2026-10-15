"""
GameEngine: owns the player, coins, obstacles and round state.

A round lasts 30 seconds or until the player loses all lives. Coins are
removed immediately after collection, which makes every coin award its
value exactly once.
"""

import random
import pygame

from game.player import Player
from game.coin import Coin, COIN_TYPES
from game.collection import check_collection
from game.renderer import WIDTH, HEIGHT


NUM_COINS = 12
ROUND_DURATION = 30.0
STARTING_LIVES = 3
OBSTACLE_COUNT = 7
OBSTACLE_MIN_SIZE = 35
OBSTACLE_MAX_SIZE = 75
COLLISION_COOLDOWN = 0.75

COIN_TYPES_LIST = tuple(COIN_TYPES.keys())


class GameEngine:
    def __init__(self):
        self._last_update_ms = pygame.time.get_ticks()
        self.reset_round()

    def reset_round(self):
        """Start a completely fresh round."""
        self.player = Player(x=WIDTH / 2, y=HEIGHT / 2)
        self.score = 0
        self.lives = STARTING_LIVES
        self.remaining_time = ROUND_DURATION
        self.elapsed_time = 0.0
        self.final_score = 0.0
        self.round_active = True
        self._collision_cooldown = 0.0

        self.obstacles = self._make_obstacles()
        self.coins = [self._random_coin() for _ in range(NUM_COINS)]
        self._last_update_ms = pygame.time.get_ticks()

    def _make_obstacles(self):
        obstacles = []
        player_start = self.player.get_rect()

        attempts = 0
        while len(obstacles) < OBSTACLE_COUNT and attempts < 500:
            attempts += 1
            width = random.randint(OBSTACLE_MIN_SIZE, OBSTACLE_MAX_SIZE)
            height = random.randint(OBSTACLE_MIN_SIZE, OBSTACLE_MAX_SIZE)
            x = random.randint(15, WIDTH - width - 15)
            y = random.randint(15, HEIGHT - height - 15)
            rect = pygame.Rect(x, y, width, height)

            # Keep the starting player position clear and avoid stacking
            # obstacles directly on top of one another.
            if rect.colliderect(player_start.inflate(70, 70)):
                continue
            if any(rect.colliderect(other.inflate(12, 12)) for other in obstacles):
                continue

            obstacles.append(rect)

        return obstacles

    def _random_coin(self):
        """Create a coin inside the play area and outside obstacles."""
        for _ in range(500):
            x = random.randint(30, WIDTH - 30)
            y = random.randint(30, HEIGHT - 30)
            coin = Coin.from_type(
                x=x,
                y=y,
                coin_type=random.choice(COIN_TYPES_LIST),
                radius=12,
            )

            if coin.get_rect().colliderect(self.player.get_rect()):
                continue
            if any(coin.get_rect().colliderect(obstacle) for obstacle in self.obstacles):
                continue

            return coin

        # Very unlikely fallback if random placement cannot find a free spot.
        return Coin.from_type(40, 40, "bronze")

    def handle_input(self, keys_pressed):
        """Move the player while keeping it outside obstacles and the play area."""
        if not self.round_active:
            if keys_pressed[pygame.K_r]:
                self.reset_round()
            return

        dx = dy = 0
        if keys_pressed[pygame.K_UP]:
            dy -= self.player.speed
        if keys_pressed[pygame.K_DOWN]:
            dy += self.player.speed
        if keys_pressed[pygame.K_LEFT]:
            dx -= self.player.speed
        if keys_pressed[pygame.K_RIGHT]:
            dx += self.player.speed

        self._move_with_obstacles(dx, dy)

    def _move_with_obstacles(self, dx, dy):
        """Move on each axis separately and penalize obstacle collisions."""
        if dx:
            old_x = self.player.x
            self.player.move(dx, 0, WIDTH, HEIGHT)
            if any(self.player.get_rect().colliderect(o) for o in self.obstacles):
                self.player.x = old_x
                self._hit_obstacle()

        if dy:
            old_y = self.player.y
            self.player.move(0, dy, WIDTH, HEIGHT)
            if any(self.player.get_rect().colliderect(o) for o in self.obstacles):
                self.player.y = old_y
                self._hit_obstacle()

    def _hit_obstacle(self):
        """Lose one life per collision, with a short cooldown between hits."""
        if self._collision_cooldown > 0 or not self.round_active:
            return

        self.lives -= 1
        self._collision_cooldown = COLLISION_COOLDOWN
        self.player.x = WIDTH / 2
        self.player.y = HEIGHT / 2

        if self.lives <= 0:
            self.lives = 0
            self.round_active = False

    def update(self, dt=None):
        """
        Advance the round.

        If dt is supplied it is interpreted as seconds. Otherwise elapsed
        real time since the previous update call is used, so an existing
        game loop that calls update() continues to work.
        """
        now = pygame.time.get_ticks()

        if dt is None:
            dt = max(0.0, (now - self._last_update_ms) / 1000.0)

        self._last_update_ms = now

        if not self.round_active:
            return

        self._collision_cooldown = max(0.0, self._collision_cooldown - dt)
        self.remaining_time = max(0.0, self.remaining_time - dt)
        self.elapsed_time = min(ROUND_DURATION, self.elapsed_time + dt)

        # Award and remove immediately: a collected coin cannot be scored again.
        collected = check_collection(self.player, self.coins)
        for coin in collected:
            self.score += coin.value
            self.coins.remove(coin)

        # Collecting every coin ends the round immediately. The final score
        # is based on points earned per second, multiplied by 100.
        if not self.coins:
            self.final_score = (self.score / max(self.elapsed_time, 0.001)) * 100
            self.round_active = False
            return

        if self.remaining_time <= 0:
            self.remaining_time = 0.0
            self.final_score = (self.score / ROUND_DURATION) * 100
            self.round_active = False

        if self.lives <= 0:
            self.final_score = (self.score / max(self.elapsed_time, 0.001)) * 100
            self.round_active = False

    def handle_event(self, event):
        """Optional event-based restart support for conventional pygame loops."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            if not self.round_active:
                self.reset_round()

    def draw(self, surface, font):
        from game import renderer

        renderer.draw_scene(surface, self.player, self.coins, self.obstacles)
        renderer.draw_text(surface, font, f"Score: {self.score}", (10, 10))
        renderer.draw_text(surface, font, f"Lives: {self.lives}", (10, 40))
        renderer.draw_text(surface, font, f"Time: {self.remaining_time:04.1f}", (10, 70))

        if not self.round_active:
            if not self.coins:
                reason = "ALL COINS COLLECTED"
            elif self.remaining_time <= 0:
                reason = "TIME UP"
            else:
                reason = "NO LIVES"

            renderer.draw_game_over(
                surface,
                font,
                self.score,
                self.final_score,
                self.elapsed_time,
                reason,
            )
