AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P2-04: Haeufigkeitsanalyse implementieren
TASK-ID: phase2_task04_frequency_analysis
PRIORITY: P1
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-26 19:39:06] phase2_task04_frequency_analysis - PROXY_PLAN (ki0)

### Summary
- Plan vollstaendig mit 6 Funktionen und 2 Dataklassen
- Integration mit DrawResult aus data_loader.py verifiziert
- Config-Thresholds in default.yaml vorhanden (min: 0.05, max: 0.20, windows)
- kenobase/analysis/__init__.py existiert und ist bereit fuer Exports
- 10+ Tests spezifiziert mit 80% Coverage-Ziel
- Keine RED FLAGS erkannt - keine globalen Werte wo team-spezifische noetig
- Granularitaet per-number ist korrekt fuer Haeufigkeitsanalyse
- Risiken angemessen dokumentiert (leere Listen, Division by Zero)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase2_task04_frequency_analysis_PROXY_PLAN_20251226_193606.md

## [2025-12-26 19:43:06] phase2_task04_frequency_analysis - EXECUTOR (ki2)

### Summary
- Implemented frequency.py with 2 dataclasses (FrequencyResult, PairFrequencyResult)
- 6 main functions: calculate_frequency, calculate_pair_frequency, classify_numbers, classify_pairs, calculate_rolling_frequency
- 2 convenience functions: get_hot_numbers, get_cold_numbers
- Integration with DrawResult from data_loader.py verified
- 29 unit tests passing with 99% coverage
- Updated kenobase/analysis/__init__.py with exports
- All edge cases handled (empty lists, division by zero, invalid params)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_phase2_task04_frequency_analysis_EXECUTOR_20251226_193906.md



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
- kenobase/analysis/frequency.py
- kenobase/analysis/__init__.py
- tests/unit/test_frequency.py

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
- Implemented frequency.py with 2 dataclasses (FrequencyResult, PairFrequencyResult)
- 6 main functions: calculate_frequency, calculate_pair_frequency, classify_numbers, classify_pairs, calculate_rolling_frequency
- 2 convenience functions: get_hot_numbers, get_cold_numbers
- Integration with DrawResult from data_loader.py verified
- 29 unit tests passing with 99% coverage
- Updated kenobase/analysis/__init__.py with exports
- All edge cases handled (empty lists, division by zero, invalid params)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_phase2_task04_frequency_analysis_EXECUTOR_20251226_193906.md

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
task: phase2_task04_frequency_analysis
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_phase2_task04_frequency_analysis_PROXY_IMPL_20251226_194306.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
