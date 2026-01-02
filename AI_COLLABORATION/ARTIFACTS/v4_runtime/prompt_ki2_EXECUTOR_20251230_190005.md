AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Test HYP_010: High-Win-Clustering
TASK-ID: TASK_020
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 18:58:04] TASK_020 - ARCHITECT (ki1)

### Summary
- HYP_CYC_006 (High-Win-Clustering) bereits in cycles_comprehensive_analysis.json vorhanden
- Daten zeigen extrem niedrige High-Win-Raten (nur 1-3 Events in >1400 Ziehungen)
- PRE_JACKPOT zeigt V2=1 HW vs NORMAL=0 (fuer alle Typen), aber N zu klein
- Chi-Quadrat-Test nicht anwendbar (expected cells <5)
- Fisher-Exact-Test als Alternative empfohlen
- Keine neuen Dateien erforderlich - nur Dokumentation der Ergebnisse
- Status: NICHT SIGNIFIKANT wegen Sample-Size-Limitation

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_020_ARCHITECT_20251230_185504.md

## [2025-12-30 19:00:05] TASK_020 - PROXY_PLAN (ki0)

### Summary
- HYP_CYC_006 data verified in results/cycles_comprehensive_analysis.json (lines 260-355)
- Sample sizes confirmed: PRE_JACKPOT=116, POST_JACKPOT=87, COOLDOWN=121, NORMAL=1133
- High-Win counts extremely sparse: V2=1 (PRE_JACKPOT only), ORIG=2 (NORMAL typ_10 only)
- Chi-quadrat test correctly identified as not applicable (expected cells < 5)
- Fisher-Exact test recommendation is appropriate for sparse 2x2 contingency tables
- No code changes required - documentation-only task
- Status correctly assessed as NICHT SIGNIFIKANT due to Sample-Size limitation
- Repro command verified: `python scripts/analyze_cycles_comprehensive.py`

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_020_PROXY_PLAN_20251230_185805.md



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
- HYP_CYC_006 data verified in results/cycles_comprehensive_analysis.json (lines 260-355)
- Sample sizes confirmed: PRE_JACKPOT=116, POST_JACKPOT=87, COOLDOWN=121, NORMAL=1133
- High-Win counts extremely sparse: V2=1 (PRE_JACKPOT only), ORIG=2 (NORMAL typ_10 only)
- Chi-quadrat test correctly identified as not applicable (expected cells < 5)
- Fisher-Exact test recommendation is appropriate for sparse 2x2 contingency tables
- No code changes required - documentation-only task
- Status correctly assessed as NICHT SIGNIFIKANT due to Sample-Size limitation
- Repro command verified: `python scripts/analyze_cycles_comprehensive.py`

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_020_PROXY_PLAN_20251230_185805.md

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
task: TASK_020
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK_020_EXECUTOR_20251230_190005.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
