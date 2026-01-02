AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Multiple Testing Korrektur
TASK-ID: TASK_031
PRIORITY: P2
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
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

## [2025-12-30 22:13:55] TASK_031 - VALIDATOR (ki3)

### Summary
- All 15 unit tests pass (pytest tests/unit/test_fdr_correction.py -v)
- FDR correction correctly uses benjamini_hochberg_fdr() from null_models.py
- Output JSON valid: 8105 p-values, 48 files, 36 unique hypotheses
- Reduction: 3539 -> 421 significant tests (88% reduction, expected for FDR)
- Markdown report correctly formatted with significant results table
- Repro command verified: python scripts/apply_fdr_correction.py
- Code quality: Type hints, docstrings, proper error handling
- No regressions in existing codebase

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK_031_VALIDATOR_20251230_221055.md




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
ROLLE: PROXY (User-Stellvertreter - Finale Freigabe)
AUFGABE: Finale Freigabe mit Projekt-Perspektive.

PFLICHTLEKTUERE (kurz):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Falls Zweifel an Integration

EFFIZIENZ-REGELN:
- Nutze VALIDATOR OUTPUT + dein Wissen aus vorherigen Proxy-Phasen
- Keine weiteren Tests, nur finale Entscheidung

VALIDATOR OUTPUT (kurz):
- All 15 unit tests pass (pytest tests/unit/test_fdr_correction.py -v)
- FDR correction correctly uses benjamini_hochberg_fdr() from null_models.py
- Output JSON valid: 8105 p-values, 48 files, 36 unique hypotheses
- Reduction: 3539 -> 421 significant tests (88% reduction, expected for FDR)
- Markdown report correctly formatted with significant results table
- Repro command verified: python scripts/apply_fdr_correction.py
- Code quality: Type hints, docstrings, proper error handling
- No regressions in existing codebase

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK_031_VALIDATOR_20251230_221055.md

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
task: TASK_031
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_031_PROXY_FINAL_20251230_221355.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
