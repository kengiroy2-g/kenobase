AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Walk-Forward: Parameter-Grid
TASK-ID: TASK_025
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 20:39:50] TASK_025 - EXECUTOR (ki2)

### Summary
- Created scripts/walk_forward_param_grid.py (550 LOC)
- Extends backtest_frozen_position_rules.py with itertools.product grid search
- Implements Benjamini-Hochberg FDR correction for multiple testing
- Quick mode (--quick): 32 combos, 3.7s runtime; Full mode: ~83 combos
- Output: ROI/hits/big-win per (param_combo, keno_type, window)
- Verified: JSON output structure correct, FDR correction applied
- Quick test result: 0/160 significant at alpha=0.10 (expected for small grid)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_025_EXECUTOR_20251230_203550.md

## [2025-12-30 20:41:50] TASK_025 - PROXY_IMPL (ki0)

### Summary
- Syntax check passed (py_compile OK)
- JSON output valid: 32 grid combos, 160 comparisons, structure correct
- BH/FDR correction implemented correctly (lines 611-650)
- Train->val->test split maintained (no leakage)
- Imports verified: KENO_PROBABILITIES, wilson_lower_bound, DataLoader all exist
- Quick mode works (3.7s runtime, 32 combos)
- 0/160 significant at alpha=0.10 (expected for small OOS period)
- No architecture conflicts or Known Bugs triggered

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_025_PROXY_IMPL_20251230_203950.md



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
- scripts/walk_forward_param_grid.py
- results/walk_forward_param_grid.json

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
- Syntax check passed (py_compile OK)
- JSON output valid: 32 grid combos, 160 comparisons, structure correct
- BH/FDR correction implemented correctly (lines 611-650)
- Train->val->test split maintained (no leakage)
- Imports verified: KENO_PROBABILITIES, wilson_lower_bound, DataLoader all exist
- Quick mode works (3.7s runtime, 32 combos)
- 0/160 significant at alpha=0.10 (expected for small OOS period)
- No architecture conflicts or Known Bugs triggered

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_025_PROXY_IMPL_20251230_203950.md

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
task: TASK_025
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK_025_VALIDATOR_20251230_204150.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
