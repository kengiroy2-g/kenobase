AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Walk-Forward Backtest Framework
TASK-ID: TASK-P03
PRIORITY: CRITICAL
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 03:34:20] TASK-P03 - EXECUTOR (ki2)

### Summary
- Phase A: Created BacktestStrategy ABC with HotNumber/ColdNumber/Random implementations
- Phase B: Integrated StrategyFactory into BacktestEngine with backward-compatibility
- Phase C: Added 27 unit tests for strategy module (all passing)
- Phase D: Verified backward-compatibility (22 existing backtest tests passing)
- CLI extended with --strategy/-s option (hot_number|cold_number|random)
- BacktestPeriodResult now includes strategy_name field
- JSON output includes strategy_name per period

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-P03_EXECUTOR_20251228_032820.md

## [2025-12-28 03:37:20] TASK-P03 - PROXY_IMPL (ki0)

### Summary
- Strategy ABC + 3 Implementations (Hot/Cold/Random) korrekt implementiert
- StrategyFactory mit register/create/list_strategies/get_default vollstaendig
- BacktestEngine mit optionalem strategy-Parameter + backward-compat
- CLI --strategy/-s Option funktioniert (verified via --help)
- 27 neue Strategy-Tests PASS, 22 bestehende Backtest-Tests PASS
- __init__.py exportiert alle Strategy-Klassen korrekt
- JSON-Output enthaelt strategy_name pro Periode (backtest.py:354)
- Game-specific thresholds korrekt verwendet (strategy.py:116-118)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P03_PROXY_IMPL_20251228_033420.md



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
- kenobase/analysis/frequency.py
- config/default.yaml
- kenobase/core/data_loader.py
- kenobase/core/config.py
- kenobase/pipeline/strategy.py (NEW - 270 lines)
- kenobase/pipeline/__init__.py (MODIFIED - exports added)
- scripts/backtest.py (MODIFIED - Strategy pattern integration)
- tests/unit/test_strategy.py (NEW - 27 tests)

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
- Strategy ABC + 3 Implementations (Hot/Cold/Random) korrekt implementiert
- StrategyFactory mit register/create/list_strategies/get_default vollstaendig
- BacktestEngine mit optionalem strategy-Parameter + backward-compat
- CLI --strategy/-s Option funktioniert (verified via --help)
- 27 neue Strategy-Tests PASS, 22 bestehende Backtest-Tests PASS
- __init__.py exportiert alle Strategy-Klassen korrekt
- JSON-Output enthaelt strategy_name pro Periode (backtest.py:354)
- Game-specific thresholds korrekt verwendet (strategy.py:116-118)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P03_PROXY_IMPL_20251228_033420.md

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
task: TASK-P03
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK-P03_VALIDATOR_20251228_033720.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
