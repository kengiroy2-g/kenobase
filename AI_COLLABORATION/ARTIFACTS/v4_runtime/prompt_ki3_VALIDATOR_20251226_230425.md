AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P5-01: Backtest-Script implementieren
TASK-ID: phase5_task01_backtest_script
PRIORITY: P1
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-26 23:01:25] phase5_task01_backtest_script - EXECUTOR (ki2)

### Summary
- Created scripts/backtest.py with BacktestEngine, BacktestPeriodResult, BacktestResult
- Implemented walk-forward backtest with train/test split per period
- Added calculate_hits(), calculate_metrics() for Precision/Recall/F1 calculation
- Integrated Physics Layer (stability_score, criticality_level) via PipelineRunner
- Created CLI with click: --data, --periods, --train-ratio, --output, --format
- Added JSON and Markdown output formatters
- Created tests/unit/test_backtest.py with 22 unit tests (all pass)
- Tests cover: metrics, engine period split, summary generation, output formatting, edge cases

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_phase5_task01_backtest_script_EXECUTOR_20251226_225625.md

## [2025-12-26 23:04:25] phase5_task01_backtest_script - PROXY_IMPL (ki0)

### Summary
- Created scripts/backtest.py (~615 LOC) with BacktestEngine, dataclasses, CLI
- Walk-forward backtest with train/test split per period implemented correctly
- Metrics (Precision/Recall/F1) semantics match ARCHITECT definition
- Physics Layer integration via PipelineRunner (stability_score, criticality_level)
- CLI with click: --data, --periods, --train-ratio, --output, --format working
- tests/unit/test_backtest.py with 22 unit tests ALL PASS (verified)
- Syntax check passed for both files (py_compile)
- get_hot_numbers threshold usage correct (max_frequency_threshold as hot_threshold)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase5_task01_backtest_script_PROXY_IMPL_20251226_230125.md



MANDATORY WORKFLOW (do first, every task incl docs):
1) Context-sync: read AI_COLLABORATION/SYSTEM_STATUS.json + relevant ADR/Docs; run git status --porcelain.
2) Data claims must cite artifact path + filter + N + repro command (no placeholders).
3) Zero != missing: if unclear, mark UNVERIFIED.
4) Line refs must be verified via: 
l -ba <file> | sed -n 'a,bp'.
5) Deliverable must include: changes + summary + repro commands + CURRENT_STATUS update.
6) No assumptions: verify from current repo snapshot.

RULE CONFIRMATION REQUIRED:
- Include "Rule Confirmation" block in output (CONFIRMED/UNVERIFIED).
- State granularity + semantics + target metric before analysis.

WORKING SET (nur relevante Dateien):
- scripts/backtest.py
- tests/unit/test_backtest.py

WORKING SET POLICY (enforced in ARCHITECT/PROXY/VALIDATOR):
- Read() ausserhalb WORKING SET kann technisch geblockt sein.
- Wenn du eine Datei ausserhalb brauchst: nutze Grep/Glob, dann fordere sie im Handoff an:

WORKING_SET_REQUEST:
- relative/path/to/file1
- relative/path/to/file2
(max 6)


WORKDIR:
- Du bist bereits im Repo-Root: C:\Users\kenfu\Documents\keno_base
- Vermeide Set-Location/cd auf \\?\\-Pfade (Windows long-path Prefix kann Tools verwirren)
ROLLE: VALIDATOR
AUFGABE: Validiere die Implementation.

EFFIZIENZ-REGELN:
- Tests nur zielgerichtet (klein starten). Keine riesigen Logs in die Antwort; speichere nach AI_COLLABORATION/ARTIFACTS/ und verlinke.
- Vermeide Repo-weite Scans; nutze WORKING SET + gezielte Reads.

VORHERIGER OUTPUT (kurz):
- Created scripts/backtest.py (~615 LOC) with BacktestEngine, dataclasses, CLI
- Walk-forward backtest with train/test split per period implemented correctly
- Metrics (Precision/Recall/F1) semantics match ARCHITECT definition
- Physics Layer integration via PipelineRunner (stability_score, criticality_level)
- CLI with click: --data, --periods, --train-ratio, --output, --format working
- tests/unit/test_backtest.py with 22 unit tests ALL PASS (verified)
- Syntax check passed for both files (py_compile)
- get_hot_numbers threshold usage correct (max_frequency_threshold as hot_threshold)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase5_task01_backtest_script_PROXY_IMPL_20251226_230125.md

VALIDIERUNG:
1. Fuehre minimale Tests aus (zielgerichtet)
2. Pruefe Code-Qualitaet
3. Verifiziere Acceptance Criteria

TOKEN HYGIENE:
- Bei Test FAIL: nur Command + kurze Fehlermeldung (max 20 Zeilen)
- Mehr Log noetig? Speichere in AI_COLLABORATION/ARTIFACTS/ und referenziere Pfad

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: APPROVED
task: phase5_task01_backtest_script
role: VALIDATOR
phase: VALIDATOR
validated_handoff: "<nur filename oder leer>"
summary:
  - <max 8 bullets>
---
# Rule Confirmation
- Rule 1 (SYSTEM_STATUS + ADR/Docs + git status): CONFIRMED/UNVERIFIED
- Rule 2 (granularity stated): <global|per-market|per-league|per-team>
- Rule 3 (semantics defined): <fields/keys>
- Rule 4 (target metric): <accuracy|calibration|bet-selection>
- Rule 5 (helper-only boundaries): CONFIRMED/UNVERIFIED
- Rule 6 (reproducibility): <command + output path> or UNVERIFIED (no placeholders)

## Task Setup
- Granularity: <global|per-market|per-league|per-team>
- Semantics: <key fields/definitions>
- Target metric: <accuracy|calibration|bet-selection>

## Repro Commands
- <command> -> <output path> or UNVERIFIED

# Validation

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki3_phase5_task01_backtest_script_VALIDATOR_20251226_230425.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
