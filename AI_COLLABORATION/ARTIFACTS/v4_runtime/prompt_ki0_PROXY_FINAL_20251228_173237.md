AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Mehrwochenschein Jackpot-Timing
TASK-ID: HYP014-001
PRIORITY: MITTEL
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 17:30:37] HYP014-001 - PROXY_IMPL (ki0)

### Summary
- multiweek_timing.py (561 lines): Monte-Carlo + Chi-Square implementation korrekt
- 5 Dataclasses (SimulationConfig, PositionDistribution, ChiSquareResult, MonteCarloComparison, MultiweekTimingResult)
- JSON export mit numpy type conversion funktioniert
- __init__.py korrekt integriert mit aliased ChiSquareResult -> MultiweekChiSquareResult
- 21 Unit Tests - ALL PASSING (pytest 0.92s)
- CLI analyze_hyp014.py funktioniert (--help verifiziert)
- Keine BUG-001..010 Red Flags erkannt
- Pattern konsistent mit gk1_waiting.py und temporal_cycles.py

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP014-001_PROXY_IMPL_20251228_172837.md

## [2025-12-28 17:32:37] HYP014-001 - VALIDATOR (ki3)

### Summary
- 21 Unit Tests ALL PASSING (pytest 0.89s)
- Syntax verified via py_compile (no errors)
- Module import via __init__.py OK (MultiweekChiSquareResult alias works)
- CLI analyze_hyp014.py --help OK
- Code review: Monte-Carlo + Chi-Square implementation correct
- 5 Dataclasses with proper type hints and docstrings
- JSON export with numpy type conversion handles edge cases
- Pattern consistent with existing modules (gk1_waiting.py, temporal_cycles.py)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_HYP014-001_VALIDATOR_20251228_173037.md



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
- kenobase/analysis/multiweek_timing.py
- kenobase/analysis/__init__.py
- scripts/analyze_hyp014.py
- tests/unit/test_multiweek_timing.py

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
- 21 Unit Tests ALL PASSING (pytest 0.89s)
- Syntax verified via py_compile (no errors)
- Module import via __init__.py OK (MultiweekChiSquareResult alias works)
- CLI analyze_hyp014.py --help OK
- Code review: Monte-Carlo + Chi-Square implementation correct
- 5 Dataclasses with proper type hints and docstrings
- JSON export with numpy type conversion handles edge cases
- Pattern consistent with existing modules (gk1_waiting.py, temporal_cycles.py)

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_HYP014-001_VALIDATOR_20251228_173037.md

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
task: HYP014-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_HYP014-001_PROXY_FINAL_20251228_173237.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
