AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Schnelle Hypothesen-Validierungen
TASK-ID: TASK-F03
PRIORITY: HIGH
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 13:19:04] TASK-F03 - ARCHITECT (ki1)

### Summary
- Plan fuer 3 schnelle Hypothesen-Validierungen erstellt
- HYP-009 (Chi-Quadrat) als erstes, schnellstes Target
- HYP-005 (Zahlenpool-Index) als Basis fuer weitere Analysen
- HYP-002 (Jackpot-Zyklen) als drittes Target
- frequency.py bereits vorhanden, Chi-Quadrat-Erweiterung noetig
- Alle Analysen nutzbar mit existierenden Daten
- Neues Script scripts/validate_hypotheses.py vorgeschlagen
- Klare Acceptance Criteria pro Hypothese definiert

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK-F03_ARCHITECT_20251227_131504.md

## [2025-12-27 13:21:04] TASK-F03 - PROXY_PLAN (ki0)

### Summary
- Plan konzeptionell geprueft - 3 Hypothesen sinnvoll priorisiert
- HYP-009 (Chi-Quadrat) schnellste Validierung - frequency.py vorhanden aber Chi-Quadrat fehlt
- HYP-005 (Zahlenpool-Index) erfordert neue Logik - Index seit GK1-Reset nicht implementiert
- HYP-002 (Jackpot-Zyklen) erfordert Zeitintervall-Analyse zwischen GK1-Events
- scripts/validate_hypotheses.py als zentrales Script sinnvoll
- Acceptance Criteria klar: p-Wert < 0.05, Korrelation r > 0.3
- scipy.stats.chisquare fuer Chi-Quadrat-Test empfohlen
- Keine architekturellen Red Flags erkannt

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-F03_PROXY_PLAN_20251227_131904.md



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
- kenobase/analysis/frequency.py
- Keno_GPTs/10-9_KGDaten_gefiltert.csv
- data/raw/keno/KENO_ab_2018.csv
- requirements.txt

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
- Plan konzeptionell geprueft - 3 Hypothesen sinnvoll priorisiert
- HYP-009 (Chi-Quadrat) schnellste Validierung - frequency.py vorhanden aber Chi-Quadrat fehlt
- HYP-005 (Zahlenpool-Index) erfordert neue Logik - Index seit GK1-Reset nicht implementiert
- HYP-002 (Jackpot-Zyklen) erfordert Zeitintervall-Analyse zwischen GK1-Events
- scripts/validate_hypotheses.py als zentrales Script sinnvoll
- Acceptance Criteria klar: p-Wert < 0.05, Korrelation r > 0.3
- scipy.stats.chisquare fuer Chi-Quadrat-Test empfohlen
- Keine architekturellen Red Flags erkannt

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-F03_PROXY_PLAN_20251227_131904.md

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
task: TASK-F03
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK-F03_EXECUTOR_20251227_132105.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
