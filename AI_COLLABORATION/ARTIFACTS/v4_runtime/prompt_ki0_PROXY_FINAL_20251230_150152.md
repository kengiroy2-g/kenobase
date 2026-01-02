AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Overlap-Metriken berechnen
TASK-ID: TASK_004
PRIORITY: P2
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
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


## [2025-12-30 15:01:52] TASK_004 - VALIDATOR (ki3)

### Summary
- All 17 unit tests PASS (pytest tests/unit/test_state_aware.py -v, 1.77s)
- Import chain verified: StateAwarePredictor, StateAwarePrediction, StateAwareReport, DEFAULT_STATE_ALPHAS
- __init__.py exports all 4 symbols at lines 63-68 and 103-107
- StateAwarePredictor correctly wraps EnsemblePredictor with state-conditional alpha
- State-specific alphas: NORMAL=0.4, COOLDOWN=0.6, RECOVERY=0.5, HOT=0.3
- Code quality: Type hints, docstrings, proper error handling (RuntimeError if not fitted)
- Acceptance criteria tests pass: state_labels_match_economic_state, f1_metric_computed_per_state
- Validation script running in background (~10min ML training)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK_004_VALIDATOR_20251230_145151.md



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
ROLLE: PROXY (User-Stellvertreter - Finale Freigabe)
AUFGABE: Finale Freigabe mit Projekt-Perspektive.

PFLICHTLEKTUERE (kurz):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Falls Zweifel an Integration

EFFIZIENZ-REGELN:
- Nutze VALIDATOR OUTPUT + dein Wissen aus vorherigen Proxy-Phasen
- Keine weiteren Tests, nur finale Entscheidung

VALIDATOR OUTPUT (kurz):
- All 17 unit tests PASS (pytest tests/unit/test_state_aware.py -v, 1.77s)
- Import chain verified: StateAwarePredictor, StateAwarePrediction, StateAwareReport, DEFAULT_STATE_ALPHAS
- __init__.py exports all 4 symbols at lines 63-68 and 103-107
- StateAwarePredictor correctly wraps EnsemblePredictor with state-conditional alpha
- State-specific alphas: NORMAL=0.4, COOLDOWN=0.6, RECOVERY=0.5, HOT=0.3
- Code quality: Type hints, docstrings, proper error handling (RuntimeError if not fitted)
- Acceptance criteria tests pass: state_labels_match_economic_state, f1_metric_computed_per_state
- Validation script running in background (~10min ML training)

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK_004_VALIDATOR_20251230_145151.md

FINALE PRUEFUNG:
1. Hat Validator alle kritischen Aspekte geprueft?
2. Wuerde der USER diese Aenderung akzeptieren?
3. Gibt es offene Architektur-Fragen die der User entscheiden sollte?

ESKALATION an User wenn:
- Architektur-Entscheidung noetig die nicht in ADRs dokumentiert ist
- Unsicherheit ueber globale vs spezifische Werte
- Potenzielle Breaking Changes

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: COMPLETE
task: TASK_004
role: PROXY
phase: PROXY_FINAL
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

# Proxy Final Review

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_004_PROXY_FINAL_20251230_150152.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
