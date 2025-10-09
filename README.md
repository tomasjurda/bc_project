# Bc projekt

Klasicky z `main.py` pomocí **F5**, kdy je ale zapotřebí mít:

- `pip install pygame-ce`
- `pip install pytmx`

Lze stáhnout z `requirements.txt`.

---

## Doporučení

- pylint
- black formatter
- flake8
- logging
- hugging face

---

## Spuštění

```bash
python -m venv myenv
myenv/Scripts/activate
pip install pygame-ce
pip install pytmx
python code/main.py
```

## RIGHT NOW AND HINTS 
- [x] obj.type pro typ InteractObject pro např dveře a obj.name pro např souřadnice / loot 
- [x] mazání hráče z předchozích map 
- [x] další mapy 
- [x] interact mechanika 
- [ ] refactoring player + entity + npc kodu + hierarchie stavů
- [ ] pridavani mechanik souboje 
- [ ] pak AI (pathfinding, test zakladních mobek, vytvoření bosse)
    