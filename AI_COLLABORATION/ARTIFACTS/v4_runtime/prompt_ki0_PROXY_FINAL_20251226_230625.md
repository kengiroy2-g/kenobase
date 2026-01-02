AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P5-01: Backtest-Script implementieren
TASK-ID: phase5_task01_backtest_script
PRIORITY: P1
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-26 23:04:25] phase5_task01_backtest_script - PROXY_IMPL (ki0)

### Summary
- Created scripts/backtest.py (~615 LOC) with BacktestEngine, dataclasses, CLI
- Walk-forward backtest with train/test split per period implemented correctly
- Metrics (Precision/Recall/F1) semantics match ARCHITECT definition
- Physics Layer integration via PipelineRunner (stability_score, criticality_level)
- CLI with click: --data, --periods, --train-ratio, --output, --format working
- tests/unit/test_backtest.py with 22 unit tests ALL PASS (verified)
- Syntax check passed for both files (py_compile)
- get_hot_numbers threshold usage correct (max_frequency_threshold as hot_threshold)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase5_task01_backtest_script_PROXY_IMPL_20251226_230125.md

## [2025-12-26 23:06:25] phase5_task01_backtest_script - VALIDATOR (ki3)

### Summary
- All 22 unit tests PASS (0.49s)
- Syntax validation for scripts/backtest.py OK
- CLI --help works correctly (via python -m scripts.backtest)
- Metrics semantics (Precision/Recall/F1) correctly implemented per ARCHITECT spec
- Physics Layer integration (stability_score, criticality_level) present
- BacktestEngine with walk-forward period split verified
- JSON and Markdown output formatters functional
- Edge cases covered (empty data, single period, extreme train_ratio)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_phase5_task01_backtest_script_VALIDATOR_20251226_230425.md




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
- scripts/backtest.py
- tests/unit/test_backtest.py

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
- All 22 unit tests PASS (0.49s)
- Syntax validation for scripts/backtest.py OK
- CLI --help works correctly (via python -m scripts.backtest)
- Metrics semantics (Precision/Recall/F1) correctly implemented per ARCHITECT spec
- Physics Layer integration (stability_score, criticality_level) present
- BacktestEngine with walk-forward period split verified
- JSON and Markdown output formatters functional
- Edge cases covered (empty data, single period, extreme train_ratio)

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_phase5_task01_backtest_script_VALIDATOR_20251226_230425.md

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
task: phase5_task01_backtest_script
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_phase5_task01_backtest_script_PROXY_FINAL_20251226_230625.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
