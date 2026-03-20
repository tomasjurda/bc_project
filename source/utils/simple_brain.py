"""
Module containing a hardcoded 'SimpleBrain' for NPC decision-making.

Used as a baseline rule-based AI system to compare against
Decision Trees and Reinforcement Learning models.
"""

import random
from source.core.settings import SHARED_ACTION_MAP_REVERSED


class SimpleBrain:
    """A simplistic rule-based AI for NPC behavior."""

    def __init__(self, strategy: str) -> None:
        self.strategy = strategy

    def predict(self, context_data: list) -> int:
        """
        Predicts the next action based on the provided context data.

        Args:
            context_data (list): A list containing game state data.
                Index 0 is expected to be the distance to the player.
                Index 2 is expected to be the NPC's stamina.

        Returns:
            int: The action ID representing the chosen behavior.
        """

        # Extract distance and stamina from the specific list indices
        dist = context_data[0]
        npc_stamina = context_data[2]

        if dist > 60:
            if self.strategy == "offensive":
                return SHARED_ACTION_MAP_REVERSED.get("RUN")
            return SHARED_ACTION_MAP_REVERSED.get("IDLE")

        # Attack if the NPC has sufficient stamina and is close enough
        roll = random.random()
        if self.strategy == "offensive":
            if npc_stamina >= 0.3 and roll >= 0.2:
                return SHARED_ACTION_MAP_REVERSED.get("LIGHT_ATTACK")
            return SHARED_ACTION_MAP_REVERSED.get("BLOCK")
        else:
            if npc_stamina >= 0.3 and roll >= 0.6:
                return SHARED_ACTION_MAP_REVERSED.get("LIGHT_ATTACK")
            return SHARED_ACTION_MAP_REVERSED.get("BLOCK")
