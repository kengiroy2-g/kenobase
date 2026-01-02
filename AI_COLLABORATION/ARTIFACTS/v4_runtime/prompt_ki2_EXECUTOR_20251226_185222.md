AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P2-01: Zahlenpool-Generator migrieren
TASK-ID: phase2_task01_number_pool
PRIORITY: P1
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-26 18:50:22] phase2_task01_number_pool - ARCHITECT (ki1)

### Summary
- Analyzed legacy V9 code in all_code/00_0_Keno_6-Kombi_Analyse_V9.py:45-85
- Identified generiere_zahlenpool_optimiert() as source function to migrate
- New module kenobase/core/number_pool.py with NumberPoolGenerator class
- Uses existing DataLoader for data input, returns set of integers
- Configurable via AnalysisConfig for period sizing
- 4 public methods: generate(), get_top_n(), get_intersections(), from_draws()
- Unit tests in tests/unit/test_number_pool.py (8 test cases)
- Integration with kenobase/core/__init__.py exports

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_phase2_task01_number_pool_ARCHITECT_20251226_184522.md

## [2025-12-26 18:52:22] phase2_task01_number_pool - PROXY_PLAN (ki0)

### Summary
- Legacy function generiere_zahlenpool_optimiert() correctly identified at V9:45-85
- Plan correctly proposes NumberPoolGenerator class with 4 public methods
- Integration with existing DataLoader (DrawResult, list[int] numbers) is coherent
- AnalysisConfig already has windows=[5,10,20,50] for period sizing - plan should use this
- __init__.py exports need updating (currently only config + data_loader)
- Algorithm migration: 3 periods x 10 draws, Top-11, intersections - well understood
- Test coverage plan (8 cases) is adequate for MVP
- No BUG-001/003 violations detected (module is per-game, no global thresholds)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase2_task01_number_pool_PROXY_PLAN_20251226_185022.md



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
- Legacy function generiere_zahlenpool_optimiert() correctly identified at V9:45-85
- Plan correctly proposes NumberPoolGenerator class with 4 public methods
- Integration with existing DataLoader (DrawResult, list[int] numbers) is coherent
- AnalysisConfig already has windows=[5,10,20,50] for period sizing - plan should use this
- __init__.py exports need updating (currently only config + data_loader)
- Algorithm migration: 3 periods x 10 draws, Top-11, intersections - well understood
- Test coverage plan (8 cases) is adequate for MVP
- No BUG-001/003 violations detected (module is per-game, no global thresholds)

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase2_task01_number_pool_PROXY_PLAN_20251226_185022.md

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
task: phase2_task01_number_pool
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_phase2_task01_number_pool_EXECUTOR_20251226_185222.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
