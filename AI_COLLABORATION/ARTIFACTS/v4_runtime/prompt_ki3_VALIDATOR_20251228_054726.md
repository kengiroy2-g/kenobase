AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Confidence Intervals
TASK-ID: TASK-P11
PRIORITY: MEDIUM
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 05:45:26] TASK-P11 - EXECUTOR (ki2)

### Summary
- Created kenobase/prediction/confidence.py with Bootstrap CI implementation
- ConfidenceInterval dataclass with lower, upper, width, is_stable properties
- ConfidenceEstimator with calculate_ci() using 1000 bootstrap resamples
- Added coverage_test() for CI validation (95% target coverage)
- Extended EnsemblePrediction with ensemble_ci and ml_ci fields
- Added predict_with_ci() and get_stable_predictions() to EnsemblePredictor
- Created 27 unit tests in test_confidence.py - all passing
- Acceptance criteria met: width < 0.3 for stable predictions, 95% CI

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-P11_EXECUTOR_20251228_054026.md

## [2025-12-28 05:47:26] TASK-P11 - PROXY_IMPL (ki0)

### Summary
- confidence.py: Bootstrap CI implementation with ConfidenceInterval, ConfidenceEstimator, PredictionWithCI
- ConfidenceEstimator uses 1000 bootstrap resamples (configurable), random_state=42 for reproducibility
- CI width < 0.3 defines stable predictions (acceptance criterion met)
- 95% CI is standard statistical practice (not a tunable global threshold - OK)
- ensemble.py extended with ensemble_ci, ml_ci Optional fields on EnsemblePrediction
- predict_with_ci() and get_stable_predictions() methods added to EnsemblePredictor
- All 27 confidence tests pass, all 16 ensemble tests pass (43 total)
- No integration issues detected - confidence module is self-contained with clean imports

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P11_PROXY_IMPL_20251228_054526.md



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
- kenobase/prediction/confidence.py
- kenobase/prediction/ensemble.py
- tests/unit/test_confidence.py

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
- confidence.py: Bootstrap CI implementation with ConfidenceInterval, ConfidenceEstimator, PredictionWithCI
- ConfidenceEstimator uses 1000 bootstrap resamples (configurable), random_state=42 for reproducibility
- CI width < 0.3 defines stable predictions (acceptance criterion met)
- 95% CI is standard statistical practice (not a tunable global threshold - OK)
- ensemble.py extended with ensemble_ci, ml_ci Optional fields on EnsemblePrediction
- predict_with_ci() and get_stable_predictions() methods added to EnsemblePredictor
- All 27 confidence tests pass, all 16 ensemble tests pass (43 total)
- No integration issues detected - confidence module is self-contained with clean imports

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P11_PROXY_IMPL_20251228_054526.md

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
task: TASK-P11
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK-P11_VALIDATOR_20251228_054726.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
