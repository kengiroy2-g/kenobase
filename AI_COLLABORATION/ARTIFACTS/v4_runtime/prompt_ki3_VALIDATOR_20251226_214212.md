AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P4-02: Least-Action Pipeline-Auswahl
TASK-ID: phase4_task02_least_action_selector
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-26 21:39:11] phase4_task02_least_action_selector - EXECUTOR (ki2)

### Summary
- Created kenobase/pipeline/least_action.py with PipelineVariant, PipelineSelector, SelectionResult
- Defined 4 DEFAULT_PIPELINE_VARIANTS (minimal, standard, extended, full)
- Integrated PipelineSelector into PipelineRunner with enable_least_action config check
- Added pipeline_selection field to PipelineResult dataclass
- Added _run_least_action_selection() and get_pipeline_selector() methods to PipelineRunner
- Updated config_snapshot to include enable_least_action flag
- All 25 unit tests pass (test_least_action.py)
- All 15 runner tests pass (no regressions)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_phase4_task02_least_action_selector_EXECUTOR_20251226_213311.md

## [2025-12-26 21:42:12] phase4_task02_least_action_selector - PROXY_IMPL (ki0)

### Summary
- Created kenobase/pipeline/least_action.py (342 lines) - PipelineVariant, PipelineSelector, SelectionResult
- 4 DEFAULT_PIPELINE_VARIANTS defined (minimal, standard, extended, full) with correct complexity ordering
- PipelineSelector correctly wraps physics.model_laws functions (calculate_pipeline_action, select_best_pipeline)
- PipelineRunner integrated with _run_least_action_selection() and get_pipeline_selector() methods
- Config flag physics.enable_least_action properly checked (line 250 in runner.py)
- config_snapshot includes enable_least_action flag (line 378 in runner.py)
- All 25 unit tests pass (test_least_action.py), all 15 runner tests pass (no regressions)
- Integration verified: pipeline_selection field populated with SelectionResult when enabled

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase4_task02_least_action_selector_PROXY_IMPL_20251226_213912.md



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
- kenobase/pipeline/least_action.py (NEW - 267 lines)
- kenobase/pipeline/__init__.py (MODIFIED - added least_action exports)
- kenobase/pipeline/runner.py (MODIFIED - integrated PipelineSelector)
- tests/unit/test_least_action.py (NEW - 25 unit tests)

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
- Created kenobase/pipeline/least_action.py (342 lines) - PipelineVariant, PipelineSelector, SelectionResult
- 4 DEFAULT_PIPELINE_VARIANTS defined (minimal, standard, extended, full) with correct complexity ordering
- PipelineSelector correctly wraps physics.model_laws functions (calculate_pipeline_action, select_best_pipeline)
- PipelineRunner integrated with _run_least_action_selection() and get_pipeline_selector() methods
- Config flag physics.enable_least_action properly checked (line 250 in runner.py)
- config_snapshot includes enable_least_action flag (line 378 in runner.py)
- All 25 unit tests pass (test_least_action.py), all 15 runner tests pass (no regressions)
- Integration verified: pipeline_selection field populated with SelectionResult when enabled

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase4_task02_least_action_selector_PROXY_IMPL_20251226_213912.md

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
task: phase4_task02_least_action_selector
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_phase4_task02_least_action_selector_VALIDATOR_20251226_214212.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
