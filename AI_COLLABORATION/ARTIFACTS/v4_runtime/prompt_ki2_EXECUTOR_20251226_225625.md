AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P5-01: Backtest-Script implementieren
TASK-ID: phase5_task01_backtest_script
PRIORITY: P1
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-26 22:54:25] phase5_task01_backtest_script - ARCHITECT (ki1)

### Summary
- Analyzed existing backtest command in scripts/analyze.py (lines 297-406) - basic but incomplete
- Identified need for dedicated scripts/backtest.py with full metrics (Precision, Recall, F1, ROI)
- Pipeline runner.py already exposes PhysicsResult and PipelineResult needed for metrics
- Config exists in default.yaml with physics/analysis settings
- DataLoader provides DrawResult with date, numbers, game_type for period splitting
- Physics metrics module provides stability_score, hurst_exponent, regime_complexity
- Frequency module provides calculate_rolling_frequency for temporal validation

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_phase5_task01_backtest_script_ARCHITECT_20251226_225024.md

## [2025-12-26 22:56:25] phase5_task01_backtest_script - PROXY_PLAN (ki0)

### Summary
- Plan correctly identifies modules: PipelineRunner, DrawResult, get_hot_numbers all exist and match plan
- DataLoader.DrawResult has date, numbers, game_type fields (verified data_loader.py:43-77)
- get_hot_numbers exists in frequency.py:335-354 with correct signature
- PipelineRunner.run() returns PipelineResult with PhysicsResult (runner.py:163-267)
- Plan proposes correct walk-forward backtest approach with train/test split
- Metrics (Precision/Recall/F1) semantics properly defined for hot-numbers prediction
- Working set request is complete and appropriate (6 files)
- No known bugs triggered (no global thresholds misapplied)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase5_task01_backtest_script_PROXY_PLAN_20251226_225425.md



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
- Plan correctly identifies modules: PipelineRunner, DrawResult, get_hot_numbers all exist and match plan
- DataLoader.DrawResult has date, numbers, game_type fields (verified data_loader.py:43-77)
- get_hot_numbers exists in frequency.py:335-354 with correct signature
- PipelineRunner.run() returns PipelineResult with PhysicsResult (runner.py:163-267)
- Plan proposes correct walk-forward backtest approach with train/test split
- Metrics (Precision/Recall/F1) semantics properly defined for hot-numbers prediction
- Working set request is complete and appropriate (6 files)
- No known bugs triggered (no global thresholds misapplied)

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase5_task01_backtest_script_PROXY_PLAN_20251226_225425.md

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
task: phase5_task01_backtest_script
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_phase5_task01_backtest_script_EXECUTOR_20251226_225625.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
