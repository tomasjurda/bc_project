# AI-Driven Game (Bachelor's Thesis Project)
An Top-Down Souls-like developed in Python using Pygame. This project was created for my Bachelor's thesis to explore, implement, and evaluate various Artificial Intelligence techniques within video games. It moves away from hardcoded, traditional game mechanics by utilizing Machine Learning (ML), Reinforcement Learning (RL), and Local Large Language Models (LLMs) to drive both combat behavior and dynamic narrative progression.

## 1. Project Overview
The game features several interconnected maps (Tutorial, Crossroads, City, Arena) where the player can explore, fight, and interact with the world.
Instead of a single AI approach, this game utilizes multiple distinct systems:

Combat AI: Enemies are driven by a Finite State Machine (FSM), but their decision-making is handled by different "Brains":
- Simple Brain: A baseline, rule-based if/else system.
- Decision Tree: A machine learning model (scikit-learn) trained on pre-recorded combat datasets.
- Reinforcement Learning (PPO): A neural network trained via Proximal Policy Optimization (stable-baselines3 / gymnasium) in a custom simulated combat environment.

Narrative AI: Non-Hostile NPCs do not use traditional dialogue trees. Instead, they interface with a local LLM via Ollama. NPCs process player text dynamically, evaluate politeness, manage internal affinity scores, and update game quests in real-time.

## 2. How to Run the Project

Prerequisites:
- Python 3.8+ installed on your system (Python 3.12.7 was used for developing and testing).
- Ollama installed locally to run the dialogue models. Download it from [ollama.com](https://ollama.com/).

### Step 1: Prepare the LLM (Ollama)
The game uses local LLMs to generate NPC dialogue without requiring an internet connection or paid API keys.
Open your terminal or command prompt and pull the necessary models:

Primary model used for high-quality reasoning
```bash
ollama pull llama3.1:8b
```

Fallback model (used automatically if your PC cannot load Llama 3.1 into memory)
```bash
ollama pull qwen2.5:3b
```

(Ensure the Ollama background service is running before starting the game).

### Step 2: Setup the Python Environment
Navigate to the project directory and set up a virtual environment:

On Windows:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

On Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Launch the Game
To play the main game:
```bash
python main.py
```

To watch or train the Reinforcement Learning agent in the custom Gymnasium environment:
```bash
python rl_training.py
```

## Controls & Debug Mode
### Standard Controls
- W, A, S, D: Move the character.
- Left Mouse Button: Light Attack.
- Right Mouse Button: Heavy Attack.
- Spacebar: Dodge.
- Hold R: Block / Parry.
- F: Feint (Cancel a Heavy Attack during its windup).
- Q: Break (Escape a stun-lock early, costs stamina).
- E: Interact (Talk to NPCs, open doors, change maps).
- Enter / Return: Send typed message in dialogue.

### Debug Mode (Toggle with X)
Pressing X during gameplay toggles a comprehensive developer UI that reveals the underlying mechanics:
Hitboxes: Renders physics collision boxes. The player's color changes based on their combat state:
- Green: Default / Vulnerable
- Red: Blocking
- Blue: Parrying (tight defensive window)
- Black: Dodging (Invincibility frames active)
Attack Hitboxes: Temporary red rectangles that spawn strictly during the lethal frames of weapon swings.
FSM States: Displays the current active state (e.g., RUN, IDLE, STUN) above entities' heads
Pathfinding: Displays the A* algorithm's pathfinding nodes (black squares) that smart enemies use to navigate around obstacles towards the player.
AI Data: Displays what "Brain" is currently piloting an enemy (tree, rl_mlp, basic) and shows the active numeric Affinity score for peaceful NPCs.

## 4. The Combat System
Combat is heavily inspired by "Souls-like" games, relying entirely on positioning, timing, and resource management.

Stamina Management: Every major action (attacking, dodging, breaking) costs Stamina. Stamina regenerates passively over time, but regenerates significantly faster when standing completely still (IDLE)..

Light vs. Heavy Attacks: Light attacks are fast and cost little stamina, but can be blocked. Heavy attacks deal massive damage and cannot be blocked (only parried or dodged), but they have a slow windup.

Feinting: By pressing F during a Heavy Attack's windup, you can cancel the attack and refund some stamina. This is used to bait the enemy AI into prematurely using their parry or dodge.

Block & Parry: Holding R raises your shield, negating light attack damage. The first 2 frames of the Block state open a Parry Window. If an attack lands during this fraction of a second, the attacker's strike is deflected, and they are thrown into a severe, prolonged stun state.

Dodging: Pressing Space executes a rapid roll, granting true Invincibility Frames (i-frames) allowing you to phase through active attack hitboxes safely.

Stun & Break: Getting hit applies damage, physical knockback, and a STUN state. If you have at least 4 stamina, you can press Q to "Break" the combo, instantly ending the stun and granting a brief 0.5s flash of immunity to reposition.

## 5. Communication & World Interaction
Rather than selecting pre-written responses from a menu, interaction with NPCs is handled dynamically by a Local LLM via a background threading client.

### How it Works
When you interact (E) with a friendly NPC, a chat interface opens. You type your responses directly to them.
The system compiles a comprehensive "Context Prompt" and sends it to the LLM. This prompt includes:
- Global Lore: World knowledge that everyone in the game knows.
- Personal Knowledge: Secrets specific to that individual NPC.
- Active Quests: The current state of relevant story flags.
- Chat History: The last few messages spoken in the conversation.

### Strict JSON Output
The LLM is constrained by a schema to output a strict JSON format containing four keys:
- thought_process: The AI's internal evaluation of what you typed (e.g., Did the player actually hand over the item, or are they just talking? Are they being rude?).
- dialogue: The actual text the NPC speaks back to you.
- affinity_change: A strict -1, 0, or 1 modification to their mood.
- quest_update: A string command to change the game's state (or NONE).

### Affinity System & Quests
Affinity: NPCs track how much they like you. Normal conversation yields 0 change. Using explicit pleasantries ("Please", "Thank you friend") yields +1. Insulting or threatening the NPC yields -1. If an NPC's affinity drops below -2, they will become enraged, the dialogue UI will force-close, and they will permanently become Hostile, attacking you on sight.

Quests: The game features tracked quests like hammer_quest (returning a lost tool to Blacksmith Grom) and city_access (convincing Guard Thomas to let you pass). Because there are no hardcoded dialogue options, players must organically convince the NPCs using natural language to trigger these quest updates!
