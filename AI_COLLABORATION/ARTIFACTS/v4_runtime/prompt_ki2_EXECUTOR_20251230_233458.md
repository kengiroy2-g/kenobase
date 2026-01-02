AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Korrelation zwischen Tickets
TASK-ID: TASK_034
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
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

## [2025-12-30 23:34:58] TASK_034 - PROXY_PLAN (ki0)

### Summary
- Plan is complete with 6 Dataclasses, 4 core functions, clear acceptance criteria
- BH-FDR already exists in null_models.py (benjamini_hochberg_fdr) - can be reused
- Integration points correct: __init__.py export section clearly identified
- 4 files in WORKING_SET match deliverables (NEW/MODIFY correctly tagged)
- Granularity per-ticket-pair appropriate for portfolio analysis
- ROI context explicit: -43% to -67% ROI tickets, diversification purpose only
- Script references SYSTEM_STATUS tickets (Typ-2,6,8,10) - ensures consistency
- Unit-Tests cover edge cases (no_overlap, full_overlap, insufficient_data)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_034_PROXY_PLAN_20251230_233258.md




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
ROLLE: EXECUTOR
AUFGABE: Fuehre den genehmigten Plan aus.

EFFIZIENZ-REGELN:
- Starte mit WORKING SET; vermeide Repo-weite Scans. Wenn du suchen musst: 1 gezieltes Grep pro Subtask, nicht breit.
- Schreibe nur kurze, entscheidungsrelevante Logs; grosse Logs nach AI_COLLABORATION/ARTIFACTS/ auslagern und verlinken.
- Aktualisiere Status ausschliesslich ueber den Handoff (keine CURRENT_STATUS edits im Body).
- Aendere niemals AI_COLLABORATION/MESSAGE_QUEUE/* oder AI_COLLABORATION/RESULTS/CURRENT_STATUS.md (nur Handoff-Ausgabe).
- Vermeide das Ausgeben von Diffs (diff --git, Patch-BlÃ¶cke). In der Antwort nur Summary + Pfade.

PLAN (kurz):
- Plan is complete with 6 Dataclasses, 4 core functions, clear acceptance criteria
- BH-FDR already exists in null_models.py (benjamini_hochberg_fdr) - can be reused
- Integration points correct: __init__.py export section clearly identified
- 4 files in WORKING_SET match deliverables (NEW/MODIFY correctly tagged)
- Granularity per-ticket-pair appropriate for portfolio analysis
- ROI context explicit: -43% to -67% ROI tickets, diversification purpose only
- Script references SYSTEM_STATUS tickets (Typ-2,6,8,10) - ensures consistency
- Unit-Tests cover edge cases (no_overlap, full_overlap, insufficient_data)

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_034_PROXY_PLAN_20251230_233258.md

REGELN:
1. Folge Checkliste exakt
2. Keine eigenen Interpretationen
3. Dokumentiere jeden Schritt
4. WICHTIG: Fuege files_changed: [...] im YAML hinzu

TOKEN HYGIENE:
- Final Output muss direkt das Handoff-Markdown sein (keine Diffs, keine Zusatztexte).
- Keine langen Command-Outputs im Handoff
- Bei Fehlern: nur Command + 20 Zeilen excerpt
- Lange Logs: speichere in AI_COLLABORATION/ARTIFACTS/ und referenziere nur Pfad

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: COMPLETE
task: TASK_034
role: EXECUTOR
phase: EXECUTOR
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

# Umsetzung

WICHTIG: Erstelle Handoff-Datei wenn fertig:
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK_034_EXECUTOR_20251230_233458.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
