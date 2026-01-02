AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Economic State Variablen/Proxies (Spieleinsatz, Jackpot, Rolling CV)
TASK-ID: ECON-001
PRIORITY: P1
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 02:08:04] ECON-001 - EXECUTOR (ki6)

### Summary
- Created kenobase/core/economic_state.py with 3 Economic Proxies
- Proxy 1: parse_spieleinsatz() - extracts betting volume from metadata
- Proxy 2: parse_jackpot() - extracts jackpot level from metadata
- Proxy 3: compute_rolling_cv() - computes coefficient of variation of hit distribution
- State classifier: classify_economic_state() maps proxies to NORMAL/COOLDOWN/HOT/RECOVERY
- Integration: extract_economic_states() processes DrawResult list
- Bet recommendation: get_bet_recommendation() returns action based on Axiom A7
- All 27 new unit tests pass; 1172 total tests pass

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_ECON-001_EXECUTOR_20251230_020304.md

## [2025-12-30 02:11:05] ECON-001 - PROXY_IMPL (ki0)

### Summary
- All 27 unit tests pass (pytest tests/unit/test_economic_state.py -v -> 27 passed)
- Python syntax valid (py_compile OK)
- Module imports correctly via kenobase.core
- __init__.py exports 8 new symbols correctly
- EconomicState dataclass + 7 functions implemented as specified
- Config YAML section added but NOT integrated into config.py (documented)
- Implementation uses hardcoded defaults (acceptable for helper-only module)
- No Known Bugs triggered (BUG-001 to BUG-010)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_ECON-001_PROXY_IMPL_20251230_020804.md



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
- kenobase/core/economic_state.py (neu zu erstellen)
- kenobase/core/__init__.py
- config/default.yaml
- tests/unit/test_economic_state.py (neu zu erstellen)
- kenobase/core/economic_state.py (new)
- tests/unit/test_economic_state.py (new)

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
- All 27 unit tests pass (pytest tests/unit/test_economic_state.py -v -> 27 passed)
- Python syntax valid (py_compile OK)
- Module imports correctly via kenobase.core
- __init__.py exports 8 new symbols correctly
- EconomicState dataclass + 7 functions implemented as specified
- Config YAML section added but NOT integrated into config.py (documented)
- Implementation uses hardcoded defaults (acceptable for helper-only module)
- No Known Bugs triggered (BUG-001 to BUG-010)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_ECON-001_PROXY_IMPL_20251230_020804.md

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
task: ECON-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki7_ECON-001_VALIDATOR_20251230_021105.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
