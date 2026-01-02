AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Test HYP_012: Overlap-Menge
TASK-ID: TASK_022
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 19:45:27] TASK_022 - ARCHITECT (ki1)

### Summary
- Context sync: gelesen AI_COLLABORATION/SYSTEM_STATUS.md (Stand 2025-12-29); SYSTEM_STATUS.json fehlt; git status zeigt dirty worktree.
- KI-Rolle geprueft: AI_COLLABORATION/KI_PROFILES/KI_1_LEAD_ARCHITECT.md; KI0 Proxy-Profil weiterhin fehlend (blocker vermerkt).
- HYP_012 Snapshot: results/overlap_statistics.json (N=1457, mean overlap 5.745 vs 5.714 erwartet, n_tests=15, Bonferroni Î±=0.00333, keine signifikanten Ergebnisse) â€“ Repro noch ausstehend.
- Repro-Pfad: scripts/analyze_cycles_comprehensive.py nutzt data/raw/keno/KENO_ab_2022_bereinigt.csv + data/processed/ecosystem/timeline_2025.csv, schreibt results/overlap_statistics.json und Log AI_COLLABORATION/ARTIFACTS/v4_runtime/TASK_022_overlap.log.
- Implementierungsplan definiert (Input-Checks, Repro+Logging, Kennzahlen-Validierung, Doku/Status-Update, Proxy/Profile-Fix).

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_022_ARCHITECT_20251230_194327.md

## [2025-12-30 19:48:37] TASK_022 - PROXY_PLAN (ki0)

### Summary
- Plan covers inputs â†’ status/profile housekeeping â†’ repro â†’ metric validation â†’ docs/logs; sequencing is coherent.
- Metrics framed as calibration vs E[Overlap]=5.714 with Bonferroni guard; per-phase diagnostics keep granularity acceptable (no BUG-001/003 triggers seen).
- SYSTEM_STATUS.json fehlt; plan step to mirror from SYSTEM_STATUS.md is appropriate.
- KI0 proxy profile spec still missing; executor must flag/request source while proceeding.
- Repro/log/output paths are explicit (analyze_cycles_comprehensive.py -> TASK_022_overlap.log, results/overlap_statistics.json; includes cycles_comprehensive_analysis.json regeneration).

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_022_PROXY_PLAN_20251230_194637.md




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
- AI_COLLABORATION/SYSTEM_STATUS.md
- AI_COLLABORATION/KI_PROFILES/KI_1_LEAD_ARCHITECT.md
- scripts/analyze_cycles_comprehensive.py
- data/raw/keno/KENO_ab_2022_bereinigt.csv
- data/processed/ecosystem/timeline_2025.csv
- results/overlap_statistics.json

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
- Plan covers inputs â†’ status/profile housekeeping â†’ repro â†’ metric validation â†’ docs/logs; sequencing is coherent.
- Metrics framed as calibration vs E[Overlap]=5.714 with Bonferroni guard; per-phase diagnostics keep granularity acceptable (no BUG-001/003 triggers seen).
- SYSTEM_STATUS.json fehlt; plan step to mirror from SYSTEM_STATUS.md is appropriate.
- KI0 proxy profile spec still missing; executor must flag/request source while proceeding.
- Repro/log/output paths are explicit (analyze_cycles_comprehensive.py -> TASK_022_overlap.log, results/overlap_statistics.json; includes cycles_comprehensive_analysis.json regeneration).

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_022_PROXY_PLAN_20251230_194637.md

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
task: TASK_022
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK_022_EXECUTOR_20251230_194837.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
