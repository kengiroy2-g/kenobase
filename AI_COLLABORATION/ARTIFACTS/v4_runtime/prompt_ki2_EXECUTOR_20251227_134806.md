AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Basis-Zahlenpool und Index-System ermitteln
TASK-ID: HYP-005
PRIORITY: HIGH
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 13:45:06] HYP-005 - ARCHITECT (ki1)

### Summary
- HYP-005 analysiert: Basis-Zahlenpool mit Index-System ermitteln
- Datenquellen identifiziert: KENO_ab_2018.csv (N=2500+), 10-9_KGDaten_gefiltert.csv (N=20 GK1-Events)
- Drei Analyse-Schritte definiert: Index-Berechnung, Korrelation, Reset-Effekt
- Neues Modul kenobase/analysis/number_index.py geplant
- Output: Index-Tabelle fuer 70 Zahlen + Korrelations-Report
- Integration in bestehende frequency.py Architektur

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_HYP-005_ARCHITECT_20251227_134206.md

## [2025-12-27 13:48:06] HYP-005 - PROXY_PLAN (ki0)

### Summary
- Plan ist konzeptionell solide: Index = Haeufigkeit seit letztem GK1-Event
- Datenquellen verifiziert: KENO_ab_2018.csv (N=2237 Zeilen), 10-9_KGDaten_gefiltert.csv (N=20 GK1-Events)
- Integration in frequency.py-Architektur passt (bestehende FrequencyResult-Muster nutzbar)
- Neues Modul number_index.py korrekt isoliert (keine Cross-File-Probleme)
- GK1-Events sind heterogen (Keno-Typ 9 und 10 gemischt) - kein Blocker, aber bei Reset-Logik beachten
- validate_hypotheses.py existiert bereits als Stub - Integration moeglich
- Output-Pfad data/results/hyp005_index_table.json muss noch erstellt werden
- Keine globalen Thresholds wo spezifische noetig - CLEAN

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-005_PROXY_PLAN_20251227_134506.md



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
- Plan ist konzeptionell solide: Index = Haeufigkeit seit letztem GK1-Event
- Datenquellen verifiziert: KENO_ab_2018.csv (N=2237 Zeilen), 10-9_KGDaten_gefiltert.csv (N=20 GK1-Events)
- Integration in frequency.py-Architektur passt (bestehende FrequencyResult-Muster nutzbar)
- Neues Modul number_index.py korrekt isoliert (keine Cross-File-Probleme)
- GK1-Events sind heterogen (Keno-Typ 9 und 10 gemischt) - kein Blocker, aber bei Reset-Logik beachten
- validate_hypotheses.py existiert bereits als Stub - Integration moeglich
- Output-Pfad data/results/hyp005_index_table.json muss noch erstellt werden
- Keine globalen Thresholds wo spezifische noetig - CLEAN

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-005_PROXY_PLAN_20251227_134506.md

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
task: HYP-005
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_HYP-005_EXECUTOR_20251227_134806.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
