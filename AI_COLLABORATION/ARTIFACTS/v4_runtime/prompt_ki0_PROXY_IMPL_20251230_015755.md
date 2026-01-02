AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Zahlenraum-Normalisierung
TASK-ID: DATA-002
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 01:53:55] DATA-002 - PROXY_PLAN (ki0)

### Summary
- Plan is mechanically complete with clear functions (normalize_number, denormalize_number, normalize_draw, normalize_numbers)
- DrawResult model verified at data_loader.py:47-80 with game_type field
- Game ranges verified at default.yaml:131-158 (KENO 1-70, EuroJackpot 1-50, Lotto 1-49)
- Percentile-based normalization to [0.0, 1.0] is appropriate for cross-game comparison
- INTEGRATION NOTE: cross_lottery_coupling.py uses KENO_MAX_NUMBER constant - future refactoring opportunity
- Normalization is helper-only (pure transform), no state dependency
- Plan addresses per-game granularity correctly (not global threshold)
- Test strategy clear: pytest tests/unit/test_normalizer.py -v

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DATA-002_PROXY_PLAN_20251230_015154.md

## [2025-12-30 01:57:55] DATA-002 - EXECUTOR (ki2)

### Summary
- Created kenobase/core/normalizer.py with Zahlenraum-Normalisierung functions
- Implemented normalize_number, denormalize_number for single values (n-min)/(max-min)
- Implemented normalize_numbers, denormalize_numbers for batch operations
- Implemented normalize_draw, normalize_draws for DrawResult integration
- Implemented cross_game_distance for cross-lottery comparison (MAE of normalized values)
- Game ranges from config: KENO 1-70, Lotto 1-49, EuroJackpot 1-50
- Bonus handling: EuroZahlen 1-12, Superzahl 0-9, KENO Plus5 skipped (5-digit code)
- Added 43 unit tests, all passing

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_DATA-002_EXECUTOR_20251230_015355.md



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
- kenobase/core/normalizer.py
- kenobase/core/__init__.py
- tests/unit/test_normalizer.py

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
- Created kenobase/core/normalizer.py with Zahlenraum-Normalisierung functions
- Implemented normalize_number, denormalize_number for single values (n-min)/(max-min)
- Implemented normalize_numbers, denormalize_numbers for batch operations
- Implemented normalize_draw, normalize_draws for DrawResult integration
- Implemented cross_game_distance for cross-lottery comparison (MAE of normalized values)
- Game ranges from config: KENO 1-70, Lotto 1-49, EuroJackpot 1-50
- Bonus handling: EuroZahlen 1-12, Superzahl 0-9, KENO Plus5 skipped (5-digit code)
- Added 43 unit tests, all passing

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_DATA-002_EXECUTOR_20251230_015355.md

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
task: DATA-002
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_DATA-002_PROXY_IMPL_20251230_015755.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
