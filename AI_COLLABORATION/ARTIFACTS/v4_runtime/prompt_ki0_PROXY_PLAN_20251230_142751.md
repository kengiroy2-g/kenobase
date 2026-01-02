AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Overlap-Metriken berechnen
TASK-ID: TASK_004
PRIORITY: P2
PHASE: PROXY_PLAN

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 13:34:48] task_004 - ARCHITECT (ki1)

### Summary
- Task: Integrate EconomicState into ML prediction pipeline (O1.5/O2.5 State-Awareness)
- Existing: economic_state.py (4 states: NORMAL/COOLDOWN/RECOVERY/HOT) + regime_detection.py (HMM-based)
- Gap: ML models (KenoPredictor, EnsemblePredictor) do not use state information
- Plan: Add StateAwarePredictor wrapper combining state detection + ensemble prediction
- New features: state-conditional thresholds, state-based alpha weighting, state-tagged predictions
- Acceptance: State-aware F1 >= baseline F1, state distribution matches economic_state labels
- Test scope: Unit tests for StateAwarePredictor, integration with existing EnsemblePredictor

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_task_004_ARCHITECT_20251230_133148.md

## [2025-12-30 14:27:51] TASK_004 - ARCHITECT (ki1)

### Summary
- Plan: Create StateAwarePredictor wrapper combining EconomicState + EnsemblePredictor
- New file: `kenobase/prediction/state_aware.py` (StateAwarePredictor class)
- Integration: Uses EconomicState (4 states: NORMAL/COOLDOWN/RECOVERY/HOT) for state-conditional predictions
- Features: state-tagged predictions, state-based alpha weighting, bet recommendations
- Acceptance: State-aware F1 >= EnsemblePredictor baseline F1; state labels match economic_state
- Tests: `tests/unit/test_state_aware.py` with unit + integration coverage
- Export: Update `kenobase/prediction/__init__.py` with new exports
- Repro: `python scripts/test_state_aware_predictor.py` -> `results/state_aware_validation.json`

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_004_ARCHITECT_20251230_142351.md



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
- Plan: Create StateAwarePredictor wrapper combining EconomicState + EnsemblePredictor
- New file: `kenobase/prediction/state_aware.py` (StateAwarePredictor class)
- Integration: Uses EconomicState (4 states: NORMAL/COOLDOWN/RECOVERY/HOT) for state-conditional predictions
- Features: state-tagged predictions, state-based alpha weighting, bet recommendations
- Acceptance: State-aware F1 >= EnsemblePredictor baseline F1; state labels match economic_state
- Tests: `tests/unit/test_state_aware.py` with unit + integration coverage
- Export: Update `kenobase/prediction/__init__.py` with new exports
- Repro: `python scripts/test_state_aware_predictor.py` -> `results/state_aware_validation.json`

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
AUFGABE: Pruefe den Plan vom ARCHITECT - NICHT nur mechanisch, sondern konzeptionell.

PFLICHTLEKTUERE (vor Review lesen):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Dein vollstaendiges Profil mit Known Bugs
2. AI_COLLABORATION/SYSTEM_STATUS.json - Aktueller Projektstatus
3. CLAUDE.md - Projektkontext (bei Architektur-Fragen)

EFFIZIENZ-REGELN:
- Arbeite mit VORHERIGER OUTPUT + TASK NOTES + Profil-Wissen
- Maximal 3-4 gezielte Reads (Profil, Status, relevante Dateien)
- Keine breiten Repo-Scans

VORHERIGER OUTPUT (kurz, no logs):
- Plan: Create StateAwarePredictor wrapper combining EconomicState + EnsemblePredictor
- New file: `kenobase/prediction/state_aware.py` (StateAwarePredictor class)
- Integration: Uses EconomicState (4 states: NORMAL/COOLDOWN/RECOVERY/HOT) for state-conditional predictions
- Features: state-tagged predictions, state-based alpha weighting, bet recommendations
- Acceptance: State-aware F1 >= EnsemblePredictor baseline F1; state labels match economic_state
- Tests: `tests/unit/test_state_aware.py` with unit + integration coverage
- Export: Update `kenobase/prediction/__init__.py` with new exports
- Repro: `python scripts/test_state_aware_predictor.py` -> `results/state_aware_validation.json`

FULL HANDOFF (nur bei Bedarf oeffnen):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_004_ARCHITECT_20251230_142351.md

PRUEFKRITERIEN (4 Dimensionen):
1. MECHANISCH: Plan vollstaendig? Schritte klar? Acceptance Criteria messbar?
2. ARCHITEKTUR: Passt zu ADRs? Keine Widersprueche?
3. INTEGRATION: Werden alle betroffenen Dateien genannt? (siehe Known Integration Points im Profil)
4. KONZEPTIONELL: Globale Werte wo spezifische noetig? Known Bugs vermieden?

RED FLAGS (sofort REJECTED):
- Globale Thresholds in team-spezifischem System (BUG-001)
- Feature ohne Orchestrator-Integration (BUG-003)
- Cross-File Aenderung ohne alle Dateien (Known Integration Points)

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: APPROVED
task: TASK_004
role: PROXY
phase: PROXY_PLAN
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

# Proxy Review

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_004_PROXY_PLAN_20251230_142751.md
- YAML Frontmatter mit status:
  - APPROVED: Plan ist gut, weiter zu Executor
  - REJECTED: Bug gefunden, zurueck zu Architect
  - ESCALATE: User-Entscheidung noetig (Architektur-Frage, Design-Wahl)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung (max 8 bullets)
