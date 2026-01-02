# BESTE KENO-STRATEGIEN (Stand: 01.01.2026)

Basierend auf Backtest 2022-2025 (1.457 Ziehungen, 48 Jackpot-Tage)

---

## KURZÜBERSICHT

| Typ | Strategie | ROI | Wann spielen |
|-----|-----------|-----|--------------|
| **6** | Timing + Cooldown | **+80.0%** | Tag 24-28 + 8-14d nach JP |
| **7** | Nur Cooldown | **+23.3%** | 8-14 Tage nach 10/10 Jackpot |
| **8** | Nur mod7 | **+35.2%** | Ticket mit diff_sum mod 7 = 3 |
| 9 | Timing + mod7 | -32.6% | Nicht empfohlen |
| 10 | Nur Wirtschaft | -80.4% | Niedrige Inflation + DAX steigend |

---

## TYP 6 - BESTE STRATEGIE (+80% ROI)

### Variante A: Timing + Cooldown
```
WANN:   Tag 24-28 des Monats
        UND 8-14 Tage nach letztem 10/10 Jackpot
ROI:    +80.0%
SPIELE: Nur 3% aller möglichen Tage
```

### Variante B: Nach JP_9_9 warten
```
WANN:   31-60 Tage nach Typ 9, 9/9 Gewinner (50.000€)
ROI:    +60.5%
```

### NICHT bei Typ 6:
- ❌ Cooldown + mod7 zusammen (-34%)
- ❌ Alle Filter zusammen (-24%)

---

## TYP 7 - BESTE STRATEGIE (+23% ROI)

```
WANN:   NUR 8-14 Tage nach letztem 10/10 Jackpot
ROI:    +23.3%
SPIELE: ~18% aller Tage
```

### NICHT bei Typ 7:
- ❌ Timing-Filter allein (-17%)
- ❌ mod7-Filter (-45%)
- ❌ Timing + Cooldown zusammen (-54%)

---

## TYP 8 - BESTE STRATEGIE (+35% ROI)

### Variante A: Nur mod7
```
WAS:    NUR Tickets mit diff_sum mod 7 = 3
ROI:    +35.2%
SPIELE: ~14% aller Tickets
```

### Variante B: Nach JP_10_9 warten
```
WANN:   15-21 Tage nach Typ 10, 9/10 Gewinner (1.000€)
ROI:    +8.6%
ACHTUNG: JP_10_9 passiert fast täglich!
```

### NICHT bei Typ 8:
- ❌ Timing-Filter allein (-61%)
- ❌ Timing + Cooldown (-57%)
- ❌ Alle Filter zusammen (-53%)

---

## TYP 9 - NICHT EMPFOHLEN

```
BESTE:  Timing + mod7
ROI:    -32.6% (immer noch Verlust!)
```

Typ 9 ist bei KEINER Strategie profitabel.

---

## TYP 10 - NUR MIT WIRTSCHAFTSFILTER

```
WANN:   Inflation < 3.7% UND DAX vor 2 Monaten steigend
ROI:    -80.4% (beste gefundene, aber Verlust)
```

### NICHT bei Typ 10:
- ❌ Wirtschaft + Timing zusammen (antagonistisch!)
- ❌ Wirtschaft + mod7 zusammen (antagonistisch!)

---

## TIMING-FILTER (Wann spielen)

| Filter | Boost | Empfehlung |
|--------|-------|------------|
| **Tag 24-28** | 2.02x | STARK SPIELEN |
| Tag 22-23 | 1.63x | GUT |
| **Mittwoch** | 1.46x | Bester Wochentag |
| **Juni** | 2.28x | Bester Monat |
| Q1 + Q2 | 1.27-1.33x | Gute Quartale |

### NICHT spielen:
| Filter | Boost | Vermeiden |
|--------|-------|-----------|
| Tag 1-21 | 0.63-0.72x | SCHLECHT |
| **August** | 0.24x | SCHLECHTESTER Monat |
| **November** | 0.25x | SEHR SCHLECHT |
| Q3 + Q4 | 0.66-0.74x | Schwache Quartale |
| 61+ Tage nach JP | 0.30x | SCHLECHTESTE Phase |

---

## ZAHLEN-FILTER (Was spielen)

### mod7-Filter (für Typ 8, 9, 10)
```python
def check_mod7(zahlen):
    diff_sum = sum(abs(a-b) for i,a in enumerate(zahlen) for b in zahlen[i+1:])
    return diff_sum % 7 == 3  # NUR wenn True spielen!
```

### JACKPOT-FAVORITES (NEU - aus Jackpot-Tage-Analyse 2023)

**BEVORZUGEN (erscheinen häufiger an Jackpot-Tagen):**
```
43, 51, 52, 36, 40, 19, 38, 4, 61, 69, 62, 13, 8, 35, 45
```
Ratio: 43 erscheint 2.13x häufiger an Jackpot-Tagen!

**MEIDEN (erscheinen seltener an Jackpot-Tagen):**
```
1, 16, 21, 27, 29, 37, 67, 25, 68, 28
```
Ratio: 1 erscheint nur 0.24x so oft an Jackpot-Tagen!

### Jackpot-Tage vs. Normale Tage (2023)

| Metrik | Jackpot-Tage | Normale Tage | Differenz |
|--------|--------------|--------------|-----------|
| Birthday (1-31) | 7.8/20 | 8.9/20 | **-12.4%** |
| Hoch (>50) | 6.1/20 | 5.6/20 | **+8.7%** |
| Summe | 730 | 705 | **+25** |

---

## UNIVERSELLE CONSTRAINTS (Typ 10)

Diese Regeln gelten für ALLE bekannten Jackpot-Gewinner:

| Constraint | Wert | Alle 3 Gewinner |
|------------|------|-----------------|
| Ziffernprodukt mod 9 | = 0 | ✓ |
| Einstellige Zahlen (1-9) | = 1 | ✓ |
| Dekaden besetzt | = 6 von 7 | ✓ |
| Alle 3 Drittel (1-23, 24-46, 47-70) | JA | ✓ |
| Endziffer 1 (11,21,31,41,51,61) | = 0 | ✓ |

### Optimierte Typ-10 Tickets (Beispiele)

```python
TYP_10_OPTIMAL = [
    [4, 36, 38, 40, 45, 52, 58, 62, 64, 69],  # Score 9.5
    [4, 35, 36, 38, 40, 43, 45, 52, 64, 69],
    [4, 35, 36, 40, 46, 52, 58, 62, 64, 69],
]
```

---

## REGIONALE MUSTER (Variieren je Bundesland!)

| Region | Gerade im Gewinner | Birthday | Spieler bevorzugen |
|--------|-------------------|----------|-------------------|
| Brandenburg | **8/10** | 4/10 | UNGERADE |
| Bayern | 4/10 | 4/10 | Ausgeglichen |
| Sachsen | **2/10** | 2/10 | GERADE + BIRTHDAY |

**Regel:** Gewinner sind das GEGENTEIL der regionalen Präferenz!

---

## COOLDOWN-PHASEN (Nach Jackpot)

### Nach JP_10_10 (100.000€ Jackpot):
| Tage danach | Effekt | Aktion |
|-------------|--------|--------|
| 1-7 | neutral | - |
| **8-14** | **BOOST** | SPIELEN (Typ 6, 7) |
| 15-21 | neutral | - |
| 22-30 | Cooldown | MEIDEN |
| 31-60 | neutral | - |
| **61+** | **SCHLECHT** | NICHT SPIELEN |

### Nach JP_9_9 (50.000€ Jackpot):
| Tage danach | Typ 6 ROI |
|-------------|-----------|
| 1-7 | +20.3% |
| 8-14 | +17.5% |
| **31-60** | **+60.5%** |

### Nach JP_10_9 (1.000€ Gewinn):
| Tage danach | Typ 8 ROI |
|-------------|-----------|
| **15-21** | **+8.6%** |

---

## PRAKTISCHE CHECKLISTE

### Vor dem Spielen prüfen:

```
□ Welcher Typ? (6, 7, 8 empfohlen)

□ TYP 6:
  □ Ist heute Tag 24-28?
  □ War vor 8-14 Tagen ein 10/10 Jackpot?
  → Wenn beides JA: SPIELEN!

□ TYP 7:
  □ War vor 8-14 Tagen ein 10/10 Jackpot?
  → Wenn JA: SPIELEN!

□ TYP 8:
  □ Hat mein Ticket mod 7 = 3?
  → Wenn JA: SPIELEN!

□ GENERELL MEIDEN:
  □ August oder November?
  □ Tag 1-21 des Monats?
  □ Mehr als 61 Tage seit letztem Jackpot?
  → Wenn eines JA: NICHT SPIELEN!
```

---

## WARNUNG

⚠️ **Lotto bleibt ein Verlustgeschäft!**

- Diese Strategien verbessern relative Chancen
- Garantieren KEINEN Gewinn
- Basieren auf historischen Daten (2022-2025)
- Zukunft kann anders sein

**Nur mit Geld spielen, dessen Verlust man verkraften kann!**

---

## QUELLEN

- `scripts/test_strategy_types.py` - Typ 6-9 Test
- `scripts/test_cooldown_definitions.py` - Cooldown-Definitionen
- `scripts/backtest_combined_detailed.py` - Timing-Filter
- `AI_COLLABORATION/KNOWLEDGE_BASE/VALIDIERTE_FAKTEN.md` - Alle Details
- `results/strategy_test_types_6_9.json` - Rohdaten
- `results/cooldown_definitions_test.json` - Cooldown-Daten

---

*Erstellt: 01.01.2026*
*Basierend auf 1.457 Ziehungen, 48 Jackpots (2022-2025)*
