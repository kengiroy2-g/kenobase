# ADR: Prediction Model Architecture

**Status:** ACCEPTED
**Date:** 2025-12-27
**Author:** EXECUTOR (TASK-S02)

## Context

Kenobase V2.0 benoetigt ein Vorhersage-Modell das:
1. Ergebnisse aus verschiedenen Hypothesen-Analysen (HYP-007 bis HYP-012) kombiniert
2. Physics-Layer Konzepte (Criticality, Avalanche) integriert
3. Messbare Metriken liefert (Ziel: F1 >= 0.45, aktuell 0.4434)

## Decision

### Architektur-Ueberblick

```
[HYP-Analysen] --> [Synthesizer] --> [Recommendation Engine] --> [Output]
     |                  |                    |
     v                  v                    v
  results/*.json   combined_score      predictions.json
                   per number (1-70)
```

### Komponenten

#### 1. HypothesisSynthesizer (kenobase/prediction/synthesizer.py)

Kombiniert Scores aus verschiedenen Hypothesen:

| Hypothese | Default-Gewicht | Signifikanz-Multiplikator |
|-----------|-----------------|---------------------------|
| HYP-007   | 0.1             | 1.0 (nicht signifikant)   |
| HYP-010   | 0.3             | 1.0 (nicht signifikant)   |
| HYP-011   | 0.3             | 1.5x wenn signifikant     |
| HYP-012   | 0.3             | 1.5x wenn signifikant     |

**Signifikanz-basierte Gewichtung (bereits implementiert):**
- Zeile 186: `weight=self.weights.get("HYP-011", 0.3) * (1.5 if is_sig else 1.0)`
- Zeile 221: `weight=self.weights.get("HYP-012", 0.3) * (1.5 if payout_sig else 1.0)`

**Score-Berechnung:**
```python
combined_score = sum(score * weight) / sum(weights)
```

**Tier-Klassifikation:**
- Tier A: combined_score >= 0.7 (starke Empfehlung)
- Tier B: 0.5 <= combined_score < 0.7 (moderate Empfehlung)
- Tier C: combined_score < 0.5 (keine Empfehlung)

#### 2. Recommendation Engine (kenobase/prediction/recommendation.py)

Wandelt Scores in Spielempfehlungen um unter Beruecksichtigung von:

1. **Zehnergruppen-Filter** (max 2 pro Gruppe)
   - Verhindert Cluster in einer Dekade
   - Implementiert in `apply_decade_filter()`

2. **Anti-Avalanche-Limit** (max 4 Zahlen empfohlen)
   - Basiert auf ADR-021: theta = 1 - p^n
   - Bei 6 Zahlen mit p=0.7: theta = 0.88 (CRITICAL)
   - Bei 4 Zahlen mit p=0.7: theta = 0.76 (WARNING)

3. **Tier-basierte Priorisierung**
   - Tier A Zahlen werden bevorzugt
   - Gruende aus signifikanten Hypothesen werden angezeigt

### Physics-Layer Integration

#### Criticality-Scoring (kenobase/physics/model_laws.py)

```python
def calculate_criticality(probability, regime_complexity):
    sensitivity = 1.0 - abs(probability - 0.5) * 2.0
    criticality = sensitivity * regime_complexity
    # Returns: (score, "LOW"|"MEDIUM"|"HIGH"|"CRITICAL")
```

**Anwendung auf Vorhersagen:**
- Zahlen mit CRITICAL Criticality werden herabgestuft
- Regime-Complexity = Anzahl Peaks in historischer Verteilung

#### Avalanche-Theorie (kenobase/physics/avalanche.py)

```python
def calculate_theta(precision, n_picks):
    return 1.0 - (precision ** n_picks)

def get_avalanche_state(theta):
    if theta < 0.50: return "SAFE"
    elif theta < 0.75: return "MODERATE"
    elif theta < 0.85: return "WARNING"
    else: return "CRITICAL"
```

**Anti-Avalanche-Strategie:**
- Max 4 Zahlen pro Empfehlung
- Warnung bei mehr als 4 Zahlen
- Formel: `max_picks_for_theta(precision, max_theta)`

### Datenfluss

```
1. results/hyp007_*.json ─┐
2. results/hyp010_*.json ─┼─> HypothesisSynthesizer.load_results()
3. results/hyp011_*.json ─┤        │
4. results/hyp012_*.json ─┘        v
                          HypothesisSynthesizer.synthesize()
                                   │
                                   v
                          dict[int, NumberScore]  (70 Zahlen)
                                   │
                                   v
                          generate_recommendations()
                                   │
                          ┌────────┴────────┐
                          v                 v
                  Zehnergruppen-     Avalanche-
                  Filter             Limit (4)
                                   │
                                   v
                          list[Recommendation]
                                   │
                                   v
                          results/prediction.json
```

### CLI-Interface (scripts/predict.py)

```bash
# Standard-Ausgabe (6 Zahlen)
python scripts/predict.py

# Anti-Avalanche-konform (4 Zahlen)
python scripts/predict.py --top 4

# JSON-Export
python scripts/predict.py --output results/prediction.json

# Detaillierte Ausgabe
python scripts/predict.py --verbose --all-scores
```

## Erweiterungsphasen

### Phase 1: Foundation (aktueller Stand)
- [x] HypothesisSynthesizer implementiert
- [x] Signifikanz-basierte Gewichtung (1.5x Multiplikator)
- [x] Recommendation Engine mit Filtern
- [x] CLI-Interface

### Phase 2: ML-Integration (geplant)
- [ ] Historische Backtest-Daten als Training-Set
- [ ] Feature-Engineering aus Hypothesen-Scores
- [ ] Gradient Boosting / XGBoost fuer Ranking
- [ ] Metriken: F1 >= 0.45

### Phase 3: Ensemble (geplant)
- [ ] Kombination mehrerer Modelle
- [ ] Confidence-Calibration
- [ ] Uncertainty-Quantification

### Phase 4: Continuous Learning (geplant)
- [ ] Automatische Daten-Updates
- [ ] Online-Learning fuer neue Ziehungen
- [ ] Performance-Monitoring

## Akzeptanzkriterien

| Metrik | Aktuell | Ziel |
|--------|---------|------|
| Backtest F1-Score | 0.4434 | >= 0.45 |
| Tier-A Precision | - | >= 0.6 |
| Anti-Avalanche Compliance | Ja | 100% |

## Reproduzierbarkeit

```bash
# Vorhersage generieren
python scripts/predict.py --config config/default.yaml --top 6

# Output: results/prediction.json
# Enthält: timestamp, hypotheses_used, recommendations, tier_summary
```

## Consequences

### Positive
- Modulare Architektur erlaubt einfache Erweiterung
- Physics-Layer verhindert uebertriebenes Risiko (Anti-Avalanche)
- Signifikanz-basierte Gewichtung priorisiert robuste Signale
- Per-number Scores (1-70) vermeiden globalen Threshold-Bug

### Negative
- Aktuelle F1 (0.4434) leicht unter Ziel (0.45)
- ML-Integration noch nicht implementiert
- Keine Online-Learning Kapazitaet

## Related ADRs
- ADR-018: Model Laws A/B/C
- ADR-020: Criticality-Based FP Detection
- ADR-021: Avalanche Critique Combi Theory

## Files
- `kenobase/prediction/synthesizer.py` - Score-Kombination
- `kenobase/prediction/recommendation.py` - Empfehlungs-Engine
- `scripts/predict.py` - CLI-Interface
- `tests/unit/test_synthesizer.py` - Unit-Tests
- `kenobase/physics/model_laws.py` - Criticality-Funktionen
- `kenobase/physics/avalanche.py` - Anti-Avalanche-Logik
