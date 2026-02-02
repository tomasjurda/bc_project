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

## RIGHT NOW
- [x] seamless přechod mezi animacemi
- [x] dodělat heavy attack = timing, animace
- [x] dodělat combat = detekce zásahů, úhyb, blok
- [x] směr bloku = kosinus(player.dir, vektor k enemy) > 0

## ROADMAP
- [ ] refactoring player + entity + npc kodu + hierarchie stavů
- [ ] pridavani mechanik souboje 
- [ ] pak AI (pathfinding, test zakladních mobek, vytvoření bosse)
    