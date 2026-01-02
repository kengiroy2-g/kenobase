# BESTE KENO-STRATEGIEN (Stand: 02.01.2026)

Basierend auf Backtest 2022-2025 (1.457 Ziehungen, 48 Jackpot-Tage)

**WICHTIG: Version 2 - Korrigierte Analyse nach Backtest-Validierung**
- Original-Version: `BESTE_STRATEGIEN_v1_backup.md`

---

## KRITISCHE ERKENNTNIS

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  JACKPOT-OPTIMIERUNG ≠ ROI-OPTIMIERUNG                                    ║
║                                                                           ║
║  Was Jackpot-Chance erhoeht, SCHADET oft der Gesamt-ROI!                 ║
║  Zwei verschiedene Strategien fuer zwei verschiedene Ziele.              ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

---

## STRATEGIE A: ROI-OPTIMIERUNG (Empfohlen)

**Ziel:** Beste Rendite ueber Zeit
**Fuer:** Typ 6, 7, 8

### Kurzuebersicht

| Typ | Strategie | ROI | Wann spielen |
|-----|-----------|-----|--------------|
| **6** | Timing + Cooldown | **+80.0%** | Tag 24-28 + 8-14d nach JP |
| **7** | Nur Cooldown | **+23.3%** | 8-14 Tage nach 10/10 Jackpot |
| **8** | Nur mod7 | **+35.2%** | Ticket mit diff_sum mod 7 = 3 |
| 9 | Timing + mod7 | -32.6% | Nicht empfohlen |

### TYP 6 - BESTE STRATEGIE (+80% ROI)

```
WICHTIG: Beide Filter ZUSAMMEN verwenden!

WANN:   Tag 24-28 des Monats
        UND 8-14 Tage nach letztem 10/10 Jackpot
ROI:    +80.0%
SPIELE: Nur ~3% aller moeglichen Tage

FEHLER: Nur Timing ODER nur Cooldown bringt NICHT +80%!
        Die Kombination ist entscheidend.
```

### TYP 7 - BESTE STRATEGIE (+23% ROI)

```
WANN:   NUR 8-14 Tage nach letztem 10/10 Jackpot
ROI:    +23.3%
SPIELE: ~18% aller Tage

NICHT bei Typ 7:
- Timing-Filter allein SCHADET (-17%)
- mod7-Filter SCHADET (-45%)
```

### TYP 8 - BESTE STRATEGIE (+35% ROI)

```
WAS:    NUR Tickets mit diff_sum mod 7 = 3
ROI:    +35.2%
SPIELE: ~14% aller Tickets

NICHT bei Typ 8:
- Timing-Filter allein SCHADET (-61%)
- Timing + Cooldown SCHADET (-57%)
```

---

## STRATEGIE B: JACKPOT-JAGD (Nur fuer Typ 10)

**Ziel:** Maximale Chance auf 10/10 Jackpot
**Fuer:** Typ 10 Spieler die negative ROI akzeptieren
**Warnung:** Basiert auf nur n=3 Jackpots - Overfitting-Risiko!

### Invarianten (alle 3 bekannten Gewinner erfuellen diese)

| Constraint | Wert | Alle 3 Gewinner |
|------------|------|-----------------|
| Ziffernprodukt mod 9 | = 0 | Ja |
| Einstellige Zahlen (1-9) | = 1 | Ja |
| Dekaden besetzt | = 6 von 7 | Ja |
| Alle 3 Drittel (1-23, 24-46, 47-70) | JA | Ja |
| Endziffer 1 (11,21,31,41,51,61) | = 0 | Ja |

### JACKPOT-FAVORITES (Validiert 2022-2025, Stabilitaet 80%)

**BEVORZUGEN (erscheinen haeufiger an Jackpot-Tagen):**
```
Kern-Zahlen (beste Vernetzung):
  43 (2.04x), 36 (1.92x), 19 (1.83x), 52 (1.77x), 38 (1.77x)

Weitere Favorites:
  13, 40, 62, 51, 45, 64, 17, 48, 4, 61
```

**MEIDEN (erscheinen seltener an Jackpot-Tagen):**
```
27 (0.21x), 1 (0.22x), 29 (0.23x), 28, 68, 25, 37, 67, 16
```

### Beste Zahlen-Paare (erscheinen gemeinsam)

| Paar | Quote an Jackpot-Tagen |
|------|------------------------|
| 36 + 43 | 38% |
| 38 + 43 | 31% |
| 4 + 43 | 31% |
| 19 + 40 | 31% |

### ROI-Warnung fuer Jackpot-Strategie

```
Invarianten + Favorites:
├── ERHOEHEN Chance auf 10/10
├── VERSCHLECHTERN Gesamt-ROI
├── Nur sinnvoll wenn NUR Jackpot zaehlt
└── Overfitting-Risiko: n=3 ist sehr klein!
```

---

## TIMING-FILTER (Wann spielen)

| Filter | Boost | Empfehlung |
|--------|-------|------------|
| **Tag 24-28** | 2.02x | STARK SPIELEN |
| Tag 22-23 | 1.63x | GUT |
| **Mittwoch** | 1.46x | Bester Wochentag |
| **Juni** | 2.28x | Bester Monat |
| Q1 + Q2 | 1.27-1.33x | Gute Quartale |

### NICHT spielen

| Filter | Boost | Vermeiden |
|--------|-------|-----------|
| Tag 1-21 | 0.63-0.72x | SCHLECHT |
| **August** | 0.24x | SCHLECHTESTER Monat |
| **November** | 0.25x | SEHR SCHLECHT |
| Q3 + Q4 | 0.66-0.74x | Schwache Quartale |
| 61+ Tage nach JP | 0.30x | SCHLECHTESTE Phase |

---

## COOLDOWN-PHASEN (Nach Jackpot)

### Nach JP_10_10 (100.000 EUR Jackpot)

| Tage danach | Effekt | Aktion |
|-------------|--------|--------|
| 1-7 | neutral | - |
| **8-14** | **BOOST** | SPIELEN (Typ 6, 7) |
| 15-21 | neutral | - |
| 22-30 | Cooldown | MEIDEN |
| 31-60 | neutral | - |
| **61+** | **SCHLECHT** | NICHT SPIELEN |

### WICHTIG: Boost nur mit Timing kombinieren (Typ 6)

```
FALSCH:  "8-14 Tage nach JP = immer gut"
RICHTIG: "Tag 24-28 UND 8-14 Tage nach JP = +80% ROI"

Der Boost allein bringt nicht viel.
Die Kombination mit Timing ist entscheidend!
```

---

## mod7-FILTER (Was spielen)

```python
def check_mod7(zahlen):
    diff_sum = sum(abs(a-b) for i,a in enumerate(zahlen) for b in zahlen[i+1:])
    return diff_sum % 7 == 3  # NUR wenn True spielen!
```

**Anwendung:**
- Typ 8: NUR mod7 verwenden (+35% ROI)
- Typ 6: NICHT mit Timing+Cooldown kombinieren (schadet!)
- Typ 10: Teil der Invarianten-Strategie

---

## PRAKTISCHE CHECKLISTE

### Fuer ROI-Optimierung (Empfohlen)

```
TYP 6:
  [ ] Ist heute Tag 24-28?
  [ ] War vor 8-14 Tagen ein 10/10 Jackpot?
  → Wenn BEIDES JA: SPIELEN!
  → Sonst: NICHT SPIELEN

TYP 7:
  [ ] War vor 8-14 Tagen ein 10/10 Jackpot?
  → Wenn JA: SPIELEN!
  → Timing ignorieren bei Typ 7

TYP 8:
  [ ] Hat mein Ticket mod 7 = 3?
  → Wenn JA: SPIELEN!
  → Timing und Cooldown ignorieren bei Typ 8
```

### Fuer Jackpot-Jagd (Typ 10)

```
[ ] Erfuellt Ticket alle Invarianten?
    [ ] Ziffernprodukt mod 9 = 0
    [ ] Genau 1 einstellige Zahl
    [ ] 6 von 7 Dekaden besetzt
    [ ] Alle 3 Drittel besetzt
    [ ] Keine Endziffer 1

[ ] Enthaelt Kern-Zahlen?
    Prioritaet: 43, 36, 19, 52, 38

[ ] Vermeidet schlechte Zahlen?
    Meiden: 27, 1, 29, 28, 68

WARNUNG: Negative ROI erwartet!
```

---

## GENERELL MEIDEN

```
[ ] August oder November?           → NICHT SPIELEN
[ ] Tag 1-21 des Monats?            → NICHT SPIELEN (ausser Typ 7/8)
[ ] Mehr als 61 Tage seit Jackpot?  → NICHT SPIELEN
[ ] Q3 oder Q4?                     → Vorsicht
```

---

## ZUSAMMENFASSUNG

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  FUER DIE MEISTEN SPIELER:                                               ║
║                                                                           ║
║  Typ 6: Tag 24-28 + Boost (8-14d nach JP)  →  +80% ROI                  ║
║  Typ 7: Nur Boost (8-14d nach JP)          →  +23% ROI                  ║
║  Typ 8: Nur mod7=3 Tickets                 →  +35% ROI                  ║
║                                                                           ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  FUER JACKPOT-JAEGER (Typ 10):                                           ║
║                                                                           ║
║  Invarianten + Favorites verwenden                                       ║
║  Akzeptiere negative ROI                                                 ║
║  Overfitting-Risiko beachten (n=3)                                       ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

---

## WARNUNG

**Lotto bleibt ein Verlustgeschaeft!**

- Diese Strategien verbessern relative Chancen
- Garantieren KEINEN Gewinn
- Basieren auf historischen Daten (2022-2025)
- Zukunft kann anders sein
- Invarianten basieren auf nur n=3 Jackpots

**Nur mit Geld spielen, dessen Verlust man verkraften kann!**

---

## QUELLEN

- `scripts/test_strategy_types.py` - Typ 6-9 Test
- `scripts/test_cooldown_definitions.py` - Cooldown-Definitionen
- `scripts/backtest_combined_detailed.py` - Timing-Filter
- `scripts/validate_jackpot_favorites.py` - Favorites-Validierung 2022-2025
- `scripts/backtest_invariant_strategy.py` - Invarianten-Backtest
- `AI_COLLABORATION/KNOWLEDGE_BASE/VALIDIERTE_FAKTEN.md` - Alle Details

---

## AENDERUNGSPROTOKOLL

| Version | Datum | Aenderung |
|---------|-------|-----------|
| v1 | 01.01.2026 | Erste Version |
| **v2** | **02.01.2026** | **Korrektur: ROI vs Jackpot-Optimierung getrennt** |
| v2 | 02.01.2026 | Klarstellung: Timing+Cooldown ZUSAMMEN noetig |
| v2 | 02.01.2026 | Favorites validiert fuer 2022-2025 (80% stabil) |
| v2 | 02.01.2026 | Overfitting-Warnung hinzugefuegt |

---

*Erstellt: 01.01.2026, Aktualisiert: 02.01.2026*
*Basierend auf 1.457 Ziehungen, 48 Jackpots (2022-2025)*
