AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Gerade/Ungerade Ratio
TASK-ID: TRANS-003
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 05:12:42] TRANS-003 - ARCHITECT (ki1)

### Summary
- TRANS-003 Gerade/Ungerade Ratio Analyse geplant
- Neues Modul kenobase/analysis/parity_ratio.py zu erstellen
- Analog zu decade_distribution.py Struktur (dataclass + Chi-Quadrat)
- Binomial-Test gegen 50/50 Erwartung
- Unit-Tests in tests/unit/test_parity_ratio.py
- Analyse-Script scripts/analyze_parity.py
- Keine Cross-Lotterie-Kopplung in Scope

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TRANS-003_ARCHITECT_20251230_050942.md

## [2025-12-30 05:14:42] TRANS-003 - PROXY_PLAN (ki0)

### Summary
- Plan folgt decade_distribution.py Template - bewaehrt und konsistent
- Binomial-Test gegen 50/50 ist statistisch korrekt fuer Paritaets-Analyse
- Working Set vollstaendig fuer Executor (Template + Init + Tests)
- Keine Cross-Lotterie-Kopplung in Scope - korrekt begrenzt
- Repro-Kommando klar definiert
- Integration in __init__.py explizit genannt
- Keine globalen Thresholds noetig (50/50 ist mathematisch fix)
- Chi-Quadrat + Binomial-Test Kombination statistisch sinnvoll

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TRANS-003_PROXY_PLAN_20251230_051242.md

## [2025-12-30 05:18:42] TRANS-003 - EXECUTOR (ki2)

### Summary
- Created parity_ratio.py module following decade_distribution.py template
- Implemented ParityBin and ParityRatioResult dataclasses
- Added is_even(), count_parity(), analyze_parity_ratio() functions
- Chi-Quadrat + Binomial-Test gegen 50/50 Erwartung implementiert
- Created 17 unit tests in test_parity_ratio.py - ALL PASSED
- Added analyze_parity.py CLI script with JSON output
- Integrated into analysis/__init__.py with all exports

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TRANS-003_EXECUTOR_20251230_051442.md



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
- kenobase/analysis/parity_ratio.py
- kenobase/analysis/__init__.py
- tests/unit/test_parity_ratio.py
- scripts/analyze_parity.py

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
- Created parity_ratio.py module following decade_distribution.py template
- Implemented ParityBin and ParityRatioResult dataclasses
- Added is_even(), count_parity(), analyze_parity_ratio() functions
- Chi-Quadrat + Binomial-Test gegen 50/50 Erwartung implementiert
- Created 17 unit tests in test_parity_ratio.py - ALL PASSED
- Added analyze_parity.py CLI script with JSON output
- Integrated into analysis/__init__.py with all exports

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TRANS-003_EXECUTOR_20251230_051442.md

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
task: TRANS-003
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TRANS-003_PROXY_IMPL_20251230_051842.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
