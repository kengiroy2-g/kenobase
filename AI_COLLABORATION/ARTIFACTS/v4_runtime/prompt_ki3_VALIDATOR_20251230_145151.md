AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Overlap-Metriken berechnen
TASK-ID: TASK_004
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 14:48:51] TASK_004 - EXECUTOR (ki2)

### Summary
- Created StateAwarePredictor class combining EconomicState + EnsemblePredictor
- Implemented state-specific alpha weighting (NORMAL=0.4, COOLDOWN=0.6, RECOVERY=0.5, HOT=0.3)
- Added StateAwarePrediction and StateAwareReport dataclasses
- Updated __init__.py with exports: StateAwarePredictor, StateAwarePrediction, StateAwareReport, DEFAULT_STATE_ALPHAS
- Created 17 unit tests - all PASS
- Created validation script: python scripts/test_state_aware_predictor.py
- Script running in background (ML training takes ~10 min on 1457 draws)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_004_EXECUTOR_20251230_142951.md

## [2025-12-30 14:51:51] TASK_004 - PROXY_IMPL (ki0)

### Summary
- StateAwarePredictor class correctly combines EconomicState + EnsemblePredictor
- State-specific alpha weighting implemented (NORMAL=0.4, COOLDOWN=0.6, RECOVERY=0.5, HOT=0.3)
- StateAwarePrediction and StateAwareReport dataclasses have correct to_dict() + save()
- __init__.py exports all 4 symbols: StateAwarePredictor, StateAwarePrediction, StateAwareReport, DEFAULT_STATE_ALPHAS
- 17 unit tests all PASS (confirmed via pytest)
- Syntax validation OK (py_compile)
- Import chain verified: from kenobase.prediction import StateAwarePredictor works
- Stale ERROR in validation JSON from earlier run; current code is correct

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_004_PROXY_IMPL_20251230_144851.md




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
- Acceptance: State-aware F1 >= EnsemblePredictor baseline F1; state labels match economic_state
- Tests: `tests/unit/test_state_aware.py` with unit + integration coverage
- Export: Update `kenobase/prediction/__init__.py` with new exports
- Repro: `python scripts/test_state_aware_predictor.py` -> `results/state_aware_validation.json`
- kenobase/prediction/state_aware.py (NEW)
- kenobase/prediction/__init__.py (UPDATED)
- tests/unit/test_state_aware.py (NEW)
- scripts/test_state_aware_predictor.py (NEW)

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
- StateAwarePredictor class correctly combines EconomicState + EnsemblePredictor
- State-specific alpha weighting implemented (NORMAL=0.4, COOLDOWN=0.6, RECOVERY=0.5, HOT=0.3)
- StateAwarePrediction and StateAwareReport dataclasses have correct to_dict() + save()
- __init__.py exports all 4 symbols: StateAwarePredictor, StateAwarePrediction, StateAwareReport, DEFAULT_STATE_ALPHAS
- 17 unit tests all PASS (confirmed via pytest)
- Syntax validation OK (py_compile)
- Import chain verified: from kenobase.prediction import StateAwarePredictor works
- Stale ERROR in validation JSON from earlier run; current code is correct

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_004_PROXY_IMPL_20251230_144851.md

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
task: TASK_004
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK_004_VALIDATOR_20251230_145151.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
