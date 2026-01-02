I need to output the handoff content directly since Write and Edit tools are not available:

---
status: COMPLETE
task: phase5_task01_backtest_script
role: ARCHITECT
phase: ARCHITECT
files_changed: []
summary:
  - Analyzed existing backtest command in scripts/analyze.py (lines 297-406) - basic but incomplete
  - Identified need for dedicated scripts/backtest.py with full metrics (Precision, Recall, F1, ROI)
  - Pipeline runner.py already exposes PhysicsResult and PipelineResult needed for metrics
  - Config exists in default.yaml with physics/analysis settings
  - DataLoader provides DrawResult with date, numbers, game_type for period splitting
  - Physics metrics module provides stability_score, hurst_exponent, regime_complexity
  - Frequency module provides calculate_rolling_frequency for temporal validation
---
# Rule Confirmation
- Rule 1 (SYSTEM_STATUS + ADR/Docs + git status): CONFIRMED (SYSTEM_STATUS.json does not exist, not a git repo)
- Rule 2 (granularity stated): per-period (backtest evaluates model across time periods)
- Rule 3 (semantics defined): hits=numbers in actual draw, predictions=hot_numbers from prior period
- Rule 4 (target metric): accuracy + calibration (Precision, Recall, F1, stability over time)
- Rule 5 (helper-only boundaries): CONFIRMED
- Rule 6 (reproducibility): `python scripts/backtest.py -d data/raw/keno/KENO.csv -p 12 -o output/backtest.json` -> output/backtest.json or UNVERIFIED (file not yet created)

## Task Setup
- Granularity: per-period (historical walk-forward backtest)
- Semantics:
  - `train_period`: draws used to identify hot/cold numbers
  - `test_period`: subsequent draws used to evaluate predictions
  - `hit`: a predicted hot number appears in actual draw
  - `miss`: a predicted hot number does NOT appear in actual draw
- Target metric: Precision, Recall, F1-Score, Stability-Score (avg across periods)

## Repro Commands
- Create: `python scripts/backtest.py --help` (after implementation)
- Run: `python scripts/backtest.py -d data/raw/keno/KENO.csv -p 12 -o output/backtest.json`
- Verify: Check output/backtest.json for period_results with metrics

---

# Implementierungsplan

## 1. Ziel
Erstelle `scripts/backtest.py` als eigenstaendiges CLI-Script fuer historisches Backtesting gemaess CLAUDE.md Section 5.1 (Phase 5: Validation & Backtest).

## 2. Anforderungen (aus CLAUDE.md)

| Anforderung | Quelle | Status |
|-------------|--------|--------|
| Historischer Backtest auf 12 Monate | Phase 5, Ticket #5.1 | Zu implementieren |
| Precision, Recall, F1 berechnen | Phase 5, Ticket #5.2 | Zu implementieren |
| Report lesbar und aussagekraeftig | Phase 5, Ticket #5.3 | Zu implementieren |
| Integration mit Physics Layer | CLAUDE.md Section 6 | Teilweise in analyze.py |

## 3. Betroffene Dateien

### Neu zu erstellen:
- `scripts/backtest.py` - Haupt-Backtest-Script

### Zu verwenden (read-only):
- `kenobase/pipeline/runner.py` - PipelineRunner, PipelineResult
- `kenobase/core/data_loader.py` - DataLoader, DrawResult
- `kenobase/core/config.py` - load_config
- `kenobase/analysis/frequency.py` - get_hot_numbers, calculate_frequency
- `kenobase/physics/metrics.py` - calculate_stability_score

## 4. Schritt-fuer-Schritt Implementierung

### Step 1: Dataclass-Definitionen (10 LOC)
```python
@dataclass
class BacktestPeriodResult:
    period_id: int
    train_start: datetime
    train_end: datetime
    test_start: datetime
    test_end: datetime
    train_draws: int
    test_draws: int
    predicted_hot: list[int]
    hits: int
    misses: int
    precision: float
    recall: float
    f1_score: float
    stability_score: float
    criticality_level: str
```

### Step 2: Backtest-Engine Klasse (50 LOC)
```python
class BacktestEngine:
    def __init__(self, config: KenobaseConfig):
        self.config = config
        self.runner = PipelineRunner(config)
    
    def run(
        self,
        draws: list[DrawResult],
        n_periods: int = 12,
        train_ratio: float = 0.8
    ) -> BacktestResult:
        """Walk-forward Backtest mit Train/Test Split pro Periode."""
        ...
```

### Step 3: Metriken-Berechnung (30 LOC)
```python
def calculate_metrics(
    predicted: list[int],
    actual_draws: list[DrawResult],
    top_k: int = 20
) -> dict:
    """
    Berechnet Precision, Recall, F1 fuer Hot-Numbers vs Actual.
    
    - Precision = hits / len(predicted)
    - Recall = hits / (hits + numbers_in_draw_not_predicted)
    - F1 = 2 * P * R / (P + R)
    """
```

### Step 4: CLI mit Click (40 LOC)
```python
@click.command()
@click.option("--config", "-c", default="config/default.yaml")
@click.option("--data", "-d", required=True)
@click.option("--periods", "-p", default=12)
@click.option("--train-ratio", default=0.8)
@click.option("--output", "-o")
@click.option("--format", "-f", type=click.Choice(["json", "csv", "markdown"]))
def main(config, data, periods, train_ratio, output, format):
    ...
```

### Step 5: Report-Generierung (20 LOC)
```python
def generate_summary(results: list[BacktestPeriodResult]) -> dict:
    """Aggregiert Metriken ueber alle Perioden."""
    return {
        "avg_precision": mean([r.precision for r in results]),
        "avg_recall": mean([r.recall for r in results]),
        "avg_f1": mean([r.f1_score for r in results]),
        "avg_stability": mean([r.stability_score for r in results]),
        "critical_periods": sum(1 for r in results if r.criticality_level == "CRITICAL"),
        "best_period": max(results, key=lambda r: r.f1_score).period_id,
        "worst_period": min(results, key=lambda r: r.f1_score).period_id,
    }
```

## 5. Acceptance Criteria

| # | Kriterium | Verifikation |
|---|-----------|--------------|
| AC1 | Script laeuft mit --help | `python scripts/backtest.py --help` zeigt Usage |
| AC2 | Backtest auf 12 Monate | Run mit echten KENO-Daten, -p 12 |
| AC3 | Precision/Recall/F1 korrekt | Unit-Test mit bekannten Werten |
| AC4 | Output valides JSON | `jq . output/backtest.json` erfolgreich |
| AC5 | Stability-Score integriert | Physics-Layer Metriken in Ergebnis |
| AC6 | Kein Crash bei wenig Daten | Graceful handling wenn draws < periods*10 |

## 6. Test-Strategie

### Unit-Tests (tests/unit/test_backtest.py):
```python
def test_calculate_metrics_perfect_prediction():
    """100% hit rate -> precision=1.0"""
    
def test_calculate_metrics_no_hits():
    """0% hit rate -> precision=0.0"""
    
def test_backtest_engine_period_split():
    """Verify train/test split is correct"""
    
def test_backtest_engine_minimum_draws():
    """Error when draws < periods * min_per_period"""
```

### Integration-Test:
```python
def test_backtest_cli_e2e(tmp_path, sample_keno_csv):
    """Full CLI run with real CSV produces valid JSON"""
```

## 7. Risiken & Mitigationen

| Risiko | Wahrscheinlichkeit | Mitigation |
|--------|-------------------|------------|
| Nicht genug Daten | MITTEL | Min-Draws Check mit klarer Fehlermeldung |
| Recall-Definition unklar | NIEDRIG | Dokumentieren: Recall = hits / numbers_per_draw |
| Performance bei vielen Perioden | NIEDRIG | Pipeline bereits optimiert |

## 8. Geschaetzter Aufwand
- Implementierung: 2h (wie in CLAUDE.md Phase 5 Ticket 5.1)
- Tests: 1h
- Gesamt: 3h

---

## WORKING_SET_REQUEST fuer EXECUTOR:
- scripts/backtest.py (neu zu erstellen)
- kenobase/pipeline/runner.py (Import: PipelineRunner, PipelineResult, PhysicsResult)
- kenobase/core/data_loader.py (Import: DataLoader, DrawResult)
- kenobase/core/config.py (Import: load_config)
- kenobase/analysis/frequency.py (Import: get_hot_numbers)
- tests/unit/test_backtest.py (neu zu erstellen)
