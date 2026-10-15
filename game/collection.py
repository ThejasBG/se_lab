"""
collection: figures out which coins the player is touching this frame.

The collection itself is applied by GameEngine.update(). Once a coin is
returned by this function, GameEngine removes it from the active coin list,
so it cannot be awarded again.
"""


def check_collection(player, coins):
    """Return the coins currently overlapping the player."""
    player_rect = player.get_rect()
    return [
        coin for coin in coins
        if player_rect.colliderect(coin.get_rect())
    ]
