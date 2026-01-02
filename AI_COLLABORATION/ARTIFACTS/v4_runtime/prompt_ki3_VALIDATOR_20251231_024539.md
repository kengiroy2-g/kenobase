AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: V1 vs V2: Cooldown-Phase Test
TASK-ID: TASK_041
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-31 02:43:39] TASK_041 - EXECUTOR (ki2)

### Summary
- Created scripts/backtest_v1_v2_cooldown.py for V1 vs V2 cooldown comparison
- Cooldown semantics: 0-30 days post-jackpot vs >30 days (WL-003 compliant)
- Tested on 11 Jackpots (2022-2024), 1877 draws, 296 cooldown / 1581 normal draws
- Key finding: V1 dominant in cooldown phase (2/3 Typen), V2 dominant in normal phase (3/3 Typen)
- ROI deltas: V2 better in normal (+2.66% to +5.50%), V1 better in cooldown for Typ9/10
- WL-003 hypothesis CONFIRMED: different model performance by phase
- Output saved to results/v1_v2_cooldown_comparison.json

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_041_EXECUTOR_20251231_024039.md

## [2025-12-31 02:45:39] TASK_041 - PROXY_IMPL (ki0)

### Summary
- Script backtest_v1_v2_cooldown.py created with correct 30-day cooldown semantics (WL-003)
- Syntax verified: py_compile passes without errors
- JSON output valid and contains complete comparison data
- Cooldown semantics correctly implemented: 0 < days_since <= 30 (line 74)
- Key finding: V1 better in cooldown (2/3 Typen), V2 better in normal (3/3 Typen)
- No integration issues: standalone script, does not modify core modules
- Imports from existing super_model_*.py scripts verified structurally correct
- Repro command verified: results/v1_v2_cooldown_comparison.json contains 185 lines valid JSON

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_041_PROXY_IMPL_20251231_024339.md



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
- scripts/super_model_v1_birthday.py
- scripts/super_model_v2_birthday_signal.py
- scripts/super_model_synthesis.py
- scripts/backtest_post_jackpot.py
- scripts/backtest_v1_v2_cooldown.py
- results/v1_v2_cooldown_comparison.json

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
- Script backtest_v1_v2_cooldown.py created with correct 30-day cooldown semantics (WL-003)
- Syntax verified: py_compile passes without errors
- JSON output valid and contains complete comparison data
- Cooldown semantics correctly implemented: 0 < days_since <= 30 (line 74)
- Key finding: V1 better in cooldown (2/3 Typen), V2 better in normal (3/3 Typen)
- No integration issues: standalone script, does not modify core modules
- Imports from existing super_model_*.py scripts verified structurally correct
- Repro command verified: results/v1_v2_cooldown_comparison.json contains 185 lines valid JSON

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_041_PROXY_IMPL_20251231_024339.md

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
task: TASK_041
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK_041_VALIDATOR_20251231_024539.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
