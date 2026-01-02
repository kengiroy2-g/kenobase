AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Zyklus-Phasen markieren
TASK-ID: TASK_003
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 14:13:50] TASK_003 - PROXY_PLAN (ki0)

### Summary
- Plan ist vollstaendig und klar strukturiert mit 6 Implementierungsschritten
- Phase-Semantik (COOLDOWN/GROWTH/HOT/UNKNOWN) korrekt definiert mit Boundaries 30/60 Tage
- Acceptance Criteria sind messbar (100% Coverage, Unit-Tests)
- WICHTIG: jackpot_correlation.py hat bereits load_gk1_events() und get_jackpot_dates() - REUSE statt duplizieren!
- Jackpot-CSV verifiziert: 20 Events 2022-02-2024, Format Datum/Keno-Typ/Gewinner/Tage
- Unit-Test Edge-Cases sinnvoll: Boundaries, kein Jackpot, mehrere Jackpots
- Integration in analysis/__init__.py korrekt geplant
- Keine BUG-001/BUG-003 Red Flags (keine globalen Thresholds, kein Orchestrator noetig)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_003_PROXY_PLAN_20251230_141150.md

## [2025-12-30 14:17:50] TASK_003 - EXECUTOR (ki2)

### Summary
- Created kenobase/analysis/cycle_phases.py with Phase enum (COOLDOWN/GROWTH/HOT/UNKNOWN)
- Phase boundaries implemented: COOLDOWN=0-30d, GROWTH=31-60d, HOT=>60d nach Jackpot
- REUSED load_gk1_events() and get_jackpot_dates() from jackpot_correlation.py (as per plan)
- Created 33 unit tests covering all edge cases (boundaries, no jackpots, multiple jackpots)
- All 33 tests pass (pytest tests/unit/test_cycle_phases.py -v)
- Exported Phase, PhaseLabel, label_phases, filter_draws_by_phase, get_phase_statistics from __init__.py
- Helper functions get_phase_for_days() and get_phase_for_date() for single-value lookups

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_003_EXECUTOR_20251230_141350.md



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
- kenobase/analysis/__init__.py
- Keno_GPTs/10-9_KGDaten_gefiltert.csv
- kenobase/core/data_loader.py
- tests/unit/test_distribution.py (als Template fuer Test-Struktur)
- kenobase/analysis/cycle_phases.py (NEW)
- tests/unit/test_cycle_phases.py (NEW)
- kenobase/analysis/__init__.py (UPDATED)

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
- Created kenobase/analysis/cycle_phases.py with Phase enum (COOLDOWN/GROWTH/HOT/UNKNOWN)
- Phase boundaries implemented: COOLDOWN=0-30d, GROWTH=31-60d, HOT=>60d nach Jackpot
- REUSED load_gk1_events() and get_jackpot_dates() from jackpot_correlation.py (as per plan)
- Created 33 unit tests covering all edge cases (boundaries, no jackpots, multiple jackpots)
- All 33 tests pass (pytest tests/unit/test_cycle_phases.py -v)
- Exported Phase, PhaseLabel, label_phases, filter_draws_by_phase, get_phase_statistics from __init__.py
- Helper functions get_phase_for_days() and get_phase_for_date() for single-value lookups

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_003_EXECUTOR_20251230_141350.md

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
task: TASK_003
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_003_PROXY_IMPL_20251230_141750.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
