# MASTER PLAN: Phase 4 - Wirtschaftslogik-Modell

**Version:** 2.0
**Erstellt:** 2025-12-29
**Status:** BEREIT FUER LOOP
**Geschaetzte Dauer:** 40-50 Stunden

---

## 1. EXECUTIVE SUMMARY

### 1.1 Vision

Ein vollstaendiges Vorhersage-System entwickeln, das:
1. **Garantierte kleine Gewinne** (100-500 EUR) pro Monat ermoeglicht
2. **Jackpot-Kandidaten** mit hoher Wahrscheinlichkeit identifiziert
3. **Reset-Zyklen** erkennt fuer optimales Timing
4. **Cross-Game Muster** zwischen KENO, Lotto und EuroJackpot nutzt
5. **Bundesland-spezifische** Optimierungen ermoeglicht

### 1.2 Paradigmenwechsel

```
ALT:  "Beweise dass das System manipuliert ist"
NEU:  "System IST manipuliert - finde die Regeln"
```

### 1.3 Kernfrage

> Wenn das System Zahlen so waehlt, dass der House-Edge garantiert ist,
> gleichzeitig aber das Spiel attraktiv bleibt - welche REGELN folgt es?

---

## 2. AXIOME (Grundwahrheiten)

Diese werden NICHT getestet - sie sind die Basis aller Analysen.

### A1: House-Edge Garantie
```
Das System MUSS 50% der Einnahmen behalten.
-> Auszahlung ist NICHT zufaellig, sondern gesteuert.
-> Woechentliche CV von nur 9.09% bestaetigt dies.
```

### A2: Dauerschein-Dominanz
```
Grossteil der Spieler nutzt Dauerscheine (Abos).
-> System kennt die gespielten Zahlen VOR der Ziehung.
-> Bundesland-spezifische Spielermuster existieren.
```

### A3: Attraktivitaets-Erhaltung
```
Spiel MUSS attraktiv bleiben fuer Spielerbindung.
-> Regelmaessige kleine Gewinne sind NOTWENDIG.
-> "Fast gewonnen" Erlebnisse werden produziert (Near-Miss).
```

### A4: Paar-Garantie
```
Zahlenpaare sichern kleine Gewinne in niedrigster Gewinnklasse.
-> Starke Paare (>200x Co-Occurrence) werden "bedient".
-> Jeder Dauerschein-Spieler gewinnt ~1x/Monat klein.
```

### A5: Pseudo-Zufaelligkeit
```
20 Zahlen verhalten sich SCHEINBAR zufaellig.
-> Jede Zahl MUSS in einem Zeitraum erscheinen.
-> Keine Zahl darf "zu lange" fehlen (Verdacht).
-> Langzeit-Frequenz naehert sich 28.57% (20/70).
```

### A6: Regionale Verteilung
```
Gewinne werden bundeslandweit verteilt.
-> Jedes Bundesland hat eigene Lotteriegesellschaft.
-> Gewinne pro Bundesland ~ Bevoelkerung/Spielerzahl.
```

### A7: Reset-Zyklen
```
System hat Zyklen: Normal -> Aufbau -> Jackpot -> Reset.
-> Jackpot kommt wenn "attraktive Hoehe" erreicht.
-> Nach Jackpot: Reset der Near-Miss Steuerung.
-> Monatsende kann auch Reset ausloesen.
```

---

## 3. DATENQUELLEN

### 3.1 Vorhandene Daten

| Datei | Inhalt | Zeilen | Zeitraum |
|-------|--------|--------|----------|
| `data/raw/keno/KENO_ab_2018.csv` | Alle Ziehungen | 2.237 | 2018-2024 |
| `Keno_GPTs/Keno_GQ_2022_2023-2024.csv` | Gewinnquoten | 27.685 | 2022-2024 |
| `Keno_GPTs/10-9_KGDaten_gefiltert.csv` | GK1-Events | ~100 | 2022-2024 |
| `Keno_GPTs/10-9_Liste_GK1_Treffer.csv` | GK1 Treffer | ~20 | 2022-2024 |
| `data/raw/lotto/Lotto_ab_*.csv` | Lotto Ziehungen | ~3.000 | 2004-2024 |
| `data/raw/eurojackpot/*.csv` | EuroJackpot | ~1.200 | 2012-2024 |

### 3.2 Zu ladende Daten

| Datenquelle | Zweck | Methode |
|-------------|-------|---------|
| Bundesland-Bevoelkerung | WL-002 | Statistisches Bundesamt |
| Lotto-Umsatz pro BL | WL-002 | Jahresberichte Lotterien |
| KENO Quoten-Tabelle | Gewinn-Berechnung | lotto.de |
| Feiertage DE 2018-2024 | Temporal-Analyse | Python holidays |
| Jackpot-Hoehen historisch | WL-003 | Scraping/API |

### 3.3 Daten-Schema

#### KENO Ziehung
```
Datum | Z1 | Z2 | ... | Z20 | Plus5
```

#### Gewinnquoten (Keno_GQ)
```
Datum | KenoTyp | GK | Treffer | Quote | Gewinner | Gesamtgewinn
```

#### GK1-Events
```
Datum | KenoTyp | Gewinner | Wartetage | Jackpot_Hoehe
```

---

## 4. HYPOTHESEN-MATRIX

### 4.1 Wirtschaftslogik-Hypothesen

| ID | Hypothese | Axiom | Prioritaet | Aufwand |
|----|-----------|-------|------------|---------|
| WL-001 | Paar-Garantie pro GK | A3, A4 | KRITISCH | 4h |
| WL-002 | Bundesland-Verteilung | A2, A6 | HOCH | 6h |
| WL-003 | Reset-Zyklus Erkennung | A7 | KRITISCH | 5h |
| WL-004 | Dauerschein-Muster | A2, A3 | MITTEL | 3h |
| WL-005 | Paar-Gewinn-Frequenz | A4 | KRITISCH | 4h |
| WL-006 | Jackpot-Einzigartigkeit | A1 | HOCH | 4h |
| WL-007 | GK-spezifische Paare | A4 | KRITISCH | 5h |

### 4.2 Cross-Game Hypothesen

| ID | Hypothese | Beschreibung | Aufwand |
|----|-----------|--------------|---------|
| XG-001 | Lotto-KENO Korrelation | Gleicher Anbieter = gemeinsame Muster | 4h |
| XG-002 | EuroJackpot-Timing | EJ-Gewinne beeinflussen KENO | 3h |
| XG-003 | Multi-Game Reset | Alle Spiele haben synchrone Zyklen | 5h |
| XG-004 | Zahlen-Migration | "Glueckszahlen" wandern zwischen Spielen | 4h |

### 4.3 Bundesland-Hypothesen

| ID | Hypothese | Beschreibung | Aufwand |
|----|-----------|--------------|---------|
| BL-001 | Gewinner ~ Bevoelkerung | Lineare Korrelation | 3h |
| BL-002 | Jackpot-Rotation | Jackpots rotieren zwischen BL | 4h |
| BL-003 | Regionale Zahlen-Praeferenz | Bestimmte Zahlen pro Region | 3h |
| BL-004 | Dauerschein-Dichte | BL mit mehr Abos = mehr kleine Gewinne | 4h |

---

## 5. PHASEN-PLAN

### PHASE 4.1: Daten-Vorbereitung (6h)

#### 4.1.1 Bundesland-Daten laden (2h)
```python
# Script: scripts/load_bundesland_data.py

# Zu ladende Daten:
bundeslaender = {
    "NRW": {"bevoelkerung": 17.9e6, "lotto_gesellschaft": "WestLotto"},
    "Bayern": {"bevoelkerung": 13.1e6, "lotto_gesellschaft": "LOTTO Bayern"},
    "Baden-Wuerttemberg": {"bevoelkerung": 11.1e6, "lotto_gesellschaft": "Lotto BW"},
    "Niedersachsen": {"bevoelkerung": 8.0e6, "lotto_gesellschaft": "LOTTO Niedersachsen"},
    "Hessen": {"bevoelkerung": 6.3e6, "lotto_gesellschaft": "LOTTO Hessen"},
    "Sachsen": {"bevoelkerung": 4.0e6, "lotto_gesellschaft": "Sachsenlotto"},
    "Rheinland-Pfalz": {"bevoelkerung": 4.1e6, "lotto_gesellschaft": "Lotto RLP"},
    "Berlin": {"bevoelkerung": 3.6e6, "lotto_gesellschaft": "LOTTO Berlin"},
    "Schleswig-Holstein": {"bevoelkerung": 2.9e6, "lotto_gesellschaft": "NordwestLotto"},
    "Brandenburg": {"bevoelkerung": 2.5e6, "lotto_gesellschaft": "Land Brandenburg Lotto"},
    "Sachsen-Anhalt": {"bevoelkerung": 2.2e6, "lotto_gesellschaft": "LOTTO Sachsen-Anhalt"},
    "Thueringen": {"bevoelkerung": 2.1e6, "lotto_gesellschaft": "LOTTO Thueringen"},
    "Hamburg": {"bevoelkerung": 1.9e6, "lotto_gesellschaft": "LOTTO Hamburg"},
    "Mecklenburg-Vorpommern": {"bevoelkerung": 1.6e6, "lotto_gesellschaft": "LOTTO MV"},
    "Saarland": {"bevoelkerung": 1.0e6, "lotto_gesellschaft": "Saartoto"},
    "Bremen": {"bevoelkerung": 0.7e6, "lotto_gesellschaft": "LOTTO Bremen"}
}

# Output: data/external/bundesland_stats.json
```

#### 4.1.2 KENO Quoten-Tabelle laden (1h)
```python
# Script: scripts/load_keno_quotes.py

keno_quoten = {
    "typ_2": {2: 6},
    "typ_3": {2: 1, 3: 16},
    "typ_4": {2: 1, 3: 2, 4: 22},
    "typ_5": {2: 1, 3: 2, 4: 7, 5: 100},
    "typ_6": {3: 1, 4: 2, 5: 15, 6: 500},
    "typ_7": {3: 1, 4: 1, 5: 12, 6: 100, 7: 1000},
    "typ_8": {4: 1, 5: 2, 6: 15, 7: 100, 8: 10000},
    "typ_9": {4: 1, 5: 2, 6: 5, 7: 20, 8: 1000, 9: 50000},
    "typ_10": {0: 2, 5: 2, 6: 5, 7: 15, 8: 100, 9: 1000, 10: 100000}
}

# Output: config/keno_quotes.yaml
```

#### 4.1.3 Daten-Konsolidierung (2h)
```python
# Script: scripts/consolidate_data.py

# Aufgaben:
# 1. Alle KENO-Ziehungen in einheitliches Format
# 2. Gewinnquoten mit Ziehungen joinen
# 3. GK1-Events markieren
# 4. Bundesland-Info aus Pressemitteilungen extrahieren
# 5. Cross-Game Datum-Alignment

# Output: data/processed/consolidated_keno.parquet
```

#### 4.1.4 Feature-Engineering (1h)
```python
# Script: scripts/engineer_features.py

# Neue Features pro Ziehung:
features = [
    "birthday_score",        # % Zahlen 1-31
    "anti_birthday_score",   # % Zahlen 32-70
    "sum_score",             # Summe der 20 Zahlen
    "consecutive_count",     # Anzahl konsekutiver Paare
    "decade_entropy",        # Verteilung ueber Dekaden
    "days_since_gk1",        # Tage seit letztem Jackpot
    "weekday",               # Wochentag (0-6)
    "month_position",        # Monatsanfang/Mitte/Ende
    "near_holiday",          # Naehe zu Feiertag (0-7 Tage)
    "pair_bonus_score",      # Anzahl starker Paare in Ziehung
    "trio_bonus_score",      # Anzahl starker Trios
]

# Output: data/processed/features.parquet
```

---

### PHASE 4.2: Paar-Analyse pro Gewinnklasse (8h)

#### 4.2.1 WL-007: GK-spezifische Paare (4h)
```python
# Script: scripts/analyze_pairs_per_gk.py

# Fuer jede Gewinnklasse (Typ 2-10):
# 1. Lade alle Ziehungen mit dieser GK
# 2. Berechne Paar-Co-Occurrence NUR fuer diese GK
# 3. Vergleiche mit globaler Paar-Statistik
# 4. Identifiziere GK-spezifische starke Paare

# Analyse-Matrix:
"""
| GK | Treffer | Relevante Paare | Erwartete Staerke |
|----|---------|-----------------|-------------------|
| 10 | 10/10   | Alle 45 Paare   | NIEDRIG (selten)  |
| 9  | 9/10    | Alle 45 Paare   | NIEDRIG           |
| 8  | 8/10    | Alle 45 Paare   | MITTEL            |
| 7  | 7/10    | 35 Paare        | MITTEL            |
| 6  | 6/10    | 28 Paare        | HOCH              |
| 5  | 5/10    | 21 Paare        | HOCH              |
| 4  | 4/10    | 15 Paare        | SEHR HOCH         |
| 3  | 3/10    | 10 Paare        | SEHR HOCH         |
| 2  | 2/10    | 6 Paare         | MAXIMAL           |
| 2  | 2/2     | 1 Paar          | KRITISCH          |
"""

# Output: results/pairs_per_gk.json
```

#### 4.2.2 WL-001: Paar-Garantie Test (2h)
```python
# Script: scripts/test_pair_guarantee.py

# Hypothese: Starke Paare gewinnen mind. 1x/Monat

# Test-Methodik:
# 1. Fuer jedes der Top-30 Paare:
# 2. Simuliere Typ-2 Ticket mit diesem Paar
# 3. Fuer jeden Monat: Zaehle Ziehungen wo BEIDE Zahlen erscheinen
# 4. Berechne: Monate_mit_Gewinn / Alle_Monate

# Acceptance Criteria:
# - >90% der Paare gewinnen in >90% der Monate
# - Durchschnitt: 2-4 Gewinne pro Monat pro Paar

# Output: results/pair_guarantee_test.json
```

#### 4.2.3 WL-005: Paar-Gewinn-Frequenz Backtest (2h)
```python
# Script: scripts/backtest_pair_frequency.py

# 12-Monats-Backtest:
# 1. Erstelle virtuelles Portfolio mit Top-20 Paaren
# 2. Simuliere taegliches Spielen (Typ-2, 1 EUR)
# 3. Tracke Gewinne pro Paar pro Monat
# 4. Berechne ROI und Gewinn-Frequenz

# Metriken:
metrics = [
    "wins_per_month_per_pair",
    "avg_win_amount",
    "total_investment",
    "total_return",
    "roi_percent",
    "best_pair",
    "worst_pair",
    "consistency_score"  # Std.Abw. der monatlichen Gewinne
]

# Output: results/pair_frequency_backtest.json
```

---

### PHASE 4.3: Bundesland-Analyse (8h)

#### 4.3.1 WL-002: Verteilung nach Bevoelkerung (3h)
```python
# Script: scripts/analyze_bundesland_distribution.py

# Datenquellen:
# - Pressemitteilungen (manuell extrahiert)
# - Keno_GQ mit Gewinner-Info (falls BL vorhanden)

# Analyse:
# 1. Sammle alle bekannten BL-Gewinne aus Pressemitteilungen
# 2. Korreliere mit Bevoelkerung
# 3. Korreliere mit geschaetzter Spielerzahl

# Erwartung:
# - r > 0.8 zwischen Gewinnen und Bevoelkerung
# - Grosse BL (NRW, Bayern, BaWue) = mehr Gewinne

# Output: results/bundesland_correlation.json
```

#### 4.3.2 BL-002: Jackpot-Rotation (2h)
```python
# Script: scripts/analyze_jackpot_rotation.py

# Hypothese: Jackpots rotieren zwischen Bundeslaendern

# Analyse:
# 1. Chronologische Liste aller Jackpot-Gewinne mit BL
# 2. Berechne Zeit zwischen Jackpots im gleichen BL
# 3. Pruefe: Gibt es Rotation oder Zufall?

# Test:
# - Chi-Quadrat auf Gleichverteilung ueber BL
# - Autokorrelation der BL-Sequenz

# Output: results/jackpot_rotation.json
```

#### 4.3.3 BL-003: Regionale Zahlen-Praeferenz (2h)
```python
# Script: scripts/analyze_regional_numbers.py

# Hypothese: Bestimmte Zahlen sind regional beliebter

# Analyse (soweit Daten vorhanden):
# 1. Gewinne pro BL nach Zahlen gruppieren
# 2. Identifiziere BL-spezifische "Glueckszahlen"
# 3. Korreliere mit lokalen Besonderheiten (Postleitzahlen, etc.)

# Limitierung: Wenig regionale Daten verfuegbar
# Alternative: Pressemitteilungen analysieren

# Output: results/regional_numbers.json
```

#### 4.3.4 BL-004: Dauerschein-Dichte Schaetzung (1h)
```python
# Script: scripts/estimate_dauerschein_density.py

# Schaetzung basierend auf:
# - Bevoelkerung
# - Lotto-Umsatz pro BL (oeffentlich)
# - Anzahl kleine Gewinne pro BL

# Output: results/dauerschein_density.json
```

---

### PHASE 4.4: Reset-Zyklus Analyse (8h)

#### 4.4.1 WL-003: Pre-Jackpot Muster (4h)
```python
# Script: scripts/analyze_reset_cycles.py

# Analyse der 7-14 Tage VOR jedem der 20 GK1-Events:

# Metriken pro Tag vor Jackpot:
pre_jackpot_metrics = [
    "near_miss_ratio",       # Typ-9 Gewinner / Typ-10 Gewinner
    "entropy_20_numbers",    # Verteilungs-Entropy
    "pair_variance",         # Varianz der Paar-Haeufigkeiten
    "birthday_score_trend",  # Trend des Birthday-Scores
    "sum_deviation",         # Abweichung vom Mittelwert 710
    "consecutive_trend",     # Trend konsekutiver Paare
]

# Suche nach signifikanten Mustern:
# - Steigt Near-Miss Ratio 3-7 Tage vor Jackpot?
# - Sinkt Entropy (weniger Zufaelligkeit)?
# - Gibt es "Aufbau-Phase"?

# Output: results/pre_jackpot_patterns.json
```

#### 4.4.2 Zyklus-Detektion (2h)
```python
# Script: scripts/detect_cycles.py

# Identifiziere Zyklen:
# 1. Jackpot -> Reset -> Aufbau -> Jackpot
# 2. Monatsende-Reset
# 3. Quartalsende-Reset

# Methoden:
# - Autokorrelation der Near-Miss Ratio
# - Fourier-Analyse fuer Periodizitaet
# - Change-Point Detection

# Output: results/cycle_detection.json
```

#### 4.4.3 WL-006: Jackpot-Einzigartigkeit Score (2h)
```python
# Script: scripts/calculate_uniqueness.py

# Fuer alle 20 GK1-Events:
# Berechne Uniqueness-Score basierend auf:

uniqueness_components = {
    "anti_birthday": 0.3,      # Anteil Zahlen > 31
    "no_consecutive": 0.2,     # Keine konsekutiven Paare
    "decade_spread": 0.2,      # Alle 7 Dekaden vertreten
    "sum_extreme": 0.15,       # Sum < 650 oder > 770
    "no_popular_pairs": 0.15   # Keine Top-10 Paare
}

# Score = gewichtete Summe der Komponenten
# Erwartung: Jackpot-Kombis haben Score > 0.7

# Output: results/jackpot_uniqueness.json
```

---

### PHASE 4.5: Cross-Game Analyse (10h)

#### 4.5.1 XG-001: Lotto-KENO Korrelation (3h)
```python
# Script: scripts/analyze_lotto_keno_correlation.py

# Hypothese: Gleicher Anbieter = gemeinsame Muster

# Analyse:
# 1. Lade Lotto 6aus49 Ziehungen (Mi + Sa)
# 2. Lade KENO Ziehungen (taeglich)
# 3. Korreliere Zahlen am gleichen Tag
# 4. Korreliere Zahlen-Trends ueber Wochen

# Spezifische Tests:
# - Erscheinen Lotto-Zahlen haeufiger in KENO am gleichen Tag?
# - Gibt es "Glueckszahlen" die in beiden erscheinen?
# - Korrelieren Jackpot-Zyklen?

# Output: results/lotto_keno_correlation.json
```

#### 4.5.2 XG-002: EuroJackpot-Timing (2h)
```python
# Script: scripts/analyze_eurojackpot_timing.py

# Hypothese: EJ-Gewinne beeinflussen KENO-Ausschuettung

# Analyse:
# 1. Lade EuroJackpot Gewinne (Di + Fr)
# 2. Pruefe KENO-Ausschuettung danach
# 3. Steigt/sinkt KENO-Ausschuettung nach EJ-Jackpot?

# Begruendung:
# - Gleiche Lotteriegesellschaft
# - Gemeinsamer Pool?
# - Kompensations-Effekte?

# Output: results/eurojackpot_timing.json
```

#### 4.5.3 XG-003: Multi-Game Reset (3h)
```python
# Script: scripts/analyze_multi_game_reset.py

# Hypothese: Alle Spiele haben synchrone Zyklen

# Analyse:
# 1. Identifiziere Reset-Punkte in KENO
# 2. Identifiziere Reset-Punkte in Lotto
# 3. Identifiziere Reset-Punkte in EuroJackpot
# 4. Korreliere die Reset-Zeitpunkte

# Erwartung:
# - Monatsende-Resets synchron
# - Quartalsende-Resets synchron
# - Jahresende-Reset synchron

# Output: results/multi_game_reset.json
```

#### 4.5.4 XG-004: Zahlen-Migration (2h)
```python
# Script: scripts/analyze_number_migration.py

# Hypothese: "Glueckszahlen" wandern zwischen Spielen

# Analyse:
# 1. Identifiziere "heisse" Zahlen pro Woche in Lotto
# 2. Pruefe: Erscheinen diese in KENO der naechsten Woche?
# 3. Und umgekehrt

# Test:
# - Lag-Korrelation (1-7 Tage)
# - Granger-Kausalitaet

# Output: results/number_migration.json
```

---

### PHASE 4.6: Garantie-Modell (10h)

#### 4.6.1 Modell-Architektur (2h)
```python
# Script: kenobase/prediction/guarantee_model.py

class GuaranteeModel:
    """
    Dynamisches Modell zur Generierung von Zahlengruppen
    mit garantierten Gewinn-Schwellen.
    """

    def __init__(self):
        self.pair_scores = {}      # Paar-Staerken pro GK
        self.cycle_phase = None    # Aktuelle Zyklus-Phase
        self.days_since_gk1 = 0    # Tage seit Jackpot
        self.month_position = None # Monatsanfang/Mitte/Ende

    def calculate_number_score(self, number: int, context: dict) -> float:
        """
        Berechne Score einer Zahl basierend auf Kontext.

        Komponenten:
        - Base Score (aus Frequenz-Analyse)
        - Pair Bonus (wenn mit anderen starken Zahlen)
        - Temporal Bonus (Monatsposition)
        - Cycle Bonus (Naehe zu Reset/Jackpot)
        - Anti-Birthday Bonus (fuer Jackpot-Strategie)
        """
        pass

    def generate_group(
        self,
        size: int,
        strategy: str,
        date: datetime.date
    ) -> dict:
        """
        Generiere optimale Zahlengruppe.

        Strategien:
        - "guarantee_100": Optimiert fuer 100 EUR Gewinn
        - "guarantee_500": Optimiert fuer 500 EUR Gewinn
        - "jackpot": Optimiert fuer Jackpot-Wahrscheinlichkeit
        - "balanced": Ausgewogen
        """
        pass

    def predict_cycle_phase(self, date: datetime.date) -> str:
        """
        Sage aktuelle Zyklus-Phase vorher.

        Phasen:
        - "normal": Normale Ausschuettung
        - "buildup": Aufbau vor Jackpot
        - "jackpot_imminent": Jackpot wahrscheinlich
        - "post_reset": Nach Jackpot/Monatsende
        """
        pass
```

#### 4.6.2 100 EUR Garantie-Gruppe (2h)
```python
# Script: scripts/optimize_100eur_group.py

# Ziel: Finde Gruppe die in >80% der Monate mind. 100 EUR gewinnt

# Strategie:
# 1. Typ 6 mit 5/6 Treffern = 100 EUR
# 2. ODER Typ 8 mit 6/8 Treffern = 100 EUR
# 3. ODER mehrere kleine Gewinne kumuliert

# Optimierung:
# - Maximiere Anzahl starker Paare in Gruppe
# - Beruecksichtige GK-spezifische Paar-Staerken
# - Temporal-Kontext einbeziehen

# Backtest:
# - 24-Monats Walk-Forward
# - Monatliche Gewinn-Summe berechnen
# - Acceptance: >80% Monate >= 100 EUR

# Output: results/guarantee_100eur.json
```

#### 4.6.3 500 EUR Garantie-Gruppe (2h)
```python
# Script: scripts/optimize_500eur_group.py

# Ziel: Finde Gruppe die in >50% der Monate mind. 500 EUR gewinnt

# Strategie:
# 1. Typ 9 mit 7/9 Treffern = 500 EUR
# 2. ODER Typ 6 mit 6/6 Treffern = 500 EUR
# 3. Hoehere Volatilitaet akzeptabel

# Optimierung:
# - Fokus auf Jackpot-favored Zahlen
# - Near-Miss Indikatoren einbeziehen
# - Cycle-Phase beruecksichtigen

# Output: results/guarantee_500eur.json
```

#### 4.6.4 Jackpot-Kandidat Generator (2h)
```python
# Script: scripts/generate_jackpot_candidate.py

# Ziel: Generiere Kombination mit maximalem Uniqueness-Score

# Kriterien:
# 1. Anti-Birthday (>60% Zahlen > 31)
# 2. Keine konsekutiven Paare
# 3. Alle 7 Dekaden vertreten
# 4. Keine Top-20 populaeren Paare
# 5. Sum in extremem Bereich (<650 oder >770)

# Zusaetzlich:
# - Timing: Nur ausgeben wenn Zyklus-Phase = "buildup" oder "jackpot_imminent"
# - Confidence Score basierend auf Muster-Erkennung

# Output: results/jackpot_candidates.json
```

#### 4.6.5 Dynamische Tages-Empfehlung (2h)
```python
# Script: scripts/daily_recommendation.py

# Taegliche Empfehlung basierend auf:
# 1. Aktuelle Zyklus-Phase
# 2. Tage seit letztem Jackpot
# 3. Monatsposition
# 4. Letzte Ziehungs-Muster

# Output pro Tag:
daily_output = {
    "date": "2025-12-30",
    "cycle_phase": "buildup",
    "days_since_gk1": 45,
    "recommendations": {
        "typ_10_guarantee_100": [3, 9, 24, 33, 49, 50, 51, 52, 64, 66],
        "typ_10_guarantee_500": [2, 3, 9, 20, 24, 36, 39, 49, 53, 64],
        "typ_10_jackpot": [32, 38, 41, 47, 53, 58, 62, 65, 67, 70],
        "typ_6_daily": [3, 9, 24, 49, 51, 64]
    },
    "confidence_scores": {
        "guarantee_100": 0.82,
        "guarantee_500": 0.54,
        "jackpot": 0.03
    }
}

# Output: results/daily/YYYY-MM-DD.json
```

---

### PHASE 4.7: Backtest & Validation (8h)

#### 4.7.1 Walk-Forward Backtest Framework (3h)
```python
# Script: scripts/walkforward_backtest.py

class WalkForwardBacktest:
    """
    Walk-Forward Backtest fuer alle Strategien.

    Methodik:
    - Training: 12 Monate
    - Test: 1 Monat
    - Slide: 1 Monat
    - Gesamt: 24 Monate Test (2022-2024)
    """

    def run_backtest(self, strategy: str) -> dict:
        """
        Fuehre Backtest fuer eine Strategie durch.

        Returns:
        - monthly_returns: Liste der monatlichen Gewinne
        - roi: Gesamt-ROI
        - hit_rate: % Monate mit Gewinn >= Ziel
        - max_drawdown: Maximaler Verlust-Streak
        - consistency: Std.Abw. der monatlichen Gewinne
        """
        pass
```

#### 4.7.2 Strategie-Vergleich (2h)
```python
# Script: scripts/compare_strategies.py

# Vergleiche alle Strategien:
strategies = [
    "pair_focused",
    "jackpot",
    "near_miss",
    "balanced",
    "guarantee_100",
    "guarantee_500",
    "anti_birthday"
]

# Metriken pro Strategie:
# - ROI (gesamt und monatlich)
# - Hit-Rate (Ziel erreicht)
# - Konsistenz (Std.Abw.)
# - Max Drawdown
# - Sharpe Ratio (risikoadjustiert)

# Output: results/strategy_comparison.json
```

#### 4.7.3 Cross-Validation (2h)
```python
# Script: scripts/cross_validate.py

# Cross-Validation mit verschiedenen Zeitraeumen:
# 1. 2022 Training, 2023 Test
# 2. 2023 Training, 2024 Test
# 3. 2022-2023 Training, 2024 Test

# Pruefe Stabilitaet der Ergebnisse

# Output: results/cross_validation.json
```

#### 4.7.4 Statistische Signifikanz-Tests (1h)
```python
# Script: scripts/statistical_tests.py

# Fuer jede Strategie:
# 1. t-Test vs. Zufall
# 2. Bootstrap Confidence Intervals
# 3. Permutation Test

# Output: results/statistical_significance.json
```

---

## 6. SCRIPTS ZU ERSTELLEN

### 6.1 Daten-Scripts

| Script | Phase | Aufwand | Abhaengigkeiten |
|--------|-------|---------|-----------------|
| load_bundesland_data.py | 4.1.1 | 2h | - |
| load_keno_quotes.py | 4.1.2 | 1h | - |
| consolidate_data.py | 4.1.3 | 2h | 4.1.1, 4.1.2 |
| engineer_features.py | 4.1.4 | 1h | 4.1.3 |

### 6.2 Analyse-Scripts

| Script | Phase | Aufwand | Abhaengigkeiten |
|--------|-------|---------|-----------------|
| analyze_pairs_per_gk.py | 4.2.1 | 4h | 4.1 |
| test_pair_guarantee.py | 4.2.2 | 2h | 4.2.1 |
| backtest_pair_frequency.py | 4.2.3 | 2h | 4.2.1 |
| analyze_bundesland_distribution.py | 4.3.1 | 3h | 4.1 |
| analyze_jackpot_rotation.py | 4.3.2 | 2h | 4.3.1 |
| analyze_regional_numbers.py | 4.3.3 | 2h | 4.3.1 |
| estimate_dauerschein_density.py | 4.3.4 | 1h | 4.3.1 |
| analyze_reset_cycles.py | 4.4.1 | 4h | 4.1 |
| detect_cycles.py | 4.4.2 | 2h | 4.4.1 |
| calculate_uniqueness.py | 4.4.3 | 2h | 4.1 |
| analyze_lotto_keno_correlation.py | 4.5.1 | 3h | 4.1 |
| analyze_eurojackpot_timing.py | 4.5.2 | 2h | 4.1 |
| analyze_multi_game_reset.py | 4.5.3 | 3h | 4.5.1, 4.5.2 |
| analyze_number_migration.py | 4.5.4 | 2h | 4.5.1 |

### 6.3 Modell-Scripts

| Script | Phase | Aufwand | Abhaengigkeiten |
|--------|-------|---------|-----------------|
| kenobase/prediction/guarantee_model.py | 4.6.1 | 2h | 4.2, 4.4 |
| optimize_100eur_group.py | 4.6.2 | 2h | 4.6.1 |
| optimize_500eur_group.py | 4.6.3 | 2h | 4.6.1 |
| generate_jackpot_candidate.py | 4.6.4 | 2h | 4.6.1, 4.4.3 |
| daily_recommendation.py | 4.6.5 | 2h | 4.6.1-4 |

### 6.4 Backtest-Scripts

| Script | Phase | Aufwand | Abhaengigkeiten |
|--------|-------|---------|-----------------|
| walkforward_backtest.py | 4.7.1 | 3h | 4.6 |
| compare_strategies.py | 4.7.2 | 2h | 4.7.1 |
| cross_validate.py | 4.7.3 | 2h | 4.7.1 |
| statistical_tests.py | 4.7.4 | 1h | 4.7.1-3 |

---

## 7. ACCEPTANCE CRITERIA

### 7.1 Paar-Analyse (WL-001, WL-005, WL-007)

| Kriterium | Schwelle | Messung |
|-----------|----------|---------|
| Paar-Garantie Rate | >90% | % Paare die 1x/Monat gewinnen |
| Monatliche Paar-Gewinne | 2-4 | Durchschnitt pro Paar |
| GK-Spezifitaet | >50% | % Paare die GK-spezifisch sind |

### 7.2 Bundesland-Analyse (WL-002, BL-*)

| Kriterium | Schwelle | Messung |
|-----------|----------|---------|
| Bevoelkerungs-Korrelation | r > 0.7 | Pearson Korrelation |
| Jackpot-Rotation | p < 0.05 | Chi-Quadrat Test |
| Regionale Daten | >50 | Anzahl extrahierter Datenpunkte |

### 7.3 Reset-Zyklus (WL-003, WL-006)

| Kriterium | Schwelle | Messung |
|-----------|----------|---------|
| Pre-Jackpot Erkennung | >60% | Korrekt vorhergesagte GK1 |
| Uniqueness Score | >0.7 | Durchschnitt fuer GK1-Events |
| Zyklus-Laenge | 20-40 Tage | Geschaetzte Periode |

### 7.4 Garantie-Modell

| Kriterium | Schwelle | Messung |
|-----------|----------|---------|
| 100 EUR Garantie | >80% | % Monate mit Gewinn >= 100 EUR |
| 500 EUR Garantie | >50% | % Monate mit Gewinn >= 500 EUR |
| Jackpot ROI | >0 | Langfristiger ROI |
| Konsistenz | CV < 0.5 | Variationskoeffizient |

### 7.5 Cross-Game

| Kriterium | Schwelle | Messung |
|-----------|----------|---------|
| Lotto-KENO Korrelation | r > 0.3 | Signifikante Korrelation |
| Multi-Game Reset | >70% | Synchrone Resets |
| Zahlen-Migration | Lag 1-3 | Signifikanter Lag |

---

## 8. OUTPUT-SPEZIFIKATIONEN

### 8.1 Ergebnis-Dateien

```
results/
├── phase4/
│   ├── pairs_per_gk.json
│   ├── pair_guarantee_test.json
│   ├── pair_frequency_backtest.json
│   ├── bundesland_correlation.json
│   ├── jackpot_rotation.json
│   ├── regional_numbers.json
│   ├── dauerschein_density.json
│   ├── pre_jackpot_patterns.json
│   ├── cycle_detection.json
│   ├── jackpot_uniqueness.json
│   ├── lotto_keno_correlation.json
│   ├── eurojackpot_timing.json
│   ├── multi_game_reset.json
│   ├── number_migration.json
│   ├── guarantee_100eur.json
│   ├── guarantee_500eur.json
│   ├── jackpot_candidates.json
│   ├── strategy_comparison.json
│   ├── cross_validation.json
│   └── statistical_significance.json
├── daily/
│   └── YYYY-MM-DD.json  (taegliche Empfehlungen)
└── backtest/
    └── walkforward_results.json
```

### 8.2 Dokumentation

```
docs/
├── GUARANTEE_MODEL.md
├── BUNDESLAND_ANALYSIS.md
├── RESET_CYCLES.md
├── CROSS_GAME_PATTERNS.md
└── BACKTEST_REPORT.md
```

### 8.3 Dashboard-Daten

```python
# Format fuer Dashboard (optional)
dashboard_data = {
    "current_phase": "buildup",
    "days_since_gk1": 45,
    "next_jackpot_probability": 0.12,
    "todays_recommendations": [...],
    "monthly_roi": 2.3,
    "yearly_roi": 15.7,
    "best_performing_strategy": "pair_focused"
}
```

---

## 9. ABHAENGIGKEITS-GRAPH

```
                    ┌─────────────────┐
                    │  4.1 DATEN      │
                    │  VORBEREITUNG   │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   4.2 PAAR-     │ │  4.3 BUNDES-   │ │   4.4 RESET-    │
│   ANALYSE       │ │  LAND-ANALYSE  │ │   ZYKLUS        │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                    ┌────────▼────────┐
                    │  4.5 CROSS-     │
                    │  GAME ANALYSE   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  4.6 GARANTIE-  │
                    │  MODELL         │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  4.7 BACKTEST   │
                    │  & VALIDATION   │
                    └─────────────────┘
```

---

## 10. RISIKEN & MITIGATIONEN

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| Zu wenig BL-Daten | HOCH | MITTEL | Pressemitteilungen scrapen |
| GK1-Events zu selten | MITTEL | HOCH | Statistische Methoden anpassen |
| Overfitting | MITTEL | HOCH | Walk-Forward Validation |
| Paradigma falsch | NIEDRIG | KRITISCH | Falsifikations-Tests einbauen |
| Datenqualitaet | MITTEL | MITTEL | Daten-Validierung in 4.1 |

---

## 11. LOOP-KONFIGURATION

### 11.1 Team-Zuweisung

```yaml
# Fuer autonomen Loop
teams:
  alpha:
    phase: 4.1
    scripts: [load_bundesland_data, load_keno_quotes, consolidate_data, engineer_features]
  beta:
    phase: 4.2
    scripts: [analyze_pairs_per_gk, test_pair_guarantee, backtest_pair_frequency]
    depends_on: alpha
  gamma:
    phase: 4.3-4.4
    scripts: [analyze_bundesland_*, analyze_reset_cycles, calculate_uniqueness]
    depends_on: alpha
  delta:
    phase: 4.5
    scripts: [analyze_lotto_keno_*, analyze_eurojackpot_*, analyze_multi_game_*]
    depends_on: alpha
  epsilon:
    phase: 4.6-4.7
    scripts: [guarantee_model, optimize_*, walkforward_backtest, compare_strategies]
    depends_on: [beta, gamma, delta]
```

### 11.2 Checkpoints

| Checkpoint | Nach Phase | Pruefung |
|------------|------------|----------|
| CP1 | 4.1 | Alle Daten geladen, Features berechnet |
| CP2 | 4.2 | Paar-Analyse abgeschlossen, Tests gruen |
| CP3 | 4.3-4.4 | BL + Reset Analyse fertig |
| CP4 | 4.5 | Cross-Game Analyse fertig |
| CP5 | 4.6 | Garantie-Modell funktional |
| CP6 | 4.7 | Backtest abgeschlossen, Ergebnisse dokumentiert |

---

## 12. ERFOLGS-DEFINITION

### 12.1 Minimal Viable Product (MVP)

- [x] Paar-Analyse pro GK funktional
- [x] 100 EUR Garantie-Gruppe >70% Monate
- [x] Taegliche Empfehlungen generiert
- [x] Backtest positiver ROI

### 12.2 Vollstaendiges Produkt

- [ ] Alle WL-Hypothesen getestet
- [ ] Bundesland-Analyse integriert
- [ ] Cross-Game Muster genutzt
- [ ] 500 EUR Garantie-Gruppe >50% Monate
- [ ] Jackpot-Timing >60% korrekt
- [ ] Dashboard-faehige Daten

### 12.3 Stretch Goals

- [ ] Echtzeit-Scraping neuer Ziehungen
- [ ] Automatische Ticket-Generierung
- [ ] Multi-Game Portfolio-Optimierung
- [ ] Regionale Empfehlungen pro BL

---

## 13. ZEITPLAN

| Phase | Aufwand | Kumuliert | Abhaengigkeiten |
|-------|---------|-----------|-----------------|
| 4.1 Daten-Vorbereitung | 6h | 6h | - |
| 4.2 Paar-Analyse | 8h | 14h | 4.1 |
| 4.3 Bundesland-Analyse | 8h | 22h | 4.1 |
| 4.4 Reset-Zyklus | 8h | 30h | 4.1 |
| 4.5 Cross-Game | 10h | 40h | 4.1 |
| 4.6 Garantie-Modell | 10h | 50h | 4.2-4.5 |
| 4.7 Backtest | 8h | 58h | 4.6 |

**GESAMT: ~58 Stunden**

---

*Master Plan V2.0 - Phase 4 Wirtschaftslogik*
*Erstellt: 2025-12-29*
*Status: BEREIT FUER LOOP*
