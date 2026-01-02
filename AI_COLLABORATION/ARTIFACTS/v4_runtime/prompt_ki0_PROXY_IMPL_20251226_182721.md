AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P1-04: Test-Infrastruktur einrichten
TASK-ID: phase1_task04_test_setup
PRIORITY: P1
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-26 18:23:21] phase1_task04_test_setup - ARCHITECT (ki1)

### Summary
- Test-Infrastruktur bereits zu 90% vorhanden
- pytest.ini existiert mit korrekten Einstellungen
- tests/ Struktur: unit/, integration/, fixtures/
- 2 Testdateien vorhanden: test_config.py (31 Tests), test_data_loader.py (27 Tests)
- 4 Fixture-Dateien vorhanden (keno, eurojackpot, lotto_old, lotto_new)
- FEHLT: conftest.py fuer gemeinsame Fixtures
- FEHLT: pytest-cov Konfiguration in pytest.ini

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_phase1_task04_test_setup_ARCHITECT_20251226_182121.md

## [2025-12-26 18:25:21] phase1_task04_test_setup - PROXY_PLAN (ki0)

### Summary
- Plan ist klar und vollstaendig: 3 Deliverables identifiziert
- conftest.py fehlt tatsaechlich (Glob bestaetigt: keine conftest.py im Repo)
- pytest.ini existiert mit korrekten Markern, --strict-markers fehlt
- 4 Fixture-Dateien vorhanden in tests/fixtures/
- Plan ist minimal und fokussiert - keine Ueberengineering
- Coverage-Config als Optional markiert - akzeptabel

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase1_task04_test_setup_PROXY_PLAN_20251226_182321.md

## [2025-12-26 18:27:21] phase1_task04_test_setup - EXECUTOR (ki2)

### Summary
- Created tests/conftest.py with 7 shared fixtures
- Added --strict-markers to pytest.ini addopts
- Fixtures: fixtures_dir, project_root, sample_numbers, sample_lotto_numbers, sample_eurojackpot_numbers, temp_data_dir, default_config_path
- Verified pytest collects 51 tests successfully
- Test run confirmed fixtures work (test_detect_keno_format passed)
- Coverage config not added (marked optional in plan)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_phase1_task04_test_setup_EXECUTOR_20251226_182521.md



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
- tests/conftest.py
- pytest.ini

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
- Created tests/conftest.py with 7 shared fixtures
- Added --strict-markers to pytest.ini addopts
- Fixtures: fixtures_dir, project_root, sample_numbers, sample_lotto_numbers, sample_eurojackpot_numbers, temp_data_dir, default_config_path
- Verified pytest collects 51 tests successfully
- Test run confirmed fixtures work (test_detect_keno_format passed)
- Coverage config not added (marked optional in plan)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_phase1_task04_test_setup_EXECUTOR_20251226_182521.md

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
task: phase1_task04_test_setup
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_phase1_task04_test_setup_PROXY_IMPL_20251226_182721.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
