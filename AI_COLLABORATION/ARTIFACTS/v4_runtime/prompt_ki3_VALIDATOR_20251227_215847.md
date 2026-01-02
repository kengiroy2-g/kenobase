AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Wiederholungs-Zyklus Analyse (7-Tage)
TASK-ID: TASK-H01
PRIORITY: HIGH
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 21:56:46] TASK-H01 - EXECUTOR (ki2)

### Summary
- Added WeeklyCycleResult and RecurrenceDaysResult dataclasses
- Implemented analyze_weekly_cycle() for weekday distribution analysis
- Implemented analyze_recurrence_days() for calendar-day based 7-day lookback
- Extended generate_recurrence_report() with weekly_cycle and recurrence_7d sections
- Added AC5/AC6 acceptance criteria for 7-day features
- Updated __all__ exports with 4 new items
- Added 10 new tests (38 total, all PASS)
- HYP-006 7-Tage-Zyklus fully implemented

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-H01_EXECUTOR_20251227_215146.md

## [2025-12-27 21:58:46] TASK-H01 - PROXY_IMPL (ki0)

### Summary
- All syntax validation PASSED (py_compile on both files)
- All 38 tests PASSED (pytest tests/unit/test_recurrence.py -v)
- WeeklyCycleResult dataclass correctly implemented (lines 107-128)
- RecurrenceDaysResult dataclass correctly implemented (lines 131-151)
- analyze_weekly_cycle() implements weekday distribution (lines 445-508)
- analyze_recurrence_days() implements calendar-day 7-day lookback (lines 511-592)
- generate_recurrence_report() extended with weekly_cycle and recurrence_7d sections
- __all__ exports verified: 4 new items available and importable

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-H01_PROXY_IMPL_20251227_215646.md



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
- kenobase/analysis/recurrence.py
- tests/unit/test_recurrence.py
- kenobase/core/data_loader.py
- config/default.yaml

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
- All syntax validation PASSED (py_compile on both files)
- All 38 tests PASSED (pytest tests/unit/test_recurrence.py -v)
- WeeklyCycleResult dataclass correctly implemented (lines 107-128)
- RecurrenceDaysResult dataclass correctly implemented (lines 131-151)
- analyze_weekly_cycle() implements weekday distribution (lines 445-508)
- analyze_recurrence_days() implements calendar-day 7-day lookback (lines 511-592)
- generate_recurrence_report() extended with weekly_cycle and recurrence_7d sections
- __all__ exports verified: 4 new items available and importable

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-H01_PROXY_IMPL_20251227_215646.md

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
task: TASK-H01
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK-H01_VALIDATOR_20251227_215847.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
