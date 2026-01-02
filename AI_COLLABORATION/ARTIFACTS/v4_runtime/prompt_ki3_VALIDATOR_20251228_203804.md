AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Unpopulaere Zahlen bei hohem Einsatz
TASK-ID: HOUSE-002
PRIORITY: P1
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 20:35:04] HOUSE-002 - EXECUTOR (ki2)

### Summary
- Added HighStakePopularityResult dataclass to stake_correlation.py
- Implemented analyze_high_stake_popularity_bias() function
- Added 7 unit tests for HOUSE-002 in test_stake_correlation.py
- Created scripts/analyze_house002.py analysis script
- Analysis ran on 365 draws: r=0.024, p=0.64 (NOT SUPPORTED)
- Output saved to results/house002_stake_popularity.json

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HOUSE-002_EXECUTOR_20251228_203104.md

## [2025-12-28 20:38:04] HOUSE-002 - PROXY_IMPL (ki0)

### Summary
- HighStakePopularityResult dataclass correctly implemented (frozen=True, 9 fields)
- analyze_high_stake_popularity_bias() function implemented lines 728-871
- Uses popularity_correlation.calculate_popularity_scores_heuristic() for popularity (lazy import)
- 7 unit tests all pass (TestAnalyzeHighStakePopularityBias class)
- Analysis script correctly runs: 365 draws, r=0.024, p=0.64, NOT SUPPORTED
- Output JSON valid and matches acceptance criteria structure
- No integration conflicts: standalone analysis combining existing modules
- Exports added to __all__ (line 879)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HOUSE-002_PROXY_IMPL_20251228_203504.md



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
- kenobase/analysis/stake_correlation.py
- tests/unit/test_stake_correlation.py
- scripts/analyze_house002.py
- results/house002_stake_popularity.json

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
- HighStakePopularityResult dataclass correctly implemented (frozen=True, 9 fields)
- analyze_high_stake_popularity_bias() function implemented lines 728-871
- Uses popularity_correlation.calculate_popularity_scores_heuristic() for popularity (lazy import)
- 7 unit tests all pass (TestAnalyzeHighStakePopularityBias class)
- Analysis script correctly runs: 365 draws, r=0.024, p=0.64, NOT SUPPORTED
- Output JSON valid and matches acceptance criteria structure
- No integration conflicts: standalone analysis combining existing modules
- Exports added to __all__ (line 879)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HOUSE-002_PROXY_IMPL_20251228_203504.md

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
task: HOUSE-002
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_HOUSE-002_VALIDATOR_20251228_203804.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
