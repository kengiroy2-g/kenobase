AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Anti-Cluster Reset-Regel
TASK-ID: TASK-H03
PRIORITY: HIGH
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 22:29:48] TASK-H03 - EXECUTOR (ki2)

### Summary
- Created cluster_reset.py with ClusterEvent, ClusterResetResult, TradingSignal dataclasses
- Implemented detect_cluster_events() - finds clusters >= threshold (default 5)
- Implemented analyze_reset_probability() - calculates P(reset | cluster) empirically
- Implemented generate_trading_signals() - generates NO-BET signals for active clusters
- Implemented generate_cluster_reset_report() - full JSON report generation
- Added exports to kenobase/analysis/__init__.py
- Created CLI script scripts/analyze_hyp003.py with argparse interface
- Created 26 unit tests in tests/unit/test_cluster_reset.py - ALL PASSING

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-H03_EXECUTOR_20251227_222348.md

## [2025-12-27 22:31:48] TASK-H03 - PROXY_IMPL (ki0)

### Summary
- cluster_reset.py implements all required functionality (detect, analyze, signals, report)
- 26/26 unit tests passing - comprehensive coverage of edge cases
- __init__.py correctly updated with all exports (lines 128-136, 251-258)
- CLI script analyze_hyp003.py is complete with argparse, logging, NumpyEncoder
- Syntax validation passed for all files
- Baseline probability correctly uses KENO formula: 1 - 20/70 = 0.714
- Lift calculation and is_significant logic correct (lift > 1.1 AND clusters >= 10)
- No Known Bugs reproduced - implementation is standalone module

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-H03_PROXY_IMPL_20251227_222948.md



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
- kenobase/analysis/cluster_reset.py (NEW)
- kenobase/analysis/__init__.py (UPDATED)
- scripts/analyze_hyp003.py (NEW)
- tests/unit/test_cluster_reset.py (NEW)

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
- cluster_reset.py implements all required functionality (detect, analyze, signals, report)
- 26/26 unit tests passing - comprehensive coverage of edge cases
- __init__.py correctly updated with all exports (lines 128-136, 251-258)
- CLI script analyze_hyp003.py is complete with argparse, logging, NumpyEncoder
- Syntax validation passed for all files
- Baseline probability correctly uses KENO formula: 1 - 20/70 = 0.714
- Lift calculation and is_significant logic correct (lift > 1.1 AND clusters >= 10)
- No Known Bugs reproduced - implementation is standalone module

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-H03_PROXY_IMPL_20251227_222948.md

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
task: TASK-H03
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK-H03_VALIDATOR_20251227_223148.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
