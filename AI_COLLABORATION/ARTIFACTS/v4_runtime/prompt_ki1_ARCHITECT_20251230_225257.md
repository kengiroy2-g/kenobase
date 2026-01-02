AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Korrelation zwischen Tickets
TASK-ID: TASK_034
PRIORITY: P2
PHASE: ARCHITECT

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 22:50:57] TASK_034 - ARCHITECT (ki1)

### Summary
- Task analysiert: Korrelation zwischen verschiedenen Ticket-Typen (Typ-2/6/8/10)
- Bestehende Module identifiziert: odds_correlation.py, popularity_correlation.py
- Neues Modul geplant: kenobase/analysis/ticket_correlation.py
- 3 Analyse-Dimensionen definiert: Zahlen-Overlap, Performance-Sync, Zeit-Korrelation
- Acceptance Criteria mit statistischen Schwellwerten festgelegt
- Repro-Command definiert fÃ¼r Validierung

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_034_ARCHITECT_20251230_224856.md

## [2025-12-30 22:52:57] TASK_034 - PROXY_PLAN (ki0)

### Summary
- Handoff zu knapp (33 Zeilen) - keine konkreten Implementierungsschritte
- Fehlende Integration mit bestehenden 4 Correlation-Modulen
- Statistische Signifikanz: |r|>0.3 ohne p-Wert/FDR ist fragwuerdig
- Tickets in SYSTEM_STATUS.json haben alle NEGATIVE ROI (-43% bis -67%)
- Nutzen der Korrelation negativer Strategien unklar
- Keine Unit-Test-Spezifikation
- kenobase/analysis/__init__.py Update nicht erwaehnt

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_034_PROXY_PLAN_20251230_225057.md



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
- (leer)

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
ROLLE: ARCHITECT
AUFGABE: Erstelle detaillierten Implementierungsplan.

EFFIZIENZ-REGELN (wie normal CLI):
- Kein Repo-weiter Scan (kein rekursives Listing, kein breitflÃ¤chiges Grep).
- Arbeite primÃ¤r mit WORKING SET + TASK NOTES; wenn leer: max 2 gezielte Datei-Finder-Queries, dann stoppen und fehlende Pfade anfordern.
- Keine Status-/Messaging-Dateien lesen/schreiben (queue/CURRENT_STATUS) ausser explizit verlangt.
- Keine langen Tool-Outputs im Handoff; grosse Logs nach AI_COLLABORATION/ARTIFACTS/ auslagern und verlinken.

SCHRITTE:
1. Analysiere Anforderungen
2. Identifiziere betroffene Dateien
3. Erstelle Schritt-fuer-Schritt Checkliste
4. Definiere Acceptance Criteria

TOKEN HYGIENE:
- Output muss direkt das Handoff-Markdown sein (keine Diffs, keine Zusatztexte).
- Schreibe Handoff mit YAML Frontmatter (---\nstatus: COMPLETE\n...\n---)
- Max 8 summary bullets
- Keine langen Logs/Diffs im Body (nur Pfade)

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: COMPLETE
task: TASK_034
role: ARCHITECT
phase: ARCHITECT
files_changed: []
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

# Implementierungsplan

WICHTIG: Erstelle Handoff-Datei wenn fertig:
- Datei: AI_COLLABORATION/HANDOFFS/ki1_TASK_034_ARCHITECT_20251230_225257.md
- YAML mit status: COMPLETE
- YAML mit files_changed: [...]
