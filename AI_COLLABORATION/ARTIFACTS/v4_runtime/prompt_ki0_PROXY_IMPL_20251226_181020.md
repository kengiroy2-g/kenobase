AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P1-03: Data Loader refactoren
TASK-ID: phase1_task03_data_loader
PRIORITY: P0
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-26 18:04:20] phase1_task03_data_loader - PROXY_PLAN (ki0)

### Summary
- KENO Format verifiziert: 22 Spalten, Semikolon, Zahlen separiert (Keno_Z1-Z20)
- EuroJackpot KRITISCH KORRIGIERT: Zahlen in Spalten 1-7 nach Datum, NICHT String
- EuroJackpot Spalten: Datum;Z1;Z2;Z3;Z4;Z5;EZ1;EZ2;Spieleinsatz;...
- Lotto Alt (ab-1955): Komma-Delimiter, 7 Spalten (Datum,z1-z6), einfachstes Format
- Lotto Neu (ab-2018): Semikolon, Spalte "Gewinnzahlen" als String braucht Split
- Plan passt zu config.py LegacyConfig (csv_delimiter, csv_date_format)
- Auto-Format-Erkennung via Header-Inspektion ist korrekt konzipiert
- DrawResult Pydantic-Model mit date/numbers/bonus/game_type sinnvoll

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase1_task03_data_loader_PROXY_PLAN_20251226_180220.md

## [2025-12-26 18:10:20] phase1_task03_data_loader - EXECUTOR (ki2)

### Summary
- DataLoader class with auto-format detection implemented
- DrawResult Pydantic model with date/numbers/bonus/game_type/metadata
- Four parser methods for KENO/EuroJackpot/Lotto-Old/Lotto-New formats
- DataFrame conversion via to_dataframe() and load_as_dataframe()
- 33 unit tests all passing (0.47s)
- 51 total tests in suite all passing
- Real data integration verified on all 4 CSV files
- Handoff: AI_COLLABORATION/HANDOFFS/ki2_phase1_task03_data_loader_EXECUTOR_20251226_180420.md

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_phase1_task03_data_loader_EXECUTOR_20251226_180420.md



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
- AI_COLLABORATION/HANDOFFS/ki1_phase1_task03_data_loader_ARCHITECT_20251226_174920.mdKeno_GPTs/Daten/Lotto_Archiv_ab-1955.csv (erste 5 Zeilen)Keno_GPTs/Daten/lotto_Stats_ab-2018.csv (erste 5 Zeilen)kenobase/core/config.py (bereits gelesen)AI_COLLABORATION/HANDOFFS/ki1_phase1_task03_data_loader_ARCHITECT_20251226_175520.mdkenobase/core/data_loader.py (NEW)kenobase/core/__init__.py (MODIFIED)tests/unit/test_data_loader.py (NEW)tests/fixtures/keno_sample.csv (NEW)tests/fixtures/eurojackpot_sample.csv (NEW)tests/fixtures/lotto_old_sample.csv (NEW)tests/fixtures/lotto_new_sample.csv (NEW)

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
- DataLoader class with auto-format detection implemented
- DrawResult Pydantic model with date/numbers/bonus/game_type/metadata
- Four parser methods for KENO/EuroJackpot/Lotto-Old/Lotto-New formats
- DataFrame conversion via to_dataframe() and load_as_dataframe()
- 33 unit tests all passing (0.47s)
- 51 total tests in suite all passing
- Real data integration verified on all 4 CSV files
- Handoff: AI_COLLABORATION/HANDOFFS/ki2_phase1_task03_data_loader_EXECUTOR_20251226_180420.md

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_phase1_task03_data_loader_EXECUTOR_20251226_180420.md

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
task: phase1_task03_data_loader
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_phase1_task03_data_loader_PROXY_IMPL_20251226_181020.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
