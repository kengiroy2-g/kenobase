AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Test HYP_005: Birthday-Avoidance in Cooldown
TASK-ID: TASK_015
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 17:38:00] TASK_015 - EXECUTOR (ki2)

### Summary
- Created scripts/backtest_birthday_cooldown.py (HYP_005 test script)
- V1 Tickets (OPTIMAL_TICKETS) from backtest_post_jackpot.py line 32-38
- V2 Tickets (BIRTHDAY_AVOIDANCE_TICKETS_V2) from super_model_synthesis.py line 164-170
- Mann-Whitney U test (non-parametric) for daily wins comparison
- Result: TREND_V2_BETTER - V2 better in 3/5 types but NOT significant (p>=0.05)
- Avg ROI Diff: +1.84% (V2 slightly better, not statistically significant)
- Acceptance NOT met: 0/5 significant tests, p<0.05 criterion failed
- Output: results/hyp005_birthday_cooldown.json (126KB, 11 jackpots analyzed)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_015_EXECUTOR_20251230_173500.md

## [2025-12-30 17:40:00] TASK_015 - PROXY_IMPL (ki0)

### Summary
- Script backtest_birthday_cooldown.py created - Python syntax VERIFIED
- V1/V2 Tickets correctly copied from source scripts (line refs accurate)
- Mann-Whitney U test used correctly (one-sided, alternative='greater' for V2>V1)
- JSON output valid (126KB, 11 jackpots, proper structure)
- Conclusion TREND_V2_BETTER accurate: avg +1.84% diff, 0/5 significant tests
- Acceptance NOT met as documented (p<0.05 AND V2>V1 required)
- No BUG-001 triggered - KENO-specific test with correct semantics
- No integration issues - standalone hypothesis test script

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_015_PROXY_IMPL_20251230_173800.md



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
- scripts/backtest_birthday_cooldown.py
- results/hyp005_birthday_cooldown.json

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
- Script backtest_birthday_cooldown.py created - Python syntax VERIFIED
- V1/V2 Tickets correctly copied from source scripts (line refs accurate)
- Mann-Whitney U test used correctly (one-sided, alternative='greater' for V2>V1)
- JSON output valid (126KB, 11 jackpots, proper structure)
- Conclusion TREND_V2_BETTER accurate: avg +1.84% diff, 0/5 significant tests
- Acceptance NOT met as documented (p<0.05 AND V2>V1 required)
- No BUG-001 triggered - KENO-specific test with correct semantics
- No integration issues - standalone hypothesis test script

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_015_PROXY_IMPL_20251230_173800.md

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
task: TASK_015
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK_015_VALIDATOR_20251230_174001.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
