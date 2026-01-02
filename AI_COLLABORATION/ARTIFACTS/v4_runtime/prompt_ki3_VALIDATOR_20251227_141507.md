AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Kern-Hypothesen Validierung
TASK-ID: HYP-002
PRIORITY: HIGH
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 14:13:07] HYP-002 - EXECUTOR (ki2)

### Summary
- Created calendar_features.py with CalendarFeatures, CalendarAnalysisResult dataclasses
- Implemented extract_calendar_features() for weekday, month, holiday, payday extraction
- Implemented analyze_calendar_correlation() with Chi-Square tests for weekday/month
- Implemented predict_next_gk1() Poisson-based prediction model with 80% CI
- Extended validate_hyp002_jackpot_zyklen() with calendar analysis and prediction
- Updated __init__.py to export new calendar_features module
- Generated hyp002_jackpot_cycles.json with full extended analysis
- All tests passed: N=20 events, 17 intervals, mean=43.3 days, KS p=0.588 (RANDOM)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HYP-002_EXECUTOR_20251227_140907.md

## [2025-12-27 14:15:07] HYP-002 - PROXY_IMPL (ki0)

### Summary
- calendar_features.py: Syntax valid, all functions implemented (extract_calendar_features, analyze_calendar_correlation, predict_next_gk1, to_dict)
- __init__.py correctly exports all 5 new symbols (CalendarFeatures, CalendarAnalysisResult, extract_calendar_features, analyze_calendar_correlation, predict_next_gk1)
- validate_hypotheses.py:310-314 imports from calendar_features; :370-379 integrates calendar and prediction
- hyp002_jackpot_cycles.json: valid JSON with complete structure (calendar_analysis, prediction, status, interpretation)
- Chi-square tests use correct threshold check (P_VALUE_THRESHOLD from line 382/396/398)
- No global thresholds introduced (BUG-001 avoided)
- Module is isolated - no unintended dependencies or coupling
- Repro command verified in handoff matches implementation

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-002_PROXY_IMPL_20251227_141307.md



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
- kenobase/analysis/calendar_features.py (NEW)
- kenobase/analysis/__init__.py (MODIFIED)
- scripts/validate_hypotheses.py (MODIFIED)
- data/results/hyp002_jackpot_cycles.json (NEW)

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
- calendar_features.py: Syntax valid, all functions implemented (extract_calendar_features, analyze_calendar_correlation, predict_next_gk1, to_dict)
- __init__.py correctly exports all 5 new symbols (CalendarFeatures, CalendarAnalysisResult, extract_calendar_features, analyze_calendar_correlation, predict_next_gk1)
- validate_hypotheses.py:310-314 imports from calendar_features; :370-379 integrates calendar and prediction
- hyp002_jackpot_cycles.json: valid JSON with complete structure (calendar_analysis, prediction, status, interpretation)
- Chi-square tests use correct threshold check (P_VALUE_THRESHOLD from line 382/396/398)
- No global thresholds introduced (BUG-001 avoided)
- Module is isolated - no unintended dependencies or coupling
- Repro command verified in handoff matches implementation

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-002_PROXY_IMPL_20251227_141307.md

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
task: HYP-002
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_HYP-002_VALIDATOR_20251227_141507.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
