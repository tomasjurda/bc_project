"""
Module containing a hardcoded 'SimpleBrain' for NPC decision-making.

Used as a baseline rule-based AI system to compare against
Decision Trees and Reinforcement Learning models.
"""

from source.core.settings import SHARED_ACTION_MAP_REVERSED


class SimpleBrain:
    """A simplistic rule-based AI for NPC behavior."""

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

        # Run towards the player if they are far away
        if dist > 60:
            return SHARED_ACTION_MAP_REVERSED.get("RUN")

        # Attack if the NPC has sufficient stamina and is close enough
        if npc_stamina >= 0.3:
            return SHARED_ACTION_MAP_REVERSED.get("LIGHT_ATTACK")

        # Default to idle if no other conditions are met
        return SHARED_ACTION_MAP_REVERSED.get("IDLE")
