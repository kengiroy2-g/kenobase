AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Near-Miss Analyse bei hohem Jackpot
TASK-ID: HOUSE-004
PRIORITY: P1
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 21:04:06] HOUSE-004 - EXECUTOR (ki2)

### Summary
- Created near_miss_jackpot.py module combining near_miss.py + jackpot_correlation.py
- Module splits GQ data by jackpot dates and compares near-miss ratios
- Chi-square test compares jackpot vs normal periods per Keno-Typ
- Hypothesis supported if >= 3 Keno-Typen show p < 0.05
- Created analyze_house004.py CLI script following existing house003 pattern
- Created test_near_miss_jackpot.py with 20 unit tests - all passing
- Repro: python -m pytest tests/unit/test_near_miss_jackpot.py -v (20 passed)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HOUSE-004_EXECUTOR_20251228_210006.md

## [2025-12-28 21:06:06] HOUSE-004 - PROXY_IMPL (ki0)

### Summary
- All 3 files created (near_miss_jackpot.py, analyze_house004.py, test_near_miss_jackpot.py)
- Syntax validation passed for all files (py_compile OK)
- All 20 unit tests passing (pytest 0.88s)
- Module imports work correctly from kenobase.analysis
- CLI --help verified working
- Imports from dependency modules (jackpot_correlation, near_miss) verified
- No global threshold issues - uses standard p<0.05 significance
- Architecture consistent with existing house002/house003 patterns

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HOUSE-004_PROXY_IMPL_20251228_210406.md



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
- kenobase/analysis/near_miss_jackpot.py
- scripts/analyze_house004.py
- tests/unit/test_near_miss_jackpot.py

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
- All 3 files created (near_miss_jackpot.py, analyze_house004.py, test_near_miss_jackpot.py)
- Syntax validation passed for all files (py_compile OK)
- All 20 unit tests passing (pytest 0.88s)
- Module imports work correctly from kenobase.analysis
- CLI --help verified working
- Imports from dependency modules (jackpot_correlation, near_miss) verified
- No global threshold issues - uses standard p<0.05 significance
- Architecture consistent with existing house002/house003 patterns

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HOUSE-004_PROXY_IMPL_20251228_210406.md

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
task: HOUSE-004
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_HOUSE-004_VALIDATOR_20251228_210606.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
