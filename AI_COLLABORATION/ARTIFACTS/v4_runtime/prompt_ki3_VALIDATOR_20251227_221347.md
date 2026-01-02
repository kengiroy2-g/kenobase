AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Core Stable Numbers identifizieren
TASK-ID: TASK-H02
PRIORITY: HIGH
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 22:11:47] TASK-H02 - EXECUTOR (ki2)

### Summary
- Created kenobase/analysis/stable_numbers.py with Model Law A implementation
- StableNumberResult dataclass with number, stability_score, is_stable, avg_frequency, std_frequency
- Stability formula: stability_score = 1 - (std / mean), clamped to [0, 1]
- analyze_stable_numbers() uses calculate_rolling_frequency from frequency.py
- Config integration: uses physics.stability_threshold (default 0.90)
- CLI: new `stable-numbers` command with --window, --threshold, --all options
- Unit tests: 19 tests, all passing
- Exports added to kenobase/analysis/__init__.py

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-H02_EXECUTOR_20251227_220747.md

## [2025-12-27 22:13:47] TASK-H02 - PROXY_IMPL (ki0)

### Summary
- stable_numbers.py implements Model Law A correctly (stability = 1 - std/mean, clamped [0,1])
- Config integration uses physics.stability_threshold (0.90) - no new global threshold
- CLI command `stable-numbers` added to analyze.py with proper options (--window, --threshold, --all)
- Exports added to kenobase/analysis/__init__.py (5 items: StableNumberResult, calculate_stability_score, analyze_stable_numbers, get_stable_numbers, export_stable_numbers)
- All 19 unit tests pass (test_stable_numbers.py)
- Syntax validation passes for all modified files
- Game-specific number_range from cfg.get_active_game() - no BUG-001 violation
- Import chain verified: kenobase.analysis -> stable_numbers OK

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-H02_PROXY_IMPL_20251227_221147.md



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
- kenobase/analysis/stable_numbers.py (NEW)
- kenobase/analysis/__init__.py (MODIFIED)
- scripts/analyze.py (MODIFIED)
- tests/unit/test_stable_numbers.py (NEW)

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
- stable_numbers.py implements Model Law A correctly (stability = 1 - std/mean, clamped [0,1])
- Config integration uses physics.stability_threshold (0.90) - no new global threshold
- CLI command `stable-numbers` added to analyze.py with proper options (--window, --threshold, --all)
- Exports added to kenobase/analysis/__init__.py (5 items: StableNumberResult, calculate_stability_score, analyze_stable_numbers, get_stable_numbers, export_stable_numbers)
- All 19 unit tests pass (test_stable_numbers.py)
- Syntax validation passes for all modified files
- Game-specific number_range from cfg.get_active_game() - no BUG-001 violation
- Import chain verified: kenobase.analysis -> stable_numbers OK

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-H02_PROXY_IMPL_20251227_221147.md

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
task: TASK-H02
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK-H02_VALIDATOR_20251227_221347.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
