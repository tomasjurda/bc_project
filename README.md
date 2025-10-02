# SKJ Projekt Roquelike game
Klasicky z `main.py` pomocí **F5**, kdy je ale zapotřebí mít:
- `pip install pygame-ce`
- `pip install pytmx`

Lze stáhnout z `requirements.txt`.


# schuzka 21.07.2025
- pylint
- black formatter
- flake8
- logging
- hugging face


python -m venv myenv        
myenv/Scripts/activate
pip install pygame-ce
pip install pytmx
python code\main.py  


# RIGHT NOW AND HINTS
- obj.type pro typ InteractObject pro např dveře a obj.name pro např souřadnice / loot
- mazání hráče z předchozích map
- další mapy
- interact mechanika
- refactoring player kodu
- pridavani mechanik souboje
- pak AI (pathfinding, test zakladních mobek, vytvoření bosse)


# ROADMAP
- 1 cooldown pro všechno, dodge + interact...
- dalsi mapy
- zmenit model + animace
- zmenit nacitani map a moznost presunu mezi lokacemi
- dokoncit ovladaci mechaniky (m1, m2, dodge, block, feint)
- implementace gridu
- implementace bosse, zakladni alg + A*
- addaptiv + RL
- NPC ve městě
- LLM komunikace
- ...

    