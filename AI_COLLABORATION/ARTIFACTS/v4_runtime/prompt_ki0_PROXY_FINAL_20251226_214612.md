AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P4-02: Least-Action Pipeline-Auswahl
TASK-ID: phase4_task02_least_action_selector
PRIORITY: P2
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-26 21:42:12] phase4_task02_least_action_selector - PROXY_IMPL (ki0)

### Summary
- Created kenobase/pipeline/least_action.py (342 lines) - PipelineVariant, PipelineSelector, SelectionResult
- 4 DEFAULT_PIPELINE_VARIANTS defined (minimal, standard, extended, full) with correct complexity ordering
- PipelineSelector correctly wraps physics.model_laws functions (calculate_pipeline_action, select_best_pipeline)
- PipelineRunner integrated with _run_least_action_selection() and get_pipeline_selector() methods
- Config flag physics.enable_least_action properly checked (line 250 in runner.py)
- config_snapshot includes enable_least_action flag (line 378 in runner.py)
- All 25 unit tests pass (test_least_action.py), all 15 runner tests pass (no regressions)
- Integration verified: pipeline_selection field populated with SelectionResult when enabled

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase4_task02_least_action_selector_PROXY_IMPL_20251226_213912.md

## [2025-12-26 21:46:12] phase4_task02_least_action_selector - VALIDATOR (ki3)

### Summary
- All 25 unit tests pass (test_least_action.py) - verified
- All 15 runner tests pass (test_runner.py) - no regressions
- Action formula verified: complexity + instability - performance matches CLAUDE.md 6.2
- Manual calculation matches selector.calculate_action() for all 4 variants
- Runner integration verified: pipeline_selection populated when enable_least_action=true
- Runner integration verified: pipeline_selection=None when enable_least_action=false
- Config snapshot correctly includes enable_least_action flag (line 378)
- mypy shows no errors in least_action.py (all errors from other modules)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_phase4_task02_least_action_selector_VALIDATOR_20251226_214212.md




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
- kenobase/pipeline/least_action.py (NEW - 267 lines)
- kenobase/pipeline/__init__.py (MODIFIED - added least_action exports)
- kenobase/pipeline/runner.py (MODIFIED - integrated PipelineSelector)
- tests/unit/test_least_action.py (NEW - 25 unit tests)

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
- All 25 unit tests pass (test_least_action.py) - verified
- All 15 runner tests pass (test_runner.py) - no regressions
- Action formula verified: complexity + instability - performance matches CLAUDE.md 6.2
- Manual calculation matches selector.calculate_action() for all 4 variants
- Runner integration verified: pipeline_selection populated when enable_least_action=true
- Runner integration verified: pipeline_selection=None when enable_least_action=false
- Config snapshot correctly includes enable_least_action flag (line 378)
- mypy shows no errors in least_action.py (all errors from other modules)

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_phase4_task02_least_action_selector_VALIDATOR_20251226_214212.md

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
task: phase4_task02_least_action_selector
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_phase4_task02_least_action_selector_PROXY_FINAL_20251226_214612.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
