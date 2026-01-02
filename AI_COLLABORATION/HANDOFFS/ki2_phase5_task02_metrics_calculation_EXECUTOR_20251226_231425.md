---
status: COMPLETE
task: phase5_task02_metrics_calculation
role: EXECUTOR
phase: EXECUTOR
files_changed:
  - kenobase/pipeline/validation_metrics.py (NEW)
  - kenobase/pipeline/__init__.py (MODIFIED)
  - scripts/backtest.py (MODIFIED)
  - tests/unit/test_validation_metrics.py (NEW)
summary:
  - Extrahierte calculate_hits, calculate_precision, calculate_recall, calculate_f1 nach validation_metrics.py
  - Erstellt ValidationMetrics dataclass mit to_dict() Methode
  - calculate_metrics() gibt ValidationMetrics zurueck, calculate_metrics_dict() gibt dict zurueck (Kompatibilitaet)
  - Aktualisiert backtest.py um extrahierte Funktionen zu importieren (keine Funktionsaenderung)
  - Erweitert pipeline/__init__.py mit allen neuen Exports
  - Erstellt 33 Unit-Tests in test_validation_metrics.py - alle bestanden
  - Verifiziert: backtest.py Tests bestehen weiterhin (22/22)
---

# Rule Confirmation
- Rule 1 (SYSTEM_STATUS + ADR/Docs + git status): CONFIRMED (SYSTEM_STATUS.json nicht vorhanden, kein Git-Repo)
- Rule 2 (granularity stated): global
- Rule 3 (semantics defined): Precision/Recall/F1 - hits/total_predictions/total_actual
- Rule 4 (target metric): accuracy
- Rule 5 (helper-only boundaries): CONFIRMED
- Rule 6 (reproducibility): `pytest tests/unit/test_validation_metrics.py tests/unit/test_backtest.py -v`

## Repro Commands
- `pytest tests/unit/test_validation_metrics.py -v` -> 33 passed
- `pytest tests/unit/test_backtest.py -v` -> 22 passed (Regression verified)
