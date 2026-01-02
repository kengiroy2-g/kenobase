AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Confidence Intervals
TASK-ID: TASK-P11
PRIORITY: MEDIUM
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 05:47:26] TASK-P11 - PROXY_IMPL (ki0)

### Summary
- confidence.py: Bootstrap CI implementation with ConfidenceInterval, ConfidenceEstimator, PredictionWithCI
- ConfidenceEstimator uses 1000 bootstrap resamples (configurable), random_state=42 for reproducibility
- CI width < 0.3 defines stable predictions (acceptance criterion met)
- 95% CI is standard statistical practice (not a tunable global threshold - OK)
- ensemble.py extended with ensemble_ci, ml_ci Optional fields on EnsemblePrediction
- predict_with_ci() and get_stable_predictions() methods added to EnsemblePredictor
- All 27 confidence tests pass, all 16 ensemble tests pass (43 total)
- No integration issues detected - confidence module is self-contained with clean imports

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P11_PROXY_IMPL_20251228_054526.md

## [2025-12-28 05:49:26] TASK-P11 - VALIDATOR (ki3)

### Summary
- confidence.py: Bootstrap CI implementation verified (1000 resamples, random_state=42)
- ConfidenceInterval dataclass: lower, upper, point_estimate, width, is_stable properties
- ConfidenceEstimator.calculate_ci() uses percentile-bootstrap method correctly
- coverage_test() validates CI schema (near 95% coverage confirmed in tests)
- ensemble.py integration: ensemble_ci, ml_ci Optional fields, predict_with_ci(), get_stable_predictions()
- All 27 confidence tests PASS (1.21s), all 16 ensemble tests PASS (1.14s)
- Acceptance criteria met: width < 0.3 for stable, 95% CI standard
- Imports verified: modules cleanly importable, no circular dependencies

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK-P11_VALIDATOR_20251228_054726.md



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
- kenobase/prediction/confidence.py
- kenobase/prediction/ensemble.py
- tests/unit/test_confidence.py

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
- confidence.py: Bootstrap CI implementation verified (1000 resamples, random_state=42)
- ConfidenceInterval dataclass: lower, upper, point_estimate, width, is_stable properties
- ConfidenceEstimator.calculate_ci() uses percentile-bootstrap method correctly
- coverage_test() validates CI schema (near 95% coverage confirmed in tests)
- ensemble.py integration: ensemble_ci, ml_ci Optional fields, predict_with_ci(), get_stable_predictions()
- All 27 confidence tests PASS (1.21s), all 16 ensemble tests PASS (1.14s)
- Acceptance criteria met: width < 0.3 for stable, 95% CI standard
- Imports verified: modules cleanly importable, no circular dependencies

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK-P11_VALIDATOR_20251228_054726.md

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
task: TASK-P11
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK-P11_PROXY_FINAL_20251228_054926.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
