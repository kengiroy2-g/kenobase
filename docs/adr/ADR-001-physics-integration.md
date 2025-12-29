# ADR-001: Physics Layer Integration

**Status:** Accepted
**Date:** 2025-12-27
**Authors:** Kenobase V2.0 Architecture Team
**Deciders:** Project Lead

## Context

Kenobase V2.0 benoetigt ein wissenschaftlich fundiertes Framework fuer die Analyse von Lottozahlen-Mustern. Das alte Kenobase-Projekt (V1-V9) verwendete Ad-hoc-Heuristiken ohne klare Validierungskriterien.

Die v_master_Criticality-Forschung bietet drei physik-inspirierte Model Laws (A/B/C) sowie eine Avalanche-Theorie, die auf Lottozahlen-Analyse uebertragen werden koennen:

1. **Model Law A (Stabilitaet):** Unterscheidet echte Gesetze von Noise
2. **Model Law B (Least-Action):** Waehlt optimale Pipeline-Konfigurationen
3. **Model Law C (Criticality):** Identifiziert instabile/riskante Vorhersagen
4. **Avalanche-Theorie:** Berechnet kumulative Verlustwahrscheinlichkeiten

### Problemstellung

- Wie validieren wir, ob ein erkanntes Muster ein echtes "Gesetz" oder Zufall ist?
- Wie waehlen wir zwischen mehreren Analyse-Pipelines?
- Wie quantifizieren wir das Risiko einer Vorhersage?
- Wie vermeiden wir kaskadierende Verluste bei Multi-Pick-Kombinationen?

## Decision

Wir integrieren die Physics Layer mit drei Modulen:

### 1. Model Laws (`kenobase/physics/model_laws.py`)

#### Law A: Stabilitaetstest

```python
stability = 1 - (std(results) / mean(results))
is_law = stability >= 0.9
```

**Funktion:** `is_law(relation, variations, threshold=0.9)`
**Zweck:** Testet ob eine Relation ueber Variationen (Zeit, Datenquellen, Parameter) stabil bleibt.

**Anwendung auf KENO:**
- Teste ob Zahlen-Muster stabil sind (z.B. "17 erscheint nach 23")
- Nur Muster mit stability >= 0.9 werden als "Gesetze" akzeptiert
- Filtert Noise von echten Regularitaeten

#### Law B: Least-Action

```python
action = complexity + instability - performance
```

Wobei:
- `complexity = num_features * 0.1 + num_rules * 0.05 + num_special_cases * 0.2`
- `instability = performance_variance`
- `performance = roi`

**Funktion:** `calculate_pipeline_action(config: PipelineConfig)`
**Zweck:** Niedrigere Action = bessere Pipeline bei gleicher Performance.

**Anwendung auf KENO:**
- Vergleiche verschiedene Analyse-Methoden
- Waehle einfachste Methode bei gleicher Vorhersagekraft
- Vermeidet Overfitting durch Komplexitaets-Penalty

#### Law C: Criticality-Score

```python
sensitivity = 1.0 - abs(probability - 0.5) * 2.0
criticality = sensitivity * regime_complexity
```

**Warning Levels:**
- `LOW`: criticality < 0.3
- `MEDIUM`: 0.3 <= criticality < 0.5
- `HIGH`: 0.5 <= criticality < 0.7
- `CRITICAL`: criticality >= 0.7

**Funktion:** `calculate_criticality(probability, regime_complexity)`
**Zweck:** Identifiziert instabile Vorhersagen nahe 50% Wahrscheinlichkeit.

**Anwendung auf KENO:**
- Hohe Sensitivity (nahe 50%) + komplexe Verteilungs-Regimes = hohes Risiko
- CRITICAL-Ziehungen werden nicht fuer Vorhersagen verwendet

### 2. Avalanche-Theorie (`kenobase/physics/avalanche.py`)

#### Theta-Berechnung

```python
theta = 1 - precision^n_picks
```

**Avalanche States:**
- `SAFE`: theta < 0.50 (Verlust < 50%)
- `MODERATE`: 0.50 <= theta < 0.75
- `WARNING`: 0.75 <= theta < 0.85
- `CRITICAL`: theta >= 0.85 (Verlust >= 85%)

**Funktionen:**
- `calculate_theta(precision, n_picks)`: Berechnet Verlustwahrscheinlichkeit
- `get_avalanche_state(theta)`: Klassifiziert in State
- `is_profitable(precision, avg_odds)`: Prueft p * q > 1

**Anwendung auf KENO:**
- 6er-Kombination mit 70% Precision: theta = 1 - 0.7^6 = 0.88 -> CRITICAL!
- Anti-Avalanche: Limitiere Picks so dass theta <= 0.75
- Break-Even nur wenn Precision * Quote > 1

### 3. Physics Metrics (`kenobase/physics/metrics.py`)

Unterstuetzende Metriken fuer die Physics Layer:

- `calculate_hurst_exponent(series)`: Langfristige Abhaengigkeit
  - H < 0.5: Mean-reverting
  - H = 0.5: Random walk
  - H > 0.5: Trending
- `calculate_autocorrelation(series, lag)`: Zeitliche Korrelation
- `count_regime_peaks(series)`: Anzahl Regime-Wechsel
- `calculate_stability_score(series)`: CV-basierter Stabilitaets-Score

## Consequences

### Positive

1. **Falsifizierbarkeit:** Alle Hypothesen haben klare Acceptance-Kriterien
2. **Risiko-Management:** Avalanche-States verhindern riskante Kombinationen
3. **Einfachheit:** Least-Action bevorzugt einfachere Modelle
4. **Wissenschaftliche Basis:** Physik-Konzepte (SOC, Criticality) sind etabliert
5. **Konfigurierbar:** Schwellenwerte in `config/default.yaml` anpassbar

### Negative

1. **Komplexitaet:** Zusaetzliche Layer erhoet Code-Komplexitaet
2. **Lernkurve:** Entwickler muessen Physics-Konzepte verstehen
3. **False Negatives:** Zu strenge Kriterien koennten valide Muster ablehnen

### Neutral

1. **Performance:** Minimaler Overhead (O(n) fuer meiste Berechnungen)
2. **Testbarkeit:** Alle Funktionen sind unit-testbar mit synthetischen Daten

## References

### Implementierung

- `kenobase/physics/model_laws.py`: Lines 19-63 (Law A), 110-142 (Law B), 173-213 (Law C)
- `kenobase/physics/avalanche.py`: Lines 38-61 (theta), 64-86 (states), 116-132 (profitable)
- `kenobase/physics/metrics.py`: Lines 14-84 (Hurst), 87-129 (Autocorrelation)

### Externe Referenzen

- Bak, P. (1987). "Self-organized criticality: 1/f noise"
- Sornette, D. (2003). "Why Stock Markets Crash"
- Prigogine, I. (1977). "Self-Organization in Nonequilibrium Systems"

### Interne Dokumente (v_master_Criticality)

- `AI_COLLABORATION/ARCHITECTURE/ADR_018_MODEL_LAWS_ALPHA_GAMMA.md`
- `AI_COLLABORATION/ARCHITECTURE/ADR_020_CRITICALITY_BASED_FP_DETECTION.md`
- `AI_COLLABORATION/ARCHITECTURE/ADR_021_AVALANCHE_CRITIQUE_COMBI_THEORY.md`
