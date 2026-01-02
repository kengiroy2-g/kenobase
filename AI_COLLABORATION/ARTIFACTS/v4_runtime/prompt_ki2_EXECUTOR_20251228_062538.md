AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Regionale Zahlen-Affinitaet (Bundesland)
TASK-ID: TASK-R03
PRIORITY: HIGH
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 06:24:38] TASK-R03 - ARCHITECT (ki1)

### Summary
- SYSTEM_STATUS.json nicht auffindbar -> Regel 1 unverified; ADR_PREDICTION_MODEL.md und MODULE_MAP.md gelesen
- Granularitaet per-market (Bundesland); Semantik: per-number regionale Affinitaet vs global baseline; Zielmetrik: bet-selection
- Plan skizziert fuer Datenfeld-Pruefung, Loader-Erweiterung, neue Analyse `regional_affinity`, Pipeline/CLI-Ausgabe und optionale Synthese-Integration
- Akzeptanzkriterien definiert (Artefakte, Tests, Dokumentation, Metrik-Checks)
- CURRENT_STATUS nicht aktualisiert (Plan-only)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK-R03_ARCHITECT_20251228_062237.md

## [2025-12-28 06:25:38] TASK-R03 - PROXY_PLAN (ki0)

### Summary
- SYSTEM_STATUS.json und KI0-Profil fehlen -> Rule 1 nur teilweise verifiziert
- Plan deckt Datenfeld-Pruefung, Loader-Anpassung, neues Analysemodul und Pipeline/CLI-Integration ab
- Per-market Granularitaet mit regionalem Bias vs globaler Baseline klar definiert; Zielmetrik bet-selection
- Tests/Artefakte/Doku als Acceptance-Kriterien benannt; Repro-Kommandos noch offen (Plan-only)
- Optionaler Synthese-Hook erwaehnt, beeinflusst Kernpfad nicht

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-R03_PROXY_PLAN_20251228_062438.md



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
- SYSTEM_STATUS.json und KI0-Profil fehlen -> Rule 1 nur teilweise verifiziert
- Plan deckt Datenfeld-Pruefung, Loader-Anpassung, neues Analysemodul und Pipeline/CLI-Integration ab
- Per-market Granularitaet mit regionalem Bias vs globaler Baseline klar definiert; Zielmetrik bet-selection
- Tests/Artefakte/Doku als Acceptance-Kriterien benannt; Repro-Kommandos noch offen (Plan-only)
- Optionaler Synthese-Hook erwaehnt, beeinflusst Kernpfad nicht

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-R03_PROXY_PLAN_20251228_062438.md

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
task: TASK-R03
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK-R03_EXECUTOR_20251228_062538.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
