AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Walk-Forward: Parameter-Grid
TASK-ID: TASK_025
PRIORITY: P2
PHASE: PROXY_FINAL

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

## [2025-12-30 20:43:50] TASK_025 - VALIDATOR (ki3)

### Summary
- Syntax check passed (py_compile OK)
- BH/FDR correction tested with 4 cases (basic, None-handling, no-sig, empty)
- JSON structure validated: all required keys present
- Data split verified: train(2023) < val(2024) < test(2025) - no leakage
- All imports verified (KENO_PROBABILITIES, get_fixed_quote, wilson_lower_bound)
- Quick mode output: 32 combos, 160 comparisons, 0 FDR-significant (expected)
- fdr_significant flag correctly added to each type result

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK_025_VALIDATOR_20251230_204150.md



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
ROLLE: PROXY (User-Stellvertreter - Finale Freigabe)
AUFGABE: Finale Freigabe mit Projekt-Perspektive.

PFLICHTLEKTUERE (kurz):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Falls Zweifel an Integration

EFFIZIENZ-REGELN:
- Nutze VALIDATOR OUTPUT + dein Wissen aus vorherigen Proxy-Phasen
- Keine weiteren Tests, nur finale Entscheidung

VALIDATOR OUTPUT (kurz):
- Syntax check passed (py_compile OK)
- BH/FDR correction tested with 4 cases (basic, None-handling, no-sig, empty)
- JSON structure validated: all required keys present
- Data split verified: train(2023) < val(2024) < test(2025) - no leakage
- All imports verified (KENO_PROBABILITIES, get_fixed_quote, wilson_lower_bound)
- Quick mode output: 32 combos, 160 comparisons, 0 FDR-significant (expected)
- fdr_significant flag correctly added to each type result

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK_025_VALIDATOR_20251230_204150.md

FINALE PRUEFUNG:
1. Hat Validator alle kritischen Aspekte geprueft?
2. Wuerde der USER diese Aenderung akzeptieren?
3. Gibt es offene Architektur-Fragen die der User entscheiden sollte?

ESKALATION an User wenn:
- Architektur-Entscheidung noetig die nicht in ADRs dokumentiert ist
- Unsicherheit ueber globale vs spezifische Werte
- Potenzielle Breaking Changes

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: COMPLETE
task: TASK_025
role: PROXY
phase: PROXY_FINAL
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

# Proxy Final Review

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_025_PROXY_FINAL_20251230_204350.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
