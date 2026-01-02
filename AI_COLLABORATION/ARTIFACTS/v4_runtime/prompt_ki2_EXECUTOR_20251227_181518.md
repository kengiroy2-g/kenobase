AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Ergebnis-Synthese und Vorhersage-Modell
TASK-ID: ISSUE-006
PRIORITY: HIGH
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 18:13:18] ISSUE-006 - ARCHITECT (ki1)

### Summary
- Analyse von 6 existierenden Hypothesen-Ergebnissen (HYP-006/007/010/011/012)
- Vorhersage-Modell erfordert Synthese aller Hypothesen-Scores
- Neues Modul: kenobase/prediction/synthesizer.py
- Neues Script: scripts/predict.py (CLI fuer Vorhersagen)
- Akzeptanzkriterien: Combined Score, Number Rankings, Backtest-Validation
- Geschaetzter Aufwand: 4-6 Stunden
- Abhaengigkeiten: Alle HYP-Analyse-Scripts muessen gelaufen sein

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_ISSUE-006_ARCHITECT_20251227_180918.md

## [2025-12-27 18:15:18] ISSUE-006 - PROXY_PLAN (ki0)

### Summary
- Plan ist architektonisch sauber: kenobase/prediction/ als neues Modul
- Verfuegbare HYP-Ergebnisse: HYP-007, HYP-010, HYP-011, HYP-012 (4 Dateien)
- Fehlend: HYP-001, HYP-004, HYP-006 Ergebnisse (Scripts existieren, aber keine JSON)
- Synthese-Ansatz valide: combined_score aus heterogenen Hypothesen
- Granularitaet per-number ist korrekt fuer KENO (70 Zahlen)
- Keine globalen Thresholds noetig - Scores normalisiert 0-1
- Integration klar: synthesizer.py liest results/*.json, predict.py nutzt Synthesizer
- Aufwand realistisch: 4-6h bei 4 verfuegbaren Hypothesen

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_ISSUE-006_PROXY_PLAN_20251227_181318.md



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
- Plan ist architektonisch sauber: kenobase/prediction/ als neues Modul
- Verfuegbare HYP-Ergebnisse: HYP-007, HYP-010, HYP-011, HYP-012 (4 Dateien)
- Fehlend: HYP-001, HYP-004, HYP-006 Ergebnisse (Scripts existieren, aber keine JSON)
- Synthese-Ansatz valide: combined_score aus heterogenen Hypothesen
- Granularitaet per-number ist korrekt fuer KENO (70 Zahlen)
- Keine globalen Thresholds noetig - Scores normalisiert 0-1
- Integration klar: synthesizer.py liest results/*.json, predict.py nutzt Synthesizer
- Aufwand realistisch: 4-6h bei 4 verfuegbaren Hypothesen

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_ISSUE-006_PROXY_PLAN_20251227_181318.md

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
task: ISSUE-006
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_ISSUE-006_EXECUTOR_20251227_181518.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
