# Reverse Engineering Tasks - Kenobase V2.0

**Erstellt:** 2025-12-27
**Quelle:** Agentenanalyse von KENO_10K, Old_Code, Hidden Data
**Status:** BEREIT FUER LOOP

---

## Executive Summary

Aus der Analyse von 148 Dateien im Keno_GPTs Ordner und dem alten Code wurden **15 neue Tasks** identifiziert:

| Prioritaet | Anzahl | Kategorie |
|------------|--------|-----------|
| CRITICAL | 3 | Core Bugs/Missing Features |
| HIGH | 6 | Neue Hypothesen |
| MEDIUM | 4 | Validierungen |
| LOW | 2 | Nice-to-Have |

---

## CRITICAL (Blocker fuer andere Tasks)

### TASK-C01: Zahlenpool Top-11 Generator
**Prioritaet:** CRITICAL (P0)
**Aufwand:** 3h
**Status:** OFFEN

**Problem:**
Der Kern-Algorithmus aus V9 fehlt in V2.0 komplett.

**Algorithmus:**
```python
1. Teile Daten in 3 x 10-Ziehungs-Perioden
2. Finde Top-11 pro Periode (nach Haeufigkeit)
3. Berechne Schnittmengen:
   - Top-11 jeder Periode ∩ Top-20 gesamt
   - Paarweise Top-11 Schnittmengen
4. Union aller Schnittmengen = Zahlenpool
```

**Acceptance Criteria:**
- [ ] `kenobase/core/number_pool.py` implementiert
- [ ] Zeitraum-Groesse konfigurierbar
- [ ] Unit-Test mit bekannten Eingaben
- [ ] Reproduziert V9-Ausgaben

**Referenz:** `all_code/00_0_Keno_6-Kombi_Analyse_V9.py` Zeilen 45-85

---

### TASK-C02: Duo/Trio/Quatro Bug-Fix
**Prioritaet:** CRITICAL (P0)
**Aufwand:** 4h
**Status:** OFFEN

**Problem:**
V9-Kommentare: "Duos, Trios, Quatros werden falsch berechnet"

**Bug-Beschreibung:**
```python
# FALSCH (V9):
combinations(aktuelle_uebereinstimmung, 2)  # Generiert ALLE Paare

# KORREKT:
# Nur NEUE Paare tracken, nicht bei jeder Ziehung neu zaehlen
```

**Acceptance Criteria:**
- [ ] Bug analysiert und dokumentiert
- [ ] Korrekte Implementierung in `pattern.py`
- [ ] Manuelle Verifikation mit Beispieldaten
- [ ] Regressions-Test

**Referenz:** `all_code/00_0_Keno_6-Kombi_Analyse_V9.py` Zeilen 103-148

---

### TASK-C03: GK1 Daten Integration
**Prioritaet:** CRITICAL (P0)
**Aufwand:** 2h
**Status:** OFFEN

**Problem:**
Wichtige Dateien sind nicht in kenobase integriert:
- `10-9_Liste_GK1_Treffer.csv` - GK1 Events mit Kombinationen
- `10-9_KGDaten_gefiltert.csv` - "Vergangene Tage seit GK1"

**Acceptance Criteria:**
- [ ] Dateien in `data/raw/keno/` importiert
- [ ] Data Loader unterstuetzt neues Format
- [ ] "Vergangene Tage" als Feature verfuegbar

---

## HIGH (Neue Hypothesen aus Datenanalyse)

### TASK-H01: Wiederholungs-Zyklus Analyse (7-Tage)
**Prioritaet:** HIGH
**Aufwand:** 3h
**Status:** OFFEN
**Quelle:** KENO_10K Analyse

**Hypothese:**
```
Gewinnzahlen folgen einem ~7-Tage-Zyklus:
- Tag 1-3: Wenig Wiederholungen (0-2)
- Tag 4-5: Zunehmende Wiederholungen (2-4)
- Tag 6-7: Peak Wiederholungen (4-6)
- Tag 8: Reset mit neuen Zahlen
```

**Evidenz aus KENO_10K:**
- 48% der Tage haben >= 3 Wiederholungen
- Max 6 von 8 Zahlen wiederholt (75%!)
- Cluster-Muster erkennbar

**Acceptance Criteria:**
- [ ] Script `scripts/analyze_repetition_cycles.py`
- [ ] Zyklus-Laenge statistisch bestimmen
- [ ] Vorhersage-Modell basierend auf Zyklus
- [ ] F1-Score >= 0.50

---

### TASK-H02: Core Stable Numbers identifizieren
**Prioritaet:** HIGH
**Aufwand:** 2h
**Status:** OFFEN
**Quelle:** KENO_10K Analyse

**Hypothese:**
```
Bestimmte Zahlen bilden einen "stabilen Kern":
KENO_10K:  [4, 38, 19, 44, 12, 25]
KENO_10K1: [36, 34, 21, 24, 25]
KENO_10K2: [3, 6, 9, 14, 21]

89-93% aller erfolgreichen Tage enthalten >= 2 Core-Zahlen
```

**Acceptance Criteria:**
- [ ] Core-Zahlen pro Zeitraum identifizieren
- [ ] Stabilitaet ueber Zeit messen
- [ ] Vorhersage: "Mindestens 2 Core-Zahlen" Regel
- [ ] Precision >= 0.70

---

### TASK-H03: Anti-Cluster Reset-Regel
**Prioritaet:** HIGH
**Aufwand:** 2h
**Status:** OFFEN
**Quelle:** KENO_10K Analyse

**Hypothese:**
```
Nach extremen Wiederholungs-Clustern (5+) folgt ein "Reset":
- Tag T: >= 5 Wiederholungen
- Tag T+1: <= 1 Wiederholung (60% der Faelle)
```

**Evidenz:**
```
05.02.2024: 6 Wiederholungen (75%)
06.02.2024: 3 Wiederholungen
07.02.2024: 1 Wiederholung (Reset!) ✓
```

**Acceptance Criteria:**
- [ ] Reset-Wahrscheinlichkeit berechnen
- [ ] Threshold fuer "Cluster" optimieren
- [ ] Trading-Signal: "Nach Cluster nicht spielen"
- [ ] Backtest-Validierung

---

### TASK-H04: GK1 Wartezeit-Verteilung
**Prioritaet:** HIGH
**Aufwand:** 3h
**Status:** OFFEN
**Quelle:** 10-9_KGDaten_gefiltert.csv

**Hypothese:**
```
GK1 (10/10 richtig) hat NICHT-zufaellige Wartezeit:
- "Vergangene Tage seit letztem GK1" clustert
- Bestimmte Intervalle sind ueberrepraesentiert
```

**Daten verfuegbar:**
- `10-9_KGDaten_gefiltert.csv`: Spalte "Vergangene Tage"
- `10-9_Liste_GK1_Treffer.csv`: GK1 Events

**Acceptance Criteria:**
- [ ] Wartezeit-Verteilung plotten
- [ ] Chi-Quadrat Test gegen Exponential
- [ ] Signifikante Cluster identifizieren
- [ ] Vorhersage-Modell fuer naechsten GK1

---

### TASK-H05: Zehnergruppen-Paar-Affinitaet
**Prioritaet:** HIGH
**Aufwand:** 2h
**Status:** OFFEN
**Quelle:** KENO_10K Analyse

**Hypothese:**
```
Bestimmte Zehnergruppen-Paare erscheinen ueberproportional:
- 30er + 40er Gruppe: 33, 34, 36 + 44, 45, 48
- Diese Kombinationen sind NICHT zufaellig
```

**Acceptance Criteria:**
- [ ] Top-5 Zehnergruppen-Paare identifizieren
- [ ] Affinitaets-Score berechnen
- [ ] Signifikanz-Test
- [ ] Integration in Kombinations-Filter

---

### TASK-H06: 111-Prinzip Falsifikation
**Prioritaet:** HIGH
**Aufwand:** 2h
**Status:** OFFEN
**Quelle:** Old Code Analyse

**Hypothese (zu testen):**
```
"Gewinnkombinationen erfuellen numerologische Regeln:
 sum(combo) ≡ 0 (mod 111 | 37 | 11 | 3)"
```

**Wissenschaftliche Bewertung:** Potenziell pseudowissenschaftlich

**Acceptance Criteria:**
- [ ] 111-Pattern-Haeufigkeit fuer Gewinne berechnen
- [ ] Vergleich gegen Random Baseline
- [ ] Chi-Quadrat Test
- [ ] DOKUMENTIERE: Bestaetigt oder Falsifiziert

---

## MEDIUM (Validierungen)

### TASK-M01: Top-Pool Size Optimierung
**Prioritaet:** MEDIUM
**Aufwand:** 2h
**Status:** OFFEN

**Problem:**
Warum genau Top-11? Ist das optimal?

**Acceptance Criteria:**
- [ ] Vergleiche Top-5, Top-11, Top-15, Top-20
- [ ] Precision/Recall fuer jede Pool-Groesse
- [ ] Optimale Groesse bestimmen
- [ ] Config-Parameter anpassen

---

### TASK-M02: Zehnergruppen-Regel Validierung
**Prioritaet:** MEDIUM
**Aufwand:** 2h
**Status:** OFFEN

**Hypothese:**
```
"Max 2 Zahlen pro Zehnergruppe" erhoht Precision
```

**Acceptance Criteria:**
- [ ] A/B Test: Mit vs. ohne Regel
- [ ] Optimaler max_per_decade Wert
- [ ] Signifikanz-Test

---

### TASK-M03: EuroJackpot Cross-Validation
**Prioritaet:** MEDIUM
**Aufwand:** 4h
**Status:** OFFEN

**Ziel:**
Teste KENO-Hypothesen auf EuroJackpot-Daten

**Acceptance Criteria:**
- [ ] EuroJackpot Analyzer implementieren
- [ ] Wiederholungs-Zyklus testen
- [ ] Core-Numbers testen
- [ ] Report: Welche Hypothesen generalisieren?

---

### TASK-M04: Summen-Fenster Analyse
**Prioritaet:** MEDIUM
**Aufwand:** 2h
**Status:** OFFEN
**Quelle:** KENO_10K Analyse

**Hypothese:**
```
Summen von Gewinnzahlen clustern in Fenstern:
- [140-170] und [190-220] ueberrepraesentiert
```

**Acceptance Criteria:**
- [ ] Summen-Verteilung plotten
- [ ] Cluster identifizieren
- [ ] Summen-Filter fuer Kombinationen

---

## LOW (Nice-to-Have)

### TASK-L01: PDF-Scraper fuer historische Daten
**Prioritaet:** LOW
**Aufwand:** 2h
**Status:** OFFEN

**Beschreibung:**
PDF → CSV Converter fuer alte Keno_GPTs Daten

---

### TASK-L02: Lotto 6aus49 Support
**Prioritaet:** LOW
**Aufwand:** 3h
**Status:** OFFEN

**Beschreibung:**
Lotto-spezifische Analyse nach KENO-Muster

---

## Daten-Inventar (Neue Quellen)

| Datei | Zeilen | Inhalt | Prioritaet |
|-------|--------|--------|------------|
| 10-9_Liste_GK1_Treffer.csv | ~100 | GK1 Events + Kombis | CRITICAL |
| 10-9_KGDaten_gefiltert.csv | ~100 | Vergangene Tage | CRITICAL |
| 10-9_NumbertoCheck.csv | ~2000 | 20er Tipp-Sets | HIGH |
| KENO_10K.csv | 33 | Erfolgreiche Vorhersagen | HIGH |
| KENO_10K1.csv | 48 | Erfolgreiche Vorhersagen | HIGH |
| KENO_10K2.csv | 70 | Erfolgreiche Vorhersagen | HIGH |
| KENO_Stats_ab-2004.csv | ~7300 | 20 Jahre Archiv | MEDIUM |
| Keno_Ziehung_GPT.csv | ~2500 | Konsolidierte Master | HIGH |

---

## Empfohlene Loop-Reihenfolge

```
Phase 1: CRITICAL (Blocker entfernen)
├── TASK-C01: Zahlenpool Generator
├── TASK-C02: Duo/Trio Bug-Fix
└── TASK-C03: GK1 Daten Integration

Phase 2: HIGH (Neue Hypothesen)
├── TASK-H01: 7-Tage Zyklus
├── TASK-H02: Core Stable Numbers
├── TASK-H03: Anti-Cluster Reset
├── TASK-H04: GK1 Wartezeit
├── TASK-H05: Zehnergruppen-Affinitaet
└── TASK-H06: 111-Prinzip Falsifikation

Phase 3: MEDIUM (Validierungen)
├── TASK-M01: Pool Size Optimierung
├── TASK-M02: Zehnergruppen-Regel
├── TASK-M03: EuroJackpot Cross-Val
└── TASK-M04: Summen-Fenster

Phase 4: LOW (Optional)
├── TASK-L01: PDF-Scraper
└── TASK-L02: Lotto Support
```

---

## Changelog

- 2025-12-27: Initiale Erstellung aus Agentenanalyse
