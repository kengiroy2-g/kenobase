AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: High-Win Analyse: Typ 8 (10.000 EUR)
TASK-ID: TASK_051
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-31 13:28:55] TASK_051 - ARCHITECT (ki1)

### Summary
- Task: High-Win Analyse fuer Typ 8 (8-aus-8 = 10.000 EUR)
- Typ 8 Quote: 8 Treffer = 10.000 EUR (laut keno_quotes.py:23)
- Existierendes Skript analyze_high_win_forensik.py analysiert nur >=400 EUR
- Backtest 2018-2024 zeigt 0 Typ-8 High-Win Events (alle high_payout_events leer)
- KEIN Typ-8 Vollgewinn im Dataset gefunden (erwartete Wahrscheinlichkeit ~1.3e-05)
- Neues Skript erforderlich: fokussierte Typ-8 Analyse mit niedrigerer Schwelle
- Empfehlung: Typ-8 spezifische Forensik mit Schwelle 100 EUR (8 Treffer=10k, 7=100, 6=15)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_051_ARCHITECT_20251231_132655.md

## [2025-12-31 13:30:55] TASK_051 - PROXY_PLAN (ki0)

### Summary
- Plan korrekt: Typ-8 Quotes verifiziert (8=10k, 7=100, 6=15, 5=2, 4=1, 0=1 EUR) in keno_quotes.py:23
- 400 EUR Threshold zu hoch fuer Typ-8 (nur 8/8=10k > 400; 7/8=100 wird verpasst)
- Empfehlung 100 EUR Threshold sinnvoll - erfasst 7/8 (100 EUR) Events
- Backtest 2018-2024 zeigt 0 high_payout_events fuer Typ-8 (threshold=400)
- Neues script backtest_typ8_analysis.py mit threshold=100 ist valider Ansatz
- Keine Architektur-Konflikte (BUG-001 nicht relevant - kein globaler Threshold)
- Repro-Pfad: `python scripts/backtest_typ8_analysis.py` -> `results/typ8_forensik.json`

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_051_PROXY_PLAN_20251231_132855.md



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
- scripts/analyze_high_win_forensik.py
- kenobase/core/keno_quotes.py
- kenobase/core/data_loader.py
- data/raw/keno/KENO_ab_2018.csv

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
- Plan korrekt: Typ-8 Quotes verifiziert (8=10k, 7=100, 6=15, 5=2, 4=1, 0=1 EUR) in keno_quotes.py:23
- 400 EUR Threshold zu hoch fuer Typ-8 (nur 8/8=10k > 400; 7/8=100 wird verpasst)
- Empfehlung 100 EUR Threshold sinnvoll - erfasst 7/8 (100 EUR) Events
- Backtest 2018-2024 zeigt 0 high_payout_events fuer Typ-8 (threshold=400)
- Neues script backtest_typ8_analysis.py mit threshold=100 ist valider Ansatz
- Keine Architektur-Konflikte (BUG-001 nicht relevant - kein globaler Threshold)
- Repro-Pfad: `python scripts/backtest_typ8_analysis.py` -> `results/typ8_forensik.json`

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_051_PROXY_PLAN_20251231_132855.md

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
task: TASK_051
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK_051_EXECUTOR_20251231_133055.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
