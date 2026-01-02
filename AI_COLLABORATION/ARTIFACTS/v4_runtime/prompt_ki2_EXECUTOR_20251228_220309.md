AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Auszahlung-Gewinner Ratio Analyse
TASK-ID: DIST-002
PRIORITY: P1
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 22:01:08] DIST-002 - ARCHITECT (ki1)

### Summary
- Auszahlung-Gewinner Ratio Analyse erweitert HYP-001 Distribution
- Datenquelle: Keno_GPTs/KENO_Quote_details_2023.csv (mit Auszahlung-Spalte)
- Neue Metrik: payout_per_winner = Auszahlung / Anzahl der Gewinner
- Erkennt Anomalien bei ungewoehnlichem Auszahlungs-Verhaeltnis
- Erweiterung des bestehenden distribution.py Moduls
- Acceptance Criteria: 6 Testfaelle definiert

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_DIST-002_ARCHITECT_20251228_215808.md

## [2025-12-28 22:03:08] DIST-002 - PROXY_PLAN (ki0)

### Summary
- Plan konzeptionell korrekt: payout_per_winner = Auszahlung / Anzahl der Gewinner
- Datenquelle verifiziert: KENO_Quote_details_2023.csv hat native Auszahlung-Spalte
- Granularitaet per-gewinnklasse (Keno-Typ x Richtige) ist korrekt
- CSV-Spalte heisst "Gewinn/1Eur" nicht "1 Euro Gewinn" - beachten
- Erweiterung distribution.py statt neues Modul - architektonisch sauber
- Working Set vollstaendig: 5 Dateien korrekt identifiziert
- Tests (test_distribution.py) muessen erweitert werden fuer neue Metrik
- Division by zero bei Gewinner=0 behandeln

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DIST-002_PROXY_PLAN_20251228_220108.md



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
- kenobase/analysis/distribution.py
- scripts/analyze_distribution.py
- tests/unit/test_distribution.py
- Keno_GPTs/KENO_Quote_details_2023.csv
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
- Plan konzeptionell korrekt: payout_per_winner = Auszahlung / Anzahl der Gewinner
- Datenquelle verifiziert: KENO_Quote_details_2023.csv hat native Auszahlung-Spalte
- Granularitaet per-gewinnklasse (Keno-Typ x Richtige) ist korrekt
- CSV-Spalte heisst "Gewinn/1Eur" nicht "1 Euro Gewinn" - beachten
- Erweiterung distribution.py statt neues Modul - architektonisch sauber
- Working Set vollstaendig: 5 Dateien korrekt identifiziert
- Tests (test_distribution.py) muessen erweitert werden fuer neue Metrik
- Division by zero bei Gewinner=0 behandeln

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DIST-002_PROXY_PLAN_20251228_220108.md

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
task: DIST-002
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_DIST-002_EXECUTOR_20251228_220309.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
