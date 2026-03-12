"""
Module defining the HostileNPC class, which represents enemies that
are immediately aggressive towards the player upon spawning.
"""

import pygame
from source.entities.entity import Entity
from source.entities.npc import NPC


class HostileNPC(NPC):
    """
    A subclass of NPC representing an enemy entity.
    It automatically flags itself as hostile upon creation, forcing it to
    immediately seek out and attack the player using its assigned AI brain.
    """

    def __init__(
        self,
        pos: tuple[float, float],
        groups: list | tuple,
        sprite_sheet: pygame.Surface,
        collisions: pygame.sprite.Group,
        player: Entity,
        brain_type: str = "basic",
    ) -> None:
        """
        Initializes the HostileNPC and sets its aggressive state.

        Args:
            pos (tuple[float, float]): Initial (x, y) spawn coordinates.
            groups (list | tuple): Pygame sprite groups to attach this entity to.
            sprite_sheet (pygame.Surface): The image grid containing animations.
            collisions (pygame.sprite.Group): Environment collision objects.
            player (Any): Reference to the target player entity.
            brain_type (str): The AI model type to load ("basic", "tree", "rl_mlp").
        """
        super().__init__(pos, groups, sprite_sheet, collisions, player, brain_type)
        self.hostile = True
