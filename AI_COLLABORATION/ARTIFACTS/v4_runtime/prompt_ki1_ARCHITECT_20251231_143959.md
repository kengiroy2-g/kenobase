AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: High-Win Forensik: Alle >450 EUR Events
TASK-ID: TASK_055
PRIORITY: P2
PHASE: ARCHITECT

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-31 14:37:59] TASK_055 - ARCHITECT (ki1)

### Summary
- Task: High-Win Forensik for events >450 EUR (not >=400 as current script)
- Existing script analyze_high_win_forensik.py uses threshold=400; needs parameter change to >450
- >450 EUR events include Typ6 6-hits(500), Typ7 7-hits(1000), Typ8 8-hits(10k), Typ9 8/9-hits, Typ10 9/10-hits
- Current result has only 14 events from 2018-2024 backtest with threshold=400
- Need separate analysis script or parameterized run with threshold=451
- Output artifact: results/high_win_forensik_gt450.json
- Repro: python scripts/analyze_high_win_forensik.py --threshold 451 --output results/high_win_forensik_gt450.json

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_055_ARCHITECT_20251231_143459.md

## [2025-12-31 14:39:59] TASK_055 - PROXY_PLAN (ki0)

### Summary (fallback)
- ---    **PROXY REVIEW COMPLETE**    ---  status: REJECTED  task: TASK_055  role: PROXY  phase: PROXY_PLAN  reviewed_handoff: "ki1_TASK_055_ARCHITECT_20251231_143459.md"  summary:    - ARCHITECT misidentified where threshold filtering occurs    - analyze_high_win_forensik.py has N ...

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_055_PROXY_PLAN_20251231_143759.md



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
ROLLE: ARCHITECT
AUFGABE: Erstelle detaillierten Implementierungsplan.

EFFIZIENZ-REGELN (wie normal CLI):
- Kein Repo-weiter Scan (kein rekursives Listing, kein breitflÃ¤chiges Grep).
- Arbeite primÃ¤r mit WORKING SET + TASK NOTES; wenn leer: max 2 gezielte Datei-Finder-Queries, dann stoppen und fehlende Pfade anfordern.
- Keine Status-/Messaging-Dateien lesen/schreiben (queue/CURRENT_STATUS) ausser explizit verlangt.
- Keine langen Tool-Outputs im Handoff; grosse Logs nach AI_COLLABORATION/ARTIFACTS/ auslagern und verlinken.

SCHRITTE:
1. Analysiere Anforderungen
2. Identifiziere betroffene Dateien
3. Erstelle Schritt-fuer-Schritt Checkliste
4. Definiere Acceptance Criteria

TOKEN HYGIENE:
- Output muss direkt das Handoff-Markdown sein (keine Diffs, keine Zusatztexte).
- Schreibe Handoff mit YAML Frontmatter (---\nstatus: COMPLETE\n...\n---)
- Max 8 summary bullets
- Keine langen Logs/Diffs im Body (nur Pfade)

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: COMPLETE
task: TASK_055
role: ARCHITECT
phase: ARCHITECT
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

# Implementierungsplan

WICHTIG: Erstelle Handoff-Datei wenn fertig:
- Datei: AI_COLLABORATION/HANDOFFS/ki1_TASK_055_ARCHITECT_20251231_143959.md
- YAML mit status: COMPLETE
- YAML mit files_changed: [...]
