AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Multiple Testing Korrektur
TASK-ID: TASK_031
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 22:03:54] TASK_031 - PROXY_PLAN (ki0)

### Summary
- Plan ist mechanisch vollstaendig: Script, Test, Report als Deliverables definiert
- benjamini_hochberg_fdr() existiert in kenobase/analysis/null_models.py:268-333 - VERIFIZIERT
- 61 JSON-Dateien mit p_value gefunden in results/ - ausreichende Datenbasis
- p_value Strukturen sind heterogen (nested keys wie mann_whitney.p_value, welch_t_test.p_value_onesided)
- Hinweis: Script muss flexible JSON-Traversierung implementieren (nicht nur top-level p_value)
- Granularity GLOBAL ist korrekt fuer FDR (alle Tests zusammen korrigieren)
- ADR-Referenz auf max 21 primaere Tests (7 Axiome x 3 Predictions) vorhanden
- Acceptance Criteria messbar: q_values berechnet, Markdown-Report, Unit-Test

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_031_PROXY_PLAN_20251230_220154.md

## [2025-12-30 22:08:54] TASK_031 - EXECUTOR (ki2)

### Summary
- Created scripts/apply_fdr_correction.py - scans all results/*.json for p_values recursively
- Handles heterogeneous p_value structures (nested keys like by_type.typ_6.p_value)
- Uses kenobase.analysis.null_models.benjamini_hochberg_fdr() for FDR correction
- Extracted 8105 p-values from 48 files, 36 unique hypotheses
- FDR correction reduced significant tests from 3539 (p<0.05) to 421 (q<0.05)
- Generated results/fdr_corrected_hypotheses.json (3.0 MB) and Markdown report
- Created tests/unit/test_fdr_correction.py with 15 passing tests
- Repro command verified: python scripts/apply_fdr_correction.py

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_031_EXECUTOR_20251230_220354.md



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
- scripts/apply_fdr_correction.py
- tests/unit/test_fdr_correction.py
- results/fdr_corrected_hypotheses.json
- results/fdr_correction_report.md

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
- Created scripts/apply_fdr_correction.py - scans all results/*.json for p_values recursively
- Handles heterogeneous p_value structures (nested keys like by_type.typ_6.p_value)
- Uses kenobase.analysis.null_models.benjamini_hochberg_fdr() for FDR correction
- Extracted 8105 p-values from 48 files, 36 unique hypotheses
- FDR correction reduced significant tests from 3539 (p<0.05) to 421 (q<0.05)
- Generated results/fdr_corrected_hypotheses.json (3.0 MB) and Markdown report
- Created tests/unit/test_fdr_correction.py with 15 passing tests
- Repro command verified: python scripts/apply_fdr_correction.py

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_031_EXECUTOR_20251230_220354.md

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
task: TASK_031
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_031_PROXY_IMPL_20251230_220854.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
