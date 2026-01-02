AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: --game Parameter fuer alle Scripts
TASK-ID: ISSUE-005
PRIORITY: LOW
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
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

## [2025-12-27 18:08:18] ISSUE-005 - VALIDATOR (ki3)

### Summary
- Syntax check: PASSED (py_compile on all 3 scripts)
- analyze.py: --game/-g in cli() group (L173-178), propagiert via ctx.obj["game"]
- analyze.py: ctx.obj.get("game") in 4 subcommands (L258, L366, L476, L521)
- backtest.py: --game/-g Option (L422-428), cfg.active_game override (L502-505)
- report.py: --game/-g Option (L277-283), dynamic title generation (L332-337)
- All scripts show --game in --help output with click.Choice validation
- Acceptance Criteria (ISSUE-005): ALL MET

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_ISSUE-005_VALIDATOR_20251227_180618.md



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
ROLLE: PROXY (User-Stellvertreter - Finale Freigabe)
AUFGABE: Finale Freigabe mit Projekt-Perspektive.

PFLICHTLEKTUERE (kurz):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Falls Zweifel an Integration

EFFIZIENZ-REGELN:
- Nutze VALIDATOR OUTPUT + dein Wissen aus vorherigen Proxy-Phasen
- Keine weiteren Tests, nur finale Entscheidung

VALIDATOR OUTPUT (kurz):
- Syntax check: PASSED (py_compile on all 3 scripts)
- analyze.py: --game/-g in cli() group (L173-178), propagiert via ctx.obj["game"]
- analyze.py: ctx.obj.get("game") in 4 subcommands (L258, L366, L476, L521)
- backtest.py: --game/-g Option (L422-428), cfg.active_game override (L502-505)
- report.py: --game/-g Option (L277-283), dynamic title generation (L332-337)
- All scripts show --game in --help output with click.Choice validation
- Acceptance Criteria (ISSUE-005): ALL MET

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_ISSUE-005_VALIDATOR_20251227_180618.md

FINALE PRUEFUNG:
1. Hat Validator alle kritischen Aspekte geprueft?
2. Wuerde der USER diese Aenderung akzeptieren?
3. Gibt es offene Architektur-Fragen die der User entscheiden sollte?

ESKALATION an User wenn:
- Architektur-Entscheidung noetig die nicht in ADRs dokumentiert ist
- Unsicherheit ueber globale vs spezifische Werte
- Potenzielle Breaking Changes

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: COMPLETE
task: ISSUE-005
role: PROXY
phase: PROXY_FINAL
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

# Proxy Final Review

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki0_ISSUE-005_PROXY_FINAL_20251227_180818.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
