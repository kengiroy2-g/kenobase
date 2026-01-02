AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Nullmodelle: schedule/block permutation
TASK-ID: NULL-001
PRIORITY: HOCH
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 02:42:06] NULL-001 - EXECUTOR (ki6)

### Summary
- Created kenobase/analysis/null_models.py with permutation-based null models
- Implemented schedule_permutation() preserving weekday structure for SCHEDULE_PRESERVING
- Implemented block_permutation() preserving weekly blocks for BLOCK_PERMUTATION
- Added NullModelRunner class integrating with NullModelType enum from axioms.py
- Implemented benjamini_hochberg_fdr() for FDR-corrected p-value computation
- Created 27 unit tests in tests/unit/test_null_models.py - all passing
- Updated analysis/__init__.py with new exports (12 symbols)
- Integrated with axiom predictions P1.3, P4.3, P6.3, P7.3 via run_axiom_prediction_test()

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_NULL-001_EXECUTOR_20251230_023706.md

## [2025-12-30 02:44:06] NULL-001 - PROXY_IMPL (ki0)

### Summary
- Verified kenobase/analysis/null_models.py syntax OK (py_compile passed)
- Confirmed 27/27 unit tests pass in tests/unit/test_null_models.py
- NullModelType enum integration with axioms.py:17-26 is clean
- schedule_permutation() correctly preserves weekday structure
- block_permutation() correctly preserves weekly blocks
- benjamini_hochberg_fdr() implements FDR correction correctly
- analysis/__init__.py exports 10 new symbols correctly
- No Known Bugs (BUG-001 to BUG-010) reproduced

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_NULL-001_PROXY_IMPL_20251230_024206.md



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
- kenobase/analysis/null_models.py
- kenobase/analysis/__init__.py
- tests/unit/test_null_models.py

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
- Verified kenobase/analysis/null_models.py syntax OK (py_compile passed)
- Confirmed 27/27 unit tests pass in tests/unit/test_null_models.py
- NullModelType enum integration with axioms.py:17-26 is clean
- schedule_permutation() correctly preserves weekday structure
- block_permutation() correctly preserves weekly blocks
- benjamini_hochberg_fdr() implements FDR correction correctly
- analysis/__init__.py exports 10 new symbols correctly
- No Known Bugs (BUG-001 to BUG-010) reproduced

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_NULL-001_PROXY_IMPL_20251230_024206.md

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
task: NULL-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki7_NULL-001_VALIDATOR_20251230_024406.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
