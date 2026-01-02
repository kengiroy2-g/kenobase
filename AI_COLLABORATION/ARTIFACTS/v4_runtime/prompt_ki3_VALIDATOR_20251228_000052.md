AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Top-Pool Size Optimierung
TASK-ID: TASK-M01
PRIORITY: MEDIUM
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 23:57:52] TASK-M01 - EXECUTOR (ki2)

### Summary
- Created scripts/optimize_pool_size.py (340 lines) - Walk-Forward optimization for top_n_per_period
- Added number_pool section to config/default.yaml with n_periods, draws_per_period, top_n_per_period, top_n_total
- Script tests pool sizes [5,11,15,20] via Walk-Forward backtest using F1-Score metric
- Optimization result (12 periods, 2237 draws): top_n=20 marginally best (F1=0.2469), top_n=11 close (F1=0.2424)
- Default top_n_per_period=11 retained (difference <2% F1, statistically insignificant)
- Results saved to results/pool_optimization.json with full metrics
- CLI verified: --help works, optimization runs successfully

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-M01_EXECUTOR_20251227_235351.md

## [2025-12-28 00:00:52] TASK-M01 - PROXY_IMPL (ki0)

### Summary
- Script optimize_pool_size.py (541 lines) syntaktisch korrekt (py_compile OK)
- Config-Sektion number_pool korrekt in default.yaml:49-57 hinzugefuegt
- JSON-Output results/pool_optimization.json valide (json.load OK)
- Ergebnis top_n=20 marginal besser (F1=0.2469) vs top_n=11 (F1=0.2424), Diff <2%
- Default top_n_per_period=11 beibehalten (statistisch insignifikant)
- Script ist standalone, keine Integration Points verletzt
- Repro-Command verifiziert via --help und Ausfuehrung

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-M01_PROXY_IMPL_20251227_235752.md



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
- scripts/optimize_pool_size.py
- config/default.yaml
- results/pool_optimization.json

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
- Script optimize_pool_size.py (541 lines) syntaktisch korrekt (py_compile OK)
- Config-Sektion number_pool korrekt in default.yaml:49-57 hinzugefuegt
- JSON-Output results/pool_optimization.json valide (json.load OK)
- Ergebnis top_n=20 marginal besser (F1=0.2469) vs top_n=11 (F1=0.2424), Diff <2%
- Default top_n_per_period=11 beibehalten (statistisch insignifikant)
- Script ist standalone, keine Integration Points verletzt
- Repro-Command verifiziert via --help und Ausfuehrung

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-M01_PROXY_IMPL_20251227_235752.md

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
task: TASK-M01
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK-M01_VALIDATOR_20251228_000052.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
