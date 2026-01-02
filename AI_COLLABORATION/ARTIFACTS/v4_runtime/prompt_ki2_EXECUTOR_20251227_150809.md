AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Pattern-Analyse und Kombinatorik
TASK-ID: HYP-006
PRIORITY: MEDIUM
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 15:06:09] HYP-006 - ARCHITECT (ki1)

### Summary
- HYP-006: Analyse wiederkehrender Gewinnzahlen (WGZ) und Pattern-Stabilitaet
- Kernfrage: Wiederholen sich Zahlen in identifizierbaren Mustern?
- Drei Analyse-Dimensionen: Wiederholungsrate, GK1-Korrelation, Paar-Stabilitaet
- Nutzt bestehendes pattern.py als Basis, erfordert neues recurrence.py Modul
- Datenbedarf: 10-9_CheckNumbers_z120.csv, 10-9_Liste_GK1_Treffer.csv
- Deliverable: Wiederholungs-Report mit metrischen Acceptance Criteria
- Geschaetzter Aufwand: 4-5 Stunden

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_HYP-006_ARCHITECT_20251227_150309.md

## [2025-12-27 15:08:09] HYP-006 - PROXY_PLAN (ki0)

### Summary
- Plan ist vollstaendig mit klaren Acceptance Criteria
- Datendateien verifiziert: 10-9_CheckNumbers_z120.csv, 10-9_Liste_GK1_Treffer.csv vorhanden
- pattern.py existiert und hat saubere Architektur (209 Zeilen, gut dokumentiert)
- Granularitaet per-draw ist korrekt fuer WGZ-Analyse
- Neues recurrence.py Modul folgt bestehender pattern.py Struktur
- Working Set Request ist komplett (6 Dateien)
- Repro-Command klar definiert
- Keine BUG-001/003 Risiken erkannt (keine globalen Thresholds, kein Orchestrator benoetigt)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-006_PROXY_PLAN_20251227_150609.md



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
- AI_COLLABORATION/HANDOFFS/ki1_HYP-006_ARCHITECT_20251227_150309.md

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
- Plan ist vollstaendig mit klaren Acceptance Criteria
- Datendateien verifiziert: 10-9_CheckNumbers_z120.csv, 10-9_Liste_GK1_Treffer.csv vorhanden
- pattern.py existiert und hat saubere Architektur (209 Zeilen, gut dokumentiert)
- Granularitaet per-draw ist korrekt fuer WGZ-Analyse
- Neues recurrence.py Modul folgt bestehender pattern.py Struktur
- Working Set Request ist komplett (6 Dateien)
- Repro-Command klar definiert
- Keine BUG-001/003 Risiken erkannt (keine globalen Thresholds, kein Orchestrator benoetigt)

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-006_PROXY_PLAN_20251227_150609.md

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
task: HYP-006
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_HYP-006_EXECUTOR_20251227_150809.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
