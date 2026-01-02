AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Zyklus-Surfen
TASK-ID: STRAT-004
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 07:03:47] STRAT-004 - EXECUTOR (ki2)

### Summary
- Created scripts/backtest_cycle_surfing.py combining regime_detection.py + temporal_cycles.py
- Implements HMM-based regime detection with train/test split at 2024-01-01 (configurable)
- Adds temporal filters: weekday bias (derived from train chi2) + holiday proximity (3-day window)
- Decision logic: PLAY if regime is favorable AND weekday passes AND not near holiday
- Hit metric: fraction of popular numbers (1-31) as ROI proxy
- Statistical test: Mann-Whitney U (one-sided) for strategy vs baseline comparison
- Output: results/cycle_surfing_backtest.json with full metrics and acceptance criteria
- Backtest result: NO_IMPROVEMENT (p=0.58) - strategy shows no significant edge

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_STRAT-004_EXECUTOR_20251230_070258.md

## [2025-12-30 07:05:47] STRAT-004 - PROXY_IMPL (ki0)

### Summary
- Syntax verified: py_compile passes without errors
- Module imports verified: regime_detection, temporal_cycles, GERMAN_HOLIDAYS all load correctly
- Train/Test split correctly implemented at configurable date (default 2024-01-01, used 2024-06-01)
- Weekday filter derived from train data chi2 (no leakage from test)
- Holiday filter uses GERMAN_HOLIDAYS with 3-day window (41 draws avoided)
- Mann-Whitney U one-sided test correctly applied (strategy vs baseline)
- Output JSON validated: results/cycle_surfing_backtest.json exists with proper structure
- Scientific finding: NO_IMPROVEMENT (p=0.58) - valid negative result, no bugs

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_STRAT-004_PROXY_IMPL_20251230_070347.md



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
- scripts/backtest_cycle_surfing.py

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
- Syntax verified: py_compile passes without errors
- Module imports verified: regime_detection, temporal_cycles, GERMAN_HOLIDAYS all load correctly
- Train/Test split correctly implemented at configurable date (default 2024-01-01, used 2024-06-01)
- Weekday filter derived from train data chi2 (no leakage from test)
- Holiday filter uses GERMAN_HOLIDAYS with 3-day window (41 draws avoided)
- Mann-Whitney U one-sided test correctly applied (strategy vs baseline)
- Output JSON validated: results/cycle_surfing_backtest.json exists with proper structure
- Scientific finding: NO_IMPROVEMENT (p=0.58) - valid negative result, no bugs

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_STRAT-004_PROXY_IMPL_20251230_070347.md

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
task: STRAT-004
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_STRAT-004_VALIDATOR_20251230_070547.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
