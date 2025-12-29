# KENO Zahlen-GRUPPEN Modell v1.0

**Erstellt:** 2025-12-29
**Paradigma:** System ist manipuliert (Grundwahrheit)

---

## Executive Summary

Das Modell integriert ALLE gefundenen Anomalien und generiert optimale Zahlen-GRUPPEN fuer KENO Typ 5-10 basierend auf drei Strategien:

| Strategie | Ziel | Beschreibung |
|-----------|------|--------------|
| **near_miss** | k-1 Treffer | Maximiere Wahrscheinlichkeit fuer Near-Miss (8/9 oder 9/10) |
| **jackpot** | k/k Treffer | Maximiere Wahrscheinlichkeit fuer Hauptgewinn |
| **balanced** | Ausgeglichen | Mix aus beiden Strategien |

---

## Integrierte Anomalien

### 1. Frequenz-basierte Anomalien

| Kategorie | Zahlen | Beschreibung |
|-----------|--------|--------------|
| **HOT** (>680) | 49, 64 | Ueberdurchschnittlich haeufig |
| **COLD** (<600) | 1, 37, 45 | Unterdurchschnittlich haeufig |
| **Jackpot-favored** | 3, 4, 9, 13, 24, 31, 35, 36, 37, 40, 41, 49, 51, 52, 64, 66, 69 | Erscheinen haeufiger an Jackpot-Tagen |

### 2. Temporale Anomalien

| Periode | Zahlen | Kontext |
|---------|--------|---------|
| **Monats-Start (1-5)** | 16, 20, 21, 25, 26, 33, 39, 41, 53, 55, 56, 60 | Bevorzugt am Monatsanfang |
| **Monats-Ende (25-31)** | 1, 2, 24, 34, 45, 48 | Bevorzugt am Monatsende |

### 3. Near-Miss Indikatoren

| Typ | Top-5 Zahlen | Interpretation |
|-----|--------------|----------------|
| **Near-Miss** | 31, 11, 25, 18, 17 | Erscheinen haeufiger an Tagen mit vielen Near-Miss Gewinnern |
| **Jackpot** | 43, 29, 30, 27, 35 | Erscheinen haeufiger an Tagen mit wenigen Near-Misses |

### 4. Paar- und Trio-Synergien

**Starkste Paare (>20% ueber Erwartung):**
```
[9, 50]   23.9%
[20, 36]  23.9%
[9, 10]   23.3%
[32, 64]  21.6%
[33, 49]  21.0%
```

**Starkste Trios (>50% ueber Erwartung):**
```
[9, 39, 50]   63.1%
[19, 28, 49]  58.8%
[27, 49, 54]  58.8%
[7, 9, 10]    58.8%
```

---

## Scoring-Modell

### Formel

```
GroupScore(Z, Strategy, Date) =
    BaseScore * ContextMultiplier
  + PairBonus
  + TrioBonus
  - DecadePenalty
  + StrategyBonus
```

### Komponenten

| Komponente | Berechnung |
|------------|------------|
| **BaseScore** | Summe der Einzel-Scores (Predictability + Lift + Deviation) |
| **ContextMultiplier** | 1.3x wenn Zahl zur Monatsperiode passt |
| **PairBonus** | +5 pro starkes Paar in der Gruppe |
| **TrioBonus** | +10 pro starkes Trio in der Gruppe |
| **DecadePenalty** | -5 wenn >2 Zahlen aus gleicher Dekade |
| **StrategyBonus** | +10-15 pro Zahl die zur Strategie passt |

---

## Empfehlungen (Stand: 2025-12-29)

### KENO Typ 10

| Strategie | Zahlen | Score |
|-----------|--------|-------|
| **NEAR_MISS** | 3, 4, 11, 17, 18, 25, 31, 37, 45, 52 | 169.23 |
| **JACKPOT** | 3, 4, 13, 24, 29, 31, 40, 51, 64, 66 | 313.79 |
| **BALANCED** | 3, 13, 24, 31, 36, 45, 49, 51, 52, 66 | 234.92 |

### KENO Typ 8

| Strategie | Zahlen | Score |
|-----------|--------|-------|
| **NEAR_MISS** | 2, 3, 11, 17, 18, 24, 25, 31 | 144.46 |
| **JACKPOT** | 4, 24, 36, 37, 40, 49, 51, 52 | 272.73 |
| **BALANCED** | 2, 4, 13, 24, 36, 37, 51, 66 | 190.02 |

### KENO Typ 6

| Strategie | Zahlen | Score |
|-----------|--------|-------|
| **NEAR_MISS** | 3, 11, 17, 24, 25, 31 | 118.68 |
| **JACKPOT** | 9, 13, 24, 37, 49, 51 | 218.41 |
| **BALANCED** | 4, 13, 24, 37, 51, 66 | 156.46 |

---

## Top-20 Zahlen (Gesamt-Score)

```
3, 51, 37, 24, 4, 49, 13, 41, 36, 66, 9, 64, 31, 52, 45, 25, 40, 2, 1, 21
```

Diese Zahlen haben die hoechsten kombinierten Scores aus:
- Jackpot-Preference (Lift)
- Predictability
- Near-Miss Indicator Score
- Temporale Stabilität

---

## Verwendung

```python
from scripts.generate_groups import NumberGroupModel
import datetime

model = NumberGroupModel()

# Empfehlungen fuer ein bestimmtes Datum
date = datetime.date(2025, 12, 29)
recommendations = model.generate_recommendations(date=date)

# Einzelne Gruppe bewerten
group = [3, 9, 24, 49, 51, 64]
score = model.calculate_group_score(group, strategy="jackpot", date=date)
print(score)
```

---

## Limitationen

1. **20 GK1-Events:** Begrenzte statistische Power fuer Jackpot-Analyse
2. **Keine Jackpot-Hoehe:** Korrelation nicht testbar
3. **Keine regionalen Daten:** HYP-003 nicht testbar
4. **System-Opazitaet:** Volle Mechanismen nicht bekannt

---

## Naechste Schritte

1. **Backtest:** Historische Validation der Gruppen-Empfehlungen
2. **Multi-Game:** Erweiterung auf EuroJackpot und Lotto 6aus49
3. **Echtzeit-Updates:** Integration neuer Ziehungsdaten
4. **Jackpot-Hoehe:** Wenn Daten verfuegbar, PRED-003 erneut testen

---

*Generiert durch Kenobase V2.0 Number-GROUP Model*
