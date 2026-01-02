AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Scraping in master_update.py implementieren
TASK-ID: ISSUE-001
PRIORITY: MEDIUM
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 17:28:16] ISSUE-001 - PROXY_PLAN (ki0)

### Summary
- ARCHITECT Plan ist vollstaendig und umsetzbar
- TODO-Stub verifiziert: master_update.py:217-219 (run_scrape returns False)
- Referenz-Scraper verifiziert: all_code/00_web_scrapping_V4_+_Datum.py (119 Zeilen, Selenium+BS4)
- MISSING DEPENDENCIES BESTAETIGT: selenium, beautifulsoup4 NICHT in requirements.txt
- MISSING CONFIG BESTAETIGT: Kein scraper-Abschnitt in default.yaml (chromedriver_path)
- ACCEPTANCE CRITERIA KONFLIKT akzeptabel: Backlog sagt update_data.py, master_update.py existiert bereits
- Hardcoded chromedriver-Pfad (Zeile 76) muss konfigurierbar werden - Plan addressiert dies
- 7 Implementierungsschritte sind klar definiert mit Deliverables

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_ISSUE-001_PROXY_PLAN_20251227_172516.md

## [2025-12-27 17:32:16] ISSUE-001 - EXECUTOR (ki2)

### Summary
- Added selenium>=4.15.0 and beautifulsoup4>=4.12.0 to requirements.txt
- Added scraper config section to default.yaml (chromedriver_path, headless, timeouts, URLs)
- Implemented KenoScraper class with configurable settings from YAML
- Replaced TODO stub in run_scrape() with full implementation
- Scraper uses Selenium+BS4 pattern from reference (all_code/00_web_scrapping_V4_+_Datum.py)
- Output saved to data/scraped/{game}_scraped_{year}.csv with auto-merge
- All syntax validated (Python + YAML), CLI tested

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_ISSUE-001_EXECUTOR_20251227_172816.md



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
- requirements.txt
- config/default.yaml
- scripts/master_update.py
- all_code/00_web_scrapping_V4_+_Datum.py

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
- Added selenium>=4.15.0 and beautifulsoup4>=4.12.0 to requirements.txt
- Added scraper config section to default.yaml (chromedriver_path, headless, timeouts, URLs)
- Implemented KenoScraper class with configurable settings from YAML
- Replaced TODO stub in run_scrape() with full implementation
- Scraper uses Selenium+BS4 pattern from reference (all_code/00_web_scrapping_V4_+_Datum.py)
- Output saved to data/scraped/{game}_scraped_{year}.csv with auto-merge
- All syntax validated (Python + YAML), CLI tested

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_ISSUE-001_EXECUTOR_20251227_172816.md

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
task: ISSUE-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_ISSUE-001_PROXY_IMPL_20251227_173216.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
