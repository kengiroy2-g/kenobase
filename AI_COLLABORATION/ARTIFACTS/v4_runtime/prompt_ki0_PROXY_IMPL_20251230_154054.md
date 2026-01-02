AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Zahlenfrequenz pro Jahr
TASK-ID: TASK_007
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 15:35:53] TASK_007 - ARCHITECT (ki1)

### Summary
- Analyse: frequency.py existiert bereits mit calculate_frequency() (Zeilen 71-138)
- Anforderung: Neue Funktion calculate_frequency_per_year() fehlt noch
- DrawResult hat date Attribut (datetime), Jahr via draw.date.year extrahierbar
- Datensatz hat Datum im Format DD.MM.YYYY (Spalte Datum)
- KENO-Daten ab 2022 und ab 2018 verfuegbar
- Neuer Script: scripts/analyze_frequency_per_year.py zur Ausgabe
- Unit-Test: tests/unit/test_frequency_per_year.py

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_007_ARCHITECT_20251230_153253.md

## [2025-12-30 15:37:54] TASK_007 - PROXY_PLAN (ki0)

### Summary
- Plan ist vollstaendig und klar strukturiert
- frequency.py existiert (389 Zeilen), calculate_frequency() als Vorlage (Zeilen 71-138)
- Neue Funktion calculate_frequency_per_year() passt zum bestehenden Pattern
- Granularitaet per-year korrekt (kein BUG-001 globaler Threshold)
- Alle betroffenen Dateien explizit genannt (frequency.py, Script, Test, Output)
- Acceptance Criteria messbar (AC1-AC5)
- Repro Command definiert: python scripts/analyze_frequency_per_year.py
- Integration mit DrawResult.date.year technisch korrekt

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_007_PROXY_PLAN_20251230_153554.md

## [2025-12-30 15:40:54] TASK_007 - EXECUTOR (ki2)

### Summary
- Added YearlyFrequencyResult dataclass to frequency.py (lines 379-395)
- Implemented calculate_frequency_per_year() function (lines 398-483)
- Created CLI script scripts/analyze_frequency_per_year.py with argparse
- Created unit tests tests/unit/test_frequency_per_year.py (11 tests, all pass)
- Generated JSON artifact results/frequency_per_year.json
- AC1-AC5 all verified (see Verification section)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_007_EXECUTOR_20251230_153754.md



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
- scripts/analyze_frequency_per_year.py
- tests/unit/test_frequency_per_year.py
- results/frequency_per_year.json

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
- Added YearlyFrequencyResult dataclass to frequency.py (lines 379-395)
- Implemented calculate_frequency_per_year() function (lines 398-483)
- Created CLI script scripts/analyze_frequency_per_year.py with argparse
- Created unit tests tests/unit/test_frequency_per_year.py (11 tests, all pass)
- Generated JSON artifact results/frequency_per_year.json
- AC1-AC5 all verified (see Verification section)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_007_EXECUTOR_20251230_153754.md

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
task: TASK_007
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_007_PROXY_IMPL_20251230_154054.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
