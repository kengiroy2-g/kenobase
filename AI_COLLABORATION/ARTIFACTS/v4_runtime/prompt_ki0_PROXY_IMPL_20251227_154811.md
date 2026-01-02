AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Korrelations-Analysen
TASK-ID: ISSUE-004
PRIORITY: MEDIUM
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 15:43:11] ISSUE-004 - PROXY_PLAN (ki0)

### Summary
- Pattern-Bug-Fix verifiziert: parallele if-Statements korrekt (pattern.py:118-131)
- 16 Unit-Tests vorhanden, mathematisch korrekt (C(n,k) Formeln)
- Plan hat 3 Schritte mit klaren Deliverables
- Granularitaet per-pattern ist korrekt fuer diesen Use-Case
- Keine globalen Thresholds (BUG-001 vermieden)
- Integration mit DataLoader/Config implizit (Executor muss beachten)
- Metriken (Precision/Recall/Lift) in Acceptance Criteria
- Aufwand 4h realistisch fuer Scope

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_ISSUE-004_PROXY_PLAN_20251227_154011.md

## [2025-12-27 15:48:11] ISSUE-004 - EXECUTOR (ki2)

### Summary
- Backtest-Script erstellt: Walk-Forward Validierung mit Precision/Recall/Lift
- Pattern.py erweitert: calculate_pattern_lift(), calculate_feature_importance(), get_significant_patterns()
- ADR-002 dokumentiert: Bug-Fix elif->if mit Validierungsmatrix
- Unit-Tests: 16/16 PASSED (test_pattern.py)
- Backtest ausgefuehrt: 218 Folds, 2237 KENO-Ziehungen
- Ergebnis: Patterns zeigen Lift ~1.0 (entspricht Zufall, Null-Hypothese nicht widerlegt)
- Acceptance Criteria: 2/3 passed (Lift nicht konsistent >1, was statistisch korrekt ist)
- Alle Deliverables gemaess Plan implementiert

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_ISSUE-004_EXECUTOR_20251227_154311.md



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
- scripts/backtest_patterns.py (NEU, 450 LOC)
- kenobase/analysis/pattern.py (ERWEITERUNG, +150 LOC)
- docs/adr/ADR-002-PATTERN-BUGFIX.md (NEU)
- AI_COLLABORATION/ARTIFACTS/pattern_backtest_test.json (OUTPUT)

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
- Backtest-Script erstellt: Walk-Forward Validierung mit Precision/Recall/Lift
- Pattern.py erweitert: calculate_pattern_lift(), calculate_feature_importance(), get_significant_patterns()
- ADR-002 dokumentiert: Bug-Fix elif->if mit Validierungsmatrix
- Unit-Tests: 16/16 PASSED (test_pattern.py)
- Backtest ausgefuehrt: 218 Folds, 2237 KENO-Ziehungen
- Ergebnis: Patterns zeigen Lift ~1.0 (entspricht Zufall, Null-Hypothese nicht widerlegt)
- Acceptance Criteria: 2/3 passed (Lift nicht konsistent >1, was statistisch korrekt ist)
- Alle Deliverables gemaess Plan implementiert

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_ISSUE-004_EXECUTOR_20251227_154311.md

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
task: ISSUE-004
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_ISSUE-004_PROXY_IMPL_20251227_154811.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
