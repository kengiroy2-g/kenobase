AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P6-04: Final Testing & Smoke Tests
TASK-ID: phase6_task04_final_testing
PRIORITY: P1
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 00:48:30] phase6_task04_final_testing - ARCHITECT (ki1)

### Summary
- All 356 unit tests pass (pytest tests/ -v)
- Test coverage at 93% (1441 statements, 96 missed)
- CLI smoke tests pass (analyze --help, info, validate)
- Physics Layer smoke tests pass (stability, criticality, avalanche, hurst)
- Combination Engine smoke tests pass (generation, decade filter)
- Number Pool smoke tests pass (pool generation from draws)
- Frequency Analysis smoke tests pass
- End-to-end integration test passes (full pipeline execution)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_phase6_task04_final_testing_ARCHITECT_20251227_003729.md

## [2025-12-27 00:50:30] phase6_task04_final_testing - PROXY_PLAN (ki0)

### Summary
- 356 unit tests ALL PASS - verified from ARCHITECT handoff
- Test coverage 93% (exceeds 80% target per CLAUDE.md)
- CLI smoke tests verified (--help, info, validate)
- Physics Layer smoke tests passed (stability, criticality, avalanche, hurst)
- Combination Engine and Number Pool smoke tests passed
- backtest.py reviewed - module imports are correct, sys.path fix is optional
- Integration test directory exists but empty - EXECUTOR should populate
- No formal smoke_test.py script exists - EXECUTOR should create

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase6_task04_final_testing_PROXY_PLAN_20251227_004830.md



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
- 356 unit tests ALL PASS - verified from ARCHITECT handoff
- Test coverage 93% (exceeds 80% target per CLAUDE.md)
- CLI smoke tests verified (--help, info, validate)
- Physics Layer smoke tests passed (stability, criticality, avalanche, hurst)
- Combination Engine and Number Pool smoke tests passed
- backtest.py reviewed - module imports are correct, sys.path fix is optional
- Integration test directory exists but empty - EXECUTOR should populate
- No formal smoke_test.py script exists - EXECUTOR should create

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase6_task04_final_testing_PROXY_PLAN_20251227_004830.md

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
task: phase6_task04_final_testing
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_phase6_task04_final_testing_EXECUTOR_20251227_005030.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
