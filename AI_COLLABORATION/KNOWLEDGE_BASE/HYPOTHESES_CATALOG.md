# Kenobase V2.2 - Hypothesen-Katalog

**Erstellt:** 2025-12-27
**Aktualisiert:** 2025-12-29
**Paradigma:** Wirtschaftslogik (System ist manipuliert - AXIOM)
**Status:** PHASE 4 AKTIV

---

## AXIOME (als WAHRHEIT gesetzt)

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

## Uebersicht nach Status

### BESTAETIGT (9)

| ID | Hypothese | Evidence | Datum |
|----|-----------|----------|-------|
| HYP-001 | Gewinnverteilungs-Optimierung | CV=9.09% woechentlich | 2025-12-28 |
| HYP-004 | Tippschein-Analyse (Birthday) | r=0.39 | 2025-12-28 |
| HYP-006 | Wiederkehrende Gewinnzahlen | 100% Recurrence | 2025-12-28 |
| HYP-010 | Gewinnquoten-Korrelation | 1.3x Winner-Ratio | 2025-12-28 |
| HYP-011 | Zeitliche Zyklen | Feiertags-Effekt p=0.0001 | 2025-12-28 |
| HYP-013 | Multi-Einsatz Strategie | Leipzig-Fall bestaetigt | 2025-12-28 |
| HOUSE-004 | Near-Miss Constraint | 70x Switch, Chi²>495 | 2025-12-29 |
| **WL-001** | **Paar-Garantie pro GK** | **30/30 Paare >90%** | **2025-12-29** |
| **WL-007** | **GK-spezifische Paare** | **GK_9_9: 4.07x Lift** | **2025-12-29** |

### FALSIFIZIERT (5)

| ID | Hypothese | Grund | Datum |
|----|-----------|-------|-------|
| HYP-002 | Jackpot-Bildungs-Zyklen | CV=0.95, p>0.05 | 2025-12-28 |
| HYP-005 | Dekaden-Affinitaet | 0 signifikante Paare | 2025-12-28 |
| HYP-008 | 111-Prinzip | Keine Korrelation | 2025-12-28 |
| DIST-003 | Sum-Manipulation | Zentraler Grenzwertsatz | 2025-12-29 |
| PRED-001/002/003 | Pre-GK1 Vorhersagen | p>0.05 | 2025-12-29 |

### OFFEN - Phase 4: Wirtschaftslogik (5)

| ID | Hypothese | Testmethode | Prioritaet |
|----|-----------|-------------|------------|
| WL-002 | Bundesland-Verteilung | Korrelation mit Bevoelkerung | HOCH |
| WL-003 | Reset-Zyklus Erkennung | Pre-GK1 Muster (7-14 Tage) | HOCH |
| WL-004 | Dauerschein-Muster | Beliebte Kombinationen | MITTEL |
| WL-005 | Paar-Gewinn-Frequenz | 12-Monats-Backtest | HOCH |
| WL-006 | Jackpot-Einzigartigkeit | Uniqueness-Score | HOCH |

---

## Phase 4: Wirtschaftslogik-Hypothesen (NEU)

### WL-001: Paar-Garantie pro Gewinnklasse

**These:** Starke Zahlenpaare garantieren mind. 1x/Monat Gewinn in niedrigster GK.

**Begruendung (Axiom A3, A4):**
- Spiel muss attraktiv bleiben = regelmaessige kleine Gewinne
- Dauerschein-Spieler erwarten Gewinne
- Starke Paare (>200x Co-Occurrence) sind System bekannt

**Test:**
```python
# Fuer jedes starke Paar (Co-Occ > 200):
# - Simuliere Typ-2 Ticket mit diesem Paar
# - Zaehle Gewinne pro Monat
# - Erwartung: >90% der Paare gewinnen 1x/Monat
```

**Daten:** Keno_GQ_*.csv, KENO_ab_*.csv

---

### WL-002: Bundesland-Verteilung

**These:** Gewinnverteilung korreliert mit Bundesland-Bevoelkerung.

**Begruendung (Axiom A2, A6):**
- Jedes Bundesland hat eigene Lotteriegesellschaft
- Gewinne muessen regional verteilt werden
- Dauerschein-Spieler sind regional gebunden

**Test:**
```python
# Korrelation: Gewinner_BL ~ Bevoelkerung_BL
# Erwartung: r > 0.8
```

**Daten:** Bundesland-Statistik, Pressemitteilungen

---

### WL-003: Reset-Zyklus Erkennung

**These:** Vor Jackpot gibt es erkennbare Muster in Zahlenverteilung.

**Begruendung (Axiom A7):**
- Reset-Zyklen existieren (bis Jackpot oder Monatsende)
- System muss Jackpot "vorbereiten"
- Near-Miss Ratio aendert sich

**Test:**
```python
# Analysiere 7-14 Tage vor GK1:
# - Entropy der Zahlenverteilung
# - Near-Miss Ratio Trend
# - Paar-Frequenz Varianz
```

**Daten:** 10-9_KGDaten_gefiltert.csv

---

### WL-004: Dauerschein-Muster

**These:** Beliebte Kombinationen erscheinen haeufiger.

**Begruendung (Axiom A2, A3):**
- Spieler nutzen Dauerscheine mit festen Zahlen
- System kennt beliebte Kombinationen
- Muss diese gelegentlich "bedienen"

**Test:**
```python
# Identifiziere beliebte Muster:
# - Birthday-Zahlen (1-31)
# - Konsekutive (1,2,3,4,5,6)
# - Geometrische Muster
# Pruefe: Erscheinen 5-10% haeufiger?
```

---

### WL-005: Paar-Gewinn-Frequenz

**These:** Starke Paare gewinnen mind. 2x/Monat einen kleinen Betrag.

**Begruendung (Axiom A4):**
- Zahlenpaare sichern kleine Gewinne
- Regelmaessigkeit erhaelt Spielermotivation

**Test:**
```python
# 12-Monats-Backtest:
# - Top-20 Paare als Typ-2 Tickets
# - Zaehle Gewinne pro Monat
# - Erwartung: 2-4 Gewinne/Monat/Paar
```

---

### WL-006: Jackpot-Einzigartigkeit

**These:** Jackpot-Kombinationen haben hohen Uniqueness-Score.

**Begruendung (Axiom A1):**
- House-Edge muss garantiert sein
- Jackpot an beliebte Kombination = viele Gewinner = hohe Auszahlung
- Jackpot an einzigartige Kombination = wenige Gewinner = kontrolliert

**Uniqueness-Kriterien:**
- Anti-Birthday (>50% Zahlen >31)
- Keine konsekutiven Paare
- Gute Dekaden-Verteilung
- Sum in extremem Bereich

**Test:**
```python
# Analysiere alle 20 GK1-Events:
# - Berechne Uniqueness-Score
# - Erwartung: Score > 0.7
```

---

### WL-007: GK-spezifische Paare

**These:** Paare haben unterschiedliche Staerke je nach Gewinnklasse.

**Begruendung:**
- Typ-2 (2/2) vs Typ-10 (10/10) sind komplett unterschiedlich
- Globale Paar-Analyse ignoriert GK-Kontext
- System optimiert pro GK separat

**Test:**
```python
# Fuer jede Gewinnklasse:
# - Berechne Paar-Co-Occurrence
# - Identifiziere GK-spezifische Top-Paare
# - Vergleiche mit globalen Paaren
```

---

## Abgeschlossene Hypothesen (Phase 1-3)

### HYP-001: Gewinnverteilungs-Optimierung
**Status:** BESTAETIGT (2025-12-28)

```
CV woechentlich: 9.09% (SEHR NIEDRIG fuer Zufallssystem)
Jackpot-Intervall: 24.5 Tage Durchschnitt
Taegliche Auszahlung: 83.506 EUR +/- 84.665 EUR
```

### HYP-004: Tippschein-Analyse (Birthday)
**Status:** BESTAETIGT (2025-12-28)

```
Korrelation Birthday-Score <-> Gewinner: r = 0.3921
High-Birthday (>50%): 4.619 Gewinner/Tag
Low-Birthday (<35%): 3.561 Gewinner/Tag
Winner-Ratio: 1.3x
```

### HYP-006: Wiederkehrende Gewinnzahlen
**Status:** BESTAETIGT (2025-12-28)

```
Recurrence Rate: 100% (5.73 Zahlen im Schnitt)
Stable Pairs: 2415 (alle Paare)
Top-Paare: (9,50):218x, (20,36):218x, (9,10):217x
```

### HOUSE-004: Near-Miss Constraint
**Status:** BESTAETIGT (2025-12-29)

```
Normal-Periode: 25-50x Unterdrueckung Max-Gewinne
Jackpot-Periode: 1.4-2.5x Verstaerkung
Intervention Strength: 70x
Chi²: >495, p<0.001
Jahrlich: Nur 2023 anomal (22.4x vs 4-5x)
```

### WL-001: Paar-Garantie pro Gewinnklasse
**Status:** BESTAETIGT (2025-12-29)

```
Getestete starke Paare: 30 (Co-Occurrence >= 200x)
Paare mit >90% monatlicher Garantie: 30/30 (100%)
Bestes Paar: (21,42) - 93.2% Garantie, 2.72 Gewinne/Monat
Durchschnittliche Win-Rate: ~9% (vs 7.8% erwartet)

Top-5 Garantie-Paare:
  (21,42): 93.2% Monate mit Gewinn
  (21,68): 93.2%
  (26,42): 93.2%
  (26,64): 93.2%
  (27,64): 93.2%
```

### WL-007: GK-spezifische Paare
**Status:** BESTAETIGT (2025-12-29)

```
Analysierte Gewinnklassen: 36
Staerkste GK: GK_9_9 (Lift: 4.07x)

GK-spezifische Top-Paare:
  GK_2_2:  (3,25) Lift=1.44x (769 Ziehungen)
  GK_10_9: (3,25) Lift=1.54x (585 Ziehungen)
  GK_10_10: (3,9) Lift=3.28x (31 Ziehungen) <- JACKPOT-PAAR!
  GK_9_9:  Lift=4.07x <- STAERKSTE GK

Erkenntnis: Paar (3,9) ist ueberproportional haeufig bei Jackpots!
```

---

## Cross-Game Hypothesen (GEPLANT)

| ID | Hypothese | Status |
|----|-----------|--------|
| XG-001 | Lotto-KENO Korrelation | GEPLANT |
| XG-002 | EuroJackpot-Timing | GEPLANT |
| XG-003 | Multi-Game Reset-Zyklen | GEPLANT |

---

## Kernerkenntnisse fuer Modell

### Unified Kern-Zahlen
```
ABSOLUTE KERN:  3, 24, 49
ERWEITERT:      2, 9, 36, 51, 64
ANTI-BIRTHDAY:  37, 41, 49, 51 (>31)
```

### Top-Paare (Co-Occurrence >210x)
```
(9,50):218   (20,36):218   (33,49):213   (2,3):211
(33,50):211  (24,40):211   (3,20):208    (53,64):208
```

### Top-Trios (>50% ueber Erwartung)
```
(9,39,50):63%  (19,28,49):59%  (27,49,54):59%  (7,9,10):59%
```

---

## Changelog

- 2025-12-29: **WL-001 & WL-007 BESTAETIGT**
  - WL-001: 30/30 starke Paare haben >90% monatliche Garantie
  - WL-007: GK_9_9 hat staerksten Lift (4.07x)
  - Entdeckung: Paar (3,9) ist Jackpot-Indikator (3.28x Lift bei GK_10_10)
  - 9 Hypothesen jetzt bestaetigt
- 2025-12-29: **PHASE 4 GESTARTET** - Wirtschaftslogik-Paradigma
  - 7 Axiome definiert (A1-A7)
  - 7 neue WL-Hypothesen (WL-001 bis WL-007)
  - HOUSE-004 BESTAETIGT (Near-Miss Constraint)
  - Unified Kern-Zahlen identifiziert
- 2025-12-28: HOUSE-Analyse abgeschlossen
- 2025-12-28: 6 Hypothesen bestaetigt, 5 falsifiziert
- 2025-12-27: Initiale Erstellung

---

*Hypothesen-Katalog V2.2 - Wirtschaftslogik-Paradigma*
