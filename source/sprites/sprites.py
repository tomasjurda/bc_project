"""
Module containing standard map sprite definitions, distinguishing between
flat background elements, solid walls, and interactive objects.
"""

import pygame


class GroundSprite(pygame.sprite.Sprite):
    """
    A non-collidable, flat texture drawn at the very bottom layer (e.g., grass, dirt).
    """

    def __init__(
        self, pos: tuple[float, float], surf: pygame.Surface, groups: list | tuple
    ) -> None:
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)


class OnGroundSprite(pygame.sprite.Sprite):
    """
    A non-collidable decoration drawn directly on top of the ground layer
    (e.g., paths, flat shadows).
    """

    def __init__(
        self, pos: tuple[float, float], surf: pygame.Surface, groups: list | tuple
    ) -> None:
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)


class WallSprite(pygame.sprite.Sprite):
    """
    A vertical tile representing a wall or boundary.
    It has the 'ysort' attribute to render properly behind or in front of the player.
    """

    def __init__(
        self, pos: tuple[float, float], surf: pygame.Surface, groups: list | tuple
    ) -> None:
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)
        self.ysort = True


class PropSprite(pygame.sprite.Sprite):
    """
    A static object placed in the world (e.g., a tree, barrel, or sign).
    It is Y-sorted alongside entities.
    """

    def __init__(
        self, pos: tuple[float, float], surf: pygame.Surface, groups: list | tuple
    ) -> None:
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)
        self.ysort = True


class InteractObjectSprite(pygame.sprite.Sprite):
    """
    An object the player can interact with by pressing an interaction key
    (e.g., doors, level transitions).

    Attributes:
        name (str): A string identifier used to lookup logic in the DataManager.
        type (str): The category of the interactable (e.g., 'door', 'invisible_door').
        invisible (bool): Optional flag indicating if the sprite should be hidden during drawing.
    """

    def __init__(
        self,
        pos: tuple[float, float],
        surf: pygame.Surface,
        groups: list | tuple,
        name: str,
        obj_type: str,
    ) -> None:
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)
        self.ysort = True
        self.name = name
        self.type = obj_type
        if obj_type == "invisible_door":
            self.invisible = True


class CollisionSprite(pygame.sprite.Sprite):
    """
    An invisible rectangular boundary used purely for physics calculations
    and pathfinding collision mapping.
    """

    def __init__(
        self, pos: tuple[float, float], surf: pygame.Surface, groups: list | tuple
    ) -> None:
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)
