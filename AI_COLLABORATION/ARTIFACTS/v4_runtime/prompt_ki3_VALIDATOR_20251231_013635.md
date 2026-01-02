AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: V1 vs V2 PARALLEL: Per Wochentag Vergleich
TASK-ID: TASK_039b
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-31 01:34:35] TASK_039b - EXECUTOR (ki2)

### Summary
- Created scripts/compare_v1_v2_weekday.py for V1 vs V2 weekday comparison
- V1 Tickets from backtest_birthday_cooldown.py lines 37-43, V2 from lines 46-52
- Compares ROI per weekday (7 Kategorien) for 5 Keno types (Typ 6-10)
- Nullmodell: weekday-preserving shuffle permutation test (1000 permutations)
- Benjamini-Hochberg correction applied across 5 types
- Result: V2 trend better (+8.53% avg), but NOT significant (0/5 BH-corrected)
- Output: results/v1_v2_weekday_comparison.json (887 lines, valid JSON)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_039b_EXECUTOR_20251231_012835.md

## [2025-12-31 01:36:35] TASK_039b - PROXY_IMPL (ki0)

### Summary
- Script scripts/compare_v1_v2_weekday.py created with correct V1/V2 ticket definitions (verified against backtest_birthday_cooldown.py:37-52)
- JSON output validated (results/v1_v2_weekday_comparison.json) with correct structure
- Nullmodell implemented correctly (weekday-preserving shuffle, 1000 permutations)
- Benjamini-Hochberg FDR correction applied across 5 types (0/5 significant)
- Result: V2 trend +8.53% avg, 3/5 types better, but NOT statistically significant
- Syntax check passed (py_compile)
- No Known Bugs triggered (BUG-001..010)
- No cross-file integration issues detected

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_039b_PROXY_IMPL_20251231_013435.md



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
- scripts/analyze_weekday_roi.py
- scripts/backtest_birthday_cooldown.py
- results/weekday_roi_analysis.json
- kenobase/core/keno_quotes.py
- scripts/compare_v1_v2_weekday.py
- results/v1_v2_weekday_comparison.json

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
- Script scripts/compare_v1_v2_weekday.py created with correct V1/V2 ticket definitions (verified against backtest_birthday_cooldown.py:37-52)
- JSON output validated (results/v1_v2_weekday_comparison.json) with correct structure
- Nullmodell implemented correctly (weekday-preserving shuffle, 1000 permutations)
- Benjamini-Hochberg FDR correction applied across 5 types (0/5 significant)
- Result: V2 trend +8.53% avg, 3/5 types better, but NOT statistically significant
- Syntax check passed (py_compile)
- No Known Bugs triggered (BUG-001..010)
- No cross-file integration issues detected

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_039b_PROXY_IMPL_20251231_013435.md

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
task: TASK_039b
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK_039b_VALIDATOR_20251231_013635.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
