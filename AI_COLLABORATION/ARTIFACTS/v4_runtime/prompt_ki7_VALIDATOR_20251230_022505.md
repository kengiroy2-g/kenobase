AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Multi-Game Timeline (daily grid) bauen
TASK-ID: DATA-001
PRIORITY: P1
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 02:22:05] DATA-001 - EXECUTOR (ki6)

### Summary
- All 24 unit tests passing (pytest tests/unit/test_timeline.py)
- Parquet output verified: 1457 days x 45 columns (2022-01-03 to 2025-12-29)
- Coverage metrics confirmed: KENO 100%, Lotto 28.5%, EJ 27.7%
- CLI script works with --use-defaults, --json-summary, --mode options
- KENO 7/wk, Lotto 2/wk (Mi+Sa), EuroJackpot 2/wk (Di+Fr) correctly aligned
- No global thresholds misused (BUG-001 N/A)
- Ready for downstream COUPLE-001/002 integration

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_DATA-001_EXECUTOR_20251230_022005.md

## [2025-12-30 02:25:05] DATA-001 - PROXY_IMPL (ki0)

### Summary
- All 24 unit tests pass (0.56s execution time)
- Parquet output verified: 1457 days x 45 columns (2022-01-03 to 2025-12-29)
- Coverage metrics confirmed: KENO 100%, Lotto 28.5%, EJ 27.7%
- CLI script syntax OK, --help works, --use-defaults functional
- Timeline module imports correctly (TimelineGrid, load_multi_game_grid)
- Game-specific thresholds in config (BUG-001 N/A)
- JSON summary validates with all expected fields
- Ready for downstream COUPLE-001/002 integration

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DATA-001_PROXY_IMPL_20251230_022205.md



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
- kenobase/core/data_loader.py (MODIFIED - added Lotto bereinigt + EJ E-format parsers)
- data/processed/timeline_grid.parquet (NEW OUTPUT - 115KB)
- results/timeline_grid_summary.json (NEW OUTPUT)
- kenobase/core/timeline.py (478 LOC)
- tests/unit/test_timeline.py (400 LOC)
- scripts/build_timeline_grid.py (211 LOC)
- data/processed/timeline_grid.parquet (115KB, 1457x45)
- results/timeline_grid_summary.json

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
- All 24 unit tests pass (0.56s execution time)
- Parquet output verified: 1457 days x 45 columns (2022-01-03 to 2025-12-29)
- Coverage metrics confirmed: KENO 100%, Lotto 28.5%, EJ 27.7%
- CLI script syntax OK, --help works, --use-defaults functional
- Timeline module imports correctly (TimelineGrid, load_multi_game_grid)
- Game-specific thresholds in config (BUG-001 N/A)
- JSON summary validates with all expected fields
- Ready for downstream COUPLE-001/002 integration

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DATA-001_PROXY_IMPL_20251230_022205.md

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
- Datei: AI_COLLABORATION/HANDOFFS/ki7_DATA-001_VALIDATOR_20251230_022505.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
