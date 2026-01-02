AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Ensemble Prediction Model
TASK-ID: TASK-P06
PRIORITY: HIGH
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 04:32:22] TASK-P06 - PROXY_IMPL (ki0)

### Summary
- EnsemblePredictor implementation verified: combines HypothesisSynthesizer (alpha) + KenoPredictor (1-alpha)
- Ensemble formula correctly implemented at line 338: ensemble_score = alpha * rule_score + (1 - alpha) * ml_prob
- __init__.py exports correctly updated with EnsemblePredictor, EnsemblePrediction, EnsembleReport
- predict.py CLI refactored with run_ensemble_mode() and run_rule_based_mode() - clean separation
- All 16 unit tests passing (verified: pytest tests/unit/test_ensemble.py -v)
- Syntax OK for all modified files (py_compile verified)
- --ensemble, --alpha, --model-path, --data-path, --tune flags visible in --help
- No Known Bugs triggered (BUG-001 N/A - KENO-specific, not global threshold issue)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P06_PROXY_IMPL_20251228_043022.md

## [2025-12-28 04:34:22] TASK-P06 - VALIDATOR (ki3)

### Summary
- All 16 unit tests passing (pytest tests/unit/test_ensemble.py -v -> 16 passed in 1.16s)
- Module imports verified: EnsemblePredictor, EnsemblePrediction, EnsembleReport
- CLI flags verified: --ensemble, --alpha, --model-path, --data-path, --tune present in --help
- Ensemble formula verified at line 338: ensemble_score = alpha * rule_score + (1-alpha) * ml_prob
- Syntax OK for kenobase/prediction/ensemble.py (py_compile passed)
- __init__.py exports correct (lines 46-50, 71-73)
- predict.py dispatch logic correct (line 413: if args.ensemble)
- Code quality: proper type hints, German docstrings, dataclass to_dict methods

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK-P06_VALIDATOR_20251228_043222.md



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
ROLLE: PROXY (User-Stellvertreter - Finale Freigabe)
AUFGABE: Finale Freigabe mit Projekt-Perspektive.

PFLICHTLEKTUERE (kurz):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Falls Zweifel an Integration

EFFIZIENZ-REGELN:
- Nutze VALIDATOR OUTPUT + dein Wissen aus vorherigen Proxy-Phasen
- Keine weiteren Tests, nur finale Entscheidung

VALIDATOR OUTPUT (kurz):
- All 16 unit tests passing (pytest tests/unit/test_ensemble.py -v -> 16 passed in 1.16s)
- Module imports verified: EnsemblePredictor, EnsemblePrediction, EnsembleReport
- CLI flags verified: --ensemble, --alpha, --model-path, --data-path, --tune present in --help
- Ensemble formula verified at line 338: ensemble_score = alpha * rule_score + (1-alpha) * ml_prob
- Syntax OK for kenobase/prediction/ensemble.py (py_compile passed)
- __init__.py exports correct (lines 46-50, 71-73)
- predict.py dispatch logic correct (line 413: if args.ensemble)
- Code quality: proper type hints, German docstrings, dataclass to_dict methods

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK-P06_VALIDATOR_20251228_043222.md

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
task: TASK-P06
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK-P06_PROXY_FINAL_20251228_043423.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
