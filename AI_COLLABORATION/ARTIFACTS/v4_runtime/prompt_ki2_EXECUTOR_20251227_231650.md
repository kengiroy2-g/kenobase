AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: 111-Prinzip Falsifikation
TASK-ID: TASK-H06
PRIORITY: HIGH
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 23:13:50] TASK-H06 - ARCHITECT (ki1)

### Summary
- 111-Prinzip definiert: Kombinationen wo Summe/111 in {1,11} oder umgekehrte Ziffern diese Eigenschaft haben
- Faktoren: 3, 11, 37, 111 (111 = 3 x 37)
- Falsifikationstest: Vergleich 111-gefilterte vs. zufaellige Kombinationen gegen historische Ziehungen
- Nullhypothese: 111-Filter hat keine bessere Trefferquote als Zufall
- Datenbasis: KENO_ab_2018.csv mit ~2000+ Ziehungen
- Metriken: Hit-Rate, Precision, Chi-Quadrat p-Wert
- Implementation: scripts/falsify_hyp008_111.py
- Erwartetes Ergebnis: HYP-008 wird widerlegt (Zufall gleich gut)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK-H06_ARCHITECT_20251227_231050.md

## [2025-12-27 23:16:50] TASK-H06 - PROXY_PLAN (ki0)

### Summary
- Plan ist methodisch korrekt: Chi-Quadrat Test + Kontrollgruppe fuer 111-Prinzip Falsifikation
- Nullhypothese klar formuliert: H0 = 111-Filter hat keine bessere Trefferquote als Zufall
- Akzeptanzkriterien messbar: p-Wert > 0.05 = widerlegt, Hit-Rate Differenz < 5% = widerlegt
- Template (analyze_hyp007.py) existiert und ist geeignet - Monte Carlo + Permutationstest Methodik
- Datenbasis verifiziert: data/raw/keno/KENO_ab_2018.csv existiert
- WORKING_SET vollstaendig fuer Executor
- Risiko-Mitigation adaequat: Kombinationsgroesse variieren bei zu wenig 111-Kombinationen
- Aufwandsschaetzung (5h) realistisch basierend auf Template-Verfuegbarkeit

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-H06_PROXY_PLAN_20251227_231350.md



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
- all_code/Iteration111_V4.py
- AI_COLLABORATION/KNOWLEDGE_BASE/HYPOTHESES_CATALOG.md
- config/default.yaml
- kenobase/core/data_loader.py
- scripts/analyze_hyp007.py (als Template)

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
- Plan ist methodisch korrekt: Chi-Quadrat Test + Kontrollgruppe fuer 111-Prinzip Falsifikation
- Nullhypothese klar formuliert: H0 = 111-Filter hat keine bessere Trefferquote als Zufall
- Akzeptanzkriterien messbar: p-Wert > 0.05 = widerlegt, Hit-Rate Differenz < 5% = widerlegt
- Template (analyze_hyp007.py) existiert und ist geeignet - Monte Carlo + Permutationstest Methodik
- Datenbasis verifiziert: data/raw/keno/KENO_ab_2018.csv existiert
- WORKING_SET vollstaendig fuer Executor
- Risiko-Mitigation adaequat: Kombinationsgroesse variieren bei zu wenig 111-Kombinationen
- Aufwandsschaetzung (5h) realistisch basierend auf Template-Verfuegbarkeit

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-H06_PROXY_PLAN_20251227_231350.md

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
task: TASK-H06
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK-H06_EXECUTOR_20251227_231650.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
