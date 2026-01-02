AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Test HYP_002: Cooldown High-Wins
TASK-ID: TASK_012
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 16:50:58] TASK_012 - EXECUTOR (ki2)

### Summary
- Extended backtest_post_jackpot.py with HYP_002 High-Wins (>=100 EUR) counting
- Added chi-square test comparing cooldown vs normal high-wins frequency
- Ran backtest: 0 high-wins in cooldown (314 draws) vs 1 in normal (330 draws)
- Result: NOT_SIGNIFICANT due to insufficient sample size (total HW=1)
- Updated HYPOTHESES_CATALOG with HYP_002 section and changelog
- Artifact saved to results/post_jackpot_backtest.json with hyp002 section
- Tendenz konsistent mit WL-003 aber statistisch nicht verwertbar

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_012_EXECUTOR_20251230_164658.md

## [2025-12-30 16:52:58] TASK_012 - PROXY_IMPL (ki0)

### Summary
- Script extended with HYP_002 high-wins counting (>=100 EUR threshold)
- Chi-square test implemented correctly with N<5 guard clause
- Results: 0 high-wins cooldown vs 1 normal = NOT_SIGNIFICANT
- JSON artifact valid with proper hyp002 section structure
- HYPOTHESES_CATALOG updated with HYP_002 section at lines 111-151
- Python syntax verified OK via py_compile
- No integration issues - standalone backtest script
- Repro command verified: `python scripts/backtest_post_jackpot.py`

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_012_PROXY_IMPL_20251230_165058.md



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
- scripts/backtest_post_jackpot.py
- results/post_jackpot_backtest.json
- AI_COLLABORATION/KNOWLEDGE_BASE/HYPOTHESES_CATALOG.md

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
- Script extended with HYP_002 high-wins counting (>=100 EUR threshold)
- Chi-square test implemented correctly with N<5 guard clause
- Results: 0 high-wins cooldown vs 1 normal = NOT_SIGNIFICANT
- JSON artifact valid with proper hyp002 section structure
- HYPOTHESES_CATALOG updated with HYP_002 section at lines 111-151
- Python syntax verified OK via py_compile
- No integration issues - standalone backtest script
- Repro command verified: `python scripts/backtest_post_jackpot.py`

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_012_PROXY_IMPL_20251230_165058.md

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
task: TASK_012
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK_012_VALIDATOR_20251230_165258.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
