# Kenobase V2.2 - Finaler Synthese-Report

**Erstellt:** 2025-12-31
**Version:** 2.2.2
**Plans Abgeschlossen:** 3 (59 Tasks total)
**Paradigma:** Axiom-First / Wirtschaftslogik

---

## Executive Summary

Das Kenobase-Projekt hat 59 Tasks in 3 Plans abgeschlossen (28+17+14). Von 24 getesteten Hypothesen wurden **13 bestaetigt**, **5 falsifiziert** und **4 als nicht signifikant** klassifiziert. Die Kernerkenntnisse: Das KENO-System zeigt messbare Muster (Paar-Garantien, Jackpot-Cooldowns, 28-Tage-Zyklen), aber **keine stabile positive ROI** ist mit korrekten festen Quoten erreichbar. Die ROI-Realitaet (House-Edge ~50%) wurde durch Quoten-Korrektur validiert.

---

## 1. Plan-Completion

| Plan | Tasks | Status |
|------|-------|--------|
| kenobase_v2_complete_plan.yaml | 28 | COMPLETE |
| kenobase_axiom_first_ecosystem_plan.yaml | 17 | COMPLETE |
| cycles_exhaustive_analysis_plan_v3.yaml | 14 | COMPLETE |
| **GESAMT** | **59** | **COMPLETE** |

---

## 2. Axiome (A1-A7)

Das **Axiom-First Paradigma** basiert auf 7 wirtschaftlichen Grundannahmen:

| ID | Axiom | Begruendung |
|----|-------|-------------|
| A1 | System hat House-Edge | 50% Redistribution gesetzlich garantiert |
| A2 | Spieler nutzen Dauerscheine | Bundesland-basierte Spielermuster |
| A3 | Spiel muss attraktiv bleiben | Kleine Gewinne regelmaessig noetig |
| A4 | Zahlenpaare sichern kleine Gewinne | Niedrigste GK wird priorisiert |
| A5 | 20 Zahlen pseudo-zufaellig | Jede Zahl muss in Periode erscheinen |
| A6 | Gewinne bundeslandweit verteilt | Pro Ziehung, pro Bundesland |
| A7 | Reset-Zyklen existieren | Bis Jackpot oder Monatsende |

---

## 3. Hypothesen-Bilanz

### 3.1 Bestaetigt (13)

| ID | Hypothese | Evidence | Datum |
|----|-----------|----------|-------|
| **HYP_CYC_001** | 28-Tage-Dauerschein-Zyklus | Typ9: FRUEH +364% vs SPAET -58% (Diff: 422%) | 2025-12-30 |
| HYP-001 | Gewinnverteilungs-Optimierung | CV=9.09% woechentlich | 2025-12-28 |
| HYP-004 | Tippschein-Analyse (Birthday) | r=0.39 | 2025-12-28 |
| HYP-006 | Wiederkehrende Gewinnzahlen | 100% Recurrence | 2025-12-28 |
| HYP-010 | Gewinnquoten-Korrelation | 1.3x Winner-Ratio | 2025-12-28 |
| HYP-011 | Zeitliche Zyklen | Feiertags-Effekt p=0.0001 | 2025-12-28 |
| HYP-013 | Multi-Einsatz Strategie | Leipzig-Fall bestaetigt | 2025-12-28 |
| HOUSE-004 | Near-Miss Constraint | 70x Switch, Chi²>495 | 2025-12-29 |
| WL-001 | Paar-Garantie pro GK | 30/30 Paare >90% | 2025-12-29 |
| WL-003 | Reset-Zyklus nach Jackpot | -66% ROI vs Normal | 2025-12-29 |
| WL-005 | Paar-Gewinn-Frequenz | 100% >=2x/Monat (Typ-2) | 2025-12-29 |
| WL-006 | Jackpot-Einzigartigkeit | 90.9% haben Uniqueness>=0.5 | 2025-12-29 |
| WL-007 | GK-spezifische Paare | GK_9_9: 4.07x Lift | 2025-12-29 |

### 3.2 Falsifiziert (5)

| ID | Hypothese | Grund | Datum |
|----|-----------|-------|-------|
| HYP-002 | Jackpot-Bildungs-Zyklen | CV=0.95, p>0.05 | 2025-12-28 |
| HYP-005 | Dekaden-Affinitaet | 0 signifikante Paare | 2025-12-28 |
| HYP-008 | 111-Prinzip | Keine Korrelation | 2025-12-28 |
| DIST-003 | Sum-Manipulation | Zentraler Grenzwertsatz | 2025-12-29 |
| PRED-001/002/003 | Pre-GK1 Vorhersagen | p>0.05 | 2025-12-29 |

### 3.3 Nicht Signifikant (4)

| ID | Hypothese | Grund | Datum |
|----|-----------|-------|-------|
| HYP_002 | Cooldown High-Wins Unterdrueckung | Sample Size zu gering (1 HW total) | 2025-12-30 |
| HYP_006 | Ticket-Alterung | Trends negativ aber Varianz hoch | 2025-12-30 |
| HYP_CYC_003 | GK-Distribution nach Phase | Chi² p>0.47 alle Typen | 2025-12-30 |
| HYP_CYC_006 | High-Win-Clustering | V2=3, ORIG=2 HW in 1457 Draws | 2025-12-30 |

### 3.4 Offen (2)

| ID | Hypothese | Prioritaet |
|----|-----------|------------|
| WL-002 | Bundesland-Verteilung | HOCH |
| WL-004 | Dauerschein-Muster | MITTEL |

---

## 4. Strategische Erkenntnisse

### 4.1 Kern-Zahlen

```
ABSOLUTE KERN:  3, 24, 49
ERWEITERT:      2, 9, 36, 51, 64
ANTI-BIRTHDAY:  37, 41, 49, 51 (>31)
```

### 4.2 Top-Paare (Co-Occurrence >210x)

```
(9,50):218   (20,36):218   (33,49):213   (2,3):211
(33,50):211  (24,40):211   (3,20):208    (53,64):208
```

### 4.3 Jackpot-Indikator

- **Paar (3,9):** 3.28x Lift bei GK_10_10 (Jackpot)
- **Jackpot-Uniqueness:** 90.9% haben Score >= 0.5

### 4.4 Timing-Strategien

1. **WL-003: Jackpot-Cooldown**
   - NICHT spielen 30 Tage nach GK10_10 Jackpot
   - ROI-Differenz: -66% vs normale Perioden

2. **HYP_CYC_001: 28-Tage-Zyklus**
   - FRUEH-Phase (Tag 1-14): +364% ROI (Typ 9)
   - SPAET-Phase (Tag 15-28): -58% ROI (Typ 9)
   - Differenz: +422%

---

## 5. ROI-Realitaet

**WICHTIG:** Keine stabile positive ROI mit korrekten festen Quoten.

### 5.1 Quoten-Fix (V2.2.2)

- **Single Source of Truth:** `kenobase/core/keno_quotes.py`
- Fruehere ROI-Tabellen waren mit falschen (inflatierten) Quoten berechnet
- Korrekte Quoten: House-Edge ~50%

### 5.2 Aktuelle ROI (2025 OOS Test)

| Keno-Typ | Portfolio-ROI | Beste Ticket ROI | Monate mit Gewinn |
|----------|---------------|------------------|-------------------|
| Typ-2 | -43.21% | -43.21% | 72/74 |
| Typ-6 | -56.42% | -56.42% | 74/74 |
| Typ-8 | -66.66% | -66.66% | 74/74 |
| Typ-10 | -56.99% | -56.99% | 74/74 |

### 5.3 Erkenntnis

- Starke Paare liefern **hohe Gewinnfrequenz** (100% Monate mit Gewinn)
- ROI bleibt **negativ** wegen House-Edge
- Strategie-Mehrwert: **Timing** (wann nicht spielen) statt Zahlen

---

## 6. Datenquellen + Reproduzierbarkeit

### 6.1 Datenquellen

| Datei | Zeitraum | Verwendung |
|-------|----------|------------|
| `data/raw/keno/KENO_ab_2022_bereinigt.csv` | 2022-2025 | Hauptanalyse |
| `Keno_GPTs/Kenogpts_2/Basis_Tab/KENO_ab_2018.csv` | 2018-2024 | Historisch |

### 6.2 Repro-Befehle

```powershell
# Tests ausfuehren (1510 passed)
python -m pytest tests/ -q

# Zyklen-Analyse
python scripts/analyze_cycles_comprehensive.py

# Post-Jackpot Backtest
python scripts/backtest_post_jackpot.py

# Taegliche Empfehlung
python scripts/daily_recommendation.py --type 9
```

### 6.3 Artifacts

| Artifact | Pfad |
|----------|------|
| Hypothesen-Katalog | `AI_COLLABORATION/KNOWLEDGE_BASE/HYPOTHESES_CATALOG.md` |
| System-Status | `AI_COLLABORATION/SYSTEM_STATUS.json` |
| Zyklen-Analyse | `results/cycles_comprehensive_analysis.json` |
| Post-Jackpot | `results/post_jackpot_backtest.json` |

---

## 7. Next Steps

### 7.1 Offene Hypothesen

1. **WL-002: Bundesland-Verteilung** (HOCH)
   - Korrelation Gewinner_BL ~ Bevoelkerung_BL
   - Daten: Pressemitteilungen, Bundesland-Statistik

2. **WL-004: Dauerschein-Muster** (MITTEL)
   - Beliebte Kombinationen identifizieren
   - Birthday-Zahlen, Konsekutive, Geometrische

### 7.2 Cross-Game Analyse (GEPLANT)

| ID | Hypothese |
|----|-----------|
| XG-001 | Lotto-KENO Korrelation |
| XG-002 | EuroJackpot-Timing |
| XG-003 | Multi-Game Reset-Zyklen |

---

## 8. Fazit

Das Kenobase V2.2 Projekt hat das **Axiom-First Paradigma** erfolgreich angewendet:

1. **13 von 24 Hypothesen bestaetigt** - Messbare Muster existieren
2. **House-Edge validiert** - Keine langfristig positive ROI
3. **Timing wichtiger als Zahlen** - Cooldown/Zyklen vermeiden
4. **Paar-Garantien funktionieren** - Aber kein Profit wegen Quoten

**Kernempfehlung:**
- Spielen nur in FRUEH-Phase (Tag 1-14)
- NICHT spielen 30 Tage nach Jackpot
- Typ 9 mit Kern-Zahlen [3, 9, 10, 20, 24, 36, 49, 51, 64]
- Erwarteter ROI: **NEGATIV** (aber besseres Timing als Zufall)

---

*Kenobase V2.2.2 - Finaler Synthese-Report*
*Generated: 2025-12-31*
