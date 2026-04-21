import csv
import random

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

NPC_DECISION_STATES = [
    SHARED_STATE_MAP["IDLE"],
    SHARED_STATE_MAP["RUN"],
    SHARED_STATE_MAP["BLOCK"],
    SHARED_STATE_MAP["HEAVY_ATTACK"],
    SHARED_STATE_MAP["STUN"],
]

MELEE_RANGE = 60


def determine_action(row):
    dist = row["dist"]
    npc_hp = row["npc_hp"]
    npc_stam = row["npc_stam"]
    p_hp = row["player_hp"]
    p_stam = row["player_stam"]
    p_action = row["player_action"]
    npc_action = row["npc_current_action"]

    # 1. Stun Escape
    if npc_action == SHARED_STATE_MAP["STUN"]:
        if npc_stam >= 0.4 and p_stam >= 0.3 and dist < MELEE_RANGE:
            return SHARED_ACTION_MAP_REVERSED["BREAK"]
        return SHARED_ACTION_MAP_REVERSED["IDLE"]

    # 2. Feinting
    if npc_action == SHARED_STATE_MAP["HEAVY_ATTACK"]:
        if p_action == SHARED_STATE_MAP["DODGE"] or dist > MELEE_RANGE:
            return SHARED_ACTION_MAP_REVERSED["FEINT"]
        return SHARED_ACTION_MAP_REVERSED["HEAVY_ATTACK"]

    # 3. Player is out of range
    if dist > MELEE_RANGE:
        if npc_stam >= 0.3:
            return SHARED_ACTION_MAP_REVERSED["RUN"]  # Close the gap
        return SHARED_ACTION_MAP_REVERSED["IDLE"]  # Rest while they are far away

    # 4. Punish Vulnerabilities (Stun / Dialog / Exhausted)
    is_player_vulnerable = p_action in [
        SHARED_STATE_MAP["DIALOG"],
        SHARED_STATE_MAP["STUN"],
    ]
    if is_player_vulnerable or p_stam < 0.20:
        if npc_stam >= 0.5:
            return SHARED_ACTION_MAP_REVERSED["HEAVY_ATTACK"]
        elif npc_stam >= 0.2:
            return SHARED_ACTION_MAP_REVERSED["LIGHT_ATTACK"]
        else:
            return SHARED_ACTION_MAP_REVERSED["IDLE"]

    # 5. Defending against attacks
    if p_action == SHARED_STATE_MAP["HEAVY_ATTACK"]:
        if npc_stam >= 0.3:
            return SHARED_ACTION_MAP_REVERSED["DODGE"]
        return SHARED_ACTION_MAP_REVERSED["BLOCK"]

    if p_action == SHARED_STATE_MAP["LIGHT_ATTACK"]:
        return SHARED_ACTION_MAP_REVERSED["BLOCK"]

    # 6. Dealing with Player Blocking
    if p_action == SHARED_STATE_MAP["BLOCK"]:
        if npc_stam >= 0.5:
            return SHARED_ACTION_MAP_REVERSED["HEAVY_ATTACK"]  # Break the guard
        else:
            return SHARED_ACTION_MAP_REVERSED["IDLE"]

    # 7. Low Resource Fallback (Survival mode)
    if npc_stam < 0.3 or npc_hp < 0.2:
        return SHARED_ACTION_MAP_REVERSED["BLOCK"]

    # 8. Neutral Game (Both in melee range, player is doing nothing/running)
    if npc_hp >= p_hp:
        if npc_stam >= 0.6:
            return SHARED_ACTION_MAP_REVERSED["HEAVY_ATTACK"]
        return SHARED_ACTION_MAP_REVERSED["LIGHT_ATTACK"]
    else:
        return SHARED_ACTION_MAP_REVERSED["LIGHT_ATTACK"]


def generate_data(num_rows):
    data = [
        [
            "dist",
            "npc_hp",
            "npc_stamina",
            "npc_current_action",
            "player_hp",
            "player_stamina",
            "player_action",
            "new_action",
        ]
    ]

    for _ in range(num_rows):
        row_dict = {
            "dist": int(random.triangular(0, 300, 40)),
            "npc_hp": round(random.uniform(0.01, 1.0), 2),
            "npc_stam": round(random.uniform(0.0, 1.0), 2),
            "npc_current_action": random.choice(NPC_DECISION_STATES),
            "player_hp": round(random.uniform(0.01, 1.0), 2),
            "player_stam": round(random.uniform(0.0, 1.0), 2),
            "player_action": random.choice(list(SHARED_STATE_MAP.values())),
        }

        row_dict["new_action"] = determine_action(row_dict)

        data.append(
            [
                row_dict["dist"],
                row_dict["npc_hp"],
                row_dict["npc_stam"],
                row_dict["npc_current_action"],
                row_dict["player_hp"],
                row_dict["player_stam"],
                row_dict["player_action"],
                row_dict["new_action"],
            ]
        )
    return data


if __name__ == "__main__":
    dataset = generate_data(10000)
    with open(
        "./data/npc_dataset_tree.csv", mode="w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerows(dataset)
    print("Dataset generated successfully!")
