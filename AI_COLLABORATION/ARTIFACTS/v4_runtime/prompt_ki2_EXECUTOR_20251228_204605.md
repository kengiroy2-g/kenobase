AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Rolling House-Edge Stabilitaet
TASK-ID: HOUSE-003
PRIORITY: P1
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 20:45:05] HOUSE-003 - ARCHITECT (ki1)

### Summary
- HOUSE-003 tests Rolling House-Edge Stability via CV over 7/14/30 day windows
- Reuses StakeDrawRecord from stake_correlation.py (restbetrag, auszahlung fields)
- New module: kenobase/analysis/house_edge_stability.py
- New script: scripts/analyze_house003.py
- Acceptance: CV < 15% on at least 2 of 3 windows indicates active payout control
- Data source: Keno_GPTs/Keno_Ziehung2023_+_Restbetrag_v2.CSV (769 records)
- Output: results/house003_rolling_stability.json

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_HOUSE-003_ARCHITECT_20251228_204205.md

## [2025-12-28 20:46:05] HOUSE-003 - PROXY_PLAN (ki0)

### Summary
- Plan is mechanically complete with clear file structure and acceptance criteria
- StakeDrawRecord reuse is valid - contains restbetrag and total_auszahlung fields (stake_correlation.py:111-132)
- CV calculation (std/mean) is mathematically correct for stability measurement
- Rolling windows 7/14/30 days are reasonable for detecting operational patterns
- Threshold CV < 15% is falsifiable and measurable
- Data source (769 records) provides sufficient data for 30-day windows (~25 windows)
- No global-vs-specific threshold conflict (BUG-001 not applicable - this is global Keno analysis)
- WORKING_SET_REQUEST is appropriate for executor needs

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HOUSE-003_PROXY_PLAN_20251228_204505.md



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
- Plan is mechanically complete with clear file structure and acceptance criteria
- StakeDrawRecord reuse is valid - contains restbetrag and total_auszahlung fields (stake_correlation.py:111-132)
- CV calculation (std/mean) is mathematically correct for stability measurement
- Rolling windows 7/14/30 days are reasonable for detecting operational patterns
- Threshold CV < 15% is falsifiable and measurable
- Data source (769 records) provides sufficient data for 30-day windows (~25 windows)
- No global-vs-specific threshold conflict (BUG-001 not applicable - this is global Keno analysis)
- WORKING_SET_REQUEST is appropriate for executor needs

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HOUSE-003_PROXY_PLAN_20251228_204505.md

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
task: HOUSE-003
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_HOUSE-003_EXECUTOR_20251228_204605.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
