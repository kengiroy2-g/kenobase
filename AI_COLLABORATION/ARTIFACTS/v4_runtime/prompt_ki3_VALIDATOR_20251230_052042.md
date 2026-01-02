AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Gerade/Ungerade Ratio
TASK-ID: TRANS-003
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 05:14:42] TRANS-003 - PROXY_PLAN (ki0)

### Summary
- Plan folgt decade_distribution.py Template - bewaehrt und konsistent
- Binomial-Test gegen 50/50 ist statistisch korrekt fuer Paritaets-Analyse
- Working Set vollstaendig fuer Executor (Template + Init + Tests)
- Keine Cross-Lotterie-Kopplung in Scope - korrekt begrenzt
- Repro-Kommando klar definiert
- Integration in __init__.py explizit genannt
- Keine globalen Thresholds noetig (50/50 ist mathematisch fix)
- Chi-Quadrat + Binomial-Test Kombination statistisch sinnvoll

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TRANS-003_PROXY_PLAN_20251230_051242.md

## [2025-12-30 05:18:42] TRANS-003 - EXECUTOR (ki2)

### Summary
- Created parity_ratio.py module following decade_distribution.py template
- Implemented ParityBin and ParityRatioResult dataclasses
- Added is_even(), count_parity(), analyze_parity_ratio() functions
- Chi-Quadrat + Binomial-Test gegen 50/50 Erwartung implementiert
- Created 17 unit tests in test_parity_ratio.py - ALL PASSED
- Added analyze_parity.py CLI script with JSON output
- Integrated into analysis/__init__.py with all exports

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TRANS-003_EXECUTOR_20251230_051442.md

## [2025-12-30 05:20:42] TRANS-003 - PROXY_IMPL (ki0)

### Summary
- All 4 files created/modified as specified
- parity_ratio.py follows decade_distribution.py template - consistent architecture
- Dataclasses ParityBin and ParityRatioResult correctly structured (frozen=True)
- Chi-Square + Binomial-Test gegen 50/50 Erwartung statistisch korrekt
- __init__.py exports all 5 symbols
- 17 unit tests ALL PASSED (verified via pytest)
- CLI script analyze_parity.py has JSON output and proper error handling
- No Known Bugs reproduced

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TRANS-003_PROXY_IMPL_20251230_051842.md



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
- kenobase/analysis/parity_ratio.py
- kenobase/analysis/__init__.py
- tests/unit/test_parity_ratio.py
- scripts/analyze_parity.py

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
- All 4 files created/modified as specified
- parity_ratio.py follows decade_distribution.py template - consistent architecture
- Dataclasses ParityBin and ParityRatioResult correctly structured (frozen=True)
- Chi-Square + Binomial-Test gegen 50/50 Erwartung statistisch korrekt
- __init__.py exports all 5 symbols
- 17 unit tests ALL PASSED (verified via pytest)
- CLI script analyze_parity.py has JSON output and proper error handling
- No Known Bugs reproduced

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TRANS-003_PROXY_IMPL_20251230_051842.md

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
task: TRANS-003
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TRANS-003_VALIDATOR_20251230_052042.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
