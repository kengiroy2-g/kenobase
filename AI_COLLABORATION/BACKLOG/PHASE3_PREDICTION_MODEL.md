# Phase 3: Prediction Model V2 - Backlog

**Erstellt:** 2025-12-28
**Basis:** Ergebnisse aus Phase 2 (Reverse Engineering)
**Status:** BEREIT FUER LOOP

---

## Executive Summary

Phase 2 hat 16 Tasks abgeschlossen und klare Erkenntnisse geliefert:

### Bestaetigt (als Features verwenden)
| Hypothese | Ergebnis | Feature-Wert |
|-----------|----------|--------------|
| Anti-Cluster Reset | 100% Reset nach 5+ | HIGH |
| Summen-Fenster [605-845] | 87% Coverage | MEDIUM |
| Holiday-Effekt | Signifikant | MEDIUM |
| Top-20 Pool | F1=0.247 optimal | HIGH |

### Falsifiziert (NICHT verwenden)
| Hypothese | Ergebnis | Grund |
|-----------|----------|-------|
| 111-Prinzip | p=0.96 | Kein Unterschied zu Random |
| Popularity Manipulation | p=0.79 | Keine Korrelation |
| Zehnergruppen-Regel | p=nan | Kein Effekt |

---

## KRITISCH (Blocker)

### TASK-P01: Feature Engineering Pipeline
**Prioritaet:** KRITISCH (P0)
**Aufwand:** 4h
**Status:** OFFEN

**Ziel:**
Bestaetigt Features in einheitliche Pipeline integrieren.

**Features zu implementieren:**
```python
features = {
    "cluster_reset": {
        "source": "hyp003_cluster_reset.json",
        "logic": "Nach 5+ Erscheinungen -> Reset-Signal",
        "weight": 1.4  # Lift aus Analyse
    },
    "sum_window": {
        "source": "sum_windows_analysis.json",
        "logic": "Summe in [605-845] = OK",
        "coverage": 0.87
    },
    "pool_top20": {
        "source": "pool_optimization.json",
        "logic": "Top-20 pro Periode statt Top-11",
        "f1_gain": 0.05
    },
    "holiday_effect": {
        "source": "hyp011_temporal_cycles.json",
        "logic": "Feiertage beruecksichtigen"
    }
}
```

**Acceptance Criteria:**
- [ ] `kenobase/prediction/feature_pipeline.py` erstellt
- [ ] Alle 4 Features integriert
- [ ] Unit-Tests fuer jedes Feature
- [ ] Feature-Importance Ranking

---

### TASK-P02: ML Model Selection
**Prioritaet:** KRITISCH (P0)
**Aufwand:** 3h
**Status:** OFFEN

**Ziel:**
Optimales ML-Modell fuer Zahlenvorhersage waehlen.

**Kandidaten:**
| Modell | Pro | Contra |
|--------|-----|--------|
| Random Forest | Robust, Feature Importance | Langsam |
| XGBoost | Schnell, akkurat | Overfitting-Risiko |
| LightGBM | Sehr schnell | Weniger interpretierbar |
| Logistic Regression | Interpretierbar | Weniger akkurat |

**Acceptance Criteria:**
- [ ] 3+ Modelle getestet
- [ ] Cross-Validation (5-fold)
- [ ] Bestes Modell dokumentiert
- [ ] Hyperparameter-Tuning

---

### TASK-P03: Walk-Forward Backtest Framework
**Prioritaet:** KRITISCH (P0)
**Aufwand:** 4h
**Status:** OFFEN

**Ziel:**
Robustes Backtest-Framework mit Walk-Forward Validation.

**Schema:**
```
[Train: 6 Monate] -> [Test: 1 Monat] -> Shift -> Repeat
         |                    |
         v                    v
    Model trainieren    Metriken messen
```

**Acceptance Criteria:**
- [ ] Walk-Forward mit konfigurierbaren Fenstern
- [ ] Metriken pro Periode: Precision, Recall, F1, ROI
- [ ] Stabilitaets-Analyse ueber alle Perioden
- [ ] Visualisierung der Ergebnisse

---

## HOCH (Core Features)

### TASK-P04: Anti-Cluster Trading Signal
**Prioritaet:** HOCH
**Aufwand:** 2h
**Status:** OFFEN

**Ziel:**
Trading-Signal basierend auf Anti-Cluster Reset implementieren.

**Logik:**
```python
def get_cluster_signal(number: int, history: list[int]) -> str:
    consecutive = count_consecutive_appearances(number, history)
    if consecutive >= 5:
        return "NO_BET"  # Reset erwartet
    elif consecutive >= 3:
        return "CAUTION"
    else:
        return "NEUTRAL"
```

**Acceptance Criteria:**
- [ ] Signal-Generator implementiert
- [ ] Integration in Prediction Pipeline
- [ ] Backtest zeigt positive ROI-Auswirkung

---

### TASK-P05: Summen-Filter Integration
**Prioritaet:** HOCH
**Aufwand:** 2h
**Status:** OFFEN

**Ziel:**
Kombinationen mit Summe ausserhalb [605-845] filtern.

**Logik:**
```python
def is_valid_sum(combination: list[int]) -> bool:
    total = sum(combination)
    return 605 <= total <= 845  # 87% Coverage
```

**Acceptance Criteria:**
- [ ] Filter in Kombinations-Engine integriert
- [ ] Konfigurierbarer Bereich in config.yaml
- [ ] Precision-Improvement gemessen

---

### TASK-P06: Ensemble Prediction Model
**Prioritaet:** HOCH
**Aufwand:** 4h
**Status:** OFFEN

**Ziel:**
Ensemble aus bestaetigten Features + ML-Modell.

**Architektur:**
```
┌─────────────────────────────────────────┐
│           ENSEMBLE PREDICTOR            │
├─────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐       │
│  │ Rule-Based  │  │  ML-Model   │       │
│  │  (0.4 wt)   │  │  (0.6 wt)   │       │
│  └──────┬──────┘  └──────┬──────┘       │
│         │                │              │
│         v                v              │
│     ┌───────────────────────────┐       │
│     │    Weighted Combination   │       │
│     └─────────────┬─────────────┘       │
│                   v                     │
│         Final Prediction                │
└─────────────────────────────────────────┘
```

**Acceptance Criteria:**
- [ ] Ensemble-Klasse implementiert
- [ ] Gewichtungs-Optimierung
- [ ] F1 >= 0.50 (Verbesserung von 0.44)

---

### TASK-P07: Prediction CLI
**Prioritaet:** HOCH
**Aufwand:** 2h
**Status:** OFFEN

**Ziel:**
CLI fuer taegliche Vorhersagen.

**Usage:**
```bash
python scripts/predict.py --game keno --date 2025-01-01 --top 10

# Output:
# Predicted Hot Numbers for 2025-01-01:
# 1. 23 (score: 0.82, signals: [CLUSTER_SAFE, SUM_OK])
# 2. 45 (score: 0.78, signals: [CLUSTER_SAFE, SUM_OK])
# ...
```

**Acceptance Criteria:**
- [ ] CLI mit --game, --date, --top Optionen
- [ ] JSON + Human-Readable Output
- [ ] Signal-Erklaerung pro Zahl

---

## MITTEL (Erweiterungen)

### TASK-P08: EuroJackpot Model Transfer
**Prioritaet:** MITTEL
**Aufwand:** 3h
**Status:** OFFEN

**Ziel:**
KENO-Modell auf EuroJackpot uebertragen.

**Anpassungen:**
- Pool: 1-50 statt 1-70
- Combo-Size: 5+2 statt 20
- Thresholds anpassen

**Acceptance Criteria:**
- [ ] EuroJackpot-spezifische Config
- [ ] Backtest F1 >= 0.15 (aktuell 0.147)
- [ ] Feature-Importance Vergleich

---

### TASK-P09: Lotto 6aus49 Model Transfer
**Prioritaet:** MITTEL
**Aufwand:** 3h
**Status:** OFFEN

**Ziel:**
KENO-Modell auf Lotto 6aus49 uebertragen.

**Anpassungen:**
- Pool: 1-49
- Combo-Size: 6
- Weniger Daten (2x/Woche)

**Acceptance Criteria:**
- [ ] Lotto-spezifische Config
- [ ] Backtest dokumentiert
- [ ] Erkenntnisse fuer Cross-Validation

---

### TASK-P10: Live Prediction Tracking
**Prioritaet:** MITTEL
**Aufwand:** 4h
**Status:** OFFEN

**Ziel:**
System fuer Tracking von Live-Vorhersagen.

**Schema:**
```
[Vorhersage] -> [Warten auf Ziehung] -> [Vergleich] -> [Metriken Update]
     |                                       |
     v                                       v
predictions.json                    tracking.json
```

**Acceptance Criteria:**
- [ ] Vorhersage-Log mit Timestamp
- [ ] Automatischer Vergleich nach Ziehung
- [ ] Kumulierte Metriken (Precision, ROI)
- [ ] Dashboard/Report

---

### TASK-P11: Confidence Intervals
**Prioritaet:** MITTEL
**Aufwand:** 2h
**Status:** OFFEN

**Ziel:**
Konfidenzintervalle fuer Vorhersagen berechnen.

**Logik:**
```python
def predict_with_confidence(numbers: list[int]) -> dict:
    predictions = []
    for n in numbers:
        score = model.predict_proba(n)
        ci_lower, ci_upper = bootstrap_confidence(score, n_samples=1000)
        predictions.append({
            "number": n,
            "score": score,
            "ci_95": [ci_lower, ci_upper]
        })
    return predictions
```

**Acceptance Criteria:**
- [ ] Bootstrap CI implementiert
- [ ] 95% und 99% Intervalle
- [ ] Visualisierung

---

## NIEDRIG (Nice-to-Have)

### TASK-P12: Web Dashboard
**Prioritaet:** NIEDRIG
**Aufwand:** 6h
**Status:** OFFEN

**Ziel:**
Einfaches Web-Dashboard fuer Vorhersagen.

**Features:**
- Aktuelle Vorhersage anzeigen
- Historische Performance
- Feature-Importance Visualisierung

**Tech Stack:**
- Streamlit (schnell zu implementieren)
- Oder: Flask + Chart.js

---

### TASK-P13: Telegram/Discord Bot
**Prioritaet:** NIEDRIG
**Aufwand:** 4h
**Status:** OFFEN

**Ziel:**
Bot fuer taegliche Vorhersage-Benachrichtigungen.

**Features:**
- Taegliche Vorhersage um 18:00
- Ergebnis-Tracking
- Performance-Report woechentlich

---

### TASK-P14: Model Explainability (SHAP)
**Prioritaet:** NIEDRIG
**Aufwand:** 3h
**Status:** OFFEN

**Ziel:**
SHAP-Werte fuer Model-Interpretation berechnen.

**Features:**
- Feature-Importance global
- Local Explanations pro Vorhersage
- Visualisierungen

---

## Empfohlene Loop-Reihenfolge

```
Phase 1: KRITISCH (Foundation)
├── TASK-P01: Feature Engineering Pipeline
├── TASK-P02: ML Model Selection
└── TASK-P03: Walk-Forward Backtest Framework

Phase 2: HOCH (Core)
├── TASK-P04: Anti-Cluster Trading Signal
├── TASK-P05: Summen-Filter Integration
├── TASK-P06: Ensemble Prediction Model
└── TASK-P07: Prediction CLI

Phase 3: MITTEL (Transfer)
├── TASK-P08: EuroJackpot Model Transfer
├── TASK-P09: Lotto 6aus49 Model Transfer
├── TASK-P10: Live Prediction Tracking
└── TASK-P11: Confidence Intervals

Phase 4: NIEDRIG (Optional)
├── TASK-P12: Web Dashboard
├── TASK-P13: Telegram/Discord Bot
└── TASK-P14: Model Explainability
```

---

## Abhaengigkeiten

```
P01 ──┬──> P04
      ├──> P05
      └──> P06 ──> P07
            │
P02 ────────┘
            │
P03 ────────┴──> P10

P06 ──┬──> P08
      └──> P09
```

---

## Metriken-Ziele

| Metrik | Aktuell | Ziel Phase 3 |
|--------|---------|--------------|
| F1-Score KENO | 0.4434 | >= 0.50 |
| F1-Score EuroJackpot | 0.1466 | >= 0.20 |
| Precision | 0.71 | >= 0.75 |
| Recall | 0.34 | >= 0.40 |
| Stability (std F1) | 0.08 | <= 0.05 |

---

## Changelog

- 2025-12-28: Initiale Erstellung aus Phase 2 Ergebnissen
