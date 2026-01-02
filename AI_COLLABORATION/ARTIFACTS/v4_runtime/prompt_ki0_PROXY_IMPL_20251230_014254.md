AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Zeitachsen-Alignment
TASK-ID: DATA-001
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 01:31:54] DATA-001 - PROXY_PLAN (ki0)

### Summary
- Plan definition: "Multi-Game Timeline (daily grid) bauen" mandates new core module
- TimelineGrid approach (011854) matches plan intent - APPROVED
- Existing _align_source_to_target() serves different purpose (event-to-event)
- Daily grid enables COUPLE-001/002 (Transfer Entropy, Cross-Spectrum) downstream
- Draw frequencies correctly identified: KENO=7/wk, Lotto=2/wk, EJ=2/wk
- Forward-fill + NaN strategy appropriate for different draw schedules
- Parquet export enables efficient downstream analysis
- Estimate 6h reasonable for core module + tests + CLI

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DATA-001_PROXY_PLAN_20251230_012954.md

## [2025-12-30 01:42:54] DATA-001 - EXECUTOR (ki2)

### Summary
- Implemented TimelineGrid class for daily grid alignment of multi-game data
- Supports KENO (daily), Lotto (Wed+Sat), EuroJackpot (Tue+Fri) draw schedules
- Added NaN and forward-fill strategies for non-draw days
- Created to_dataframe() and to_numbers_matrix() export methods
- Added parquet export with tuple/matrix modes
- Fixed data_loader for LOTTO_ab_2022_bereinigt.csv (L1-L6 format)
- Fixed data_loader for EJ_ab_2022_bereinigt.csv (E1-E5/Euro1-2 format)
- 24 tests passing, 63 total with data_loader tests

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_DATA-001_EXECUTOR_20251230_013154.md



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
- kenobase/core/timeline.py (NEW - 378 lines)
- tests/unit/test_timeline.py (NEW - 401 lines)
- scripts/build_timeline_grid.py (NEW - 125 lines)
- kenobase/core/data_loader.py (MODIFIED - added Lotto bereinigt + EJ E-format parsers)
- data/processed/timeline_grid.parquet (NEW OUTPUT - 115KB)
- results/timeline_grid_summary.json (NEW OUTPUT)

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
- Implemented TimelineGrid class for daily grid alignment of multi-game data
- Supports KENO (daily), Lotto (Wed+Sat), EuroJackpot (Tue+Fri) draw schedules
- Added NaN and forward-fill strategies for non-draw days
- Created to_dataframe() and to_numbers_matrix() export methods
- Added parquet export with tuple/matrix modes
- Fixed data_loader for LOTTO_ab_2022_bereinigt.csv (L1-L6 format)
- Fixed data_loader for EJ_ab_2022_bereinigt.csv (E1-E5/Euro1-2 format)
- 24 tests passing, 63 total with data_loader tests

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_DATA-001_EXECUTOR_20251230_013154.md

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
task: DATA-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_DATA-001_PROXY_IMPL_20251230_014254.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
