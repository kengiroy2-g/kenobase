AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Korrelation zwischen Tickets
TASK-ID: TASK_034
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 23:34:58] TASK_034 - PROXY_PLAN (ki0)

### Summary
- Plan is complete with 6 Dataclasses, 4 core functions, clear acceptance criteria
- BH-FDR already exists in null_models.py (benjamini_hochberg_fdr) - can be reused
- Integration points correct: __init__.py export section clearly identified
- 4 files in WORKING_SET match deliverables (NEW/MODIFY correctly tagged)
- Granularity per-ticket-pair appropriate for portfolio analysis
- ROI context explicit: -43% to -67% ROI tickets, diversification purpose only
- Script references SYSTEM_STATUS tickets (Typ-2,6,8,10) - ensures consistency
- Unit-Tests cover edge cases (no_overlap, full_overlap, insufficient_data)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_034_PROXY_PLAN_20251230_233258.md


## [2025-12-30 23:39:58] TASK_034 - EXECUTOR (ki2)

### Summary
- Created ticket_correlation.py with 6 dataclasses and 6 core functions
- Implemented 3 analysis dimensions: Overlap (Jaccard), ROI-Sync (Spearman), Timing (lift)
- BH-FDR from null_models.py reused for multiple testing correction
- Added 12 exports to analysis/__init__.py
- Script produces results/ticket_correlation.json with 6 pair correlations
- Unit tests: 20 tests pass, covering all 5 required scenarios
- Key finding: Typ-2+Typ-6 best diversification (0.65), Typ-8+Typ-10 most correlated (0.46)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_034_EXECUTOR_20251230_233458.md



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
- kenobase/analysis/ticket_correlation.py (NEW)
- kenobase/analysis/__init__.py (MODIFY - add exports)
- scripts/analyze_ticket_correlation.py (NEW)
- tests/unit/test_ticket_correlation.py (NEW)
- kenobase/analysis/__init__.py (MODIFY - 12 exports added)
- results/ticket_correlation.json (NEW - generated output)

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
- Created ticket_correlation.py with 6 dataclasses and 6 core functions
- Implemented 3 analysis dimensions: Overlap (Jaccard), ROI-Sync (Spearman), Timing (lift)
- BH-FDR from null_models.py reused for multiple testing correction
- Added 12 exports to analysis/__init__.py
- Script produces results/ticket_correlation.json with 6 pair correlations
- Unit tests: 20 tests pass, covering all 5 required scenarios
- Key finding: Typ-2+Typ-6 best diversification (0.65), Typ-8+Typ-10 most correlated (0.46)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_034_EXECUTOR_20251230_233458.md

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
task: TASK_034
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_034_PROXY_IMPL_20251230_233958.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
