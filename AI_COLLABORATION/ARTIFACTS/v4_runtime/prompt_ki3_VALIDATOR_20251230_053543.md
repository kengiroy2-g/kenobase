AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Spread-Index
TASK-ID: TRANS-004
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 05:33:43] TRANS-004 - EXECUTOR (ki2)

### Summary
- Created kenobase/analysis/spread_index.py (232 lines) following parity_ratio.py pattern
- SpreadIndex formula: (Max-Min)/Max normalized to [0,1]
- Dataclasses: SpreadBin (bin statistics), SpreadIndexResult (aggregated result)
- Functions: calculate_spread_index, calculate_spread_for_draws, create_spread_bins, analyze_spread_index
- Chi-square test against uniform distribution across 5 bins
- Guardrail: 15% deviation threshold (configurable via guardrail_ratio parameter)
- Created tests/unit/test_spread_index.py with 26 tests (all passing)
- Updated kenobase/analysis/__init__.py exports with 6 new symbols

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TRANS-004_EXECUTOR_20251230_052943.md

## [2025-12-30 05:35:43] TRANS-004 - PROXY_IMPL (ki0)

### Summary
- All 26 tests pass (pytest verified)
- spread_index.py follows parity_ratio.py pattern correctly (frozen dataclasses, chi-square, guardrail)
- Syntax verified with py_compile for both source and tests
- Formula (Max-Min)/Max correctly implemented and normalized to [0,1]
- __init__.py exports all 6 symbols correctly at lines 318-325 and 612-618
- SpreadBin and SpreadIndexResult dataclasses match pattern from parity_ratio.py
- Guardrail: 15% deviation threshold (configurable) correctly implemented
- No integration issues detected - module is standalone analysis helper

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TRANS-004_PROXY_IMPL_20251230_053343.md



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
- kenobase/analysis/spread_index.py
- tests/unit/test_spread_index.py
- kenobase/analysis/__init__.py

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
- All 26 tests pass (pytest verified)
- spread_index.py follows parity_ratio.py pattern correctly (frozen dataclasses, chi-square, guardrail)
- Syntax verified with py_compile for both source and tests
- Formula (Max-Min)/Max correctly implemented and normalized to [0,1]
- __init__.py exports all 6 symbols correctly at lines 318-325 and 612-618
- SpreadBin and SpreadIndexResult dataclasses match pattern from parity_ratio.py
- Guardrail: 15% deviation threshold (configurable) correctly implemented
- No integration issues detected - module is standalone analysis helper

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TRANS-004_PROXY_IMPL_20251230_053343.md

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
task: TRANS-004
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TRANS-004_VALIDATOR_20251230_053543.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
