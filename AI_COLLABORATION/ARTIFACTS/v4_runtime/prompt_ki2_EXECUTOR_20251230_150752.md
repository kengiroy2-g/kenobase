AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Gewinnklassen für V1 und V2 parallel berechnen
TASK-ID: TASK_005
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 15:05:52] TASK_005 - ARCHITECT (ki1)

### Summary
- Task-Ziel: Gewinnklassen fÃ¼r V1 (OPTIMAL_TICKETS_KI1) und V2 (BIRTHDAY_AVOIDANCE_TICKETS_V2) parallel berechnen
- Single Source of Truth fÃ¼r Quoten: kenobase/core/keno_quotes.py (Zeilen 16-26)
- Bestehende Backtest-Logik in scripts/backtest_models.py nutzt bereits get_gewinnklasse() (Zeile 111-114)
- V1 und V2 Tickets definiert in scripts/super_model_synthesis.py (importiert in daily_recommendation.py)
- Funktion get_fixed_quote() akzeptiert (keno_type, hits) -> payout in EUR
- Gewinnklassen-Mapping: _GK_LABELS_BY_TYPE in backtest_models.py (Zeilen 27-33)
- Empfehlung: Neues Modul kenobase/prediction/win_class_calculator.py erstellen
- Test-Datei: tests/unit/test_win_class_calculator.py

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_005_ARCHITECT_20251230_150352.md

## [2025-12-30 15:07:52] TASK_005 - PROXY_PLAN (ki0)

### Summary
- Plan verifiziert: Gewinnklassen fuer V1 (OPTIMAL_TICKETS_KI1) und V2 (BIRTHDAY_AVOIDANCE_TICKETS_V2) berechnen
- Single Source of Truth korrekt: kenobase/core/keno_quotes.py (Zeilen 16-26)
- Bestehende get_gewinnklasse() in backtest_models.py:111-124 nutzbar
- V1/V2 Ticket-Definitionen in super_model_synthesis.py verifiziert
- Architektur-konform: keine Red Flags
- Empfehlung fuer neues Helper-Modul ist sinnvoll (DRY)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_005_PROXY_PLAN_20251230_150552.md



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
- Plan verifiziert: Gewinnklassen fuer V1 (OPTIMAL_TICKETS_KI1) und V2 (BIRTHDAY_AVOIDANCE_TICKETS_V2) berechnen
- Single Source of Truth korrekt: kenobase/core/keno_quotes.py (Zeilen 16-26)
- Bestehende get_gewinnklasse() in backtest_models.py:111-124 nutzbar
- V1/V2 Ticket-Definitionen in super_model_synthesis.py verifiziert
- Architektur-konform: keine Red Flags
- Empfehlung fuer neues Helper-Modul ist sinnvoll (DRY)

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_005_PROXY_PLAN_20251230_150552.md

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
task: TASK_005
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK_005_EXECUTOR_20251230_150752.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
