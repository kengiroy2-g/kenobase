AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Korrelation zwischen Tickets
TASK-ID: TASK_034
PRIORITY: P2
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 23:42:58] TASK_034 - PROXY_IMPL (ki0)

### Summary
- All 5 files in WORKING_SET created/modified correctly (ticket_correlation.py, __init__.py, script, tests, JSON)
- 6 dataclasses + 6 functions implemented as specified in plan
- BH-FDR correctly reused from null_models.py (benjamini_hochberg_fdr)
- 20/20 unit tests pass covering all required scenarios
- JSON output valid and tickets match SYSTEM_STATUS.json exactly
- Ticket data consistency verified (Typ-2,6,8,10 numbers match)
- Diversification scoring logic correct (higher = more diversified)
- Negative ROI context properly documented in docstrings and JSON output

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_034_PROXY_IMPL_20251230_233958.md

## [2025-12-30 23:45:59] TASK_034 - VALIDATOR (ki3)

### Summary
- 20/20 unit tests pass (all test classes covering overlap, ROI sync, timing, diversification, full analysis)
- All 12 exports verified working via direct import from kenobase.analysis
- Ticket numbers match SYSTEM_STATUS.json exactly (Typ-2,6,8,10)
- Diversification logic correct (low Jaccard → high diversification score)
- JSON output valid and reproducible via script
- Best diversification: Typ-2+Typ-6 (Jaccard=0.0, div=0.65)
- Worst diversification: Typ-8+Typ-10 (Jaccard=0.64, div=0.46)
- Negative ROI context properly documented in docstrings and JSON

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK_034_VALIDATOR_20251230_234258.md



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
- kenobase/analysis/__init__.py (MODIFY - 12 exports added)
- results/ticket_correlation.json (NEW - generated output)

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
ROLLE: PROXY (User-Stellvertreter - Finale Freigabe)
AUFGABE: Finale Freigabe mit Projekt-Perspektive.

PFLICHTLEKTUERE (kurz):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Falls Zweifel an Integration

EFFIZIENZ-REGELN:
- Nutze VALIDATOR OUTPUT + dein Wissen aus vorherigen Proxy-Phasen
- Keine weiteren Tests, nur finale Entscheidung

VALIDATOR OUTPUT (kurz):
- 20/20 unit tests pass (all test classes covering overlap, ROI sync, timing, diversification, full analysis)
- All 12 exports verified working via direct import from kenobase.analysis
- Ticket numbers match SYSTEM_STATUS.json exactly (Typ-2,6,8,10)
- Diversification logic correct (low Jaccard → high diversification score)
- JSON output valid and reproducible via script
- Best diversification: Typ-2+Typ-6 (Jaccard=0.0, div=0.65)
- Worst diversification: Typ-8+Typ-10 (Jaccard=0.64, div=0.46)
- Negative ROI context properly documented in docstrings and JSON

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK_034_VALIDATOR_20251230_234258.md

FINALE PRUEFUNG:
1. Hat Validator alle kritischen Aspekte geprueft?
2. Wuerde der USER diese Aenderung akzeptieren?
3. Gibt es offene Architektur-Fragen die der User entscheiden sollte?

ESKALATION an User wenn:
- Architektur-Entscheidung noetig die nicht in ADRs dokumentiert ist
- Unsicherheit ueber globale vs spezifische Werte
- Potenzielle Breaking Changes

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: COMPLETE
task: TASK_034
role: PROXY
phase: PROXY_FINAL
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

# Proxy Final Review

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_034_PROXY_FINAL_20251230_234559.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
