"""
Module containing a hardcoded 'SimpleBrain' for NPC decision-making.

Used as a baseline rule-based AI system to compare against
Decision Trees and Reinforcement Learning models.
"""

import random
from source.core.settings import (
    SHARED_ACTION_MAP_REVERSED,
    SHARED_STATE_MAP_REVERSED,
    MELEE_RANGE,
)


class SimpleBrain:
    """A simplistic rule-based AI for NPC behavior."""

    def __init__(self, strategy: str) -> None:
        self.strategy = strategy
        self.npc_passive_counter = 0

    def predict(self, context_data: list) -> int:
        """
        Predicts the next action based on the provided context data.
        """
        dist = context_data[0]
        npc_stamina = context_data[2]
        player_action = SHARED_STATE_MAP_REVERSED.get(context_data[6], "IDLE")
        npc_action = SHARED_STATE_MAP_REVERSED.get(context_data[3], "IDLE")

        # 1. ACTION COMMITMENT
        if npc_action in ["LIGHT_ATTACK", "HEAVY_ATTACK"]:
            return SHARED_ACTION_MAP_REVERSED.get(npc_action)

        # 2. DISTANCE MANAGEMENT
        if dist > MELEE_RANGE:
            if self.strategy == "offensive" and npc_stamina > 0.3:
                return SHARED_ACTION_MAP_REVERSED.get("RUN")
            return SHARED_ACTION_MAP_REVERSED.get("IDLE")

        # 3. REACT TO PLAYER ACTIONS
        if player_action in ["LIGHT_ATTACK", "HEAVY_ATTACK"]:
            return SHARED_ACTION_MAP_REVERSED.get("BLOCK")

        if player_action == "BLOCK":
            if self.strategy == "offensive" and npc_stamina >= 0.5:
                # Offensive enemies try to break the guard
                return SHARED_ACTION_MAP_REVERSED.get("HEAVY_ATTACK")

        # 4. INITIATE ACTIONS (Player is IDLE, RUNNING, or STUNNED)
        if self.strategy == "offensive":
            if npc_stamina >= 0.3:
                return SHARED_ACTION_MAP_REVERSED.get("LIGHT_ATTACK")
            return SHARED_ACTION_MAP_REVERSED.get("BLOCK")

        elif self.strategy == "defensive":
            if player_action == "STUN" or self.npc_passive_counter > 10:
                self.npc_passive_counter = 0
                if npc_stamina >= 0.5:
                    return SHARED_ACTION_MAP_REVERSED.get("HEAVY_ATTACK")
                return SHARED_ACTION_MAP_REVERSED.get("LIGHT_ATTACK")

            self.npc_passive_counter += 1
            return SHARED_ACTION_MAP_REVERSED.get("BLOCK")

        # Fallback
        return SHARED_ACTION_MAP_REVERSED.get("IDLE")
