AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Scraping in master_update.py implementieren
TASK-ID: ISSUE-001
PRIORITY: MEDIUM
PHASE: PROXY_PLAN

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 17:22:16] ISSUE-001 - PROXY_PLAN (ki0)

### Summary
- FALSCHE BEHAUPTUNG: selenium/beautifulsoup4 NICHT in requirements.txt
- FEHLENDE CONFIG: Kein scraper-Abschnitt in default.yaml (chromedriver-Pfad)
- ACCEPTANCE CRITERIA KONFLIKT: Backlog fordert update_data.py, Handoff nutzt master_update.py
- Hardcoded chromedriver-Pfad (Zeile 76) in Referenz-Code erkannt aber Config-Loesung fehlt
- WORKING_SET unvollstaendig: requirements.txt muss geaendert werden
- Repro-Command nicht verifizierbar (Script existiert, aber Scraping TODO)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_ISSUE-001_PROXY_PLAN_20251227_171916.md

## [2025-12-27 17:25:16] ISSUE-001 - ARCHITECT (ki1)

### Summary
- Verified TODO stub at master_update.py:217-219 (run_scrape returns False)
- Reference scraper at all_code/00_web_scrapping_V4_+_Datum.py (Selenium+BS4, 119 lines)
- MISSING from requirements.txt: selenium, beautifulsoup4 (PROXY was correct)
- MISSING from default.yaml: scraper config section (chromedriver_path, headless mode)
- Acceptance criteria uses update_data.py but ISSUE-007 created master_update.py - recommend wrapper
- 7 implementation steps defined with file-level changes
- Estimated effort: 4-6 hours (matches backlog)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_ISSUE-001_ARCHITECT_20251227_172216.md



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
AUFGABE: Pruefe den Plan vom ARCHITECT - NICHT nur mechanisch, sondern konzeptionell.

PFLICHTLEKTUERE (vor Review lesen):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Dein vollstaendiges Profil mit Known Bugs
2. AI_COLLABORATION/SYSTEM_STATUS.json - Aktueller Projektstatus
3. CLAUDE.md - Projektkontext (bei Architektur-Fragen)

EFFIZIENZ-REGELN:
- Arbeite mit VORHERIGER OUTPUT + TASK NOTES + Profil-Wissen
- Maximal 3-4 gezielte Reads (Profil, Status, relevante Dateien)
- Keine breiten Repo-Scans

VORHERIGER OUTPUT (kurz, no logs):
- Verified TODO stub at master_update.py:217-219 (run_scrape returns False)
- Reference scraper at all_code/00_web_scrapping_V4_+_Datum.py (Selenium+BS4, 119 lines)
- MISSING from requirements.txt: selenium, beautifulsoup4 (PROXY was correct)
- MISSING from default.yaml: scraper config section (chromedriver_path, headless mode)
- Acceptance criteria uses update_data.py but ISSUE-007 created master_update.py - recommend wrapper
- 7 implementation steps defined with file-level changes
- Estimated effort: 4-6 hours (matches backlog)

FULL HANDOFF (nur bei Bedarf oeffnen):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_ISSUE-001_ARCHITECT_20251227_172216.md

PRUEFKRITERIEN (4 Dimensionen):
1. MECHANISCH: Plan vollstaendig? Schritte klar? Acceptance Criteria messbar?
2. ARCHITEKTUR: Passt zu ADRs? Keine Widersprueche?
3. INTEGRATION: Werden alle betroffenen Dateien genannt? (siehe Known Integration Points im Profil)
4. KONZEPTIONELL: Globale Werte wo spezifische noetig? Known Bugs vermieden?

RED FLAGS (sofort REJECTED):
- Globale Thresholds in team-spezifischem System (BUG-001)
- Feature ohne Orchestrator-Integration (BUG-003)
- Cross-File Aenderung ohne alle Dateien (Known Integration Points)

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: APPROVED
task: ISSUE-001
role: PROXY
phase: PROXY_PLAN
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

# Proxy Review

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki0_ISSUE-001_PROXY_PLAN_20251227_172516.md
- YAML Frontmatter mit status:
  - APPROVED: Plan ist gut, weiter zu Executor
  - REJECTED: Bug gefunden, zurueck zu Architect
  - ESCALATE: User-Entscheidung noetig (Architektur-Frage, Design-Wahl)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung (max 8 bullets)
