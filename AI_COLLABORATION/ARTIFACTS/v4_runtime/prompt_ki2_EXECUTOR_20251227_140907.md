AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Kern-Hypothesen Validierung
TASK-ID: HYP-002
PRIORITY: HIGH
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 14:07:07] HYP-002 - ARCHITECT (ki1)

### Summary
- HYP-002 fokussiert auf Jackpot-Bildungs-Zyklen (Zeitintervalle zwischen GK1-Events)
- Existierendes Script validate_hypotheses.py implementiert bereits KS-Test + Runs-Test
- Datenbedarf: 10-9_KGDaten_gefiltert.csv (GK1-Events mit Vergangene Tage Spalte)
- Erweiterte Analyse fehlt: Kalender-Korrelation (Feiertage, Gehaltstermine)
- Erweiterte Analyse fehlt: Vorhersage-Modell fuer naechsten GK1
- EXECUTOR soll Kalender-Korrelation und Vorhersage-Report hinzufuegen
- Output: data/results/hyp002_jackpot_cycles.json mit erweiterten Statistiken

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_HYP-002_ARCHITECT_20251227_140407.md

## [2025-12-27 14:09:07] HYP-002 - PROXY_PLAN (ki0)

### Summary
- Plan ist vollstaendig und klar strukturiert mit 4 Haupt-Schritten
- Existierende Implementierung verifiziert (validate_hypotheses.py:294-389)
- Datei 10-9_KGDaten_gefiltert.csv existiert im Repo
- Acceptance Criteria sind messbar (Chi-Quadrat Tests, JSON-Output)
- Keine globalen Thresholds wo game-spezifische noetig (BUG-001 vermieden)
- Neues Modul calendar_features.py ist isoliert (keine versteckte Kopplung)
- WORKING_SET_REQUEST ist korrekt und vollstaendig
- holidays Package korrekt als optional markiert (Fallback vorhanden)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-002_PROXY_PLAN_20251227_140707.md



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
- Plan ist vollstaendig und klar strukturiert mit 4 Haupt-Schritten
- Existierende Implementierung verifiziert (validate_hypotheses.py:294-389)
- Datei 10-9_KGDaten_gefiltert.csv existiert im Repo
- Acceptance Criteria sind messbar (Chi-Quadrat Tests, JSON-Output)
- Keine globalen Thresholds wo game-spezifische noetig (BUG-001 vermieden)
- Neues Modul calendar_features.py ist isoliert (keine versteckte Kopplung)
- WORKING_SET_REQUEST ist korrekt und vollstaendig
- holidays Package korrekt als optional markiert (Fallback vorhanden)

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-002_PROXY_PLAN_20251227_140707.md

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
task: HYP-002
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_HYP-002_EXECUTOR_20251227_140907.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
