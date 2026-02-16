# Bc projekt

## HOW TO RUN THE PROGRAM
### WINDOWS
```bash
python -m venv myenv
myenv/Scripts/activate
python -m pip install -r requirements.txt
python code/main.py
```

### LINUX
```bash
python3 -m venv myenv
source myenv/bin/activate
python3 -m pip install -r requirements.txt
python3 code/main.py
```


## CONTROLS
### COMBAT
- WASD = movement
- SPACE = dodge
- LEFT MOUSE BUTTON = light attack
- RIGHT MOUSE BUTTON = heavy attack
    - F = feint 
- R (hold) = Block
- Q = break when stunned

### OTHER
- E = interacting (doors)
- X = debug mode


## DATASET
data/npc_dataset.csv
- dist (int): distance to player
- npc_hp_status (cat): CRITICAL = (1-19)% , HURT = (20-49)% , OK = (50-100)%
- npc_stamina_status (cat): TIRED = (0-29)% , OK = (30-100)%
- npc_current_action (cat): can be IDLE, RUN, BLOCK, HEAVY_ATTACK or STUN
- player_hp_status (cat): CRITICAL = (1-19)% , HURT = (20-49)% , OK = (50-100)%
- player_stamina_status (cat): TIRED = (0-29)% , OK = (30-100)%
- player_action (cat): can be any state (IDLE, RUN, BLOCK, DODGE, LIGHT_ATTACK, HEAVY_ATTACK, STUN)
- new_action (cat): how should the NPC react


## ROADMAP PROJEKTU

- [x] vytvoření základní rpg hry
- [x] dokončení combat systému
- [x] základní stavová logika řešení animací a ovládání
- [x] implementace path findingu pro npc
- [x] implementace základní rozhodovací mechaniky a jednoduchého if/else + rozhodování pomocí DecisionTreeClasifier
- [x] vytvoření trénovacího prostředí s použitím gymnasium a natrénování modelu PPO (stable_baselines3) pomocí Reinforcement learning
- [ ] využití LLM pro interakci s NPC
