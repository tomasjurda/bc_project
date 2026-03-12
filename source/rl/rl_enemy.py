"""
Module defining the Reinforcement Learning (RL) driven enemy NPC.
"""

import random
from source.entities.npc import NPC


class RLEnemy(NPC):
    """
    An enemy NPC whose actions are dictated by a trained RL model (PPO).

    Attributes:
        forced_action (int): The action dictated by the RL environment.
        current_action (int): The action currently being executed.
        default_pos (tuple): The original spawn position of the enemy.
        hostile (bool): Flag indicating if the NPC attacks the player.
    """

    def __init__(self, pos, groups, sprite_sheet, collisions, player):
        """
        Initializes the RL Enemy with a starting position and game context.

        Args:
            pos (tuple | list): The starting coordinates (x, y).
            groups (list): Pygame sprite groups this entity belongs to.
            sprite_sheet (pygame.Surface): The sprite sheet for animations.
            collisions (pygame.sprite.Group): Group of collision sprites.
            player (Entity): Reference to the player/entity which this entity should attack.
        """
        super().__init__(
            pos, groups, sprite_sheet, collisions, player, brain_type="rl_mlp"
        )

        self.forced_action = 0
        self.current_action = 0

        # Default position used for resetting the environment
        self.default_pos = pos

        self.hostile = True

    def set_action(self, action_code: int):
        """
        Forces the enemy to take a specific action dictated by the RL model.

        Args:
            action_code (int): The integer code representing the action to take.
        """
        self.forced_action = action_code

    def decide_action(self) -> int:
        """
        Determines the enemy's next action, factoring in reaction cooldowns.

        Returns:
            int: The action code the enemy will execute.
        """
        if self.cooldowns["reaction"] > 0:
            return self.current_action

        new_action = self.forced_action

        # If the chosen action is different from the current one,
        # apply a randomized reaction delay to simulate human-like response times
        if new_action != self.current_action:
            self.current_action = new_action
            self.cooldowns["reaction"] = random.triangular(0.3, 0.45, 0.35)

        return self.current_action
