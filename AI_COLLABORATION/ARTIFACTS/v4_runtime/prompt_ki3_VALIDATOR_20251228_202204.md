AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Jackpot-Hoehe vs. Zahlentyp Korrelation
TASK-ID: HOUSE-001
PRIORITY: P1
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 20:20:04] HOUSE-001 - EXECUTOR (ki2)

### Summary
- Created jackpot_correlation.py module (557 lines) following odds_correlation.py pattern
- Implemented GK1Event, NumberTypeStats, JackpotCorrelationResult, JackpotAnalysisSummary dataclasses
- Functions: load_gk1_events, analyze_jackpot_correlation, chi_square_test, run_hyp015_analysis
- Created test_jackpot_correlation.py with 32 unit tests (all passing)
- Created analyze_hyp015_jackpot.py CLI script
- Updated __init__.py with 22 new exports for HYP-015
- Analysis ran successfully: N=737 draws, 18 jackpot, 719 normal
- Result: NO significant correlation (Pearson r=0.017, p=0.65, Chi2 p=0.74)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HOUSE-001_EXECUTOR_20251228_201404.md

## [2025-12-28 20:22:04] HOUSE-001 - PROXY_IMPL (ki0)

### Summary
- All 5 files created/modified as documented
- Syntax check passed (py_compile)
- JSON output validates correctly
- 32/32 unit tests pass (2 expected warnings for edge cases)
- __init__.py exports 22 new symbols for HYP-015
- Results show hypothesis FALSIFIED (r=0.017, p=0.65)
- Acceptance criteria correctly evaluated (|r|<0.2, p>0.05)
- Module pattern consistent with odds_correlation.py

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HOUSE-001_PROXY_IMPL_20251228_202004.md



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
- kenobase/core/data_loader.py
- config/default.yaml
- Keno_GPTs/10-9_KGDaten_gefiltert.csv
- data/raw/keno/KENO_ab_2018.csv
- kenobase/analysis/jackpot_correlation.py
- tests/unit/test_jackpot_correlation.py
- scripts/analyze_hyp015_jackpot.py
- results/hyp015_jackpot_correlation.json

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
- All 5 files created/modified as documented
- Syntax check passed (py_compile)
- JSON output validates correctly
- 32/32 unit tests pass (2 expected warnings for edge cases)
- __init__.py exports 22 new symbols for HYP-015
- Results show hypothesis FALSIFIED (r=0.017, p=0.65)
- Acceptance criteria correctly evaluated (|r|<0.2, p>0.05)
- Module pattern consistent with odds_correlation.py

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HOUSE-001_PROXY_IMPL_20251228_202004.md

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
task: HOUSE-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_HOUSE-001_VALIDATOR_20251228_202204.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
