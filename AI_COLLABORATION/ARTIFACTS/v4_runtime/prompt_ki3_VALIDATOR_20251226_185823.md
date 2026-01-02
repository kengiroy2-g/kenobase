AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P2-01: Zahlenpool-Generator migrieren
TASK-ID: phase2_task01_number_pool
PRIORITY: P1
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-26 18:56:23] phase2_task01_number_pool - EXECUTOR (ki2)

### Summary
- Created kenobase/core/number_pool.py with NumberPoolGenerator class
- Migrated algorithm from Legacy V9 generiere_zahlenpool_optimiert() (lines 45-85)
- 4 public methods: generate(), get_top_n(), get_intersections(), from_draws()
- Configurable parameters: n_periods=3, draws_per_period=10, top_n_per_period=11, top_n_total=20
- Updated kenobase/core/__init__.py with NumberPoolGenerator and PeriodAnalysis exports
- Created tests/unit/test_number_pool.py with 18 test cases
- All 18 tests pass, 100% code coverage achieved

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_phase2_task01_number_pool_EXECUTOR_20251226_185222.md

## [2025-12-26 18:58:23] phase2_task01_number_pool - PROXY_IMPL (ki0)

### Summary
- NumberPoolGenerator class correctly implements Legacy V9 algorithm (3 periods x 10 draws, Top-11, intersections)
- 4 public methods as planned: generate(), get_top_n(), get_intersections(), from_draws()
- Configurable parameters with sensible defaults (n_periods=3, draws_per_period=10, top_n_per_period=11, top_n_total=20)
- PeriodAnalysis dataclass correctly captures period name, frequency counts, and top_n set
- __init__.py correctly updated with NumberPoolGenerator and PeriodAnalysis exports
- All 18 unit tests pass (pytest tests/unit/test_number_pool.py -v)
- Syntax validation passed (py_compile)
- Import validation passed

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase2_task01_number_pool_PROXY_IMPL_20251226_185623.md



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
- kenobase/core/number_pool.py
- kenobase/core/__init__.py
- tests/unit/test_number_pool.py

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
- NumberPoolGenerator class correctly implements Legacy V9 algorithm (3 periods x 10 draws, Top-11, intersections)
- 4 public methods as planned: generate(), get_top_n(), get_intersections(), from_draws()
- Configurable parameters with sensible defaults (n_periods=3, draws_per_period=10, top_n_per_period=11, top_n_total=20)
- PeriodAnalysis dataclass correctly captures period name, frequency counts, and top_n set
- __init__.py correctly updated with NumberPoolGenerator and PeriodAnalysis exports
- All 18 unit tests pass (pytest tests/unit/test_number_pool.py -v)
- Syntax validation passed (py_compile)
- Import validation passed

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase2_task01_number_pool_PROXY_IMPL_20251226_185623.md

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
task: phase2_task01_number_pool
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_phase2_task01_number_pool_VALIDATOR_20251226_185823.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
