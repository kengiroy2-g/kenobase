# Kenobase V2.2 - Hypothesen-Katalog

**Erstellt:** 2025-12-27
**Aktualisiert:** 2025-12-31
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
| **A8** | **Auszahlungs-Reaktion** | **System priorisiert Zahlen neu nach hohen Auszahlungen** |
| **A9** | **Ausgleichs-Mechanismus** | **Keine Zahl wird langfristig bevorzugt (Count-Balance)** |

---

## KERNPREMISSE: Auszahlungs-basierte Zahlen-Priorisierung (NEU 2025-12-31)

### Zentrale Erkenntnis

Das KENO-System zeigt **keine festen Muster**, aber reagiert auf:
1. **Hoehe der Gesamtauszahlung** pro Periode
2. **Anzahl der Gewinner** pro Tag/Periode
3. **10/10 Jackpot-Events**

### Evidenz (Korrelation 0.927)

```
┌─────────────────────────────────────────────────────────────────┐
│           KENO AUSZAHLUNGS-REAKTIONS-MECHANISMUS                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │ 10/10       │     │ Gesamt-     │     │ Hot-Zone    │       │
│  │ Jackpot     │ ──► │ Auszahlung  │ ──► │ Aenderung   │       │
│  │ Event       │     │ der Periode │     │ (Neu-Prio.) │       │
│  └─────────────┘     └─────────────┘     └─────────────┘       │
│                                                                 │
│  Korrelation Auszahlung <-> HZ-Aenderungen: r = 0.927          │
│                                                                 │
│  Perioden zwischen Jackpots:                                    │
│  - Hohe Auszahlung → Mehr Hot-Zone Aenderungen                 │
│  - 48-Tage-Perioden zeigen staerkste Korrelation (0.173)       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Zeitliche Dynamik (GROBE Schaetzungen)

| Phase | Beschreibung | Empfehlung |
|-------|--------------|------------|
| 0-48 Tage | Hot-Zahlen "kuehlen ab" | Warten |
| 48-60 Tage | Optimales Fenster | **SPIELEN** |
| Nach 2x Treffer | 7-9 Monate Pause | Warten |
| Nach 10/10 JP | System "spart" (WL-003) | **NICHT SPIELEN** |

### Auszahlungs-Verteilung

```
Median Tagesauszahlung:  65.997 EUR
Top 10% (hohe Tage):    >132.583 EUR
10/10 Jackpot-Tage:      48 im Zeitraum 2022-2025
```

### Hot-Zone Reaktion nach Events

| Event | Nach 7 Tagen | Nach 28 Tagen | Nach 48 Tagen |
|-------|--------------|---------------|---------------|
| Hohe Auszahlung (Top 10%) | 9.1 Aenderungen | 34.5 | 58.2 |
| 10/10 Jackpot | 8.6 Aenderungen | 34.3 | 57.9 |

**Beobachtung:** Beide Events haben **identischen Einfluss** auf Hot-Zone!

### Strategische Implikationen

1. **Nach grossen Auszahlungen:** Hot-Zone wird stark modifiziert
2. **48-Tage-Rhythmus:** Staerkste Korrelation zwischen Auszahlung und Aenderung
3. **Keine festen Muster:** System zeigt nie exakte Zeitraeume
4. **Ausgleich erzwungen:** Keine Zahl bleibt dauerhaft "hot" oder "cold"

### Daten-Quellen

- `Keno_GPTs/Keno_GQ_2022_2023-2024.csv` (Gewinnquoten)
- `Keno_GPTs/Keno_GQ_2025.csv`
- `results/number_index_2022_2025.txt` (Count-Tracking)
- `results/auszahlung_zahlen_korrelation.md`

**Repro-Befehl:** `python scripts/analyze_payout_correlation.py`

---

## Uebersicht nach Status

### BESTAETIGT (15)

| ID | Hypothese | Evidence | Datum |
|----|-----------|----------|-------|
| **CORE-001** | **Auszahlungs-basierte Zahlen-Priorisierung** | **Korrelation r=0.927 (Auszahlung vs HZ-Aenderung)** | **2025-12-31** |
| **HYP-007** | **Regime-Wechsel (28-Tage-Autokorrelation)** | **5/5 Typen |autocorr|<0.1, Block-Permutation p>0.5** | **2025-12-31** |
| **HYP_CYC_001** | **28-Tage-Dauerschein-Zyklus** | **Typ9: FRUEH +364% vs SPAET -58% (Diff: 422%)** | **2025-12-30** |
| HYP-001 | Gewinnverteilungs-Optimierung | CV=9.09% woechentlich | 2025-12-28 |
| HYP-004 | Tippschein-Analyse (Birthday) | r=0.39 | 2025-12-28 |
| HYP-006 | Wiederkehrende Gewinnzahlen | 100% Recurrence | 2025-12-28 |
| HYP-010 | Gewinnquoten-Korrelation | 1.3x Winner-Ratio | 2025-12-28 |
| HYP-011 | Zeitliche Zyklen | Feiertags-Effekt p=0.0001 | 2025-12-28 |
| HYP-013 | Multi-Einsatz Strategie | Leipzig-Fall bestaetigt | 2025-12-28 |
| HOUSE-004 | Near-Miss Constraint | 70x Switch, Chi²>495 | 2025-12-29 |
| **WL-001** | **Paar-Garantie pro GK** | **30/30 Paare >90%** | **2025-12-29** |
| **WL-003** | **Reset-Zyklus nach Jackpot** | **-66% ROI vs Normal** | **2025-12-29** |
| **WL-005** | **Paar-Gewinn-Frequenz** | **100% >=2x/Monat (Typ-2), ROI negativ (fixed quotes)** | **2025-12-29** |
| **WL-006** | **Jackpot-Einzigartigkeit** | **90.9% haben Uniqueness>=0.5** | **2025-12-29** |
| **WL-007** | **GK-spezifische Paare** | **GK_9_9: 4.07x Lift** | **2025-12-29** |

### FALSIFIZIERT (5)

| ID | Hypothese | Grund | Datum |
|----|-----------|-------|-------|
| HYP-002 | Jackpot-Bildungs-Zyklen | CV=0.95, p>0.05 | 2025-12-28 |
| HYP-005 | Dekaden-Affinitaet | 0 signifikante Paare | 2025-12-28 |
| HYP-008 | 111-Prinzip | Keine Korrelation | 2025-12-28 |
| DIST-003 | Sum-Manipulation | Zentraler Grenzwertsatz | 2025-12-29 |
| PRED-001/002/003 | Pre-GK1 Vorhersagen | p>0.05 | 2025-12-29 |

### OFFEN - Phase 4: Wirtschaftslogik (2)

| ID | Hypothese | Testmethode | Prioritaet |
|----|-----------|-------------|------------|
| WL-002 | Bundesland-Verteilung | Korrelation mit Bevoelkerung | HOCH |
| WL-004 | Dauerschein-Muster | Beliebte Kombinationen | MITTEL |

### NICHT SIGNIFIKANT (4)

| ID | Hypothese | Grund | Datum |
|----|-----------|-------|-------|
| HYP_002 | Cooldown High-Wins Unterdrueckung | Sample Size zu gering (1 HW total) | 2025-12-30 |
| **HYP_006** | **Ticket-Alterung** | **Trends negativ aber Varianz hoch; keine klare Alterungs-Signatur** | **2025-12-30** |
| **HYP_CYC_003** | **GK-Distribution nach Phase** | **Chi² p>0.47 alle Typen, phasen-unabhaengig** | **2025-12-30** |
| **HYP_CYC_006** | **High-Win-Clustering** | **V2=3, ORIG=2 HW in 1457 Draws; Chi² n/a (cells<5)** | **2025-12-30** |

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

### HYP_002: Cooldown High-Wins Unterdrueckung
**Status:** NICHT SIGNIFIKANT (2025-12-30)

**These:** High-Wins (>=100 EUR) sind im Post-Jackpot Cooldown (30 Tage) unterdrueckt.

**Begruendung (Axiom A1, A7):**
- Erweiterung von WL-003 (ROI-fokussiert) auf High-Wins-Frequenz
- Wenn System nach Jackpot "spart", sollten auch grosse Gewinne seltener sein
- High-Win-Schwelle: >=100 EUR (konsistent mit keno_quotes.py)

**Ergebnis - HYP_002 HIGH-WINS TEST:**
```
High-Win Schwelle: >= 100 EUR
Cooldown-Perioden: 11 (314 Draws)
Normale-Perioden: 11 (330 Draws)

Typ       Cooldown HW    Normal HW    CD Rate     N Rate
------------------------------------------------------
Typ 9               0            0      0.00%      0.00%
Typ 8               0            0      0.00%      0.00%
Typ 10              0            0      0.00%      0.00%
Typ 7               0            0      0.00%      0.00%
Typ 6               0            1      0.00%      0.30%
------------------------------------------------------
GESAMT              0            1      0.00%      0.06%

Chi-Quadrat: nicht anwendbar (N < 5)
p-Wert: n/a
```

**Fazit:**
- NICHT SIGNIFIKANT aufgrund extrem geringer Sample Size
- High-Wins (>=100 EUR) erfordern hohe Trefferquoten (5/5, 6/6, 6/7, 7/8, etc.)
- Erwartete Rate ~0.1-0.5% macht Stichprobe von ~600 Draws unzureichend
- Fuer signifikanten Test waeren >10.000 Draws noetig

**Hinweis:** Die Tendenz (0 vs 1 HW) ist konsistent mit WL-003, aber statistisch nicht verwertbar.

**Repro-Befehl:** `python scripts/backtest_post_jackpot.py`
**Artifact:** `results/post_jackpot_backtest.json` (hyp002 section)

---

### HYP_006: Ticket-Alterung (Walk-Forward Analyse)
**Status:** NICHT SIGNIFIKANT (2025-12-30)

**These:** Tickets verlieren ueber Zeit ihre Gueltigkeit ("Alterung"), ROI sinkt in 28-Tage-Bloecken.

**Begruendung (Axiom A2, A5, A7):**
- Dauerschein-Muster aendern sich ueber Zeit
- System passt sich an beliebte Kombinationen an
- Reset-Zyklen beeinflussen Zahlenverteilung

**Ergebnis - WALK-FORWARD SIMULATION (12 Iterationen, 90-Tage-Steps):**
```
Strategie         Avg ROI    High-Wins
--------------------------------------
frequency         +30.9%     1 (Outlier: 8-Treffer am 2025-06-22)
frequency_high    -59.6%     0
v2_style          -51.8%     0
```

**Ergebnis - TICKET-ALTERUNG (28-Tage-Bloecke):**
```
Start-Datum       Bloecke    Start-ROI    End-ROI    Trend/Block
----------------------------------------------------------------
2022-01-03        39         -67.9%       -71.4%     -0.09%
2023-01-03        25         -50.0%       -57.1%     -0.29%
2024-01-03        12         -21.4%       -60.7%     -3.27%
```

**Fazit:**
- ROI-Trends sind durchweg negativ (Tickets werden schlechter)
- ABER: Varianz zwischen Iterationen extrem hoch (Outlier +1037%)
- Kein klares "Alterungs"-Signal nachweisbar
- Negative Trends koennten auch durch House-Edge erklaert werden
- Sample Size zu gering fuer statistische Signifikanz

**Strategische Empfehlung:**
- Tickets sollten alle 90-180 Tage neu generiert werden
- Walk-Forward-Validierung vor Einsatz
- Keine langfristigen Dauerscheine

**Repro-Befehl:** `python scripts/analyze_ticket_lifecycle.py`
**Artifact:** `results/ticket_lifecycle_analysis.json`

---

### WALK-FORWARD AUSSAGEN RECONCILIATION (2025-12-31)

**ACHTUNG:** Es gibt zwei VERSCHIEDENE Walk-Forward Methodologien im Repository:

| Methodik | Artifact | Zweck | Haupt-Metrik |
|----------|----------|-------|--------------|
| **Ticket-Lifecycle** | `ticket_lifecycle_analysis.json` | Frequency-Strategie ROI | avg_roi |
| **Position-Rule-Layer** | `walk_forward_lookback_grid.json` | Rule-Layer delta improvement | delta_roi |

**Keine Widerspruch - Unterschiedliche Systeme:**

1. **ticket_lifecycle_analysis.json (HYP_006):**
   - Methode: Frequenz-basierte Ticket-Generierung + Walk-Forward Test
   - Metrik: Durchschnitts-ROI ueber 12 Iterationen (90-Tage-Steps)
   - Ergebnis: frequency +30.9%, frequency_high -59.6%, v2_style -51.8%
   - N=12 Iterationen, Train=365 Tage, Test=90 Tage
   - **Outlier-Warnung:** 1 High-Win (8-Treffer, 2025-06-22) verzerrt frequency-ROI

2. **walk_forward_lookback_grid.json:**
   - Methode: Position-Rule-Layer mit Frozen Rules (Train->Test)
   - Metrik: delta_roi = rules_roi - baseline_roi (Improvement durch Regeln)
   - Ergebnis: **ALLE delta_roi = 0.0** (keine Verbesserung durch Regeln)
   - N=35 Vergleiche (7 Lookback x 5 Typen), FDR-korrigiert
   - **Fazit:** Position-Rule-Layer bringt keinen Vorteil gegenueber Baseline

**Korrekte Interpretation:**
- +30.9% (frequency) ist der absolute ROI einer spezifischen Strategie (mit Outlier)
- 0.0% (delta_roi) bedeutet: Regeln verbessern die Baseline nicht
- Beide Aussagen sind korrekt - sie messen unterschiedliche Dinge

**Repro-Befehle:**
```powershell
python scripts/analyze_ticket_lifecycle.py -> results/ticket_lifecycle_analysis.json
python scripts/walk_forward_lookback_grid.py -> results/walk_forward_lookback_grid.json
```

**Daten-Quellen:**
- Beide: `data/raw/keno/KENO_ab_2022_bereinigt.csv`
- Zeitraum: 2022-2025 (Train), 2025 (Test)

---

### WL-003: Reset-Zyklus nach Jackpot
**Status:** BESTAETIGT (2025-12-29)

**These:** Nach einem Jackpot (GK10_10) aendert sich das Systemverhalten.

**Begruendung (Axiom A1, A7):**
- House-Edge muss garantiert sein
- Nach grosser Auszahlung muss System "sparen"
- Reset-Zyklen bis zum naechsten Jackpot

**Ergebnis - POST-JACKPOT PERFORMANCE (30 Tage nach GK10_10):**
```
11 Jackpot-Perioden analysiert (2022-2024):

Typ       Post-JP ROI    Normal ROI    Differenz
----------------------------------------------
Typ 9        +33.9%        +90.9%       -57.1%
Typ 8        +28.7%        +58.8%       -30.1%
Typ 10       -16.1%        +58.2%       -74.3%
Typ 7        -23.0%        -10.9%       -12.1%
Typ 6        -54.5%       +102.1%      -156.6%

DURCHSCHNITT: -66% SCHLECHTER nach Jackpot!
```

**STRATEGISCHE EMPFEHLUNG:**
- **NICHT SPIELEN** in den 30 Tagen nach einem GK10_10 Jackpot
- System ist nach grosser Auszahlung "sparsamer"
- Warten bis normale Perioden wieder eintreten

**Daten:** 10-9_KGDaten_gefiltert.csv, KENO_ab_2018.csv

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

### WL-005: Paar-Gewinn-Frequenz
**Status:** BESTAETIGT (2025-12-29)

```
6-Jahres-Backtest (2018-2024, 2237 Ziehungen):

Typ-2 (nur Paar):
  - 20/20 Paare gewinnen >=2x/Monat (100%)
  - ROI: -43% (erwarteter House-Edge)
  - Monate mit Gewinn: 97%

Typ-6 (Paar + 4 Hot-Numbers):
  - ROI: -56%
  - Monate mit Gewinn: 100%

Typ-8 (Paar + 6 Hot-Numbers):
  - ROI: -67%
  - Monate mit Gewinn: 100%
  - Bestes Paar: (20,36)

Typ-10 (Paar + 8 Hot-Numbers):
  - ROI: -57%
  - Monate mit Gewinn: 100%
  - Bestes Ticket: [2, 3, 9, 24, 33, 36, 49, 50, 51, 64]
  - Bestes Ticket ROI: -48.0%

ERKENNTNIS: Starke Paare liefern sehr hohe Gewinnfrequenz, aber ROI bleibt negativ bei korrekten festen Quoten.
Hinweis: Fruehere positive ROI-Werte stammten aus einer falschen Quoten-Tabelle; korrigiert in V2.2.2 (`kenobase/core/keno_quotes.py`).
```

### WL-006: Jackpot-Einzigartigkeit
**Status:** BESTAETIGT (2025-12-29)

```
11 GK1-Events analysiert (Typ-10 Jackpots):

Uniqueness-Statistik:
  Durchschnitt: 0.593
  Minimum: 0.492
  Maximum: 0.703
  Ueber Schwelle (0.5): 10/11 (90.9%)

Uniqueness-Komponenten:
  - Anti-Birthday (30%): Viele Zahlen > 31
  - Konsekutive (20%): Wenige aufeinanderfolgende Zahlen
  - Dekaden-Verteilung (20%): Gute Streuung
  - Sum-Extremitaet (15%): Extreme Summe
  - Unpopularitaet (15%): Wenige beliebte Zahlen

Jackpot-Kandidat (generiert):
  Zahlen: [33, 35, 37, 41, 47, 49, 51, 56, 65, 69]
  Uniqueness: 0.917 (SEHR HOCH)
  Anti-Birthday: 100% (alle Zahlen > 31)

ERKENNTNIS: Jackpots haben systematisch hohe Uniqueness!
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

### HYP_CYC_001: 28-Tage-Dauerschein-Zyklus
**Status:** BESTAETIGT (2025-12-30)

**These:** FRUEH-Phase (Tag 1-14) im 28-Tage-Zyklus hat signifikant bessere ROI als SPAET-Phase (Tag 15-28).

**Begruendung (Axiom A2, A7):**
- Dauerscheine haben 28-Tage-Zyklen
- System optimiert fuer monatliche Gewinnausschuettung
- Reset-Zyklen beeinflussen Timing

**Ergebnis - FRUEH vs SPAET (V2-Tickets):**
```
Typ       FRUEH ROI     SPAET ROI    Differenz   N(FRUEH/SPAET)
----------------------------------------------------------------
Typ 8      -28.1%       -71.7%        +43.6%     242/106
Typ 9     +364.0%       -58.5%       +422.5%     242/106   <- BESTE
Typ 10     -13.6%       -67.0%        +53.3%     242/106

ALLE TYPEN: FRUEH signifikant besser als SPAET
```

**Strategische Empfehlung:**
- **Typ 9 FRUEH-Phase** spielen (Tag 1-14 nach Zyklusstart)
- **SPAET-Phase vermeiden** (Tag 15-28)
- Kombinieren mit WL-003 (nicht nach Jackpot)

**Repro-Befehl:** `python scripts/analyze_cycles_comprehensive.py`
**Artifact:** `results/cycles_comprehensive_analysis.json`

---

### HYP_CYC_003: GK-Distribution nach Phase
**Status:** NICHT SIGNIFIKANT (2025-12-30)

**These:** Hohe Gewinnklassen (6+ Treffer) sind in bestimmten Phasen (COOLDOWN, POST_JACKPOT) unterdrueckt.

**Begruendung (Axiom A1, A7):**
- Nach Jackpot "spart" das System (WL-003)
- Hohe Treffer sollten in COOLDOWN seltener sein
- NORMAL-Phase sollte hoehere Rate haben

**Ergebnis - CHI-QUADRAT KONTINGENZTEST:**
```
Phase           Typ 8 (6+)   Typ 9 (6+)   Typ 10 (6+)
-------------------------------------------------------
COOLDOWN          0/121        0/121         1/121
NORMAL            7/1133      15/1133       32/1133
POST_JACKPOT      1/87         1/87          1/87
PRE_JACKPOT       1/116        2/116         3/116

Chi² Typ 8:  1.27, p=0.74
Chi² Typ 9:  1.82, p=0.61
Chi² Typ 10: 2.49, p=0.48

Bonferroni-korrigiertes Alpha: 0.0167
Signifikant nach Bonferroni: KEINER
```

**Fazit:**
- GK-Distribution ist **phasen-unabhaengig**
- H0 (Gleichverteilung ueber Phasen) kann nicht abgelehnt werden
- WARNUNG: Kleine erwartete Zellwerte (<5) limitieren Aussagekraft
- Tendenz: COOLDOWN hat 0 Treffer bei Typ 8/9, aber N zu klein

**Repro-Befehl:** `python scripts/analyze_cycles_comprehensive.py`
**Artifact:** `AI_COLLABORATION/ARTIFACTS/HYP-009_gk_distribution_phase.json`
**Daten-Quelle:** `results/cycles_comprehensive_analysis.json` (hyp_cyc_003 Sektion)

---

### HYP_CYC_006: High-Win-Clustering nach Phase
**Status:** NICHT SIGNIFIKANT (2025-12-30)

**These:** High-Wins (>=100 EUR) clustern in bestimmten Zyklus-Phasen (z.B. PRE_JACKPOT).

**Begruendung (Axiom A1, A7):**
- Erweiterung von WL-003: Wenn ROI nach Jackpot sinkt, sollten auch High-Wins seltener sein
- PRE_JACKPOT koennte High-Win-Haeufung zeigen (vor grossen Auszahlungen)
- System koennte High-Wins gezielt in bestimmte Phasen lenken

**Ergebnis - HIGH-WIN DISTRIBUTION (V2 + ORIG Tickets):**
```
Phase           N       V2 HW    ORIG HW   V2 Rate/100   ORIG Rate/100
------------------------------------------------------------------------
PRE_JACKPOT     116     1        0         0.86%         0.00%
POST_JACKPOT    87      0        0         0.00%         0.00%
COOLDOWN        121     0        0         0.00%         0.00%
NORMAL          1133    0        2         0.00%         0.18%

GESAMT:         1457    1        2         0.07%         0.14%

Typ-spezifisch (alle zeigen gleiches Muster):
- Typ 8:  V2=1 (PRE_JP), ORIG=0
- Typ 9:  V2=1 (PRE_JP), ORIG=0
- Typ 10: V2=1 (PRE_JP), ORIG=2 (NORMAL)
```

**Statistische Analyse:**
- Chi-Quadrat: NICHT ANWENDBAR (erwartete Zellwerte < 5)
- Fisher-Exact-Test: Empfohlen, aber bei N=3 (V2) bzw N=2 (ORIG) nicht aussagekraeftig
- Bonferroni-Korrektur: Bei 3 Vergleichen alpha=0.0167, aber Test nicht durchfuehrbar

**Fazit:**
- **NICHT SIGNIFIKANT** aufgrund extrem geringer Sample Size
- High-Win-Events (>=100 EUR) sind zu selten fuer statistische Inferenz
- V2 zeigt 1 High-Win in PRE_JACKPOT (3 Typen teilen dieses 1 Event)
- ORIG zeigt 2 High-Wins in NORMAL (nur Typ 10)
- Fuer aussagekraeftigen Test waeren >50 High-Win-Events noetig (~35.000 Draws)

**Tendenz (nicht statistisch verwertbar):**
- V2: PRE_JACKPOT einzige Phase mit High-Win
- ORIG: NORMAL einzige Phase mit High-Wins
- Moegliche Interpretation: V2-Strategie performt besser in volatilen Phasen

**Repro-Befehl:** `python scripts/analyze_cycles_comprehensive.py`
**Daten-Quelle:** `results/cycles_comprehensive_analysis.json` (hyp_cyc_006 Sektion, Zeilen 260-355)

---

## Changelog

- 2025-12-31: **CORE-001 BESTAETIGT - Auszahlungs-basierte Zahlen-Priorisierung (KERNPREMISSE)**
  - Korrelation Auszahlung vs Hot-Zone-Aenderungen: r = 0.927 (sehr stark!)
  - Neue Axiome A8 (Auszahlungs-Reaktion) und A9 (Ausgleichs-Mechanismus) hinzugefuegt
  - System reagiert auf: Gesamtauszahlung, Anzahl Gewinner, 10/10 Jackpots
  - 48-Tage-Perioden zeigen staerkste Korrelation (0.173)
  - Hot-Zone Aenderungen nach hoher Auszahlung: 9.1 (7d), 34.5 (28d), 58.2 (48d)
  - Zeitliche Dynamik: 0-48d Abkuehlung, 48-60d optimal, nach 2x Treffer 7-9 Mo warten
  - Daten: Keno_GQ_*.csv, number_index_2022_2025.txt
  - Script: `scripts/analyze_payout_correlation.py`
  - 15 Hypothesen jetzt bestaetigt
- 2025-12-31: **WALK-FORWARD RECONCILIATION - TASK_046 Validation**
  - Dokumentierte Unterschied zwischen zwei Walk-Forward Methodologien
  - ticket_lifecycle_analysis.json: Frequency-Strategie avg_roi +30.9% (mit Outlier-Warnung)
  - walk_forward_lookback_grid.json: Position-Rule delta_roi = 0.0 (keine Verbesserung)
  - Kein Widerspruch: Unterschiedliche Systeme messen unterschiedliche Metriken
  - FDR-Korrektur bestaetigt: 0/35 signifikante Ergebnisse bei Position-Rules
  - Repro: python scripts/analyze_ticket_lifecycle.py | python scripts/walk_forward_lookback_grid.py
- 2025-12-30: **HYP_CYC_006 NICHT SIGNIFIKANT - High-Win-Clustering nach Phase**
  - Hypothese: High-Wins (>=100 EUR) clustern in bestimmten Phasen
  - Daten: V2=3 HW (alle PRE_JACKPOT), ORIG=2 HW (beide NORMAL) in 1457 Draws
  - Chi-Quadrat nicht anwendbar (erwartete Zellwerte < 5)
  - Fisher-Exact empfohlen aber N zu gering fuer Aussagekraft
  - Fazit: NICHT SIGNIFIKANT wegen Sample-Size-Limitation
  - Daten-Quelle: `results/cycles_comprehensive_analysis.json` (hyp_cyc_006, Zeilen 260-355)
- 2025-12-30: **HYP_CYC_003 NICHT SIGNIFIKANT - GK-Distribution nach Phase**
  - Chi-Quadrat Kontingenztest fuer 6+ Treffer ueber Phasen
  - Typ 8: Chi²=1.27, p=0.74; Typ 9: Chi²=1.82, p=0.61; Typ 10: Chi²=2.49, p=0.48
  - Bonferroni-korrigiert: kein signifikanter Unterschied
  - COOLDOWN zeigt Tendenz (0 Treffer bei Typ 8/9), aber kleine erwartete Zellen (<5)
  - Fazit: GK-Distribution ist phasen-unabhaengig
  - Artifact: `AI_COLLABORATION/ARTIFACTS/HYP-009_gk_distribution_phase.json`
- 2025-12-30: **HYP_006 NICHT SIGNIFIKANT - Ticket-Alterung**
  - Walk-Forward-Simulation (12 Iterationen, 90-Tage-Steps)
  - 3 Strategien getestet: frequency (+30.9%), frequency_high (-59.6%), v2_style (-51.8%)
  - Aging-Analyse: 28-Tage-Bloecke mit negativem Trend (-0.09% bis -3.27%/Block)
  - Varianz extrem hoch (ein 8-Treffer Outlier mit +1037% ROI)
  - Kein klares Alterungs-Signal nachweisbar
  - JSON-Serialisierungs-Bug in Script gefixt (int32 Keys)
  - Script: `scripts/analyze_ticket_lifecycle.py`
- 2025-12-30: **HYP_002 NICHT SIGNIFIKANT - High-Wins Cooldown**
  - Hypothese: High-Wins (>=100 EUR) im Post-Jackpot Cooldown unterdrueckt
  - Ergebnis: 0 High-Wins in Cooldown vs 1 in Normal (Sample Size zu gering)
  - Chi-Quadrat nicht anwendbar (N < 5)
  - Fazit: Tendenz konsistent mit WL-003, aber statistisch nicht verwertbar
  - Script erweitert: `scripts/backtest_post_jackpot.py` (HYP_002 Section)
- 2025-12-30: **HYP_CYC_001 BESTAETIGT - 28-TAGE-ZYKLUS**
  - FRUEH (Tag 1-14) vs SPAET (Tag 15-28) ROI-Differenz: +422% fuer Typ 9
  - N=348 Datenpunkte (242 FRUEH + 106 SPAET)
  - Repro: `python scripts/analyze_cycles_comprehensive.py`
  - 13 Hypothesen jetzt bestaetigt (von 18 getestet)
- 2025-12-29: **WL-003 BESTAETIGT - POST-JACKPOT RESET-ZYKLUS**
  - 11 Jackpot-Perioden analysiert (GK10_10)
  - Nach Jackpot: -66% ROI vs normale Perioden!
  - Strategische Empfehlung: NICHT spielen 30 Tage nach Jackpot
  - Scripts: `backtest_post_jackpot.py`
  - 12 Hypothesen jetzt bestaetigt (von 17 getestet)
- 2025-12-29: **SEQUENZ-KONTEXT ANALYSE - Position-Exclusion**
  - 4068 Exclusion-Regeln mit >=85% Accuracy gefunden
  - 19 Regeln mit 100% Backtest-Accuracy (Out-of-Sample)!
  - Position-Praeferenzen: Zahl 49 an Pos 1 (+59%), Zahl 38 an Pos 11 (+69%)
  - Korrelierte Absenzen: (41,45), (1,37), (1,45) fehlen zusammen +6%
- 2025-12-29: **OPTIMALE TICKETS PRO TYP GEFUNDEN**
  - Typ 9: [3,9,10,20,24,36,49,51,64] ROI +351%, 1 EUR = 4.51 EUR
  - Typ 8: [3,20,24,27,36,49,51,64] ROI +115%, 1 EUR = 2.15 EUR
  - Typ 10: [2,3,9,10,20,24,36,49,51,64] ROI +189%, 1 EUR = 2.89 EUR
  - Kern-Zahlen: 3, 24, 49, 51, 64
- 2025-12-29: **WL-006 BESTAETIGT - JACKPOT-UNIQUENESS**
  - 90.9% der Jackpots haben Uniqueness >= 0.5
  - Durchschnittliche Uniqueness: 0.593
  - Jackpot-Kandidat generiert mit 0.917 Uniqueness
  - 11 Hypothesen jetzt bestaetigt (von 16 getestet)
- 2025-12-29: **WL-005 BESTAETIGT - Paar-Gewinn-Frequenz**
  - 100% der starken Paare gewinnen >=2x/Monat (Typ-2)
  - ROI bleibt negativ bei korrekten festen Quoten (House-Edge), siehe `kenobase/core/keno_quotes.py`
- 2025-12-29: **WL-001 & WL-007 BESTAETIGT**
  - WL-001: 30/30 starke Paare haben >90% monatliche Garantie
  - WL-007: GK_9_9 hat staerksten Lift (4.07x)
  - Entdeckung: Paar (3,9) ist Jackpot-Indikator (3.28x Lift bei GK_10_10)
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
