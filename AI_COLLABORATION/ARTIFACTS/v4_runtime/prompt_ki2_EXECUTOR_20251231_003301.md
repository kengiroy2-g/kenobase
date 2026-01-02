AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: V1 vs V2 PARALLEL: Gesamt-Performance
TASK-ID: TASK_038
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-31 00:31:01] TASK_038 - ARCHITECT (ki1)

### Summary
- V1 vs V2 Performance-Analyse anhand existierender Backtests durchgefuehrt
- V2 uebertrifft V1 in bestimmten Strategien (pair_focused Typ6/7 zeigt positive ROI)
- V1 hat kein Ticket mit positiver ROI im Vergleichszeitraum
- Original-Modell bleibt Baseline (-38% bis -55% ROI je nach Typ)
- Beste Strategie V2 Typ6 pair_focused: +53.24% ROI (2018-2024, N=2237)
- Zweitbeste: V2 Typ7 pair_focused: +28.79% ROI
- Overfitting-Risiko hoch - keine OOS-Validierung in diesen Zahlen
- Implementierungsplan fuer EXECUTOR bereitgestellt

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_038_ARCHITECT_20251231_002901.md

## [2025-12-31 00:33:01] TASK_038 - PROXY_PLAN (ki0)

### Summary
- Plan basiert auf existierenden Artefakten - keine neuen Berechnungen noetig
- Datenintegritaet verifiziert: backtest_v1_v2_comparison.json enthaelt N=2237 (2018-2024)
- ROI-Behauptungen korrekt: V2 Typ6 pair_focused +53.24%, V2 Typ7 pair_focused +28.79%
- Kritische Warnung im Plan: Overfitting-Risiko angemessen dokumentiert
- SYSTEM_STATUS.json zeigt keine stabile positive ROI nach Quoten-Korrektur
- Plan fordert nur Synthese-Report, kein neuer Code - akzeptabel
- Acceptance Criteria sind messbar und erfuellt
- EXECUTOR Aufgaben klar definiert: results/v1_v2_performance_synthesis.md erstellen

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_038_PROXY_PLAN_20251231_003101.md



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
- results/backtest_v1_v2_comparison.json
- results/super_model_comparison_summary.md
- kenobase/core/keno_quotes.py (falls Quote-Verifikation noetig)
- AI_COLLABORATION/HANDOFFS/ki1_TASK_038_ARCHITECT_20251231_002901.md

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
- Plan basiert auf existierenden Artefakten - keine neuen Berechnungen noetig
- Datenintegritaet verifiziert: backtest_v1_v2_comparison.json enthaelt N=2237 (2018-2024)
- ROI-Behauptungen korrekt: V2 Typ6 pair_focused +53.24%, V2 Typ7 pair_focused +28.79%
- Kritische Warnung im Plan: Overfitting-Risiko angemessen dokumentiert
- SYSTEM_STATUS.json zeigt keine stabile positive ROI nach Quoten-Korrektur
- Plan fordert nur Synthese-Report, kein neuer Code - akzeptabel
- Acceptance Criteria sind messbar und erfuellt
- EXECUTOR Aufgaben klar definiert: results/v1_v2_performance_synthesis.md erstellen

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_038_PROXY_PLAN_20251231_003101.md

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
task: TASK_038
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK_038_EXECUTOR_20251231_003301.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
