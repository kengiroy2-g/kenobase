AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Multiple Testing Korrektur
TASK-ID: TASK_031
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 22:08:54] TASK_031 - EXECUTOR (ki2)

### Summary
- Created scripts/apply_fdr_correction.py - scans all results/*.json for p_values recursively
- Handles heterogeneous p_value structures (nested keys like by_type.typ_6.p_value)
- Uses kenobase.analysis.null_models.benjamini_hochberg_fdr() for FDR correction
- Extracted 8105 p-values from 48 files, 36 unique hypotheses
- FDR correction reduced significant tests from 3539 (p<0.05) to 421 (q<0.05)
- Generated results/fdr_corrected_hypotheses.json (3.0 MB) and Markdown report
- Created tests/unit/test_fdr_correction.py with 15 passing tests
- Repro command verified: python scripts/apply_fdr_correction.py

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_031_EXECUTOR_20251230_220354.md

## [2025-12-30 22:10:55] TASK_031 - PROXY_IMPL (ki0)

### Summary
- Scripts/apply_fdr_correction.py: Syntax valid, correctly uses benjamini_hochberg_fdr() from null_models.py
- Recursive p_value extraction handles nested JSON structures (by_type.typ_6.p_value etc.)
- FDR correction reduces significant tests from 3539 to 421 (88% reduction) - expected behavior
- Tests: 15/15 pass covering extraction, FDR math, directory scanning, and report generation
- Output JSON validated: 8105 p-values from 48 files, 36 unique hypotheses
- Markdown report generated with proper tables and summary statistics
- No integration conflicts detected (standalone script, no orchestrator changes needed)
- ADR constraint on max 21 primary tests documented in report footer

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_031_PROXY_IMPL_20251230_220854.md



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
- scripts/apply_fdr_correction.py
- tests/unit/test_fdr_correction.py
- results/fdr_corrected_hypotheses.json
- results/fdr_correction_report.md

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
- Scripts/apply_fdr_correction.py: Syntax valid, correctly uses benjamini_hochberg_fdr() from null_models.py
- Recursive p_value extraction handles nested JSON structures (by_type.typ_6.p_value etc.)
- FDR correction reduces significant tests from 3539 to 421 (88% reduction) - expected behavior
- Tests: 15/15 pass covering extraction, FDR math, directory scanning, and report generation
- Output JSON validated: 8105 p-values from 48 files, 36 unique hypotheses
- Markdown report generated with proper tables and summary statistics
- No integration conflicts detected (standalone script, no orchestrator changes needed)
- ADR constraint on max 21 primary tests documented in report footer

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_031_PROXY_IMPL_20251230_220854.md

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
task: TASK_031
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK_031_VALIDATOR_20251230_221055.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
