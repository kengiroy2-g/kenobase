# KENOBASE QUICK REFERENCE

**Schnellreferenz fuer KI und Entwickler**

---

## SCHNELLSTART

```bash
# 1. Daten bereinigen
python scripts/clean_keno_csv.py data/raw/keno/NEUE_DATEN.csv data/raw/keno/KENO_bereinigt.csv

# 2. Super-Modell testen
python scripts/test_super_model_2025.py

# 3. Empfehlung fuer morgen
python scripts/dynamic_recommendation.py
```

---

## BESTE KONFIGURATION

```python
BEST_MODEL = {
    "jackpot_warning": True,   # 30 Tage Cooldown
    "exclusion_rules": True,   # Position-Regeln
    "anti_birthday": True,     # Zahlen >31
}
```

---

## OPTIMALE TICKETS

| Typ | Ticket | Hinweis |
|-----|--------|---------|
| 9 | [3, 9, 10, 20, 24, 36, 49, 51, 64] | Backtests/ROI: `results/super_model_test_2025.json` |
| 10 | [2, 3, 9, 10, 20, 24, 36, 49, 51, 64] | Quoten: `kenobase/core/keno_quotes.py` |
| 8 | [3, 20, 24, 27, 36, 49, 51, 64] | Keine Gewinngarantie |

**Kern-Zahlen:** 3, 24, 49, 51, 64

---

## REGELN

### WANN SPIELEN
- Heuristiken (z.B. Jackpot-Cooldown) sind *nicht* als Profit-Regel zu verstehen.
- Axiom-First: erst Train->Test (frozen rules) + Nullmodell/Negative Controls.

### WANN NICHT SPIELEN
- Keine "immer/nie" Regeln ohne reproduzierbare OOS-Validierung.

---

## EXCLUSION-REGELN (100% Accuracy)

```
Wenn Zahl X an Position Y gestern -> Exclude Z heute

(4, 17)  -> [70]
(24, 2)  -> [22]
(4, 14)  -> [25]
(14, 7)  -> [38]
(5, 2)   -> [13]
(68, 20) -> [65]
(50, 4)  -> [64]
(1, 8)   -> [33]
```

---

## DATENFORMAT

```csv
Datum;Keno_Z1;Keno_Z2;...;Keno_Z20;Keno_Plus5;Keno_Spieleinsatz
01.01.2018;29;51;28;1;50;27;34;32;21;63;61;26;42;68;48;65;6;19;64;11;32646;304.198,00
```

---

## ORDNERSTRUKTUR

```
data/raw/
├── keno/           # KENO Daten
├── lotto/          # Lotto 6aus49
├── eurojackpot/    # EuroJackpot
└── gluecksspirale/ # Gluecksspirale
```

---

## WICHTIGSTE SCRIPTS

| Script | Zweck |
|--------|-------|
| `super_model_synthesis.py` | Modell trainieren |
| `test_super_model_2025.py` | Out-of-Sample Test |
| `clean_keno_csv.py` | Daten bereinigen |
| `dynamic_recommendation.py` | Empfehlungen |
| `backtest_post_jackpot.py` | Jackpot-Analyse |

---

## DOKUMENTATION

| Datei | Inhalt |
|-------|--------|
| `docs/METHODIK_SUPER_MODEL.md` | Vollstaendige Methodik |
| `docs/SUPER_MODEL.md` | Modell-Beschreibung |
| `docs/DATENFORMATE.md` | Alle Datenformate |
| `AI_COLLABORATION/KNOWLEDGE_BASE/HYPOTHESES_CATALOG.md` | Hypothesen |

---

## KENO QUOTEN

```python
# Typ 9 Quoten
{9: 50000, 8: 5000, 7: 500, 6: 50, 5: 10, 4: 2}

# Typ 10 Quoten
{10: 100000, 9: 10000, 8: 1000, 7: 100, 6: 15, 5: 5, 0: 2}
```

---

## KONTAKT

- **Repository:** https://github.com/kengiroy2-g/kenobase
- **Issues:** GitHub Issues

---

*Quick Reference V1.0 - 2025-12-29*
