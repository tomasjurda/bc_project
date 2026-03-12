"""
Main module for running the game.

This module acts as the entry point, initializing the Game instance
and starting the primary application loop.
"""

from source.core.game import Game


if __name__ == "__main__":
    game_instance = Game()
    game_instance.run()
