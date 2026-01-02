AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Walk-Forward Backtest Framework
TASK-ID: TASK-P03
PRIORITY: CRITICAL
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 03:26:19] TASK-P03 - ARCHITECT (ki1)

### Summary
- Walk-Forward Backtest Framework bereits implementiert in scripts/backtest.py
- BacktestEngine mit Train/Test-Split pro Periode vorhanden
- Metriken (Precision/Recall/F1) in validation_metrics.py extrahiert
- Physics-Layer Integration via PipelineRunner funktional
- Game-specific thresholds aus config/default.yaml werden verwendet
- Erweiterungsplan: Multi-Strategy-Support + Confidence-Intervals
- Hauptaufgabe: Refactoring fuer erweiterbare Strategy-Schnittstelle
- Tests: tests/unit/test_backtest.py zu erstellen

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK-P03_ARCHITECT_20251228_032419.md

## [2025-12-28 03:28:20] TASK-P03 - PROXY_PLAN (ki0)

### Summary
- Plan ist vollstaendig und klar strukturiert (4 Phasen A-D)
- Game-specific thresholds korrekt in config/default.yaml:120-148 definiert (BUG-001 AVOIDED)
- BacktestEngine nutzt game_config.get_hot_threshold() (backtest.py:193-195) - VERIFIZIERT
- Strategy-Abstraktion sinnvoll als Erweiterung (Factory-Pattern)
- Backward-Compatibility explizit als Risiko adressiert
- Alle betroffenen Dateien im WORKING_SET genannt
- Acceptance Criteria messbar (AC5: avg_f1 >= 0.30, AC6: std_f1 <= 0.15)
- Tests-Plan umfassend (unit + integration)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P03_PROXY_PLAN_20251228_032619.md



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
- scripts/backtest.py
- kenobase/pipeline/validation_metrics.py
- kenobase/analysis/frequency.py
- config/default.yaml
- kenobase/core/data_loader.py
- kenobase/core/config.py

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
- Plan ist vollstaendig und klar strukturiert (4 Phasen A-D)
- Game-specific thresholds korrekt in config/default.yaml:120-148 definiert (BUG-001 AVOIDED)
- BacktestEngine nutzt game_config.get_hot_threshold() (backtest.py:193-195) - VERIFIZIERT
- Strategy-Abstraktion sinnvoll als Erweiterung (Factory-Pattern)
- Backward-Compatibility explizit als Risiko adressiert
- Alle betroffenen Dateien im WORKING_SET genannt
- Acceptance Criteria messbar (AC5: avg_f1 >= 0.30, AC6: std_f1 <= 0.15)
- Tests-Plan umfassend (unit + integration)

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P03_PROXY_PLAN_20251228_032619.md

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
task: TASK-P03
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK-P03_EXECUTOR_20251228_032820.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
