AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Test HYP_013: Overlap-Birthday-Anteil nach Phase
TASK-ID: TASK_023
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 20:04:48] TASK_023 - ARCHITECT (ki1)

### Summary
- Kontext gelesen: SYSTEM_STATUS.json (2025-12-29) und cycles_exhaustive_analysis_plan_v3.yaml; git status aufgenommen.
- Scope geklÃ¤rt: Phase-level Overlap/Birthday-Share (PRE/POST/COOLDOWN/NORMAL) auf KENO-Ziehungen, Erwartung 5.714 Overlap & 31/70 Birthday-Rate.
- Metriken/Tests definiert: Overlap-Count & Birthday-Ratio mit z-Tests gg. Erwartung, Kruskal-Wallis + Mann-Whitney per Phase, Bonferroni-FDR Guardrails.
- Implementierungsplan: Daten/Jackpots laden, Phasen labeln, Overlap+Birthday Features berechnen, Phasen-Stats + Signifikanz ableiten, Artefakte (JSON+MD) + CURRENT_STATUS Update.
- Acceptance-Kriterien fixiert: reproduzierbarer Run, erwartete Datendeckung (>=2022), korrigierte p-Values dokumentiert, Hypothese support/reject flag im Output.

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_023_ARCHITECT_20251230_200048.md

## [2025-12-30 20:05:48] TASK_023 - PROXY_PLAN (ki0)

### Summary (fallback)
- --- status: APPROVED task: TASK_023 role: PROXY phase: PROXY_PLAN --- - Plan deckt End-to-End ab (Definitionen, Datenpfade, Feature-Build, Stats, Artefakte, CURRENT_STATUS/REPRO). - Tests/Signifikanz sauber umrissen (z/z+KW/MW, Bonferroni/FDR, Sample>=50 oder UNVERIFIED). - Repro ...

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_023_PROXY_PLAN_20251230_200448.md



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
---
status: APPROVED
task: TASK_023
role: PROXY
phase: PROXY_PLAN
---
- Plan deckt End-to-End ab (Definitionen, Datenpfade, Feature-Build, Stats, Artefakte, CURRENT_STATUS/REPRO).
- Tests/Signifikanz sauber umrissen (z/z+KW/MW, Bonferroni/FDR, Sample>=50 oder UNVERIFIED).
- Repro-Command klar benannt; Outcome-Flag und korrigierte p-Werte gefordert.
- Daten- und Phasen-Label-Quellen spezifiziert inkl. Fallback (GK1-Spalte).
- Risiken: KI0-Profil fehlend (nicht gefunden); Availability von timeline_2025.csv muss beim Execute verifiziert werden.


FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_023_PROXY_PLAN_20251230_200448.md

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
task: TASK_023
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK_023_EXECUTOR_20251230_200548.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
