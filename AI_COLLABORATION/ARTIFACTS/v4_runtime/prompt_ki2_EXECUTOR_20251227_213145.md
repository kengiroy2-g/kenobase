AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: GK1 Daten Integration
TASK-ID: TASK-C03
PRIORITY: CRITICAL
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 21:19:45] TASK-C03 - PROXY_PLAN (ki0)

### Summary
- Plan mischt Felder aus zwei verschiedenen CSV-Formate in einem Modell
- 10-9_KGDaten_gefiltert.csv hat NUR: Datum, Keno-Typ, Anzahl der Gewinner, Vergangene Tage
- 10-9_Liste_GK1_Treffer.csv hat ZUSAETZLICH: Date_Check, Anzahl Treffer, z1-z6
- GK1Event-Modell-Definition ist inkonsistent mit Quell-Daten
- Empfehlung: Zwei separate Modelle oder JOIN-Logik definieren
- DataLoader-Integration passt zur existierenden Architektur (parser_map Pattern)
- Acceptance Criteria sind messbar aber basieren auf falschem Modell

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-C03_PROXY_PLAN_20251227_211745.md

## [2025-12-27 21:28:45] TASK-C03 - ARCHITECT (ki1)

### Summary
- KORRIGIERT: Zwei separate Modelle statt einem inkonsistenten GK1Event
- GK1Summary-Modell fuer 10-9_KGDaten_gefiltert.csv (21 Zeilen, 4 Spalten)
- GK1Hit-Modell fuer 10-9_Liste_GK1_Treffer.csv (5 Zeilen, 12 Spalten)
- Beide CSVs nutzen Komma-Delimiter, deutsches Datumsformat (DD.MM.YYYY)
- Integration via _parse_gk1_summary() und _parse_gk1_hits() in DataLoader
- 5 Implementierungs-Schritte mit Acceptance Criteria

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK-C03_ARCHITECT_20251227_212445.md

## [2025-12-27 21:31:45] TASK-C03 - PROXY_PLAN (ki0)

### Summary
- Korrigierter Plan adressiert vorheriges Rejection - zwei Modelle statt einem
- GK1Summary fuer 10-9_KGDaten_gefiltert.csv (4 Spalten)
- GK1Hit fuer 10-9_Liste_GK1_Treffer.csv (12 Spalten mit z1-z6)
- Beide CSVs: Komma-Delimiter, deutsches Datumsformat
- Integration via parser_map Pattern - passt zu DataLoader-Architektur
- Konzept korrekt, Handoff-Details unvollstaendig aber rekonstruierbar
- WORKING_SET und Implementierungsanleitung im Handoff ergaenzt

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-C03_PROXY_PLAN_20251227_212845.md



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
- Korrigierter Plan adressiert vorheriges Rejection - zwei Modelle statt einem
- GK1Summary fuer 10-9_KGDaten_gefiltert.csv (4 Spalten)
- GK1Hit fuer 10-9_Liste_GK1_Treffer.csv (12 Spalten mit z1-z6)
- Beide CSVs: Komma-Delimiter, deutsches Datumsformat
- Integration via parser_map Pattern - passt zu DataLoader-Architektur
- Konzept korrekt, Handoff-Details unvollstaendig aber rekonstruierbar
- WORKING_SET und Implementierungsanleitung im Handoff ergaenzt

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-C03_PROXY_PLAN_20251227_212845.md

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
task: TASK-C03
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK-C03_EXECUTOR_20251227_213145.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
