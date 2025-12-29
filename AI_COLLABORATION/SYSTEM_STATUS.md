# KENOBASE System Status

**Stand:** 2025-12-29 (Update 3)
**Version:** 2.2.2 (Quoten-Fix, ROI korrigiert)

---

## Update: Paar-basierte Tickets (Gewinnfrequenz ja, Profit nein)

**Wichtig:** Die frueheren positiven ROI-Werte stammten aus einer *falschen* Quoten-Tabelle in einigen Phase-4 Skripten.
Die korrekten festen Quoten (1 EUR Einsatz) kommen aus:
- `Keno_GPTs/Keno_GQ_2022_2023-2024.csv` ("1 Euro Gewinn")
- Source of truth: `kenobase/core/keno_quotes.py`

### 6-Jahres-Backtest (2018-2024, 2237 Ziehungen)

Basis: `scripts/backtest_pair_guarantee.py` (Top-20 starke Paare pro Typ).

| KENO Typ | ROI (Top-20 Paare, Portfolio) | Bestes Pair-Ticket (ROI-max) | Monate mit Gewinn (bestes Ticket) |
|----------|-------------------------------|------------------------------|-----------------------------------|
| Typ-2  | -43.21% | (9,50) -> [9,50] | 72/74 (97.3%) |
| Typ-6  | -56.42% | (24,40) -> [3,24,40,49,51,64] | 74/74 (100%) |
| Typ-8  | -66.66% | (20,36) -> [2,3,20,24,36,49,51,64] | 74/74 (100%) |
| Typ-10 | -56.99% | (33,50) -> [2,3,9,24,33,36,49,50,51,64] | 74/74 (100%) |

---

## Bestaetigte Hypothesen (11)

| ID | Hypothese | Evidence | Datum |
|----|-----------|----------|-------|
| WL-001 | Paar-Garantie pro GK | 30/30 Paare >90% | 2025-12-29 |
| WL-005 | Paar-Gewinn-Frequenz | 100% >=2x/Monat | 2025-12-29 |
| WL-006 | Jackpot-Einzigartigkeit | 90.9% Uniqueness>=0.5 | 2025-12-29 |
| WL-007 | GK-spezifische Paare | GK_9_9: 4.07x Lift | 2025-12-29 |
| HOUSE-004 | Near-Miss Constraint | 70x Switch | 2025-12-29 |
| HYP-001 | Gewinnverteilungs-Optimierung | CV=9.09% | 2025-12-28 |
| HYP-004 | Birthday-Analyse | r=0.39 | 2025-12-28 |
| HYP-006 | Wiederkehrende Gewinnzahlen | 100% Recurrence | 2025-12-28 |
| HYP-010 | Gewinnquoten-Korrelation | 1.3x Winner-Ratio | 2025-12-28 |
| HYP-011 | Zeitliche Zyklen | Feiertags-Effekt | 2025-12-28 |
| HYP-013 | Multi-Einsatz Strategie | Leipzig-Fall | 2025-12-28 |

---

## Empfohlenes Ticket (Typ-10)

```
BESTES PAAR-TICKET (Backtest): 2, 3, 9, 24, 33, 36, 49, 50, 51, 64

Hinweis:
- Dieses Ticket ist im Pair-Backtest das ROI-beste Typ-10 Ticket (trotz negativer ROI).
- 100% Monate mit irgendeinem Gewinn (≠ Profit).
```

---

## Axiome (Grundwahrheiten)

| # | Axiom | Begruendung |
|---|-------|-------------|
| A1 | System hat House-Edge | 50% Redistribution gesetzlich garantiert |
| A2 | Spieler nutzen Dauerscheine | Bundesland-basierte Spielermuster |
| A3 | Spiel muss attraktiv bleiben | Kleine Gewinne regelmaessig noetig |
| A4 | Zahlenpaare sichern kleine Gewinne | Niedrigste GK wird priorisiert |
| A5 | 20 Zahlen pseudo-zufaellig | Jede Zahl muss in Periode erscheinen |
| A6 | Gewinne bundeslandweit verteilt | Pro Ziehung, pro Bundesland |
| A7 | Reset-Zyklen existieren | Bis Jackpot oder Monatsende |

---

## Top-Paare fuer Garantie-Modell

### Global (Co-Occurrence >210x)
```
(9,50):218   (20,36):218   (9,10):217   (32,64):214
(33,49):213  (33,50):211   (24,40):211  (2,3):211
```

### Jackpot-Indikator (GK_10_10)
```
Paar (3,9): 3.28x Lift bei Jackpots!
```

### Typ-2 Garantie (>93% Monate mit Gewinn)
```
(21,42): 93.2% Garantie, 2.72 Gewinne/Monat
(21,68): 93.2%
(26,42): 93.2%
```

---

## Offene Hypothesen

| ID | Hypothese | Prioritaet |
|----|-----------|------------|
| WL-002 | Bundesland-Verteilung | HOCH |
| WL-003 | Reset-Zyklus Erkennung | HOCH |
| WL-004 | Dauerschein-Muster | MITTEL |

---

## Naechste Schritte

1. **Walk-Forward Backtest** - Out-of-Sample Validation (gegen Overfitting)
2. **WL-003: Reset-Zyklus Erkennung** - Pre-GK1 Muster finden
3. **Cross-Game Analyse** - KENO-Lotto-EuroJackpot Korrelationen

---

*Generiert durch Kenobase V2.2.2 - Quoten-Fix & Re-Backtest*

