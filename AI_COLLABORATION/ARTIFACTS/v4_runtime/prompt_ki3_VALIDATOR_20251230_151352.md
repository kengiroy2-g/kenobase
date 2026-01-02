AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Gewinnklassen für V1 und V2 parallel berechnen
TASK-ID: TASK_005
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
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

## [2025-12-30 15:11:52] TASK_005 - EXECUTOR (ki2)

### Summary
- Created kenobase/prediction/win_class_calculator.py (DRY helper module)
- GK_LABELS_BY_TYPE mapping derived from KENO_FIXED_QUOTES_BY_TYPE
- get_gewinnklasse() returns WinClassResult dataclass
- evaluate_v1_v2_parallel() evaluates V1/V2 tickets in parallel
- 20 unit tests passing in tests/unit/test_win_class_calculator.py
- Exported all symbols via kenobase/prediction/__init__.py
- Single Source of Truth preserved: kenobase/core/keno_quotes.py

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_005_EXECUTOR_20251230_150752.md

## [2025-12-30 15:13:52] TASK_005 - PROXY_IMPL (ki0)

### Summary
- Syntax check passed (py_compile)
- All 20 unit tests passing in 1.63s
- Module exports verified via kenobase/prediction/__init__.py
- Single Source of Truth preserved: GK_LABELS_BY_TYPE derived from KENO_FIXED_QUOTES_BY_TYPE
- Type alignment verified: both cover Typ 2-10
- DRY helper module correctly uses get_fixed_quote() from keno_quotes.py
- ROI calculation correct: (winnings - einsatz) / einsatz
- No architecture violations or red flags detected

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_005_PROXY_IMPL_20251230_151152.md



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
- kenobase/prediction/win_class_calculator.py
- kenobase/prediction/__init__.py
- tests/unit/test_win_class_calculator.py

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
ROLLE: VALIDATOR
AUFGABE: Validiere die Implementation.

EFFIZIENZ-REGELN:
- Tests nur zielgerichtet (klein starten). Keine riesigen Logs in die Antwort; speichere nach AI_COLLABORATION/ARTIFACTS/ und verlinke.
- Vermeide Repo-weite Scans; nutze WORKING SET + gezielte Reads.

VORHERIGER OUTPUT (kurz):
- Syntax check passed (py_compile)
- All 20 unit tests passing in 1.63s
- Module exports verified via kenobase/prediction/__init__.py
- Single Source of Truth preserved: GK_LABELS_BY_TYPE derived from KENO_FIXED_QUOTES_BY_TYPE
- Type alignment verified: both cover Typ 2-10
- DRY helper module correctly uses get_fixed_quote() from keno_quotes.py
- ROI calculation correct: (winnings - einsatz) / einsatz
- No architecture violations or red flags detected

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_005_PROXY_IMPL_20251230_151152.md

VALIDIERUNG:
1. Fuehre minimale Tests aus (zielgerichtet)
2. Pruefe Code-Qualitaet
3. Verifiziere Acceptance Criteria

TOKEN HYGIENE:
- Bei Test FAIL: nur Command + kurze Fehlermeldung (max 20 Zeilen)
- Mehr Log noetig? Speichere in AI_COLLABORATION/ARTIFACTS/ und referenziere Pfad

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: APPROVED
task: TASK_005
role: VALIDATOR
phase: VALIDATOR
validated_handoff: "<nur filename oder leer>"
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

# Validation

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK_005_VALIDATOR_20251230_151352.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
