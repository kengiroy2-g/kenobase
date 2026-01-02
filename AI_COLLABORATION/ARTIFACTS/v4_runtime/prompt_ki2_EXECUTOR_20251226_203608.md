AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P3-02: Avalanche-Theorie implementieren
TASK-ID: phase3_task02_avalanche
PRIORITY: P1
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-26 20:34:08] phase3_task02_avalanche - ARCHITECT (ki1)

### Summary
- Avalanche module already fully implemented at kenobase/physics/avalanche.py (229 lines)
- All 8 functions present: calculate_theta, get_avalanche_state, is_profitable, calculate_expected_value, analyze_combination, max_picks_for_theta, get_avalanche_state_with_thresholds
- AvalancheState enum (SAFE/MODERATE/WARNING/CRITICAL) and AvalancheResult NamedTuple defined
- Tests exist at tests/unit/test_avalanche.py with 28 tests (all passing)
- Test coverage at 90% (62 statements, 6 missing - edge cases in threshold func and max_picks)
- Module exported via kenobase/physics/__init__.py
- Config integration present in config/default.yaml (enable_avalanche, anti_avalanche_mode)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_phase3_task02_avalanche_ARCHITECT_20251226_203108.md

## [2025-12-26 20:36:08] phase3_task02_avalanche - PROXY_PLAN (ki0)

### Summary
- ARCHITECT correctly identified task as ALREADY COMPLETE - no work needed
- avalanche.py (229 lines) implements all 8 required functions per CLAUDE.md Section 6.4
- All 28 tests pass (verified via pytest - 0.09s execution)
- AvalancheState enum correctly defines SAFE/MODERATE/WARNING/CRITICAL thresholds
- theta = 1 - p^n formula correctly implemented with edge case handling
- Module properly exported via kenobase/physics/__init__.py (all 11 exports present)
- Config integration confirmed in default.yaml lines 42-44 (enable_avalanche, anti_avalanche_mode)
- Recommendation: SKIP to next task (P3-03 or P3-04)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase3_task02_avalanche_PROXY_PLAN_20251226_203408.md



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
- ARCHITECT correctly identified task as ALREADY COMPLETE - no work needed
- avalanche.py (229 lines) implements all 8 required functions per CLAUDE.md Section 6.4
- All 28 tests pass (verified via pytest - 0.09s execution)
- AvalancheState enum correctly defines SAFE/MODERATE/WARNING/CRITICAL thresholds
- theta = 1 - p^n formula correctly implemented with edge case handling
- Module properly exported via kenobase/physics/__init__.py (all 11 exports present)
- Config integration confirmed in default.yaml lines 42-44 (enable_avalanche, anti_avalanche_mode)
- Recommendation: SKIP to next task (P3-03 or P3-04)

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase3_task02_avalanche_PROXY_PLAN_20251226_203408.md

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
task: phase3_task02_avalanche
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_phase3_task02_avalanche_EXECUTOR_20251226_203608.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
