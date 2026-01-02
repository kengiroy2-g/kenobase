AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Zyklus-Phasen markieren
TASK-ID: TASK_003
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 14:17:50] TASK_003 - EXECUTOR (ki2)

### Summary
- Created kenobase/analysis/cycle_phases.py with Phase enum (COOLDOWN/GROWTH/HOT/UNKNOWN)
- Phase boundaries implemented: COOLDOWN=0-30d, GROWTH=31-60d, HOT=>60d nach Jackpot
- REUSED load_gk1_events() and get_jackpot_dates() from jackpot_correlation.py (as per plan)
- Created 33 unit tests covering all edge cases (boundaries, no jackpots, multiple jackpots)
- All 33 tests pass (pytest tests/unit/test_cycle_phases.py -v)
- Exported Phase, PhaseLabel, label_phases, filter_draws_by_phase, get_phase_statistics from __init__.py
- Helper functions get_phase_for_days() and get_phase_for_date() for single-value lookups

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_003_EXECUTOR_20251230_141350.md

## [2025-12-30 14:19:50] TASK_003 - PROXY_IMPL (ki0)

### Summary
- All 33 unit tests pass (pytest tests/unit/test_cycle_phases.py -v)
- Module syntax verified (py_compile OK)
- Phase boundaries correct: COOLDOWN=0-30d, GROWTH=31-60d, HOT=>60d, UNKNOWN=vor Jackpot
- Proper REUSE of load_gk1_events() and get_jackpot_dates() from jackpot_correlation.py (no duplication)
- Export in __init__.py lines 326-336 + __all__ lines 630-639 - korrekt und vollstaendig
- PhaseLabel frozen dataclass immutable (test verified)
- No BUG-001/BUG-003 violations (boundaries are module-scoped constants, no orchestrator needed)
- TYPE_CHECKING import for DrawResult avoids circular import

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_003_PROXY_IMPL_20251230_141750.md



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
- kenobase/analysis/__init__.py
- Keno_GPTs/10-9_KGDaten_gefiltert.csv
- kenobase/core/data_loader.py
- tests/unit/test_distribution.py (als Template fuer Test-Struktur)
- kenobase/analysis/cycle_phases.py (NEW)
- tests/unit/test_cycle_phases.py (NEW)
- kenobase/analysis/__init__.py (UPDATED)

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
- All 33 unit tests pass (pytest tests/unit/test_cycle_phases.py -v)
- Module syntax verified (py_compile OK)
- Phase boundaries correct: COOLDOWN=0-30d, GROWTH=31-60d, HOT=>60d, UNKNOWN=vor Jackpot
- Proper REUSE of load_gk1_events() and get_jackpot_dates() from jackpot_correlation.py (no duplication)
- Export in __init__.py lines 326-336 + __all__ lines 630-639 - korrekt und vollstaendig
- PhaseLabel frozen dataclass immutable (test verified)
- No BUG-001/BUG-003 violations (boundaries are module-scoped constants, no orchestrator needed)
- TYPE_CHECKING import for DrawResult avoids circular import

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_003_PROXY_IMPL_20251230_141750.md

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
task: TASK_003
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK_003_VALIDATOR_20251230_141950.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
