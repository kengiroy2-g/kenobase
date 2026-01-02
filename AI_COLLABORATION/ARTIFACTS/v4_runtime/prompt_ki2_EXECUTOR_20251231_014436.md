AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: V1 vs V2 PARALLEL: Per 28-Tage-Zyklus
TASK-ID: TASK_039c
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-31 01:43:35] TASK_039c - ARCHITECT (ki1)

### Summary
- Task: Implement V1 vs V2 comparison per 28-day cycle (calendar-month proxy)
- Existing infrastructure in scripts/compare_v1_v2_phases.py provides template
- Extend with cycle_start_date segmentation (28 days rolling)
- Output metrics per cycle with ROI, games played, high wins
- Target: scripts/compare_v1_v2_cycles.py -> results/v1_v2_cycle_comparison.json
- Reuses SuperModelV1, SuperModelV2, simulate_ticket from existing modules
- Granularity: per-28-day-cycle (~28 draws per cycle)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_039c_ARCHITECT_20251231_014035.md

## [2025-12-31 01:44:36] TASK_039c - PROXY_PLAN (ki0)

### Summary
- Plan vollstaendig: Target script/output klar definiert
- Template vorhanden: scripts/compare_v1_v2_phases.py (469 Zeilen) liefert robuste Basis
- Granularitaet angemessen: per-28-day-cycle statt GK1-Cooldown Phase
- Semantik klar: cycle_idx, start/end dates, v1/v2 ROI, delta, winner
- Keine globalen Thresholds wo spezifische noetig (BUG-001 N/A)
- Imports verifiziert: SuperModelV1, SuperModelV2, simulate_ticket existieren
- Repro-Kommando angegeben: python scripts/compare_v1_v2_cycles.py
- Output-Pfad konsistent: results/v1_v2_cycle_comparison.json

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_039c_PROXY_PLAN_20251231_014336.md



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
- AI_COLLABORATION/HANDOFFS/ki1_TASK_039c_ARCHITECT_20251231_014035.md

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
- Plan vollstaendig: Target script/output klar definiert
- Template vorhanden: scripts/compare_v1_v2_phases.py (469 Zeilen) liefert robuste Basis
- Granularitaet angemessen: per-28-day-cycle statt GK1-Cooldown Phase
- Semantik klar: cycle_idx, start/end dates, v1/v2 ROI, delta, winner
- Keine globalen Thresholds wo spezifische noetig (BUG-001 N/A)
- Imports verifiziert: SuperModelV1, SuperModelV2, simulate_ticket existieren
- Repro-Kommando angegeben: python scripts/compare_v1_v2_cycles.py
- Output-Pfad konsistent: results/v1_v2_cycle_comparison.json

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_039c_PROXY_PLAN_20251231_014336.md

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
task: TASK_039c
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK_039c_EXECUTOR_20251231_014436.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
