AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Ensemble Prediction Model
TASK-ID: TASK-P06
PRIORITY: HIGH
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 04:23:22] TASK-P06 - PROXY_PLAN (ki0)

### Summary
- Architecture verified: HypothesisSynthesizer + KenoPredictor both exist and have compatible interfaces
- Synthesizer outputs NumberScore with combined_score (0-1), ML model outputs probability (0-1) - compatible for weighted ensemble
- Weights alpha=0.4 (rule) + 0.6 (ml) reasonable given ML typically outperforms rule-based
- New file kenobase/prediction/ensemble.py - correct location, follows existing module pattern
- __init__.py exports need update - correctly identified
- scripts/predict.py needs --ensemble flag - correctly identified
- Target F1 >= 0.50 from 0.4434 baseline is measurable and reasonable
- No global threshold issues (BUG-001 not applicable - this is KENO-specific)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P06_PROXY_PLAN_20251228_042122.md

## [2025-12-28 04:30:22] TASK-P06 - EXECUTOR (ki2)

### Summary
- Created EnsemblePredictor class combining Rule-Based + ML (alpha=0.4/0.6 weights)
- Implemented EnsemblePrediction and EnsembleReport dataclasses
- Updated __init__.py exports for EnsemblePredictor, EnsemblePrediction, EnsembleReport
- Added --ensemble, --alpha, --model-path, --data-path, --tune flags to predict.py
- Refactored predict.py into run_ensemble_mode() and run_rule_based_mode()
- Created 16 unit tests (all passing)
- Ensemble formula: ensemble_score = alpha * rule_score + (1 - alpha) * ml_probability

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-P06_EXECUTOR_20251228_042322.md



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
- ML Model KenoPredictor + KenoTrainer exist (`model.py`, `trainer.py`)
- Gap: No EnsemblePredictor class to combine both approaches
- Target F1 >= 0.50 (improvement from 0.4434 baseline)
- New file needed: `kenobase/prediction/ensemble.py`
- kenobase/prediction/ensemble.py (NEW)
- kenobase/prediction/__init__.py (MODIFIED)
- scripts/predict.py (MODIFIED)
- tests/unit/test_ensemble.py (NEW)

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
- Created EnsemblePredictor class combining Rule-Based + ML (alpha=0.4/0.6 weights)
- Implemented EnsemblePrediction and EnsembleReport dataclasses
- Updated __init__.py exports for EnsemblePredictor, EnsemblePrediction, EnsembleReport
- Added --ensemble, --alpha, --model-path, --data-path, --tune flags to predict.py
- Refactored predict.py into run_ensemble_mode() and run_rule_based_mode()
- Created 16 unit tests (all passing)
- Ensemble formula: ensemble_score = alpha * rule_score + (1 - alpha) * ml_probability

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-P06_EXECUTOR_20251228_042322.md

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
task: TASK-P06
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK-P06_PROXY_IMPL_20251228_043022.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
