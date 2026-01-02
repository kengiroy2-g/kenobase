AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P4-02: Least-Action Pipeline-Auswahl
TASK-ID: phase4_task02_least_action_selector
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-26 21:33:11] phase4_task02_least_action_selector - PROXY_PLAN (ki0)

### Summary
- VERIFIED: Model Law B (Least-Action) already implemented in kenobase/physics/model_laws.py (lines 99-170)
- VERIFIED: PipelineConfig, calculate_pipeline_action(), select_best_pipeline() exist and are correct
- VERIFIED: Config flag physics.enable_least_action exists in config/default.yaml (line 35, value=true)
- VERIFIED: runner.py does NOT use enable_least_action - only enable_model_laws (line 214)
- VERIFIED: No kenobase/pipeline/least_action.py file exists (Glob returned empty)
- ARCHITECT plan is consistent with CLAUDE.md Section 4.1 architecture
- Plan correctly identifies all three deliverables needed
- No Known Bugs triggered (no global thresholds, no orchestrator bypass)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase4_task02_least_action_selector_PROXY_PLAN_20251226_213011.md

## [2025-12-26 21:39:11] phase4_task02_least_action_selector - EXECUTOR (ki2)

### Summary
- Created kenobase/pipeline/least_action.py with PipelineVariant, PipelineSelector, SelectionResult
- Defined 4 DEFAULT_PIPELINE_VARIANTS (minimal, standard, extended, full)
- Integrated PipelineSelector into PipelineRunner with enable_least_action config check
- Added pipeline_selection field to PipelineResult dataclass
- Added _run_least_action_selection() and get_pipeline_selector() methods to PipelineRunner
- Updated config_snapshot to include enable_least_action flag
- All 25 unit tests pass (test_least_action.py)
- All 15 runner tests pass (no regressions)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_phase4_task02_least_action_selector_EXECUTOR_20251226_213311.md



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
- Created kenobase/pipeline/least_action.py with PipelineVariant, PipelineSelector, SelectionResult
- Defined 4 DEFAULT_PIPELINE_VARIANTS (minimal, standard, extended, full)
- Integrated PipelineSelector into PipelineRunner with enable_least_action config check
- Added pipeline_selection field to PipelineResult dataclass
- Added _run_least_action_selection() and get_pipeline_selector() methods to PipelineRunner
- Updated config_snapshot to include enable_least_action flag
- All 25 unit tests pass (test_least_action.py)
- All 15 runner tests pass (no regressions)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_phase4_task02_least_action_selector_EXECUTOR_20251226_213311.md

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
task: phase4_task02_least_action_selector
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_phase4_task02_least_action_selector_PROXY_IMPL_20251226_213912.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
