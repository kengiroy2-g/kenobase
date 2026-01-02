AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: ML Model Selection
TASK-ID: TASK-P02
PRIORITY: CRITICAL
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 03:07:19] TASK-P02 - ARCHITECT (ki1)

### Summary
- ML Model Selection fuer KENO Zahlenvorhersage analysiert
- 4 Kandidaten bewertet - LightGBM empfohlen
- Feature-Set aus Phase 2 definiert (4 bestaetigt, 3 falsifiziert)
- Cross-Validation Schema mit 5-Fold + Walk-Forward spezifiziert
- Hyperparameter-Tuning via Optuna vorgeschlagen
- Acceptance Criteria F1 >= 0.50, Stability std <= 0.05
- Dependencies TASK-P01 (Feature Pipeline)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK-P02_ARCHITECT_20251228_030218.md

## [2025-12-28 03:09:19] TASK-P02 - PROXY_PLAN (ki0)

### Summary
- ARCHITECT Handoff ist minimal aber Kernentscheidungen sind korrekt
- LightGBM-Empfehlung ist vernuenftig (schnell, handles categorical, native LGBM Ranker)
- Feature-Set aus TASK-P01 (20 Features) steht bereit in kenobase/features/
- Cross-Validation Schema (5-Fold + Walk-Forward) ist Standard fuer Zeitreihendaten
- F1 >= 0.50 Ziel ist realistisch (aktuell 0.4434 per PHASE3_PREDICTION_MODEL.md)
- Stability std <= 0.05 passend zu Metriken-Ziel in Backlog
- Dependency TASK-P01 ist COMPLETE - Pipeline bereit
- Empfehlung: EXECUTOR soll kenobase/prediction/model.py erstellen

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P02_PROXY_PLAN_20251228_030719.md



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
- ARCHITECT Handoff ist minimal aber Kernentscheidungen sind korrekt
- LightGBM-Empfehlung ist vernuenftig (schnell, handles categorical, native LGBM Ranker)
- Feature-Set aus TASK-P01 (20 Features) steht bereit in kenobase/features/
- Cross-Validation Schema (5-Fold + Walk-Forward) ist Standard fuer Zeitreihendaten
- F1 >= 0.50 Ziel ist realistisch (aktuell 0.4434 per PHASE3_PREDICTION_MODEL.md)
- Stability std <= 0.05 passend zu Metriken-Ziel in Backlog
- Dependency TASK-P01 ist COMPLETE - Pipeline bereit
- Empfehlung: EXECUTOR soll kenobase/prediction/model.py erstellen

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P02_PROXY_PLAN_20251228_030719.md

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
task: TASK-P02
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK-P02_EXECUTOR_20251228_030919.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
