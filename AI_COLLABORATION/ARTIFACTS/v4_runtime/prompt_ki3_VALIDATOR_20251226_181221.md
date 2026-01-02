AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P1-03: Data Loader refactoren
TASK-ID: phase1_task03_data_loader
PRIORITY: P0
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-26 18:10:20] phase1_task03_data_loader - EXECUTOR (ki2)

### Summary
- DataLoader class with auto-format detection implemented
- DrawResult Pydantic model with date/numbers/bonus/game_type/metadata
- Four parser methods for KENO/EuroJackpot/Lotto-Old/Lotto-New formats
- DataFrame conversion via to_dataframe() and load_as_dataframe()
- 33 unit tests all passing (0.47s)
- 51 total tests in suite all passing
- Real data integration verified on all 4 CSV files
- Handoff: AI_COLLABORATION/HANDOFFS/ki2_phase1_task03_data_loader_EXECUTOR_20251226_180420.md

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_phase1_task03_data_loader_EXECUTOR_20251226_180420.md

## [2025-12-26 18:12:20] phase1_task03_data_loader - PROXY_IMPL (ki0)

### Summary
- DataLoader module with auto-format detection fully implemented
- DrawResult Pydantic model validates numbers (positive, sorted) and bonus (non-negative)
- Four parsers: KENO (20 Zahlen), EuroJackpot (5+2), Lotto-Alt (6), Lotto-Neu (6+ZZ)
- Format detection based on header inspection (Keno_Z1, 5 aus 50, z1-z6, Gewinnzahlen)
- LegacyConfig compatibility: csv_delimiter, csv_date_format match DataLoader defaults
- DataFrame conversion with sorted date index implemented
- 33 unit tests all passing (0.49s), real data integration tests pass
- Exports in __init__.py korrekt: DataLoader, DrawResult, GameType, FormatInfo

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase1_task03_data_loader_PROXY_IMPL_20251226_181020.md




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
- AI_COLLABORATION/HANDOFFS/ki1_phase1_task03_data_loader_ARCHITECT_20251226_174920.mdKeno_GPTs/Daten/Lotto_Archiv_ab-1955.csv (erste 5 Zeilen)Keno_GPTs/Daten/lotto_Stats_ab-2018.csv (erste 5 Zeilen)kenobase/core/config.py (bereits gelesen)AI_COLLABORATION/HANDOFFS/ki1_phase1_task03_data_loader_ARCHITECT_20251226_175520.mdkenobase/core/data_loader.py (NEW)kenobase/core/__init__.py (MODIFIED)tests/unit/test_data_loader.py (NEW)tests/fixtures/keno_sample.csv (NEW)tests/fixtures/eurojackpot_sample.csv (NEW)tests/fixtures/lotto_old_sample.csv (NEW)tests/fixtures/lotto_new_sample.csv (NEW)

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
- DataLoader module with auto-format detection fully implemented
- DrawResult Pydantic model validates numbers (positive, sorted) and bonus (non-negative)
- Four parsers: KENO (20 Zahlen), EuroJackpot (5+2), Lotto-Alt (6), Lotto-Neu (6+ZZ)
- Format detection based on header inspection (Keno_Z1, 5 aus 50, z1-z6, Gewinnzahlen)
- LegacyConfig compatibility: csv_delimiter, csv_date_format match DataLoader defaults
- DataFrame conversion with sorted date index implemented
- 33 unit tests all passing (0.49s), real data integration tests pass
- Exports in __init__.py korrekt: DataLoader, DrawResult, GameType, FormatInfo

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase1_task03_data_loader_PROXY_IMPL_20251226_181020.md

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
task: phase1_task03_data_loader
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_phase1_task03_data_loader_VALIDATOR_20251226_181221.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
