AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Confidence Intervals
TASK-ID: TASK-P11
PRIORITY: MEDIUM
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 05:38:26] TASK-P11 - ARCHITECT (ki1)

### Summary
- Analysiert bestehende confidence-Implementierung in model.py:117 (PredictionResult.confidence)
- Identifiziert Luecke: Keine statistischen Konfidenzintervalle fuer Vorhersagen
- Bestehend: Einfache distanz-basierte confidence in model.py:296
- Plan: Bootstrap-basierte CI fuer ensemble_score und ml_probability
- Ziel-Module: kenobase/prediction/confidence.py (neu), ensemble.py (Integration)
- Implementierung: 95% CI via Percentile-Bootstrap (1000 Resamples)
- Acceptance: CI coverage test, width < 0.3 fuer stabile Vorhersagen

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK-P11_ARCHITECT_20251228_053526.md

## [2025-12-28 05:40:26] TASK-P11 - PROXY_PLAN (ki0)

### Summary
- Plan ist mechanisch vollstaendig: Bootstrap CI fuer ensemble_score + ml_probability
- Ziel-Datei confidence.py (neu) klar definiert
- Integration in ensemble.py:74 (EnsemblePrediction.confidence) vorgesehen
- Acceptance Criteria messbar: CI coverage test + width < 0.3
- Keine globalen Thresholds - 95% ist Standard fuer CI (OK)
- Bootstrap mit 1000 Resamples ist Standard-Praxis
- Keine CLAUDE.md/ADR Konflikte identifiziert
- WORKING_SET erweitert um ensemble.py fuer Executor

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P11_PROXY_PLAN_20251228_053826.md



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
- Plan ist mechanisch vollstaendig: Bootstrap CI fuer ensemble_score + ml_probability
- Ziel-Datei confidence.py (neu) klar definiert
- Integration in ensemble.py:74 (EnsemblePrediction.confidence) vorgesehen
- Acceptance Criteria messbar: CI coverage test + width < 0.3
- Keine globalen Thresholds - 95% ist Standard fuer CI (OK)
- Bootstrap mit 1000 Resamples ist Standard-Praxis
- Keine CLAUDE.md/ADR Konflikte identifiziert
- WORKING_SET erweitert um ensemble.py fuer Executor

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P11_PROXY_PLAN_20251228_053826.md

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
task: TASK-P11
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK-P11_EXECUTOR_20251228_054026.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
