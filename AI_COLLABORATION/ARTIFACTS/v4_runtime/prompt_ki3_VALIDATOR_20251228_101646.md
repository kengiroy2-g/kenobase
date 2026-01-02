AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Model Explainability (SHAP)
TASK-ID: TASK-P14
PRIORITY: LOW
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 10:13:46] TASK-P14 - EXECUTOR (ki2)

### Summary
- Created kenobase/prediction/explainability.py with SHAPExplainer class
- TreeExplainer for LightGBM (optimal O(n) performance)
- Methods: explain_single, explain_batch, summary_plot, force_plot
- SHAPExplanation dataclass with to_dict() and get_top_features()
- validate_shap_native_correlation() acceptance test function
- Added shap>=0.44.0 to requirements.txt (line 48-49)
- Config extension ml.shap in config/default.yaml (lines 260-268)
- 15 unit tests all passing in tests/unit/test_explainability.py

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-P14_EXECUTOR_20251228_100746.md

## [2025-12-28 10:16:46] TASK-P14 - PROXY_IMPL (ki0)

### Summary
- SHAPExplainer class correctly implements TreeExplainer for LightGBM (O(n) performance)
- SHAPExplanation dataclass with to_dict() and get_top_features() properly structured
- Graceful degradation when SHAP not installed (HAS_SHAP flag)
- validate_shap_native_correlation() acceptance test function implemented
- Config extension at config/default.yaml:260-268 under ml.shap section
- shap>=0.44.0 added to requirements.txt (line 49)
- Module exports added to kenobase/prediction/__init__.py
- All 15 unit tests passing (verified: pytest tests/unit/test_explainability.py -v)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P14_PROXY_IMPL_20251228_101346.md



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
- kenobase/prediction/explainability.py
- kenobase/prediction/__init__.py
- requirements.txt
- config/default.yaml
- tests/unit/test_explainability.py

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
- SHAPExplainer class correctly implements TreeExplainer for LightGBM (O(n) performance)
- SHAPExplanation dataclass with to_dict() and get_top_features() properly structured
- Graceful degradation when SHAP not installed (HAS_SHAP flag)
- validate_shap_native_correlation() acceptance test function implemented
- Config extension at config/default.yaml:260-268 under ml.shap section
- shap>=0.44.0 added to requirements.txt (line 49)
- Module exports added to kenobase/prediction/__init__.py
- All 15 unit tests passing (verified: pytest tests/unit/test_explainability.py -v)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P14_PROXY_IMPL_20251228_101346.md

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
task: TASK-P14
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK-P14_VALIDATOR_20251228_101646.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
