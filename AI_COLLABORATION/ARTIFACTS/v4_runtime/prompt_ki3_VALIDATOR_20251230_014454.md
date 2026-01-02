AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Zeitachsen-Alignment
TASK-ID: DATA-001
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 01:42:54] DATA-001 - EXECUTOR (ki2)

### Summary
- Implemented TimelineGrid class for daily grid alignment of multi-game data
- Supports KENO (daily), Lotto (Wed+Sat), EuroJackpot (Tue+Fri) draw schedules
- Added NaN and forward-fill strategies for non-draw days
- Created to_dataframe() and to_numbers_matrix() export methods
- Added parquet export with tuple/matrix modes
- Fixed data_loader for LOTTO_ab_2022_bereinigt.csv (L1-L6 format)
- Fixed data_loader for EJ_ab_2022_bereinigt.csv (E1-E5/Euro1-2 format)
- 24 tests passing, 63 total with data_loader tests

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_DATA-001_EXECUTOR_20251230_013154.md

## [2025-12-30 01:44:54] DATA-001 - PROXY_IMPL (ki0)

### Summary
- TimelineGrid core module correctly implements daily grid alignment
- KENO (7/wk), Lotto (2/wk Wed+Sat), EuroJackpot (2/wk Tue+Fri) patterns correctly defined
- NaN and forward-fill strategies implemented and tested
- 24 unit tests passing, good coverage of edge cases
- Parquet export works in both tuple and matrix modes
- CLI script with --use-defaults and --json-summary options
- Output validates: 1457 days, 45 columns, 3 games aligned
- Coverage metrics match expected draw frequencies

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DATA-001_PROXY_IMPL_20251230_014254.md



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
- kenobase/core/timeline.py (NEW - 378 lines)
- tests/unit/test_timeline.py (NEW - 401 lines)
- scripts/build_timeline_grid.py (NEW - 125 lines)
- kenobase/core/data_loader.py (MODIFIED - added Lotto bereinigt + EJ E-format parsers)
- data/processed/timeline_grid.parquet (NEW OUTPUT - 115KB)
- results/timeline_grid_summary.json (NEW OUTPUT)

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
- TimelineGrid core module correctly implements daily grid alignment
- KENO (7/wk), Lotto (2/wk Wed+Sat), EuroJackpot (2/wk Tue+Fri) patterns correctly defined
- NaN and forward-fill strategies implemented and tested
- 24 unit tests passing, good coverage of edge cases
- Parquet export works in both tuple and matrix modes
- CLI script with --use-defaults and --json-summary options
- Output validates: 1457 days, 45 columns, 3 games aligned
- Coverage metrics match expected draw frequencies

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DATA-001_PROXY_IMPL_20251230_014254.md

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
task: DATA-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_DATA-001_VALIDATOR_20251230_014454.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
