AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Regionale Zahlen-Affinitaet (Bundesland)
TASK-ID: TASK-R03
PRIORITY: HIGH
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 06:36:38] TASK-R03 - EXECUTOR (ki2)

### Summary
- Added regional affinity analysis (lift + z-score per Bundesland) with smoothing/thresholds and exposed helpers for top lifts.
- DataLoader now normalizes region metadata (Bundesland/Region/State) and config gained regional_affinity settings with defaults.
- PipelineRunner integrates regional affinity step and exposes results in CLI output; analyze CLI can export JSON via --regional-affinity-output.
- New docs at docs/regional_affinity.md cover method, config, and repro; unit tests added for analysis behavior.
- Artifact results/regional_affinity.json generated from data/raw/keno/KENO_ab_2018.csv (2237 draws) but contains warning: no region metadata present.

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-R03_EXECUTOR_20251228_062538.md

## [2025-12-28 06:38:38] TASK-R03 - PROXY_IMPL (ki0)

### Summary
- regional_affinity.py implements lift + z-score per Bundesland with Laplace smoothing and configurable thresholds
- Config integration complete: RegionalAffinityConfig in config.py lines 124-131, default.yaml lines 95-105
- Pipeline runner integrates analysis at Step 2.6 (lines 248-265) and exposes result in PipelineResult
- CLI (analyze.py) exposes --regional-affinity-output flag with proper JSON export
- Unit tests (4) pass covering edge cases (empty, no metadata, insufficient draws, computation)
- JSON artifact generated; no region metadata in source CSV so output contains expected warning
- No Known Bugs reproduced; config paths align with YAML structure; no cross-file integration gaps
- Syntax check passed for all core files

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-R03_PROXY_IMPL_20251228_063638.md



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
- kenobase/analysis/regional_affinity.py
- kenobase/analysis/__init__.py
- kenobase/pipeline/runner.py
- scripts/analyze.py
- tests/unit/test_regional_affinity.py
- docs/regional_affinity.md
- results/regional_affinity.json
- results/analyze_pipeline.json

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
- regional_affinity.py implements lift + z-score per Bundesland with Laplace smoothing and configurable thresholds
- Config integration complete: RegionalAffinityConfig in config.py lines 124-131, default.yaml lines 95-105
- Pipeline runner integrates analysis at Step 2.6 (lines 248-265) and exposes result in PipelineResult
- CLI (analyze.py) exposes --regional-affinity-output flag with proper JSON export
- Unit tests (4) pass covering edge cases (empty, no metadata, insufficient draws, computation)
- JSON artifact generated; no region metadata in source CSV so output contains expected warning
- No Known Bugs reproduced; config paths align with YAML structure; no cross-file integration gaps
- Syntax check passed for all core files

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-R03_PROXY_IMPL_20251228_063638.md

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
task: TASK-R03
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK-R03_VALIDATOR_20251228_063838.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
