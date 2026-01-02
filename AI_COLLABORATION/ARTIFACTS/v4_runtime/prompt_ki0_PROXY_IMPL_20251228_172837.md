AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Mehrwochenschein Jackpot-Timing
TASK-ID: HYP014-001
PRIORITY: MITTEL
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 17:21:37] HYP014-001 - ARCHITECT (ki1)

### Summary
- HYP014: Mehrwochenschein Jackpot-Timing Analyse planen
- Neues Modul kenobase/analysis/multiweek_timing.py erstellen
- Script scripts/analyze_hyp014.py fuer Analyse anlegen
- Monte-Carlo Simulation fuer Abo-Perioden-Timing
- Acceptance Criteria fuer statistische Signifikanz definiert
- Tests in tests/unit/test_multiweek_timing.py

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_HYP014-001_ARCHITECT_20251228_171837.md

## [2025-12-28 17:23:37] HYP014-001 - PROXY_PLAN (ki0)

### Summary
- Plan folgt bestehendem Muster von gk1_waiting.py und temporal_cycles.py
- Monte-Carlo Simulation ist korrekter Ansatz da keine echten Abo-Daten
- Chi-Quadrat Test konsistent mit HYP-002 und HYP-011 Modulen
- Dataclasses + JSON Export folgen etabliertem Pattern
- WORKING_SET ausreichend fuer Implementierung
- Acceptance Criteria sind messbar und verifizierbar
- Keine BUG-001/002/003 Red Flags erkannt
- Modul-Integration in __init__.py erforderlich (dokumentiert)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP014-001_PROXY_PLAN_20251228_172137.md

## [2025-12-28 17:28:37] HYP014-001 - EXECUTOR (ki2)

### Summary
- Created kenobase/analysis/multiweek_timing.py with 540 lines
- Monte-Carlo simulation for abo-period timing analysis
- Chi-Square uniformity test for position distributions
- Dataclasses: SimulationConfig, PositionDistribution, ChiSquareResult, MonteCarloComparison, MultiweekTimingResult
- JSON export with numpy type conversion
- Script scripts/analyze_hyp014.py with CLI arguments
- 21 unit tests in tests/unit/test_multiweek_timing.py - ALL PASSING
- Module integrated into kenobase/analysis/__init__.py

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HYP014-001_EXECUTOR_20251228_172337.md



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
ROLLE: PROXY (User-Stellvertreter mit Projekt-Kontext)
AUFGABE: Pruefe die Implementation - NICHT nur mechanisch, sondern auf Architektur-Konsistenz.

PFLICHTLEKTUERE (vor Review):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Known Bugs & Integration Points
2. AI_COLLABORATION/SYSTEM_STATUS.json - Bei Architektur-Fragen

EFFIZIENZ-REGELN:
- Arbeite mit VORHERIGER OUTPUT + WORKING SET + Profil-Wissen
- Maximal 3-4 gezielte Reads
- Minimaler Sanity-Check (python -m py_compile, JSON-Validierung)

VORHERIGER OUTPUT (kurz):
- Created kenobase/analysis/multiweek_timing.py with 540 lines
- Monte-Carlo simulation for abo-period timing analysis
- Chi-Square uniformity test for position distributions
- Dataclasses: SimulationConfig, PositionDistribution, ChiSquareResult, MonteCarloComparison, MultiweekTimingResult
- JSON export with numpy type conversion
- Script scripts/analyze_hyp014.py with CLI arguments
- 21 unit tests in tests/unit/test_multiweek_timing.py - ALL PASSING
- Module integrated into kenobase/analysis/__init__.py

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HYP014-001_EXECUTOR_20251228_172337.md

PRUEFKRITERIEN (4 Dimensionen):
1. MECHANISCH: Alle Schritte ausgefuehrt? Syntax OK? Acceptance Criteria erfuellt?
2. ARCHITEKTUR: Implementation passt zu ADRs? Keine Widersprueche eingefuehrt?
3. INTEGRATION: ALLE betroffenen Dateien geaendert? (siehe Known Integration Points)
   - hybrid_prediction_engine.py geaendert? -> production_orchestrator.py pruefen!
   - Config geaendert? -> Code der Config liest pruefen!
   - Threshold geaendert? -> Ist er global oder spezifisch?
4. KNOWN BUGS: Keiner der 10 Known Bugs reproduziert? (BUG-001 bis BUG-010)

RED FLAGS (sofort REJECTED):
- Aenderung in Datei A ohne korrespondierende Aenderung in Datei B
- Globale Werte wo spezifische noetig (BUG-001)
- Feature implementiert aber nicht im Orchestrator eingebunden (BUG-003)
- Config-Pfad im Code stimmt nicht mit YAML-Struktur (BUG-002)

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: APPROVED
task: HYP014-001
role: PROXY
phase: PROXY_IMPL
reviewed_handoff: "<nur filename oder leer>"
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

# Proxy Review (Implementation)

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki0_HYP014-001_PROXY_IMPL_20251228_172837.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
