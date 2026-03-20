"""
Module containing the DataManager class, which acts as a centralized, static
data access layer. It handles loading JSON configurations, global lore,
and lazy-loading heavy machine learning models.
"""

import json
from os.path import join
from typing import Any

from joblib import load
from stable_baselines3 import PPO
from source.utils.simple_brain import SimpleBrain


class DataManager:
    """
    A static manager class responsible for loading and providing access to
    game data such as NPC dialogues, map configurations, and AI models.
    """

    _npc_database = {}
    _map_database = {}
    _mlp_brain = None
    _tree_brain = None

    @classmethod
    def load_map_and_npc_data(cls):
        """
        Loads the static map and NPC data from JSON files into memory.
        This should be called exactly ONCE during Game.__init__.
        """
        with open(join("data", "nonhostile_npcs.json"), "r", encoding="utf-8") as f:
            cls._npc_database = json.load(f)

        with open(join("data", "map_data.json"), "r", encoding="utf-8") as f:
            cls._map_database = json.load(f)

    @classmethod
    def get_door_route(
        cls, map_name: str, map_mode: str, door_id: str
    ) -> dict | str | None:
        """
        Safely fetches the destination level and spawn point for a specific door.

        Args:
            map_name (str): The name of the current map.
            map_mode (str): The current mode of the map (e.g., "basic", "tree").
            door_id (str): The identifier of the door being interacted with.

        Returns:
            dict | str | None: Route data containing target level and position, or None if not found.
        """
        map_info = cls._map_database.get(map_name, {}).get(map_mode, {})
        return map_info.get("doors", {}).get(door_id)

    @classmethod
    def get_npc_data(cls, npc_id: str) -> dict:
        """
        Retrieves the configuration and dialogue data for a specific NPC.

        Args:
            npc_id (str): The unique identifier for the NPC.

        Returns:
            dict: The NPC's data dictionary, or an empty dict if not found.
        """
        return cls._npc_database.get(npc_id, {})

    @classmethod
    def get_global_lore(cls) -> str:
        """
        Fetches the shared world knowledge that all LLM-driven NPCs possess.

        Returns:
            str: A string containing the global lore/context of the game world.
        """
        global_lore_data = cls._npc_database.get("GLOBAL_LORE", {})
        return global_lore_data.get("world_knowledge", "")

    @classmethod
    def get_map_npcs(cls, map_name: str, map_mode: str) -> dict:
        """
        Retrieves the list of NPCs that should spawn in a specific map and mode.

        Args:
            map_name (str): The name of the map.
            map_mode (str): The mode of the map (e.g., "spectate", "basic").

        Returns:
            dict: A dictionary of NPC spawn data.
        """
        return cls._map_database.get(map_name, {}).get(map_mode, {}).get("npcs", {})

    @classmethod
    def preload_ai_models(cls) -> None:
        """
        Forces the heavy ML models (PPO and Decision Tree) to load into RAM immediately.
        This prevents game-freezing lag spikes the first time an AI enemy spawns.
        """
        print("Preloading AI Models...")
        cls.get_brain("tree")
        cls.get_brain("rl_mlp")
        print("AI Models loaded successfully!")

    @classmethod
    def get_brain(cls, brain_type: str) -> Any:
        """
        Lazy-loads and returns the requested machine learning model or basic brain.
        Caches the model so it is only loaded from disk once.

        Args:
            brain_type (str): The type of AI model to load ("rl_mlp", "tree", or other).

        Returns:
            Any: The requested model object (PPO, joblib model, or SimpleBrain).
        """
        if brain_type == "rl_mlp":
            if cls._mlp_brain is None:
                print("Loading PyTorch RL Model...")
                cls._mlp_brain = PPO.load(
                    join("data", "rl_models", "ppo_agent.zip"), device="cpu"
                )
            return cls._mlp_brain

        elif brain_type == "tree":
            if cls._tree_brain is None:
                print("Loading Decision Tree Model...")
                cls._tree_brain = load(join("data", "npc_brain_tree_model.joblib"))
            return cls._tree_brain

        if brain_type == "basic_offensive":
            return SimpleBrain("offensive")
        return SimpleBrain("defensive")
