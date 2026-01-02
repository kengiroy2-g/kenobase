# STRATEGIE-EMPFEHLUNG: Konsolidierte Synthese

**Stand:** 2025-12-31
**Version:** 1.0.0
**Paradigma:** Axiom-First (keine Pattern-Suche, wirtschaftliche Constraints zuerst)

---

## WARNUNG: Risiko-Hinweis

**WICHTIG:** Dieses Dokument fasst Backtests und Hypothesen zusammen. Es gibt KEINE Garantie fuer zukuenftige Gewinne. KENO hat einen gesetzlichen House-Edge von ~50%.

- Alle ROI-Zahlen sind historische Backtests (2025 OOS)
- Single-Event Risk: Typ-9 Dual-Profit stammt aus EINEM 1000-EUR-Event (2025-07-22)
- Reproduzierbarkeit: Alle Claims mit Repro-Commands verifizierbar

---

## 1. Executive Summary

### Beste Strategie: Typ-9 Dual-Strategy (Birthday-Avoidance)

| Metrik | Wert | Quelle |
|--------|------|--------|
| **ROI 2025 OOS** | +87.5% | `results/dual_strategy_2025_test.json:112` |
| **Win-Days** | 167 / 363 | `results/dual_strategy_2025_test.json:115` |
| **High-Win Events** | 1 (8 Treffer, 1000 EUR) | `results/dual_strategy_2025_test.json:103-108` |
| **Investiert** | 726 EUR (2x 363 Tage @ 1 EUR) | `results/dual_strategy_2025_test.json:113` |
| **Gewonnen** | 1361 EUR | `results/dual_strategy_2025_test.json:114` |

### Kritische Einschraenkung

Der positive ROI beruht auf **einem einzelnen High-Win Event** am 2025-07-22:
- Ticket B traf 8 von 9 Zahlen
- Gewinn: 1000 EUR (Quote Typ-9 bei 8 Treffern)
- Ohne dieses Event: ROI waere negativ

---

## 2. Empfohlene Tickets

### Strategie A: Typ-9 Dual (Beste Performance)

**Ticket A (Original):**
```
[3, 9, 10, 20, 24, 36, 49, 51, 64]
```
- ROI: -47.4%
- Win-Days: 106 / 363

**Ticket B (Birthday-Avoidance V2):**
```
[3, 7, 36, 43, 48, 51, 58, 61, 64]
```
- ROI: +222.3%
- Win-Days: 101 / 363
- High-Win: 1 (8 Treffer @ 2025-07-22)

**Dual kombiniert:**
- ROI: **+87.5%**
- Diversifikation: 127 Tage mit unterschiedlichen Ergebnissen

### Strategie B: Typ-8 Dual (Defensiv)

**Ticket A:**
```
[3, 20, 24, 27, 36, 49, 51, 64]
```

**Ticket B (V2):**
```
[3, 36, 43, 48, 51, 58, 61, 64]
```

**Dual kombiniert:**
- ROI: -57.0%
- Win-Days: 132 / 363

### Strategie C: Typ-10 Dual

**Ticket A:**
```
[2, 3, 9, 10, 20, 24, 36, 49, 51, 64]
```

**Ticket B (V2):**
```
[3, 7, 13, 36, 43, 48, 51, 58, 61, 64]
```

**Dual kombiniert:**
- ROI: -39.8%
- Win-Days: 104 / 363

---

## 3. Bestaetigt Hypothesen (11)

| ID | Hypothese | Evidence | Datum |
|----|-----------|----------|-------|
| **WL-001** | Paar-Garantie pro GK | 30/30 Paare >90% | 2025-12-29 |
| **WL-005** | Paar-Gewinn-Frequenz | 100% >=2x/Monat | 2025-12-29 |
| **WL-006** | Jackpot-Einzigartigkeit | 90.9% Uniqueness>=0.5 | 2025-12-29 |
| **WL-007** | GK-spezifische Paare | GK_9_9: 4.07x Lift | 2025-12-29 |
| **HOUSE-004** | Near-Miss Constraint | 70x Switch | 2025-12-29 |
| **HYP-001** | Gewinnverteilungs-Optimierung | CV=9.09% | 2025-12-28 |
| **HYP-004** | Birthday-Analyse | r=0.39 | 2025-12-28 |
| **HYP-006** | Wiederkehrende Gewinnzahlen | 100% Recurrence | 2025-12-28 |
| **HYP-010** | Gewinnquoten-Korrelation | 1.3x Winner-Ratio | 2025-12-28 |
| **HYP-011** | Zeitliche Zyklen | Feiertags-Effekt | 2025-12-28 |
| **HYP-013** | Multi-Einsatz Strategie | Leipzig-Fall | 2025-12-28 |

---

## 4. Axiome (Wirtschaftliche Constraints)

| ID | Axiom | Begruendung |
|----|-------|-------------|
| **A1** | System hat House-Edge | 50% Redistribution gesetzlich garantiert |
| **A2** | Spieler nutzen Dauerscheine | Bundesland-basierte Spielermuster |
| **A3** | Spiel muss attraktiv bleiben | Kleine Gewinne regelmaessig noetig |
| **A4** | Zahlenpaare sichern kleine Gewinne | Niedrigste GK wird priorisiert |
| **A5** | 20 Zahlen pseudo-zufaellig | Jede Zahl muss in Periode erscheinen |
| **A6** | Gewinne bundeslandweit verteilt | Pro Ziehung, pro Bundesland |
| **A7** | Reset-Zyklen existieren | Bis Jackpot oder Monatsende |

---

## 5. Birthday-Avoidance V2 Tickets

### Kern-Idee

Bei GK1-Events (Jackpots) erscheinen Birthday-Zahlen (1-31) in manchen Analysen unterrepraesentiert. V2 nutzt dies als *Heuristik*.

### Empfohlene Tickets

```python
BIRTHDAY_AVOIDANCE_TICKETS_V2 = {
    8:  [3, 36, 43, 48, 51, 58, 61, 64],
    9:  [3, 7, 36, 43, 48, 51, 58, 61, 64],     # BESTE WAHL
    10: [3, 7, 13, 36, 43, 48, 51, 58, 61, 64],
}
```

### Jackpot-Favoriten (High Frequency bei Jackpots)

```
[51, 58, 61, 7, 36, 13, 43, 15, 3, 48]
```

### Jackpot-Vermeidung

```
[6, 68, 27, 5, 16, 1, 25, 20, 8]
```

---

## 6. Repro-Commands

### Dual-Strategy 2025 Test

```powershell
python scripts/test_dual_2025.py
# Output: results/dual_strategy_2025_test.json
```

### Taegliche Empfehlung

```powershell
# Standard (Typ 8, 9, 10)
python scripts/daily_recommendation.py

# Nur Typ 9 (beste Performance)
python scripts/daily_recommendation.py --type 9

# Dual-Strategie anzeigen
python scripts/daily_recommendation.py --dual

# Mit JSON-Export
python scripts/daily_recommendation.py --save
```

### Super-Model Test 2025

```powershell
python scripts/super_model_synthesis.py
# Output: results/super_model_test_2025.json
```

---

## 7. Rangfolge der Strategien

| Rang | Strategie | ROI 2025 | Risiko | Empfehlung |
|------|-----------|----------|--------|------------|
| 1 | Typ-9 Dual (V2 + Original) | +87.5% | HIGH (Single-Event) | Nur mit Verlusttoleranz |
| 2 | Typ-9 Single (V2) | +222.3% | VERY HIGH | Maximum Varianz |
| 3 | Typ-10 Dual | -39.8% | MEDIUM | Konservativ |
| 4 | Typ-8 Dual | -57.0% | MEDIUM | Defensiv |
| 5 | Nicht spielen | 0% | NONE | House-Edge vermeiden |

---

## 8. Offene Hypothesen

| ID | Hypothese | Prioritaet |
|----|-----------|------------|
| WL-002 | Bundesland-Verteilung | HOCH |
| WL-003 | Reset-Zyklus Erkennung | HOCH |
| WL-004 | Dauerschein-Muster | MITTEL |

---

## 9. Quellen

- `AI_COLLABORATION/SYSTEM_STATUS.json` - Hypothesen-Katalog
- `results/dual_strategy_2025_test.json` - 2025 OOS Backtest
- `docs/SUPER_MODEL.md` - V1 Modell (historisch)
- `scripts/daily_recommendation.py` - Taegliche Empfehlung
- `kenobase/core/keno_quotes.py` - Single Source of Truth fuer Quoten

---

## 10. Fazit

**Axiom-First Erkenntnis:** Die wirtschaftlichen Constraints (House-Edge, Attraktivitaet) begrenzen jede statistische Strategie. Der positive ROI bei Typ-9 Dual beruht auf Varianz (Single High-Win Event), nicht auf systematischem Edge.

**Empfehlung:**
1. Wenn spielen: Typ-9 Dual mit bewusstem Verlustrisiko
2. Besser: Nicht spielen (House-Edge ~50%)
3. Forschung: WL-003 Reset-Zyklus Erkennung koennte den wichtigsten Timing-Vorteil bieten (Jackpot-Cooldown)

---

*Generiert durch Kenobase V2.2 - Axiom-First Synthese*
