AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: DATA-03: Lotto-Daten migrieren
TASK-ID: data_migration_lotto
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 01:57:32] data_migration_lotto - EXECUTOR (ki2)

### Summary
- Added _parse_lotto_archiv() method to DataLoader for ISO8601+dash-separated format
- Updated _parse_lotto() to detect and route archiv format automatically
- Created test fixture lotto_archiv_sample.csv with 3 sample rows
- Added TestLottoArchivParser class with 4 unit tests + 1 integration test
- Copied 3 source files to data/raw/lotto/ (141KB + 200KB + 122KB)
- All 38 data_loader tests pass (including 5 new tests)
- Verified real data: 4764 archiv, 4886 old, 638 new draws loaded

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_data_migration_lotto_EXECUTOR_20251227_015332.md

## [2025-12-27 01:59:32] data_migration_lotto - PROXY_IMPL (ki0)

### Summary
- Implementation mechanically complete: _parse_lotto_archiv() added at data_loader.py:565-630
- Format detection in _parse_lotto() properly routes archiv format via first-line check
- Test fixture lotto_archiv_sample.csv has correct ISO8601+dash format (3 rows)
- All 38 tests pass including 5 new archiv tests (TestLottoArchivParser class)
- 3 files migrated to data/raw/lotto/ (141KB + 200KB + 122KB)
- Real data loads correctly: 4764 archiv, 4886 old, 638 new draws
- ~124 archiv rows have 7 numbers - source data issue, parser correctly skips them
- No architecture conflicts - follows existing _parse_lotto_* pattern

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_data_migration_lotto_PROXY_IMPL_20251227_015732.md



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
- kenobase/core/data_loader.py
- tests/unit/test_data_loader.py
- tests/fixtures/lotto_archiv_sample.csv
- data/raw/lotto/Lotto_Archiv_ab-1955.csv
- data/raw/lotto/lotto_Stats_ab-2018.csv
- data/raw/lotto/Lotto_archiv_bereinigt.csv

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
- Implementation mechanically complete: _parse_lotto_archiv() added at data_loader.py:565-630
- Format detection in _parse_lotto() properly routes archiv format via first-line check
- Test fixture lotto_archiv_sample.csv has correct ISO8601+dash format (3 rows)
- All 38 tests pass including 5 new archiv tests (TestLottoArchivParser class)
- 3 files migrated to data/raw/lotto/ (141KB + 200KB + 122KB)
- Real data loads correctly: 4764 archiv, 4886 old, 638 new draws
- ~124 archiv rows have 7 numbers - source data issue, parser correctly skips them
- No architecture conflicts - follows existing _parse_lotto_* pattern

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_data_migration_lotto_PROXY_IMPL_20251227_015732.md

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
task: data_migration_lotto
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_data_migration_lotto_VALIDATOR_20251227_015933.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
