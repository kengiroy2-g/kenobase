AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: EuroJackpot Model Transfer
TASK-ID: TASK-P08
PRIORITY: MEDIUM
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 04:55:24] TASK-P08 - PROXY_PLAN (ki0)

### Summary
- APPROVED: Plan is sound, minimal changes needed
- VERIFIED: EuroJackpot CSV exists (data/raw/eurojackpot/eurojackpot_archiv_bereinigt.csv, 15963 bytes)
- VERIFIED: CLI --game flag already implemented (analyze.py:177-188)
- VERIFIED: Config has games.eurojackpot section with correct thresholds (lines 129-137)
- CRITICAL FIX NEEDED: sum_windows.expected_mean hardcoded to 710 in config.py:105
- SOLUTION: Compute expected_mean dynamically from game config in runner.py
- Integration test with EuroJackpot data will validate end-to-end

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P08_PROXY_PLAN_20251228_045323.md

## [2025-12-28 04:58:24] TASK-P08 - EXECUTOR (ki2)

### Summary
- Added GameConfig.get_expected_sum_mean() method (config.py:60-69)
- Modified _run_sum_analysis() to compute expected_mean dynamically (runner.py:404-411)
- Updated _get_config_snapshot() to include game info and dynamic expected_mean (runner.py:458-488)
- KENO: E[sum] = 20 * (1+70)/2 = 710.0 (verified)
- EuroJackpot: E[sum] = 5 * (1+50)/2 = 127.5 (verified)
- Lotto: E[sum] = 6 * (1+49)/2 = 150.0 (verified)
- Integration test passed: 526 EuroJackpot draws, actual mean=126.1 (1.1% deviation)
- CLI --game flag already works: analyze.py -g eurojackpot analyze -d data/...

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-P08_EXECUTOR_20251228_045524.md



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
- kenobase/core/config.py
- kenobase/pipeline/runner.py

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
- Added GameConfig.get_expected_sum_mean() method (config.py:60-69)
- Modified _run_sum_analysis() to compute expected_mean dynamically (runner.py:404-411)
- Updated _get_config_snapshot() to include game info and dynamic expected_mean (runner.py:458-488)
- KENO: E[sum] = 20 * (1+70)/2 = 710.0 (verified)
- EuroJackpot: E[sum] = 5 * (1+50)/2 = 127.5 (verified)
- Lotto: E[sum] = 6 * (1+49)/2 = 150.0 (verified)
- Integration test passed: 526 EuroJackpot draws, actual mean=126.1 (1.1% deviation)
- CLI --game flag already works: analyze.py -g eurojackpot analyze -d data/...

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-P08_EXECUTOR_20251228_045524.md

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
task: TASK-P08
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK-P08_PROXY_IMPL_20251228_045824.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
