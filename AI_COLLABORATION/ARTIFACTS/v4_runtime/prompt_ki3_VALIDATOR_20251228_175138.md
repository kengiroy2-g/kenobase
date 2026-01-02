AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Regionale Verteilung via Pressemitteilungen
TASK-ID: HYP003-002
PRIORITY: HOCH
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 17:48:38] HYP003-002 - EXECUTOR (ki2)

### Summary
- Created kenobase/scraper/converters.py with KenoWinnerRecord -> DrawResult conversion
- Added load_scraped_winners() and load_all_scraped_winners() for JSON loading
- Implemented calculate_distribution_chi2() in regional_affinity.py for Chi-Quadrat test
- Added BUNDESLAND_POPULATION_SHARE (16 Bundeslaender) for expected distribution
- Created scripts/analyze_hyp003_regional.py for end-to-end HYP-003 regional analysis
- Added 26 unit tests (13 for regional_affinity, 13 for converters) - all pass
- Script runs successfully but needs more scraped data (only 2 records from 1 Bundesland)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HYP003-002_EXECUTOR_20251228_173938.md

## [2025-12-28 17:51:38] HYP003-002 - PROXY_IMPL (ki0)

### Summary
- All 6 files created/modified correctly (converters.py, regional_affinity.py, __init__.py, analyze_hyp003_regional.py, 2 test files)
- Syntax check passed for all Python files
- All 26 unit tests pass (13 regional_affinity + 13 converters)
- Region keys consistent: GERMAN_REGIONS (16) == BUNDESLAND_POPULATION_SHARE (16)
- Population shares sum to 1.001 (correct rounding)
- Chi-Quadrat implementation includes proper p-value calculation via gamma functions
- Granularity per-bundesland confirmed (no global thresholds - BUG-001 avoided)
- Integration points correct: converters.py exports in __init__.py, uses regions.py normalize_region()

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP003-002_PROXY_IMPL_20251228_174838.md



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
- kenobase/core/regions.py
- scripts/scrape_press.py
- AI_COLLABORATION/KNOWLEDGE_BASE/REGIONAL_DATA_RESEARCH.md
- kenobase/scraper/converters.py (NEW)
- kenobase/scraper/__init__.py
- scripts/analyze_hyp003_regional.py (NEW)
- tests/unit/test_regional_affinity.py
- tests/unit/test_converters.py (NEW)

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
- All 6 files created/modified correctly (converters.py, regional_affinity.py, __init__.py, analyze_hyp003_regional.py, 2 test files)
- Syntax check passed for all Python files
- All 26 unit tests pass (13 regional_affinity + 13 converters)
- Region keys consistent: GERMAN_REGIONS (16) == BUNDESLAND_POPULATION_SHARE (16)
- Population shares sum to 1.001 (correct rounding)
- Chi-Quadrat implementation includes proper p-value calculation via gamma functions
- Granularity per-bundesland confirmed (no global thresholds - BUG-001 avoided)
- Integration points correct: converters.py exports in __init__.py, uses regions.py normalize_region()

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP003-002_PROXY_IMPL_20251228_174838.md

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
task: HYP003-002
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_HYP003-002_VALIDATOR_20251228_175138.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
