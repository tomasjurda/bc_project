"""
Module containing global configuration constants, window dimensions,
and mappings for translating discrete entity states to integer values
used by Machine Learning and Reinforcement Learning models.
"""

# Window and Grid Settings
# WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
TILE_SIZE = 64

# Maps string state names to unique integers. Used for compiling the
# observation context array for the RL environment and Decision Tree.
SHARED_STATE_MAP = {
    "IDLE": 0,
    "RUN": 1,
    "DODGE": 2,
    "BLOCK": 3,
    "LIGHT_ATTACK": 4,
    "HEAVY_ATTACK": 5,
    "STUN": 6,
    "DEATH": 7,
    "DIALOG": 8,
}

# Maps integer outputs from the RL agent/Decision Tree back to readable
# string action commands for the FSM to execute.
SHARED_ACTION_MAP = {
    0: "IDLE",
    1: "RUN",
    2: "DODGE",
    3: "BLOCK",
    4: "LIGHT_ATTACK",
    5: "HEAVY_ATTACK",
    6: "FEINT",
    7: "BREAK",
}

# Reverse mapping of SHARED_ACTION_MAP used to quickly fetch the integer
# code for a specific action (e.g., inside the SimpleBrain baseline model).
SHARED_ACTION_MAP_REVERSED = {
    "IDLE": 0,
    "RUN": 1,
    "DODGE": 2,
    "BLOCK": 3,
    "LIGHT_ATTACK": 4,
    "HEAVY_ATTACK": 5,
    "FEINT": 6,
    "BREAK": 7,
}
