AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Cross-Type High-Win Vergleich
TASK-ID: TASK_054
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-31 14:22:58] TASK_054 - ARCHITECT (ki1)

### Summary
- Analyzed existing high-win forensik data (Typ6=11, Typ7=3, Typ8=0, Typ9=0, Typ10=0)
- Typ-9/10 absence is statistically expected (P(0 events)>95% for both)
- Cross-type comparison script needed to unify analyses into single report
- Key metrics: birthday_ratio, weekday_distribution, strategy, payout efficiency
- Plan: new script `scripts/analyze_cross_type_highwin.py` with unified output
- Implementation reuses existing forensik JSON as data source
- Output: `results/cross_type_highwin_comparison.json`

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_054_ARCHITECT_20251231_142058.md

## [2025-12-31 14:24:58] TASK_054 - PROXY_PLAN (ki0)

### Summary
- Plan is mechanically complete with clear A->B->C->D phases
- Granularity correctly per-keno-type (Typ-6..10)
- Reuses existing forensik JSON files as data source - no re-computation
- Typ-9/10 null-results correctly handled (statistically expected absence)
- Working set contains all required source files
- Output path results/cross_type_highwin_comparison.json is consistent with project structure
- No global threshold issue (BUG-001) - descriptive comparison only
- Template script analyze_typ7_highwin.py provides clean pattern to follow

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_054_PROXY_PLAN_20251231_142258.md



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
- scripts/analyze_typ7_highwin.py
- results/high_win_forensik.json
- results/typ9_highwin_forensik.json
- results/typ10_highwin_forensik.json

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
- Plan is mechanically complete with clear A->B->C->D phases
- Granularity correctly per-keno-type (Typ-6..10)
- Reuses existing forensik JSON files as data source - no re-computation
- Typ-9/10 null-results correctly handled (statistically expected absence)
- Working set contains all required source files
- Output path results/cross_type_highwin_comparison.json is consistent with project structure
- No global threshold issue (BUG-001) - descriptive comparison only
- Template script analyze_typ7_highwin.py provides clean pattern to follow

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_054_PROXY_PLAN_20251231_142258.md

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
task: TASK_054
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK_054_EXECUTOR_20251231_142458.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
