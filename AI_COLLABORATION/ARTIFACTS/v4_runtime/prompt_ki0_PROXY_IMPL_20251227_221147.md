AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Core Stable Numbers identifizieren
TASK-ID: TASK-H02
PRIORITY: HIGH
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 22:07:47] TASK-H02 - PROXY_PLAN (ki0)

### Summary
- Plan ist konzeptionell solide: Core Stable Numbers via Rolling Frequency + Model Law A
- Stabilitaetsformel korrekt: stability_score = 1 - (std/mean) (per-number granularity)
- Config-Integration nutzt existierenden physics.stability_threshold (0.90) - kein neuer globaler Wert noetig
- WORKING_SET_REQUEST vollstaendig: frequency.py, __init__.py, analyze.py, default.yaml, data_loader.py
- CLI-Integration als neuer Click-Command (nicht --flag) empfohlen - konsistent mit bestehendem Pattern
- Keine BUG-001 Verletzung: nutzt game-specific config via cfg.get_active_game()
- Keine BUG-003 Verletzung: kenobase/analysis/__init__.py muss erweitert werden (explizit genannt)
- Output-Pfad results/stable_numbers_keno.json ist reproduzierbar

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-H02_PROXY_PLAN_20251227_220547.md

## [2025-12-27 22:11:47] TASK-H02 - EXECUTOR (ki2)

### Summary
- Created kenobase/analysis/stable_numbers.py with Model Law A implementation
- StableNumberResult dataclass with number, stability_score, is_stable, avg_frequency, std_frequency
- Stability formula: stability_score = 1 - (std / mean), clamped to [0, 1]
- analyze_stable_numbers() uses calculate_rolling_frequency from frequency.py
- Config integration: uses physics.stability_threshold (default 0.90)
- CLI: new `stable-numbers` command with --window, --threshold, --all options
- Unit tests: 19 tests, all passing
- Exports added to kenobase/analysis/__init__.py

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-H02_EXECUTOR_20251227_220747.md



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
- kenobase/analysis/stable_numbers.py (NEW)
- kenobase/analysis/__init__.py (MODIFIED)
- scripts/analyze.py (MODIFIED)
- tests/unit/test_stable_numbers.py (NEW)

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
- Created kenobase/analysis/stable_numbers.py with Model Law A implementation
- StableNumberResult dataclass with number, stability_score, is_stable, avg_frequency, std_frequency
- Stability formula: stability_score = 1 - (std / mean), clamped to [0, 1]
- analyze_stable_numbers() uses calculate_rolling_frequency from frequency.py
- Config integration: uses physics.stability_threshold (default 0.90)
- CLI: new `stable-numbers` command with --window, --threshold, --all options
- Unit tests: 19 tests, all passing
- Exports added to kenobase/analysis/__init__.py

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-H02_EXECUTOR_20251227_220747.md

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
task: TASK-H02
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK-H02_PROXY_IMPL_20251227_221147.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
