AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Konzept-Synthese erstellen
TASK-ID: TASK-F01
PRIORITY: CRITICAL
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 12:47:03] TASK-F01 - ARCHITECT (ki1)

### Summary
- V2.0 Modernisierung: 27 Tasks COMPLETE, kenobase/ Struktur verifiziert
- Backlog: 20 Issues (2 DONE, 18 OFFEN), Hypothesen-Katalog existiert
- Physics Layer: Model Laws + Avalanche implementiert, Validation OFFEN
- Naechste Prioritaet: HYP-009 (Chi-Quadrat) -> HYP-005 (Zahlenpool)
- Daten: 3 Spiele migriert, Scraping-Integration TODO
- Handoff erstellt: ki1_TASK-F01_ARCHITECT_20251227_124503.md

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK-F01_ARCHITECT_20251227_124503.md

## [2025-12-27 12:49:03] TASK-F01 - PROXY_PLAN (ki0)

### Summary
- V2.0 Modernisierung COMPLETE: kenobase/ mit 18 .py Dateien in core/, analysis/, physics/, pipeline/
- Backlog: 20 Issues (2 DONE, 18 OFFEN) - strukturiert nach HOCH/MITTEL/NIEDRIG
- Physics Layer vollstaendig implementiert: model_laws.py, avalanche.py, metrics.py
- Thresholds: per-game bereits umgesetzt (ISSUE-002 DONE)
- Naechste Prioritaet korrekt: HYP-009 (Chi-Quadrat) -> HYP-005 (Zahlenpool)
- Datenquellen dokumentiert in DATA_SOURCES.md, Master-Script vorhanden
- Keine RED FLAGS: Keine globalen Werte wo spielspezifische noetig
- Plan ist konsistent mit CLAUDE.md Architektur

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-F01_PROXY_PLAN_20251227_124703.md



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
- V2.0 Modernisierung COMPLETE: kenobase/ mit 18 .py Dateien in core/, analysis/, physics/, pipeline/
- Backlog: 20 Issues (2 DONE, 18 OFFEN) - strukturiert nach HOCH/MITTEL/NIEDRIG
- Physics Layer vollstaendig implementiert: model_laws.py, avalanche.py, metrics.py
- Thresholds: per-game bereits umgesetzt (ISSUE-002 DONE)
- Naechste Prioritaet korrekt: HYP-009 (Chi-Quadrat) -> HYP-005 (Zahlenpool)
- Datenquellen dokumentiert in DATA_SOURCES.md, Master-Script vorhanden
- Keine RED FLAGS: Keine globalen Werte wo spielspezifische noetig
- Plan ist konsistent mit CLAUDE.md Architektur

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-F01_PROXY_PLAN_20251227_124703.md

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
task: TASK-F01
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK-F01_EXECUTOR_20251227_124903.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
