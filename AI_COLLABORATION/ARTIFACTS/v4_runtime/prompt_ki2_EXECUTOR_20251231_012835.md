AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: V1 vs V2 PARALLEL: Per Wochentag Vergleich
TASK-ID: TASK_039b
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-31 01:26:35] TASK_039b - ARCHITECT (ki1)

### Summary
- TASK_039b erweitert existierende Weekday-ROI-Analyse um V1/V2 Vergleich
- Existiert bereits: scripts/analyze_weekday_roi.py (nur V2)
- V1 Tickets definiert in scripts/backtest_birthday_cooldown.py lines 37-43
- V2 Tickets definiert in scripts/backtest_birthday_cooldown.py lines 46-52
- Nullmodell vorhanden (weekday shuffle, p=0.374 nicht signifikant)
- TASK_013 zeigt Di bester Tag (+423% ROI), Mo schlechtester (-67%)
- Plan: Neues Script compare_v1_v2_weekday.py oder Erweiterung

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_039b_ARCHITECT_20251231_012335.md

## [2025-12-31 01:28:35] TASK_039b - PROXY_PLAN (ki0)

### Summary
- Plan ist vollstaendig mit klarer Implementierungs-Checkliste (A1-D3)
- V1/V2 Ticket-Definitionen verifiziert in backtest_birthday_cooldown.py lines 37-52
- Granularitaet korrekt: per-weekday (7 Kategorien)
- Nullmodell spezifiziert (weekday-preserving shuffle, Permutationstest)
- Multiple-Testing-Korrektur (BH) erwaehnt - wichtig bei 7 Wochentagen
- Output-Schema klar definiert mit Acceptance Criteria
- WORKING_SET ist ausreichend fuer Implementation
- Keine Red Flags (globale Thresholds, fehlende Integration)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_039b_PROXY_PLAN_20251231_012635.md



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
- scripts/analyze_weekday_roi.py
- scripts/backtest_birthday_cooldown.py
- results/weekday_roi_analysis.json
- kenobase/core/keno_quotes.py

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
- Plan ist vollstaendig mit klarer Implementierungs-Checkliste (A1-D3)
- V1/V2 Ticket-Definitionen verifiziert in backtest_birthday_cooldown.py lines 37-52
- Granularitaet korrekt: per-weekday (7 Kategorien)
- Nullmodell spezifiziert (weekday-preserving shuffle, Permutationstest)
- Multiple-Testing-Korrektur (BH) erwaehnt - wichtig bei 7 Wochentagen
- Output-Schema klar definiert mit Acceptance Criteria
- WORKING_SET ist ausreichend fuer Implementation
- Keine Red Flags (globale Thresholds, fehlende Integration)

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_039b_PROXY_PLAN_20251231_012635.md

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
task: TASK_039b
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK_039b_EXECUTOR_20251231_012835.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
