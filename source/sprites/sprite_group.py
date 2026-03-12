"""
Module containing the AllSprites custom Pygame group, which handles
camera scrolling (offset) and depth-based rendering (Y-sorting).
"""

import pygame
from source.core.settings import WINDOW_HEIGHT, WINDOW_WIDTH, TILE_SIZE


class AllSprites(pygame.sprite.Group):
    """
    A custom Pygame sprite group that overrides the standard draw method
    to implement a dynamic camera offset and pseudo-3D Y-sorting.

    Attributes:
        offset (pygame.Vector2): The dynamic camera offset calculated based on player position.
    """

    def __init__(self) -> None:
        """Initializes the custom sprite group and sets up the camera offset vector."""
        super().__init__()
        self.offset = pygame.Vector2()

    def draw(
        self,
        surface: pygame.Surface,
        player_pos: tuple[float, float],
        map_width: int,
        map_height: int,
        debug_mode: bool,
    ) -> None:
        """
        Calculates camera offset and renders all sprites to the screen.
        Background and floor tiles are drawn first, followed by Y-sorted entities
        (like players and props) to create a sense of depth.

        Args:
            surface (pygame.Surface): The main display surface to draw onto.
            player_pos (tuple[float, float]): The (x, y) coordinates of the player.
            map_width (int): Total width of the current map in tiles.
            map_height (int): Total height of the current map in tiles.
            debug_mode (bool): If True, draws attack hitboxes and other debug UI elements.
        """
        self.offset.x = max(
            0,
            min(player_pos[0] - WINDOW_WIDTH / 2, map_width * TILE_SIZE - WINDOW_WIDTH),
        )
        self.offset.y = max(
            0,
            min(
                player_pos[1] - WINDOW_HEIGHT / 2,
                map_height * TILE_SIZE - WINDOW_HEIGHT,
            ),
        )

        ground_and_col_sprites = [
            sprite for sprite in self if not hasattr(sprite, "ysort")
        ]
        ysort_sprites = [sprite for sprite in self if hasattr(sprite, "ysort")]

        for sprite in ground_and_col_sprites:
            surface.blit(
                sprite.image,
                (
                    int(sprite.rect.topleft[0] - self.offset.x),
                    int(sprite.rect.topleft[1] - self.offset.y),
                ),
            )
        for sprite in sorted(
            ysort_sprites, key=lambda sprite: sprite.rect.bottomright[1]
        ):
            if hasattr(sprite, "invisible"):
                continue
            surface.blit(
                sprite.image,
                (
                    int(sprite.rect.topleft[0] - self.offset.x),
                    int(sprite.rect.topleft[1] - self.offset.y),
                ),
            )
            if hasattr(sprite, "draw_ui"):
                sprite.draw_ui(surface, self.offset, debug_mode)
            if hasattr(sprite, "attack_hitbox") and debug_mode:
                if sprite.attack_hitbox:
                    pygame.draw.rect(
                        surface,
                        (255, 0, 0),
                        sprite.attack_hitbox.move(-self.offset.x, -self.offset.y),
                    )
