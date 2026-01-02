AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: --game Parameter fuer alle Scripts
TASK-ID: ISSUE-005
PRIORITY: LOW
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 18:03:18] ISSUE-005 - EXECUTOR (ki2)

### Summary
- Added --game/-g option to analyze.py cli() group with context propagation
- All subcommands (analyze, backtest, validate, info) use ctx.obj["game"]
- Added --game/-g option to backtest.py standalone command
- Added --game/-g option to report.py for dynamic title generation
- All scripts validate game via click.Choice(["keno", "eurojackpot", "lotto"])
- Override pattern: --game overrides config.active_game when provided
- Backward compatible: existing CLI calls without --game work unchanged

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_ISSUE-005_EXECUTOR_20251227_175918.md

## [2025-12-27 18:06:18] ISSUE-005 - PROXY_IMPL (ki0)

### Summary
- analyze.py: --game/-g Option in cli() group (L171-184), ctx.obj propagiert
- analyze.py: alle 4 subcommands (analyze, backtest, validate, info) nutzen ctx.obj.get("game")
- backtest.py: standalone --game/-g Option in main() (L422-428), cfg.active_game gesetzt (L502-505)
- report.py: --game/-g Option (L277-283), dynamischer Titel (L332-337)
- click.Choice(["keno", "eurojackpot", "lotto"]) validiert in allen Scripts
- Override-Pattern konsistent, backward compatible
- Syntax-Check: PASSED

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_ISSUE-005_PROXY_IMPL_20251227_180318.md



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
- scripts/analyze.py
- scripts/backtest.py
- scripts/report.py
- kenobase/core/config.py

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
- analyze.py: --game/-g Option in cli() group (L171-184), ctx.obj propagiert
- analyze.py: alle 4 subcommands (analyze, backtest, validate, info) nutzen ctx.obj.get("game")
- backtest.py: standalone --game/-g Option in main() (L422-428), cfg.active_game gesetzt (L502-505)
- report.py: --game/-g Option (L277-283), dynamischer Titel (L332-337)
- click.Choice(["keno", "eurojackpot", "lotto"]) validiert in allen Scripts
- Override-Pattern konsistent, backward compatible
- Syntax-Check: PASSED

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_ISSUE-005_PROXY_IMPL_20251227_180318.md

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
task: ISSUE-005
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_ISSUE-005_VALIDATOR_20251227_180618.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
