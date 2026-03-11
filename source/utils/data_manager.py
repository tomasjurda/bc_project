import json
from os.path import join

from joblib import load
from stable_baselines3 import PPO
from source.utils.simple_brain import SimpleBrain


class DataManager:
    _npc_database = {}
    _map_database = {}
    _mlp_brain = None
    _tree_brain = None

    @classmethod
    def load_map_and_npc_data(cls):
        """Called ONCE in Game.__init__"""
        with open(join("data", "nonhostile_npcs.json"), "r", encoding="utf-8") as f:
            cls._npc_database = json.load(f)

        with open(join("data", "map_data.json"), "r", encoding="utf-8") as f:
            cls._map_database = json.load(f)

    @classmethod
    def get_door_route(cls, map_name, map_mode, door_id):
        """Safely fetches where a door goes."""
        map_info = cls._map_database.get(map_name, {}).get(map_mode, {})
        return map_info.get("doors", {}).get(door_id)

    @classmethod
    def get_npc_data(cls, npc_id):
        return cls._npc_database.get(npc_id, {})

    @classmethod
    def get_global_lore(cls):
        """Fetches the shared world knowledge for all NPCs."""
        global_lore_data = cls._npc_database.get("GLOBAL_LORE", {})
        return global_lore_data.get("world_knowledge", "")

    @classmethod
    def get_map_npcs(cls, map_name, map_mode):
        return cls._map_database.get(map_name, {}).get(map_mode, {}).get("npcs", {})

    @classmethod
    def preload_ai_models(cls):
        """Forces the heavy ML models to load into RAM immediately."""
        print("Preloading AI Models...")
        cls.get_brain("tree")
        cls.get_brain("rl_mlp")
        print("AI Models loaded successfully!")

    @classmethod
    def get_brain(cls, brain_type):
        """Lazy-loads and returns the requested ML model."""
        if brain_type == "rl_mlp":
            if cls._mlp_brain is None:
                print("Loading PyTorch RL Model...")
                cls._mlp_brain = PPO.load(
                    join("data", "rl_models", "ppo_rpg_agent.zip")
                )
            return cls._mlp_brain

        elif brain_type == "tree":
            if cls._tree_brain is None:
                print("Loading Decision Tree Model...")
                cls._tree_brain = load(join("data", "npc_brain_tree_model.joblib"))
            return cls._tree_brain

        return SimpleBrain()
