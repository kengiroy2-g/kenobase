AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Korrelation zwischen Tickets
TASK-ID: TASK_034
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 23:39:58] TASK_034 - EXECUTOR (ki2)

### Summary
- Created ticket_correlation.py with 6 dataclasses and 6 core functions
- Implemented 3 analysis dimensions: Overlap (Jaccard), ROI-Sync (Spearman), Timing (lift)
- BH-FDR from null_models.py reused for multiple testing correction
- Added 12 exports to analysis/__init__.py
- Script produces results/ticket_correlation.json with 6 pair correlations
- Unit tests: 20 tests pass, covering all 5 required scenarios
- Key finding: Typ-2+Typ-6 best diversification (0.65), Typ-8+Typ-10 most correlated (0.46)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_034_EXECUTOR_20251230_233458.md

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
ROLLE: VALIDATOR
AUFGABE: Validiere die Implementation.

EFFIZIENZ-REGELN:
- Tests nur zielgerichtet (klein starten). Keine riesigen Logs in die Antwort; speichere nach AI_COLLABORATION/ARTIFACTS/ und verlinke.
- Vermeide Repo-weite Scans; nutze WORKING SET + gezielte Reads.

VORHERIGER OUTPUT (kurz):
- All 5 files in WORKING_SET created/modified correctly (ticket_correlation.py, __init__.py, script, tests, JSON)
- 6 dataclasses + 6 functions implemented as specified in plan
- BH-FDR correctly reused from null_models.py (benjamini_hochberg_fdr)
- 20/20 unit tests pass covering all required scenarios
- JSON output valid and tickets match SYSTEM_STATUS.json exactly
- Ticket data consistency verified (Typ-2,6,8,10 numbers match)
- Diversification scoring logic correct (higher = more diversified)
- Negative ROI context properly documented in docstrings and JSON output

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_034_PROXY_IMPL_20251230_233958.md

VALIDIERUNG:
1. Fuehre minimale Tests aus (zielgerichtet)
2. Pruefe Code-Qualitaet
3. Verifiziere Acceptance Criteria

TOKEN HYGIENE:
- Bei Test FAIL: nur Command + kurze Fehlermeldung (max 20 Zeilen)
- Mehr Log noetig? Speichere in AI_COLLABORATION/ARTIFACTS/ und referenziere Pfad

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: APPROVED
task: TASK_034
role: VALIDATOR
phase: VALIDATOR
validated_handoff: "<nur filename oder leer>"
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

# Validation

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK_034_VALIDATOR_20251230_234258.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
