AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P3-01: Model Laws A/B/C implementieren
TASK-ID: phase3_task01_model_laws
PRIORITY: P1
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-26 20:15:08] phase3_task01_model_laws - ARCHITECT (ki1)

### Summary
- Physics module exists as empty stub: kenobase/physics/__init__.py
- Config system (PhysicsConfig) already supports Model Laws parameters
- Three new files needed: model_laws.py, avalanche.py, metrics.py
- Laws A/B/C specs fully defined in CLAUDE.md Section 6
- Test file tests/unit/test_model_laws.py must be created
- Integration with config via PhysicsConfig thresholds

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_phase3_task01_model_laws_ARCHITECT_20251226_201207.md

## [2025-12-26 20:17:08] phase3_task01_model_laws - PROXY_PLAN (ki0)

### Summary
- Physics module stub exists (kenobase/physics/__init__.py, 2 lines)
- PhysicsConfig verified in config.py:60-79 with all Model Law parameters
- Three files to create: model_laws.py, avalanche.py, metrics.py
- CLAUDE.md Section 6 provides complete specs for Laws A/B/C
- Test location confirmed: tests/unit/ exists (test_model_laws.py to be created)
- Thresholds are global (stability=0.9, criticality_warning=0.7, criticality_critical=0.85)
- No BUG-001 violation: global thresholds appropriate for physics formulas
- Integration path clear: PhysicsConfig -> model_laws.py functions

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase3_task01_model_laws_PROXY_PLAN_20251226_201508.md



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
- Physics module stub exists (kenobase/physics/__init__.py, 2 lines)
- PhysicsConfig verified in config.py:60-79 with all Model Law parameters
- Three files to create: model_laws.py, avalanche.py, metrics.py
- CLAUDE.md Section 6 provides complete specs for Laws A/B/C
- Test location confirmed: tests/unit/ exists (test_model_laws.py to be created)
- Thresholds are global (stability=0.9, criticality_warning=0.7, criticality_critical=0.85)
- No BUG-001 violation: global thresholds appropriate for physics formulas
- Integration path clear: PhysicsConfig -> model_laws.py functions

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase3_task01_model_laws_PROXY_PLAN_20251226_201508.md

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
task: phase3_task01_model_laws
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_phase3_task01_model_laws_EXECUTOR_20251226_201708.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
