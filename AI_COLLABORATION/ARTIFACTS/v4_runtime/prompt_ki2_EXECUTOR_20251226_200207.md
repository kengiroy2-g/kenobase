AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P2-05: Duo/Trio/Quatro BUG-FIX
TASK-ID: phase2_task05_duo_trio_quatro_fix
PRIORITY: P0
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-26 20:00:07] phase2_task05_duo_trio_quatro_fix - ARCHITECT (ki1)

### Summary
- Bug identified in V9:130-135: exclusive elif loses sub-combinations
- 4-match only extracts quatro (loses 4 trios + 6 duos)
- 3-match only extracts trio (loses 3 duos)
- Fix: Use parallel if statements instead of exclusive elif
- Create kenobase/analysis/pattern.py with PatternResult dataclass
- Integrate with existing frequency.py module structure
- Add comprehensive unit tests in tests/unit/test_pattern.py
- Update analysis/__init__.py exports

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_phase2_task05_duo_trio_quatro_fix_ARCHITECT_20251226_195407.md

## [2025-12-26 20:02:07] phase2_task05_duo_trio_quatro_fix - PROXY_PLAN (ki0)

### Summary
- Bug verified in V9:130-135: exclusive elif chain loses sub-combinations
- Math confirmed: 4-match yields C(4,4)+C(4,3)+C(4,2)=1+4+6=11 patterns, V9 only extracts 1
- Fix approach sound: parallel if statements instead of elif
- New pattern.py is distinct from frequency.py (combo-vs-draw overlap vs draw-internal pairs)
- Integration path clear: __init__.py needs PatternResult + extract_patterns exports
- Working set request is appropriate for executor
- No architecture conflicts detected
- Ready for implementation

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase2_task05_duo_trio_quatro_fix_PROXY_PLAN_20251226_200007.md



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
- Bug verified in V9:130-135: exclusive elif chain loses sub-combinations
- Math confirmed: 4-match yields C(4,4)+C(4,3)+C(4,2)=1+4+6=11 patterns, V9 only extracts 1
- Fix approach sound: parallel if statements instead of elif
- New pattern.py is distinct from frequency.py (combo-vs-draw overlap vs draw-internal pairs)
- Integration path clear: __init__.py needs PatternResult + extract_patterns exports
- Working set request is appropriate for executor
- No architecture conflicts detected
- Ready for implementation

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase2_task05_duo_trio_quatro_fix_PROXY_PLAN_20251226_200007.md

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
task: phase2_task05_duo_trio_quatro_fix
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_phase2_task05_duo_trio_quatro_fix_EXECUTOR_20251226_200207.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
