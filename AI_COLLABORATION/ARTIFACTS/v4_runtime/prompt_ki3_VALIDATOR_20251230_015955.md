AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Zahlenraum-Normalisierung
TASK-ID: DATA-002
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 01:57:55] DATA-002 - EXECUTOR (ki2)

### Summary
- Created kenobase/core/normalizer.py with Zahlenraum-Normalisierung functions
- Implemented normalize_number, denormalize_number for single values (n-min)/(max-min)
- Implemented normalize_numbers, denormalize_numbers for batch operations
- Implemented normalize_draw, normalize_draws for DrawResult integration
- Implemented cross_game_distance for cross-lottery comparison (MAE of normalized values)
- Game ranges from config: KENO 1-70, Lotto 1-49, EuroJackpot 1-50
- Bonus handling: EuroZahlen 1-12, Superzahl 0-9, KENO Plus5 skipped (5-digit code)
- Added 43 unit tests, all passing

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_DATA-002_EXECUTOR_20251230_015355.md

## [2025-12-30 01:59:55] DATA-002 - PROXY_IMPL (ki0)

### Summary
- normalizer.py implementiert korrekt (n-min)/(max-min) Formel
- Alle 43 Unit-Tests bestanden (pytest 0.40s)
- Syntax-Check fuer beide Dateien OK
- __init__.py korrekt um Normalizer-Exports erweitert
- Game ranges konsistent mit config/default.yaml (KENO 1-70, Lotto 1-49, EuroJackpot 1-50)
- Bonus-Handling korrekt: EuroZahlen 1-12, Superzahl 0-9, KENO Plus5 skipped
- cross_game_distance verwendet MAE - mathematisch korrekt
- Keine Known Bugs reproduziert, keine Architektur-Verletzungen

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DATA-002_PROXY_IMPL_20251230_015755.md



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
- kenobase/core/normalizer.py
- kenobase/core/__init__.py
- tests/unit/test_normalizer.py

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
- normalizer.py implementiert korrekt (n-min)/(max-min) Formel
- Alle 43 Unit-Tests bestanden (pytest 0.40s)
- Syntax-Check fuer beide Dateien OK
- __init__.py korrekt um Normalizer-Exports erweitert
- Game ranges konsistent mit config/default.yaml (KENO 1-70, Lotto 1-49, EuroJackpot 1-50)
- Bonus-Handling korrekt: EuroZahlen 1-12, Superzahl 0-9, KENO Plus5 skipped
- cross_game_distance verwendet MAE - mathematisch korrekt
- Keine Known Bugs reproduziert, keine Architektur-Verletzungen

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DATA-002_PROXY_IMPL_20251230_015755.md

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
task: DATA-002
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_DATA-002_VALIDATOR_20251230_015955.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
