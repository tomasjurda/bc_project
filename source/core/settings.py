# WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
TILE_SIZE = 64

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
