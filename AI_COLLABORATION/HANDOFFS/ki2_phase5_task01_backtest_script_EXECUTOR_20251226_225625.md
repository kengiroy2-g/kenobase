---
status: COMPLETE
task: phase5_task01_backtest_script
role: EXECUTOR
phase: EXECUTOR
files_changed:
  - scripts/backtest.py
  - tests/unit/test_backtest.py
summary:
  - Created scripts/backtest.py with BacktestEngine, BacktestPeriodResult, BacktestResult
  - Implemented walk-forward backtest with train/test split per period
  - Added calculate_hits(), calculate_metrics() for Precision/Recall/F1 calculation
  - Integrated Physics Layer (stability_score, criticality_level) via PipelineRunner
  - Created CLI with click: --data, --periods, --train-ratio, --output, --format
  - Added JSON and Markdown output formatters
  - Created tests/unit/test_backtest.py with 22 unit tests (all pass)
  - Tests cover: metrics, engine period split, summary generation, output formatting, edge cases
---
# Rule Confirmation
- Rule 1 (SYSTEM_STATUS + ADR/Docs + git status): CONFIRMED (SYSTEM_STATUS.json missing, not a git repo)
- Rule 2 (granularity stated): per-period (walk-forward backtest across time periods)
- Rule 3 (semantics defined): hits=predicted hot in actual draw, precision=hits/predicted, recall=hits/drawn
- Rule 4 (target metric): accuracy + calibration (Precision, Recall, F1, Stability)
- Rule 5 (helper-only boundaries): CONFIRMED
- Rule 6 (reproducibility): `PYTHONPATH=. python scripts/backtest.py --help` -> Usage info (verified)

## Task Setup
- Granularity: per-period (historical walk-forward backtest)
- Semantics: train_period=draws for prediction, test_period=draws for evaluation, hit=hot number in actual draw
- Target metric: Precision, Recall, F1-Score, Stability-Score

## Repro Commands
- `PYTHONPATH=. python scripts/backtest.py --help` -> Usage info (verified, exits 0)
- `PYTHONPATH=. python -m pytest tests/unit/test_backtest.py -v` -> 22 passed in 0.50s

# Umsetzung

## Erstellte Dateien

### scripts/backtest.py (~400 LOC)
- **BacktestPeriodResult**: Dataclass fuer einzelne Perioden-Ergebnisse
- **BacktestResult**: Dataclass fuer Gesamt-Backtest mit Summary
- **calculate_hits()**: Zaehlt Treffer von vorhergesagten Zahlen
- **calculate_metrics()**: Berechnet Precision, Recall, F1
- **BacktestEngine**: Walk-Forward Engine mit PipelineRunner Integration
- **format_result_json()** / **format_result_markdown()**: Output Formatter
- **CLI**: Click-basiert mit --data, --periods, --train-ratio, --output, --format

### tests/unit/test_backtest.py (~350 LOC)
- 22 Unit-Tests: Hits, Metrics, Engine, Formatting, Edge Cases
- Alle Tests bestanden

## Acceptance Criteria

| # | Kriterium | Status |
|---|-----------|--------|
| AC1 | --help funktioniert | PASS |
| AC2 | 12 Perioden moeglich | PASS |
| AC3 | Precision/Recall/F1 korrekt | PASS |
| AC4 | Valides JSON Output | PASS |
| AC5 | Stability-Score integriert | PASS |
| AC6 | Graceful bei wenig Daten | PASS |
