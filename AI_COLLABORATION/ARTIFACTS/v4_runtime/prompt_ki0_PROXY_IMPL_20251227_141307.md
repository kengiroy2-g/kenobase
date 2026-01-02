AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Kern-Hypothesen Validierung
TASK-ID: HYP-002
PRIORITY: HIGH
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 14:09:07] HYP-002 - PROXY_PLAN (ki0)

### Summary
- Plan ist vollstaendig und klar strukturiert mit 4 Haupt-Schritten
- Existierende Implementierung verifiziert (validate_hypotheses.py:294-389)
- Datei 10-9_KGDaten_gefiltert.csv existiert im Repo
- Acceptance Criteria sind messbar (Chi-Quadrat Tests, JSON-Output)
- Keine globalen Thresholds wo game-spezifische noetig (BUG-001 vermieden)
- Neues Modul calendar_features.py ist isoliert (keine versteckte Kopplung)
- WORKING_SET_REQUEST ist korrekt und vollstaendig
- holidays Package korrekt als optional markiert (Fallback vorhanden)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-002_PROXY_PLAN_20251227_140707.md

## [2025-12-27 14:13:07] HYP-002 - EXECUTOR (ki2)

### Summary
- Created calendar_features.py with CalendarFeatures, CalendarAnalysisResult dataclasses
- Implemented extract_calendar_features() for weekday, month, holiday, payday extraction
- Implemented analyze_calendar_correlation() with Chi-Square tests for weekday/month
- Implemented predict_next_gk1() Poisson-based prediction model with 80% CI
- Extended validate_hyp002_jackpot_zyklen() with calendar analysis and prediction
- Updated __init__.py to export new calendar_features module
- Generated hyp002_jackpot_cycles.json with full extended analysis
- All tests passed: N=20 events, 17 intervals, mean=43.3 days, KS p=0.588 (RANDOM)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HYP-002_EXECUTOR_20251227_140907.md



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
- kenobase/analysis/calendar_features.py (NEW)
- kenobase/analysis/__init__.py (MODIFIED)
- scripts/validate_hypotheses.py (MODIFIED)
- data/results/hyp002_jackpot_cycles.json (NEW)

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
- Created calendar_features.py with CalendarFeatures, CalendarAnalysisResult dataclasses
- Implemented extract_calendar_features() for weekday, month, holiday, payday extraction
- Implemented analyze_calendar_correlation() with Chi-Square tests for weekday/month
- Implemented predict_next_gk1() Poisson-based prediction model with 80% CI
- Extended validate_hyp002_jackpot_zyklen() with calendar analysis and prediction
- Updated __init__.py to export new calendar_features module
- Generated hyp002_jackpot_cycles.json with full extended analysis
- All tests passed: N=20 events, 17 intervals, mean=43.3 days, KS p=0.588 (RANDOM)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HYP-002_EXECUTOR_20251227_140907.md

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
task: HYP-002
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_HYP-002_PROXY_IMPL_20251227_141307.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
