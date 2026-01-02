AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Mehrwochenschein Jackpot-Timing
TASK-ID: HYP014-001
PRIORITY: MITTEL
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 17:28:37] HYP014-001 - EXECUTOR (ki2)

### Summary
- Created kenobase/analysis/multiweek_timing.py with 540 lines
- Monte-Carlo simulation for abo-period timing analysis
- Chi-Square uniformity test for position distributions
- Dataclasses: SimulationConfig, PositionDistribution, ChiSquareResult, MonteCarloComparison, MultiweekTimingResult
- JSON export with numpy type conversion
- Script scripts/analyze_hyp014.py with CLI arguments
- 21 unit tests in tests/unit/test_multiweek_timing.py - ALL PASSING
- Module integrated into kenobase/analysis/__init__.py

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HYP014-001_EXECUTOR_20251228_172337.md

## [2025-12-28 17:30:37] HYP014-001 - PROXY_IMPL (ki0)

### Summary
- multiweek_timing.py (561 lines): Monte-Carlo + Chi-Square implementation korrekt
- 5 Dataclasses (SimulationConfig, PositionDistribution, ChiSquareResult, MonteCarloComparison, MultiweekTimingResult)
- JSON export mit numpy type conversion funktioniert
- __init__.py korrekt integriert mit aliased ChiSquareResult -> MultiweekChiSquareResult
- 21 Unit Tests - ALL PASSING (pytest 0.92s)
- CLI analyze_hyp014.py funktioniert (--help verifiziert)
- Keine BUG-001..010 Red Flags erkannt
- Pattern konsistent mit gk1_waiting.py und temporal_cycles.py

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP014-001_PROXY_IMPL_20251228_172837.md



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
- kenobase/analysis/multiweek_timing.py
- kenobase/analysis/__init__.py
- scripts/analyze_hyp014.py
- tests/unit/test_multiweek_timing.py

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
- multiweek_timing.py (561 lines): Monte-Carlo + Chi-Square implementation korrekt
- 5 Dataclasses (SimulationConfig, PositionDistribution, ChiSquareResult, MonteCarloComparison, MultiweekTimingResult)
- JSON export mit numpy type conversion funktioniert
- __init__.py korrekt integriert mit aliased ChiSquareResult -> MultiweekChiSquareResult
- 21 Unit Tests - ALL PASSING (pytest 0.92s)
- CLI analyze_hyp014.py funktioniert (--help verifiziert)
- Keine BUG-001..010 Red Flags erkannt
- Pattern konsistent mit gk1_waiting.py und temporal_cycles.py

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP014-001_PROXY_IMPL_20251228_172837.md

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
task: HYP014-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_HYP014-001_VALIDATOR_20251228_173037.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
