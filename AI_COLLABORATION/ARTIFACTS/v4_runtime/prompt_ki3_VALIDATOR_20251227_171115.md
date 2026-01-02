AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Infrastruktur und Automatisierung
TASK-ID: HYP-012
PRIORITY: LOW
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 17:09:15] HYP-012 - EXECUTOR (ki2)

### Summary
- Created stake_correlation.py module following HYP-010 pattern
- Implemented StakeCorrelationResult, NumberStakeClassification, StakeAnalysisSummary dataclasses
- Added load_stake_data() for CSV with semicolon delimiter and German number format
- Implemented analyze_stake_correlation(), analyze_auszahlung_correlation(), analyze_restbetrag_correlation()
- Created analyze_hyp012.py script with CLI interface
- Created test_stake_correlation.py with 15 unit tests (all passing)
- Updated analysis/__init__.py with new exports
- Verified with real data: 365 draws loaded, analysis complete

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HYP-012_EXECUTOR_20251227_170315.md

## [2025-12-27 17:11:15] HYP-012 - PROXY_IMPL (ki0)

### Summary
- All 4 files in WORKING SET verified (stake_correlation.py, analyze_hyp012.py, test_stake_correlation.py, __init__.py)
- Syntax check passed for all Python files
- All 15 unit tests pass (pytest -v)
- Module follows HYP-010 pattern correctly (dataclasses, load function, analyze functions, run_hypXXX)
- __init__.py properly exports all HYP-012 symbols with section comment
- CLI script runs successfully with 365 draws from real data
- JSON output is valid and saved to results/hyp012_stake_correlation.json
- No Known Bug patterns detected (no global thresholds, no orchestrator integration needed)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-012_PROXY_IMPL_20251227_170915.md



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
- kenobase/analysis/stake_correlation.py
- scripts/analyze_hyp012.py
- tests/unit/test_stake_correlation.py
- kenobase/analysis/__init__.py

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
- All 4 files in WORKING SET verified (stake_correlation.py, analyze_hyp012.py, test_stake_correlation.py, __init__.py)
- Syntax check passed for all Python files
- All 15 unit tests pass (pytest -v)
- Module follows HYP-010 pattern correctly (dataclasses, load function, analyze functions, run_hypXXX)
- __init__.py properly exports all HYP-012 symbols with section comment
- CLI script runs successfully with 365 draws from real data
- JSON output is valid and saved to results/hyp012_stake_correlation.json
- No Known Bug patterns detected (no global thresholds, no orchestrator integration needed)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-012_PROXY_IMPL_20251227_170915.md

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
task: HYP-012
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_HYP-012_VALIDATOR_20251227_171115.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
