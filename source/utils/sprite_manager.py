"""Module responsible for managing loaded spritesheets"""

import pygame


class SpriteManager:
    spritesheets = {}

    @staticmethod
    def add_spritesheet(spritesheet_name, spritesheet_path):
        SpriteManager.spritesheets[spritesheet_name] = pygame.image.load(
            spritesheet_path
        ).convert_alpha()

    @staticmethod
    def get_spritesheet(spritesheet_name):
        return SpriteManager.spritesheets[spritesheet_name]
