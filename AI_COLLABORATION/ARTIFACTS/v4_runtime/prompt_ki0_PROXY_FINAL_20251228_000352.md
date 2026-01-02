AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Top-Pool Size Optimierung
TASK-ID: TASK-M01
PRIORITY: MEDIUM
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 00:00:52] TASK-M01 - PROXY_IMPL (ki0)

### Summary
- Script optimize_pool_size.py (541 lines) syntaktisch korrekt (py_compile OK)
- Config-Sektion number_pool korrekt in default.yaml:49-57 hinzugefuegt
- JSON-Output results/pool_optimization.json valide (json.load OK)
- Ergebnis top_n=20 marginal besser (F1=0.2469) vs top_n=11 (F1=0.2424), Diff <2%
- Default top_n_per_period=11 beibehalten (statistisch insignifikant)
- Script ist standalone, keine Integration Points verletzt
- Repro-Command verifiziert via --help und Ausfuehrung

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-M01_PROXY_IMPL_20251227_235752.md

## [2025-12-28 00:03:52] TASK-M01 - VALIDATOR (ki3)

### Summary
- Syntax validation PASS (py_compile OK)
- CLI --help output correct with examples and options
- JSON output valid (results/pool_optimization.json)
- Config section number_pool correctly added at default.yaml:49-57
- Default top_n_per_period=11 retained (F1 diff only 1.86%, not significant)
- NumberPoolGenerator correctly used in lines 255-260
- Walk-Forward backtest logic verified (no data leak)
- All 4 pool sizes [5,11,15,20] tested across 12 periods, 2237 draws

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK-M01_VALIDATOR_20251228_000052.md



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
- scripts/optimize_pool_size.py
- config/default.yaml
- results/pool_optimization.json

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
- Syntax validation PASS (py_compile OK)
- CLI --help output correct with examples and options
- JSON output valid (results/pool_optimization.json)
- Config section number_pool correctly added at default.yaml:49-57
- Default top_n_per_period=11 retained (F1 diff only 1.86%, not significant)
- NumberPoolGenerator correctly used in lines 255-260
- Walk-Forward backtest logic verified (no data leak)
- All 4 pool sizes [5,11,15,20] tested across 12 periods, 2237 draws

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK-M01_VALIDATOR_20251228_000052.md

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
task: TASK-M01
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK-M01_PROXY_FINAL_20251228_000352.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
