AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Zeitliche Zyklen in Ziehungen identifizieren
TASK-ID: HYP-011
PRIORITY: MEDIUM
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 16:15:12] HYP-011 - ARCHITECT (ki1)

### Summary
- HYP-011 analysiert zeitliche Zyklen (Wochentag, Monat, Jahr, Feiertage) in KENO-Ziehungen
- Existierende calendar_features.py bereits vorhanden mit Grundfunktionen
- Neues Modul temporal_cycles.py erstellen fuer erweiterte Zyklenanalyse
- Analyse-Script scripts/analyze_hyp011.py implementieren
- Chi-Quadrat-Tests fuer Gleichverteilung pro Zeitdimension
- Datenbasis KENO_ab_2018.csv mit Datum vorhanden
- Erwarteter Aufwand 3-4h

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_HYP-011_ARCHITECT_20251227_161212.md

## [2025-12-27 16:17:13] HYP-011 - PROXY_PLAN (ki0)

### Summary
- Existing calendar_features.py provides Chi-square tests for weekday/month - reusable
- New temporal_cycles.py architecturally sound (separate KENO analysis from GK1 calendar)
- KENO_ab_2018.csv verified: Datum column present, ~7 years daily data
- Chi-Quadrat methodology correct for uniform distribution test
- No new thresholds (standard p=0.05 significance)
- WORKING_SET_REQUEST complete
- No modifications to existing calendar_features.py needed
- Estimated 3-4h reasonable

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-011_PROXY_PLAN_20251227_161512.md



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
- Existing calendar_features.py provides Chi-square tests for weekday/month - reusable
- New temporal_cycles.py architecturally sound (separate KENO analysis from GK1 calendar)
- KENO_ab_2018.csv verified: Datum column present, ~7 years daily data
- Chi-Quadrat methodology correct for uniform distribution test
- No new thresholds (standard p=0.05 significance)
- WORKING_SET_REQUEST complete
- No modifications to existing calendar_features.py needed
- Estimated 3-4h reasonable

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-011_PROXY_PLAN_20251227_161512.md

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
task: HYP-011
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_HYP-011_EXECUTOR_20251227_161713.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
