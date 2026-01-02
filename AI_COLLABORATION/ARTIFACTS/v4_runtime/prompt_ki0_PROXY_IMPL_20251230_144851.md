AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Overlap-Metriken berechnen
TASK-ID: TASK_004
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 14:29:51] TASK_004 - PROXY_PLAN (ki0)

### Summary
- Plan creates StateAwarePredictor wrapper combining EconomicState + EnsemblePredictor
- EconomicState exists in kenobase/core/economic_state.py with 4 states (NORMAL/COOLDOWN/RECOVERY/HOT)
- EnsemblePredictor exists in kenobase/prediction/ensemble.py with working fit/predict interface
- Acceptance criteria measurable: State-aware F1 >= EnsemblePredictor baseline F1
- Working Set complete: all 6 files listed correctly (3 new, 3 existing)
- Integration with __init__.py exports clearly specified
- Repro command defined: python scripts/test_state_aware_predictor.py -> results/state_aware_validation.json

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_004_PROXY_PLAN_20251230_142751.md

## [2025-12-30 14:48:51] TASK_004 - EXECUTOR (ki2)

### Summary
- Created StateAwarePredictor class combining EconomicState + EnsemblePredictor
- Implemented state-specific alpha weighting (NORMAL=0.4, COOLDOWN=0.6, RECOVERY=0.5, HOT=0.3)
- Added StateAwarePrediction and StateAwareReport dataclasses
- Updated __init__.py with exports: StateAwarePredictor, StateAwarePrediction, StateAwareReport, DEFAULT_STATE_ALPHAS
- Created 17 unit tests - all PASS
- Created validation script: python scripts/test_state_aware_predictor.py
- Script running in background (ML training takes ~10 min on 1457 draws)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_004_EXECUTOR_20251230_142951.md



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
- Acceptance: State-aware F1 >= EnsemblePredictor baseline F1; state labels match economic_state
- Tests: `tests/unit/test_state_aware.py` with unit + integration coverage
- Export: Update `kenobase/prediction/__init__.py` with new exports
- Repro: `python scripts/test_state_aware_predictor.py` -> `results/state_aware_validation.json`
- kenobase/prediction/state_aware.py (NEW)
- kenobase/prediction/__init__.py (UPDATED)
- tests/unit/test_state_aware.py (NEW)
- scripts/test_state_aware_predictor.py (NEW)

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
- Created StateAwarePredictor class combining EconomicState + EnsemblePredictor
- Implemented state-specific alpha weighting (NORMAL=0.4, COOLDOWN=0.6, RECOVERY=0.5, HOT=0.3)
- Added StateAwarePrediction and StateAwareReport dataclasses
- Updated __init__.py with exports: StateAwarePredictor, StateAwarePrediction, StateAwareReport, DEFAULT_STATE_ALPHAS
- Created 17 unit tests - all PASS
- Created validation script: python scripts/test_state_aware_predictor.py
- Script running in background (ML training takes ~10 min on 1457 draws)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_004_EXECUTOR_20251230_142951.md

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
task: TASK_004
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_004_PROXY_IMPL_20251230_144851.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
