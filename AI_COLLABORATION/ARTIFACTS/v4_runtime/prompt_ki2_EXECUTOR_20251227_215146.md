AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Wiederholungs-Zyklus Analyse (7-Tage)
TASK-ID: TASK-H01
PRIORITY: HIGH
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 21:49:46] TASK-H01 - ARCHITECT (ki1)

### Summary
- Analysiert: 7-Tage Wiederholungs-Zyklus erweitert bestehendes recurrence.py
- Bestehend: analyze_recurrence() unterstuetzt window=1 (Tag-zu-Tag)
- Erweiterung: Neuer Parameter window=7 fuer Wochen-Zyklen
- Neue Funktion: analyze_weekly_cycle() fuer Wochentagsverteilung
- Tests: Erweiterung test_recurrence.py mit 7-Tage Szenarien
- Keine neuen Dateien noetig - Erweiterung bestehender Module
- HYP-006 Acceptance Criteria bleiben gueltig

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK-H01_ARCHITECT_20251227_214746.md

## [2025-12-27 21:51:46] TASK-H01 - PROXY_PLAN (ki0)

### Summary
- Plan ist vollstaendig und korrekt strukturiert
- Bestehender Code verifiziert: analyze_recurrence() hat bereits window-Parameter (Zeile 107-109)
- recurrence.py hat 523 Zeilen, 5 Haupt-Funktionen - wie dokumentiert
- Neue Funktionen analyze_weekly_cycle() und analyze_recurrence_days() sind klar spezifiziert
- Tests vorhanden: test_recurrence.py mit 27+ Tests in 5 Testklassen
- Keine globalen Thresholds - per-draw Granularitaet korrekt
- Working Set ist minimal und passend (4 Dateien)
- Acceptance Criteria sind messbar und verifizierbar

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-H01_PROXY_PLAN_20251227_214946.md



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
- kenobase/analysis/recurrence.py
- tests/unit/test_recurrence.py
- kenobase/core/data_loader.py
- config/default.yaml

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
- Plan ist vollstaendig und korrekt strukturiert
- Bestehender Code verifiziert: analyze_recurrence() hat bereits window-Parameter (Zeile 107-109)
- recurrence.py hat 523 Zeilen, 5 Haupt-Funktionen - wie dokumentiert
- Neue Funktionen analyze_weekly_cycle() und analyze_recurrence_days() sind klar spezifiziert
- Tests vorhanden: test_recurrence.py mit 27+ Tests in 5 Testklassen
- Keine globalen Thresholds - per-draw Granularitaet korrekt
- Working Set ist minimal und passend (4 Dateien)
- Acceptance Criteria sind messbar und verifizierbar

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-H01_PROXY_PLAN_20251227_214946.md

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
task: TASK-H01
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK-H01_EXECUTOR_20251227_215146.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
