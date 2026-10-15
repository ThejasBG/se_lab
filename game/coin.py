"""
Coin: a static collectible circle.

Coins have a type, value and colour. The type is presentation/gameplay data;
collision is still handled through the coin's bounding rectangle.
"""

import pygame


COIN_TYPES = {
    "bronze": {"value": 1, "color": (176, 110, 55)},
    "silver": {"value": 3, "color": (190, 190, 200)},
    "gold": {"value": 5, "color": (245, 205, 55)},
}


class Coin:
    def __init__(self, x, y, radius=12, value=1, color=(230, 190, 60),
                 coin_type="bronze"):
        self.x = x
        self.y = y
        self.radius = radius
        self.value = value
        self.color = color
        self.coin_type = coin_type

    @classmethod
    def from_type(cls, x, y, coin_type, radius=12):
        if coin_type not in COIN_TYPES:
            raise ValueError(f"Unknown coin type: {coin_type}")
        data = COIN_TYPES[coin_type]
        return cls(
            x=x,
            y=y,
            radius=radius,
            value=data["value"],
            color=data["color"],
            coin_type=coin_type,
        )

    def get_rect(self):
        return pygame.Rect(
            int(self.x - self.radius), int(self.y - self.radius),
            self.radius * 2, self.radius * 2,
        )
