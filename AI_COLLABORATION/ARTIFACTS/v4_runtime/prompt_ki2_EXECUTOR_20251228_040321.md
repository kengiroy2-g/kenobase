AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Summen-Filter Integration
TASK-ID: TASK-P05
PRIORITY: HIGH
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 04:01:21] TASK-P05 - ARCHITECT (ki1)

### Summary
- CombinationEngine hat bereits min_sum/max_sum Filter (combination_engine.py:97-98,202-215)
- sum_distribution.py analysiert Summen, liefert Cluster-Ranges (SumCluster dataclass)
- Integration fehlt: Summen-Filter soll aus Cluster-Analyse konfiguriert werden
- Neues Modul combination_filter.py baut Bruecke zwischen sum_distribution und CombinationEngine
- Config-Integration: min_sum/max_sum aus detected Clusters oder manuell
- Pipeline-Runner muss um Summen-Analyse-Schritt erweitert werden
- predict.py nutzt bereits generate_recommendations mit max_per_decade

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK-P05_ARCHITECT_20251228_035721.md

## [2025-12-28 04:03:21] TASK-P05 - PROXY_PLAN (ki0)

### Summary
- CombinationEngine hat min_sum/max_sum in __init__ (Z.97-98) und _passes_sum_filter (Z.202-215) - VERIFIZIERT
- sum_distribution.py liefert SumCluster mit range_min/range_max (Z.60-76) - VERIFIZIERT
- Config hat bereits sum_windows Section (default.yaml Z.86-94) mit enabled, bin_width, expected_mean
- Integration-Plan ist konzeptionell solide: combination_filter.py als Bruecke-Modul
- PipelineRunner (runner.py) hat keine Summen-Analyse - muss erweitert werden
- Keine globalen Thresholds wo game-spezifische noetig (games Section hat eigene Thresholds)
- from_config Factory (Z.258-304) kann um sum_bounds erweitert werden
- Geschaetzter Aufwand 6.5h ist realistisch

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P05_PROXY_PLAN_20251228_040121.md



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
- CombinationEngine hat min_sum/max_sum in __init__ (Z.97-98) und _passes_sum_filter (Z.202-215) - VERIFIZIERT
- sum_distribution.py liefert SumCluster mit range_min/range_max (Z.60-76) - VERIFIZIERT
- Config hat bereits sum_windows Section (default.yaml Z.86-94) mit enabled, bin_width, expected_mean
- Integration-Plan ist konzeptionell solide: combination_filter.py als Bruecke-Modul
- PipelineRunner (runner.py) hat keine Summen-Analyse - muss erweitert werden
- Keine globalen Thresholds wo game-spezifische noetig (games Section hat eigene Thresholds)
- from_config Factory (Z.258-304) kann um sum_bounds erweitert werden
- Geschaetzter Aufwand 6.5h ist realistisch

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P05_PROXY_PLAN_20251228_040121.md

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
task: TASK-P05
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK-P05_EXECUTOR_20251228_040321.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
