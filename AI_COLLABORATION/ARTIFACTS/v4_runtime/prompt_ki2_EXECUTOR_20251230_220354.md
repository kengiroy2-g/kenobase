AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Multiple Testing Korrektur
TASK-ID: TASK_031
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 22:01:54] TASK_031 - ARCHITECT (ki1)

### Summary
- TASK: Multiple Testing Korrektur - implementiere FDR-Korrektur fuer alle Hypothesen-Tests
- benjamini_hochberg_fdr() existiert bereits in kenobase/analysis/null_models.py (Zeilen 268-333)
- Problem: 14+ HYP-Tests haben p_values, aber keine FDR-Korrektur wird konsolidiert angewendet
- Loesung: Neues Script scripts/apply_fdr_correction.py das alle p_values aus results/*.json sammelt
- Output: results/fdr_corrected_hypotheses.json mit q_values und significant_after_correction Flag
- ADR bestimmt max 21 primaere Tests (7 Axiome x 3 Predictions) mit alpha=0.05
- Acceptance Criteria: q_values berechnet, Markdown-Report generiert, Unit-Test vorhanden

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_031_ARCHITECT_20251230_215854.md

## [2025-12-30 22:03:54] TASK_031 - PROXY_PLAN (ki0)

### Summary
- Plan ist mechanisch vollstaendig: Script, Test, Report als Deliverables definiert
- benjamini_hochberg_fdr() existiert in kenobase/analysis/null_models.py:268-333 - VERIFIZIERT
- 61 JSON-Dateien mit p_value gefunden in results/ - ausreichende Datenbasis
- p_value Strukturen sind heterogen (nested keys wie mann_whitney.p_value, welch_t_test.p_value_onesided)
- Hinweis: Script muss flexible JSON-Traversierung implementieren (nicht nur top-level p_value)
- Granularity GLOBAL ist korrekt fuer FDR (alle Tests zusammen korrigieren)
- ADR-Referenz auf max 21 primaere Tests (7 Axiome x 3 Predictions) vorhanden
- Acceptance Criteria messbar: q_values berechnet, Markdown-Report, Unit-Test

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_031_PROXY_PLAN_20251230_220154.md



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
- Plan ist mechanisch vollstaendig: Script, Test, Report als Deliverables definiert
- benjamini_hochberg_fdr() existiert in kenobase/analysis/null_models.py:268-333 - VERIFIZIERT
- 61 JSON-Dateien mit p_value gefunden in results/ - ausreichende Datenbasis
- p_value Strukturen sind heterogen (nested keys wie mann_whitney.p_value, welch_t_test.p_value_onesided)
- Hinweis: Script muss flexible JSON-Traversierung implementieren (nicht nur top-level p_value)
- Granularity GLOBAL ist korrekt fuer FDR (alle Tests zusammen korrigieren)
- ADR-Referenz auf max 21 primaere Tests (7 Axiome x 3 Predictions) vorhanden
- Acceptance Criteria messbar: q_values berechnet, Markdown-Report, Unit-Test

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_031_PROXY_PLAN_20251230_220154.md

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
task: TASK_031
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK_031_EXECUTOR_20251230_220354.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
