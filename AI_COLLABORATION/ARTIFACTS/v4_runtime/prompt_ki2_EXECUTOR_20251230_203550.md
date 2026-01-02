AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Walk-Forward: Parameter-Grid
TASK-ID: TASK_025
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 20:33:49] TASK_025 - ARCHITECT (ki1)

### Summary
- Walk-Forward Parameter Grid builds on existing frozen_position_rules backtest
- Extends backtest_frozen_position_rules.py with itertools.product grid search
- Parameter space: 10+ parameters with ~100 grid points total
- Output: ROI/hits/big-win metrics per (param_combo, keno_type, window)
- Uses existing train->val->test splits (no new data leakage)
- ~2h implementation, ~30min-1h runtime on full grid
- Results saved to results/walk_forward_param_grid.json

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_025_ARCHITECT_20251230_203049.md

## [2025-12-30 20:35:50] TASK_025 - PROXY_PLAN (ki0)

### Summary
- Plan extends existing backtest_frozen_position_rules.py with grid search
- Existing script has ~13 tunable parameters (lines 84-111)
- Architecture sound: reuses train->val->test split (no new leakage)
- Output to results/walk_forward_param_grid.json (no conflict)
- CONCERN: Multiple testing (100 grid x 5 types x 4 windows = 2000+ comparisons)
- MITIGATION REQUIRED: Implement BH/FDR correction per CLAUDE.md Section 3.0
- Repro command specified: python scripts/walk_forward_param_grid.py --output results/walk_forward_param_grid.json
- Runtime estimate reasonable (~30min-1h for full grid)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_025_PROXY_PLAN_20251230_203349.md



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
- (leer)

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
ROLLE: EXECUTOR
AUFGABE: Fuehre den genehmigten Plan aus.

EFFIZIENZ-REGELN:
- Starte mit WORKING SET; vermeide Repo-weite Scans. Wenn du suchen musst: 1 gezieltes Grep pro Subtask, nicht breit.
- Schreibe nur kurze, entscheidungsrelevante Logs; grosse Logs nach AI_COLLABORATION/ARTIFACTS/ auslagern und verlinken.
- Aktualisiere Status ausschliesslich ueber den Handoff (keine CURRENT_STATUS edits im Body).
- Aendere niemals AI_COLLABORATION/MESSAGE_QUEUE/* oder AI_COLLABORATION/RESULTS/CURRENT_STATUS.md (nur Handoff-Ausgabe).
- Vermeide das Ausgeben von Diffs (diff --git, Patch-BlÃ¶cke). In der Antwort nur Summary + Pfade.

PLAN (kurz):
- Plan extends existing backtest_frozen_position_rules.py with grid search
- Existing script has ~13 tunable parameters (lines 84-111)
- Architecture sound: reuses train->val->test split (no new leakage)
- Output to results/walk_forward_param_grid.json (no conflict)
- CONCERN: Multiple testing (100 grid x 5 types x 4 windows = 2000+ comparisons)
- MITIGATION REQUIRED: Implement BH/FDR correction per CLAUDE.md Section 3.0
- Repro command specified: python scripts/walk_forward_param_grid.py --output results/walk_forward_param_grid.json
- Runtime estimate reasonable (~30min-1h for full grid)

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_025_PROXY_PLAN_20251230_203349.md

REGELN:
1. Folge Checkliste exakt
2. Keine eigenen Interpretationen
3. Dokumentiere jeden Schritt
4. WICHTIG: Fuege files_changed: [...] im YAML hinzu

TOKEN HYGIENE:
- Final Output muss direkt das Handoff-Markdown sein (keine Diffs, keine Zusatztexte).
- Keine langen Command-Outputs im Handoff
- Bei Fehlern: nur Command + 20 Zeilen excerpt
- Lange Logs: speichere in AI_COLLABORATION/ARTIFACTS/ und referenziere nur Pfad

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: COMPLETE
task: TASK_025
role: EXECUTOR
phase: EXECUTOR
files_changed: []
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

# Umsetzung

WICHTIG: Erstelle Handoff-Datei wenn fertig:
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK_025_EXECUTOR_20251230_203550.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
