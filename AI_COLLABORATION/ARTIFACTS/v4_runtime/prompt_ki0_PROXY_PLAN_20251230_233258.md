AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Korrelation zwischen Tickets
TASK-ID: TASK_034
PRIORITY: P2
PHASE: PROXY_PLAN

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 23:00:57] TASK_034 - PROXY_PLAN (ki0)

### Summary
- Handoff (225557) enthält nur 19-Zeilen Bestätigung, KEIN detaillierter Plan
- ARCHITECT behauptet Punkte (FDR, Unit-Tests, __init__.py) ohne Implementierungsdetails
- Fehlende Strukturen: Dataclass-Definitionen, Funktions-Signaturen fehlen
- Keine konkrete WORKING_SET_REQUEST für EXECUTOR sichtbar
- 5+ bestehende Correlation-Module in __init__.py - Abgrenzung unklar
- SYSTEM_STATUS: ALLE Tickets haben negative ROI (-43% bis -67%)
- Nutzen-Argumentation ("Diversifikation negativer Strategien") unzureichend
- REJECTED - zurück an ARCHITECT für vollständigen Implementierungsplan

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_034_PROXY_PLAN_20251230_225857.md

## [2025-12-30 23:32:58] TASK_034 - ARCHITECT (ki1)

### Summary
- Neues Modul ticket_correlation.py mit 3 Analyse-Dimensionen (Overlap, ROI-Sync, Timing)
- Nutzt Spearman + BH-FDR bei n>=5 Tests (Pattern aus odds_correlation.py)
- Dataclasses: TicketPair, OverlapResult, SyncResult, TicketCorrelationResult
- Haupt-Funktion: analyze_ticket_correlation(tickets, backtest_results)
- Script produziert JSON in results/ticket_correlation.json
- Unit-Tests mit 5 Testfaellen (Coverage-Ziel 85%)
- ROI-Kontext: Alle Tickets haben negative ROI - Analyse dient Portfolio-Diversifikation

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_034_ARCHITECT_20251230_232858.md



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
- kenobase/analysis/ticket_correlation.py (NEW)
- kenobase/analysis/__init__.py (MODIFY - add exports)
- scripts/analyze_ticket_correlation.py (NEW)
- tests/unit/test_ticket_correlation.py (NEW)

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
- Neues Modul ticket_correlation.py mit 3 Analyse-Dimensionen (Overlap, ROI-Sync, Timing)
- Nutzt Spearman + BH-FDR bei n>=5 Tests (Pattern aus odds_correlation.py)
- Dataclasses: TicketPair, OverlapResult, SyncResult, TicketCorrelationResult
- Haupt-Funktion: analyze_ticket_correlation(tickets, backtest_results)
- Script produziert JSON in results/ticket_correlation.json
- Unit-Tests mit 5 Testfaellen (Coverage-Ziel 85%)
- ROI-Kontext: Alle Tickets haben negative ROI - Analyse dient Portfolio-Diversifikation

FULL HANDOFF (nur bei Bedarf oeffnen):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_034_ARCHITECT_20251230_232858.md

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
task: TASK_034
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_034_PROXY_PLAN_20251230_233258.md
- YAML Frontmatter mit status:
  - APPROVED: Plan ist gut, weiter zu Executor
  - REJECTED: Bug gefunden, zurueck zu Architect
  - ESCALATE: User-Entscheidung noetig (Architektur-Frage, Design-Wahl)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung (max 8 bullets)
