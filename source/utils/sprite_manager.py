"""
Module responsible for managing and caching loaded spritesheets
to prevent redundant disk reads and optimize rendering performance.
"""

from os.path import join
import pygame


class SpriteManager:
    """
    A static manager class that loads, caches, and provides global access
    to all pygame spritesheets used by entities in the game.
    """

    # Internal cache storing loaded image surfaces mapped to their string names
    _spritesheets = {}

    @classmethod
    def add_spritesheet(cls, spritesheet_name: str, spritesheet_path: str) -> None:
        """
        Loads a spritesheet from the disk, optimizes it, and stores it in the cache.

        Args:
            spritesheet_name (str): The unique identifier key for the spritesheet.
            spritesheet_path (str): The file path to the image asset.
        """

        # .convert_alpha() optimizes the image format for the specific display
        cls._spritesheets[spritesheet_name] = pygame.image.load(
            spritesheet_path
        ).convert_alpha()

    @classmethod
    def get_spritesheet(cls, spritesheet_name: str) -> pygame.Surface:
        """
        Retrieves a cached spritesheet by its identifier name.

        Args:
            spritesheet_name (str): The identifier key of the requested spritesheet.

        Returns:
            pygame.Surface: The cached pygame image surface.
        """
        return cls._spritesheets[spritesheet_name]

    @classmethod
    def load_sprites(cls):
        """
        Pre-loads all standard entity spritesheets into memory.
        This is called once during the initial Game setup.
        """
        SpriteManager.add_spritesheet(
            "player", join("graphics", "models", "player_model.png")
        )
        SpriteManager.add_spritesheet(
            "basic_offensive", join("graphics", "models", "basic_npc.png")
        )
        SpriteManager.add_spritesheet(
            "basic_defensive", join("graphics", "models", "basic_npc.png")
        )
        SpriteManager.add_spritesheet(
            "tree", join("graphics", "models", "tree_model_npc.png")
        )
        SpriteManager.add_spritesheet(
            "rl_mlp", join("graphics", "models", "rl_model_npc.png")
        )
        SpriteManager.add_spritesheet(
            "guard_thomas", join("graphics", "models", "guard_thomas.png")
        )
        SpriteManager.add_spritesheet(
            "blacksmith_grom", join("graphics", "models", "blacksmith_grom.png")
        )
        SpriteManager.add_spritesheet(
            "merchant_silas", join("graphics", "models", "merchant_silas.png")
        )
