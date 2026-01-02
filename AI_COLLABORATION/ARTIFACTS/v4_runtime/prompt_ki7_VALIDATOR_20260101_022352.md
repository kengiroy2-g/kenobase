AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: A1-02: FRUEH-Phase isoliert testen (Tag 1-14)
TASK-ID: SYN_002
PRIORITY: P0
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2026-01-01 02:21:52] SYN_002 - EXECUTOR (ki6)

### Summary
- Added SubCooldownPhase enum (FRUEH/SPAET/NORMAL/UNKNOWN) to cycle_phases.py
- Added get_sub_cooldown_phase() function with FRUEH=1-14d, SPAET=15-30d, NORMAL=>30d
- Created test_frueh_phase_isolated.py script analog to test_cooldown_rule_isolated.py
- Train/Test split (2022-2023/2024), Chi2-Test, Mann-Whitney U implemented
- Negative Control with random 14d windows (excluding jackpot periods)
- Hypothesis CONFIRMED: FRUEH worse than SPAET in 5/5 train, 5/5 test
- Train FRUEH worse vs NORMAL: 5/5, Test: 4/5
- Output saved to results/frueh_phase_isolated_test.json (15KB)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_SYN_002_EXECUTOR_20260101_021652.md

## [2026-01-01 02:23:52] SYN_002 - PROXY_IMPL (ki0)

### Summary
- SubCooldownPhase enum correctly added with FRUEH/SPAET/NORMAL/UNKNOWN
- get_sub_cooldown_phase() uses FRUEH_MAX_DAYS=14, SPAET_MAX_DAYS=30 (no magic numbers)
- __all__ exports updated correctly (line 330-344)
- test_frueh_phase_isolated.py follows SYN_001 template structure exactly
- Train/Test split correctly implemented (2022-2023 train, 2024 test)
- Negative control excludes 31 days after each jackpot (correct exclusion logic)
- Hypothesis CONFIRMED: FRUEH worse than SPAET in 5/5 train, 5/5 test
- JSON output validates successfully (15KB)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_SYN_002_PROXY_IMPL_20260101_022152.md



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
- kenobase/analysis/cycle_phases.py
- scripts/test_frueh_phase_isolated.py
- results/frueh_phase_isolated_test.json

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
- SubCooldownPhase enum correctly added with FRUEH/SPAET/NORMAL/UNKNOWN
- get_sub_cooldown_phase() uses FRUEH_MAX_DAYS=14, SPAET_MAX_DAYS=30 (no magic numbers)
- __all__ exports updated correctly (line 330-344)
- test_frueh_phase_isolated.py follows SYN_001 template structure exactly
- Train/Test split correctly implemented (2022-2023 train, 2024 test)
- Negative control excludes 31 days after each jackpot (correct exclusion logic)
- Hypothesis CONFIRMED: FRUEH worse than SPAET in 5/5 train, 5/5 test
- JSON output validates successfully (15KB)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_SYN_002_PROXY_IMPL_20260101_022152.md

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
task: SYN_002
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
- Datei: AI_COLLABORATION/HANDOFFS/ki7_SYN_002_VALIDATOR_20260101_022352.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
