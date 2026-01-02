AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Summen-Filter Integration
TASK-ID: TASK-P05
PRIORITY: HIGH
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 04:03:21] TASK-P05 - PROXY_PLAN (ki0)

### Summary
- CombinationEngine hat min_sum/max_sum in __init__ (Z.97-98) und _passes_sum_filter (Z.202-215) - VERIFIZIERT
- sum_distribution.py liefert SumCluster mit range_min/range_max (Z.60-76) - VERIFIZIERT
- Config hat bereits sum_windows Section (default.yaml Z.86-94) mit enabled, bin_width, expected_mean
- Integration-Plan ist konzeptionell solide: combination_filter.py als Bruecke-Modul
- PipelineRunner (runner.py) hat keine Summen-Analyse - muss erweitert werden
- Keine globalen Thresholds wo game-spezifische noetig (games Section hat eigene Thresholds)
- from_config Factory (Z.258-304) kann um sum_bounds erweitert werden
- Geschaetzter Aufwand 6.5h ist realistisch

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P05_PROXY_PLAN_20251228_040121.md

## [2025-12-28 04:09:21] TASK-P05 - EXECUTOR (ki2)

### Summary
- Added SumWindowsConfig to config.py with enabled, bin_width, expected_mean, manual_min_sum/max_sum
- Created combination_filter.py bridge module with SumBounds dataclass and derive functions
- Extended PipelineRunner.run() with Step 2.5 Sum Distribution Analysis
- Added _run_sum_analysis() method that analyzes sums and derives bounds from clusters
- Extended PipelineResult with sum_distribution_result and sum_bounds fields
- Created 13 unit tests for combination_filter module (all passing)
- Integration verified: Pipeline correctly derives bounds [605-825] from KENO data

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-P05_EXECUTOR_20251228_040321.md



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
- kenobase/core/config.py
- kenobase/core/combination_filter.py
- kenobase/pipeline/runner.py
- tests/unit/test_combination_filter.py

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
- Added SumWindowsConfig to config.py with enabled, bin_width, expected_mean, manual_min_sum/max_sum
- Created combination_filter.py bridge module with SumBounds dataclass and derive functions
- Extended PipelineRunner.run() with Step 2.5 Sum Distribution Analysis
- Added _run_sum_analysis() method that analyzes sums and derives bounds from clusters
- Extended PipelineResult with sum_distribution_result and sum_bounds fields
- Created 13 unit tests for combination_filter module (all passing)
- Integration verified: Pipeline correctly derives bounds [605-825] from KENO data

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-P05_EXECUTOR_20251228_040321.md

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
task: TASK-P05
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK-P05_PROXY_IMPL_20251228_040921.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
