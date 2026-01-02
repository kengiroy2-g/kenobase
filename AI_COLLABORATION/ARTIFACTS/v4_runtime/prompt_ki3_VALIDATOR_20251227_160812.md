AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Gewinnquoten mit gezogenen Zahlen korrelieren
TASK-ID: HYP-010
PRIORITY: MEDIUM
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 16:06:12] HYP-010 - EXECUTOR (ki2)

### Summary
- Created odds_correlation.py module with OddsCorrelationResult, NumberClassification, OddsAnalysisSummary dataclasses
- Implemented load_gq_winner_data() with German number format handling (1.443 = 1443)
- Implemented calculate_number_winner_scores() joining GQ data with draws on date
- Implemented analyze_odds_correlation() with Pearson + Spearman dual correlation
- Implemented classify_numbers_by_popularity() with median +/- 1 std threshold
- Created analyze_hyp010.py script with CLI args and JSON output
- Created 15 unit tests (all passing)
- Analysis result: r=0.08 (Pearson), p=0.49 - NOT SIGNIFICANT

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HYP-010_EXECUTOR_20251227_160012.md

## [2025-12-27 16:08:12] HYP-010 - PROXY_IMPL (ki0)

### Summary
- odds_correlation.py (557 lines) - Well-structured module with proper dataclasses
- German number format handling (1.443 = 1443) correctly implemented in load_gq_winner_data()
- Pearson + Spearman dual correlation via scipy.stats
- safe/popular classification with median +/- 1 std threshold
- CLI script (analyze_hyp010.py) with proper argparse and JSON output
- __init__.py correctly exports all 10 public symbols
- 15 unit tests all passing (0.79s)
- Analysis result: r=0.08, p=0.49 - NOT SIGNIFICANT (hypothesis rejected)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-010_PROXY_IMPL_20251227_160612.md



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
- kenobase/analysis/odds_correlation.py
- kenobase/analysis/__init__.py
- scripts/analyze_hyp010.py
- tests/unit/test_odds_correlation.py
- results/hyp010_odds_correlation.json

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
- odds_correlation.py (557 lines) - Well-structured module with proper dataclasses
- German number format handling (1.443 = 1443) correctly implemented in load_gq_winner_data()
- Pearson + Spearman dual correlation via scipy.stats
- safe/popular classification with median +/- 1 std threshold
- CLI script (analyze_hyp010.py) with proper argparse and JSON output
- __init__.py correctly exports all 10 public symbols
- 15 unit tests all passing (0.79s)
- Analysis result: r=0.08, p=0.49 - NOT SIGNIFICANT (hypothesis rejected)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-010_PROXY_IMPL_20251227_160612.md

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
task: HYP-010
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_HYP-010_VALIDATOR_20251227_160812.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
