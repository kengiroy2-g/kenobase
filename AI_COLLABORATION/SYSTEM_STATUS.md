# KENOBASE System Status

**Stand:** 2025-12-29
**Version:** 2.1.0 (Number-GROUP Model)

---

## Aktueller Status: OPERATIONAL

### Paradigma
**GRUNDWAHRHEIT:** Das KENO-System ist manipuliert. Alle Analysen basieren auf dieser Annahme.

---

## Abgeschlossene Analysen

### Phase 1: Constraint-Analyse (DONE)

| Constraint | Verdict | Evidence |
|------------|---------|----------|
| HOUSE-004 Near-Miss | **ANOMALOUS** | 70x Switch zwischen Normal/Jackpot |
| DIST-003 Sum-Clustering | NATURAL | Zentraler Grenzwertsatz |

### Phase 2: Vorhersage-Tests (DONE)

| Test | Ergebnis | p-Wert |
|------|----------|--------|
| PRED-001 (Pre-GK1 Near-Miss) | FALSIFIZIERT | 0.81 |
| PRED-002 (Wartezeit) | FALSIFIZIERT | 0.125 |
| PRED-003 (Jackpot-Korrelation) | FALSIFIZIERT | 0.83 |

**Erklaerung:** Vorhersagen falsifiziert weil HOUSE-004 jahresspezifisch ist (nur 2023 anomal).

### Phase 3: Jahrliche Segmentierung (DONE)

| Jahr | HOUSE-004 Anomalie | Ratio-Differenz |
|------|-------------------|-----------------|
| 2022 | NEIN | 4.7x |
| 2023 | **JA** | 22.4x |
| 2024 | NEIN | 5.2x |

### Phase 4: Zahlen-Analyse (DONE)

| Analyse | Datei | Erkenntnisse |
|---------|-------|--------------|
| Frequenz-Kontext | number_frequency_context.json | Hot/Cold, Jackpot-favored, Temporal |
| Paar/Trio | number_pairs_analysis.json | 30 starke Paare, 20 starke Trios |
| Near-Miss Indikatoren | near_miss_numbers.json | 20 NM-Indikatoren, 20 JP-Indikatoren |

### Phase 5: Zahlen-GRUPPEN Modell (DONE)

| Komponente | Status | Datei |
|------------|--------|-------|
| Generator | OPERATIONAL | scripts/generate_groups.py |
| Empfehlungen | AKTUELL | results/group_recommendations.json |
| Dokumentation | COMPLETE | docs/NUMBER_GROUP_MODEL.md |

---

## Kernerkenntnisse

### 1. HOUSE-004: Near-Miss Constraint
- Normal-Periode: 25-50x Unterdrueckung von Max-Gewinnen
- Jackpot-Periode: 1.4-2.5x Verstaerkung
- **Intervention Strength:** 70x

### 2. Jahresspezifische Anomalien
- 2023 war das einzige Jahr mit signifikanter HOUSE-004 Anomalie
- Moeglicherweise Systemanpassung oder statistische Fluktuation

### 3. Zahlen-Kategorien

**Jackpot-favored (17 Zahlen):**
```
3, 4, 9, 13, 24, 31, 35, 36, 37, 40, 41, 49, 51, 52, 64, 66, 69
```

**Near-Miss Indikatoren (Top 5):**
```
31, 11, 25, 18, 17
```

**Jackpot Indikatoren (Top 5):**
```
43, 29, 30, 27, 35
```

**Starke Paare (Top 5):**
```
[9, 50], [20, 36], [9, 10], [32, 64], [33, 49]
```

**Starke Trios (Top 3):**
```
[9, 39, 50], [19, 28, 49], [27, 49, 54]
```

### 4. Top-20 Zahlen (Gesamt-Score)
```
3, 51, 37, 24, 4, 49, 13, 41, 36, 66, 9, 64, 31, 52, 45, 25, 40, 2, 1, 21
```

---

## Aktuelle Empfehlungen (29.12.2025)

### Periode: MONATS-ENDE

**KENO Typ 10 - Jackpot-Strategie:**
```
3, 4, 13, 24, 29, 31, 40, 51, 64, 66
```
Score: 313.79

**KENO Typ 10 - Near-Miss-Strategie:**
```
3, 4, 11, 17, 18, 25, 31, 37, 45, 52
```
Score: 169.23

**KENO Typ 10 - Balanced:**
```
3, 13, 24, 31, 36, 45, 49, 51, 52, 66
```
Score: 234.92

---

## Offene Aufgaben

| Prioritaet | Aufgabe | Status |
|------------|---------|--------|
| P1 | Backtest der Gruppen-Empfehlungen | OFFEN |
| P1 | Multi-Game Erweiterung (EuroJackpot, Lotto) | OFFEN |
| P2 | Jackpot-Hoehe Daten sammeln | OFFEN |
| P2 | Regionale Daten (HYP-003) | OFFEN |
| P3 | Echtzeit-Update Pipeline | OFFEN |

---

## Datei-Uebersicht

### Ergebnisse (results/)
- constraint_model.json - Mathematisches Constraint-Modell
- yearly_segmentation.json - Jahrliche HOUSE-004 Analyse
- event_correlation.json - Deutsche Events Korrelation
- number_frequency_context.json - Zahlen-Frequenz Analyse
- number_pairs_analysis.json - Paar/Trio Analyse
- near_miss_numbers.json - Near-Miss Indikatoren
- group_recommendations.json - Aktuelle Gruppen-Empfehlungen
- pred001_pre_gk1_analysis.json - PRED-001 Test
- pred002_waiting_time_analysis.json - PRED-002 Test
- pred003_jackpot_correlation.json - PRED-003 Test

### Dokumentation (docs/)
- CONSTRAINT_MODEL.md - Constraint-Modell Dokumentation
- NUMBER_GROUP_MODEL.md - Gruppen-Modell Dokumentation

### Skripte (scripts/)
- generate_groups.py - Zahlen-Gruppen Generator
- analyze_*.py - Diverse Analyse-Skripte

---

## Naechste Session

1. **Backtest starten:** Historische Validation der Empfehlungen
2. **EuroJackpot Daten laden:** Multi-Game Erweiterung
3. **Lotto 6aus49 integrieren:** Gemeinsame Muster suchen

---

*Automatisch generiert durch Kenobase V2.1.0*
