"""Module responsible for managing loaded spritesheets"""

from os.path import join
import pygame


class SpriteManager:
    _spritesheets = {}

    @classmethod
    def add_spritesheet(cls, spritesheet_name, spritesheet_path):
        cls._spritesheets[spritesheet_name] = pygame.image.load(
            spritesheet_path
        ).convert_alpha()

    @classmethod
    def get_spritesheet(cls, spritesheet_name):
        return cls._spritesheets[spritesheet_name]

    @classmethod
    def load_sprites(cls):
        SpriteManager.add_spritesheet(
            "player", join("graphics", "models", "player.png")
        )
        SpriteManager.add_spritesheet(
            "basic_npc", join("graphics", "models", "basic_npc.png")
        )
        SpriteManager.add_spritesheet(
            "tree", join("graphics", "models", "tree_model.png")
        )
        SpriteManager.add_spritesheet(
            "rl_mlp", join("graphics", "models", "rl_model.png")
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
