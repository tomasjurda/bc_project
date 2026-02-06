# Bc projekt

## HOW TO RUN THE PROGRAM
```bash
python -m venv myenv
myenv/Scripts/activate
python -m pip install -r requirements.txt
python code/main.py
```

## CONTROLS
- WASD = movement
- SPACE = dodge
- LEFT MOUSE BUTTON = light attack
- RIGHT MOUSE BUTTON = heavy attack
    - F = feint 
- R (hold) = Block
- E = interacting (doors)
- X = debug mode

## DATASET
data/npc_dataset.csv
- dist (int): distance to player
- npc_hp_status (cat): CRITICAL = (1-19)% , HURT = (20-49)% , OK = (50-100)%
- npc_stamina_status (cat): TIRED = (0-29)% , OK = (30-100)%
- npc_current_action (cat): can be IDLE, RUN, BLOCK or HEAVY_ATTACK
- player_hp_status (cat): CRITICAL = (1-19)% , HURT = (20-49)% , OK = (50-100)%
- player_stamina_status (cat): TIRED = (0-29)% , OK = (30-100)%
- player_action (cat): can be any state (IDLE, RUN, BLOCK, DODGE, LIGHT_ATTACK, HEAVY_ATTACK, HURT)
- new_action (cat): how should the NPC react

## ROADMAP
- pathfinding A*
- RL: vytvoření env (gymnasium), trénink
- jednoduché AI základních nepřátel
- využití LLM pro interakci s NPC
