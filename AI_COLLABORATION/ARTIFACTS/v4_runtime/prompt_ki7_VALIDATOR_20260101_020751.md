AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: A1-01: Cooldown-Regel isoliert testen (30d nach 10/10)
TASK-ID: SYN_001
PRIORITY: P0
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2026-01-01 01:35:50] SYN_001 - EXECUTOR (ki6)

### Summary
- Created isolated Cooldown-Rule test script (A1-01: 30d nach 10/10)
- Implements Train/Test Split (2022-2023 vs 2024) per Axiom-First
- Negative Control: random 30d windows without Jackpot relation
- Chi2-Test + Mann-Whitney U + Fisher's Exact for low sample sizes
- Train: 5/5 types show cooldown ROI < normal ROI
- Test: 4/5 types show cooldown ROI < normal ROI
- 0 statistically significant effects (expected with only 11 Jackpots)
- Hypothesis status: CONFIRMED (consistent directional effect)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_SYN_001_EXECUTOR_20260101_013150.md

## [2026-01-01 02:07:51] SYN_001 - PROXY_IMPL (ki0)

### Summary
- Script syntaktisch korrekt (py_compile OK)
- JSON-Output validiert (results/cooldown_rule_isolated_test.json)
- Train/Test Split korrekt: 2022-2023 vs 2024
- Negative Control implementiert: random 30d windows ohne Jackpot-Bezug
- Chi2 + Mann-Whitney + Fisher's Exact Tests korrekt angewandt
- Ergebnis: 5/5 Train + 4/5 Test = Cooldown ROI < Normal ROI (CONFIRMED)
- 0 statistische Signifikanz (erwartet bei nur 11 Jackpots - geringe Power)
- Axiom-First Workflow eingehalten (A1+A7 -> Prediction -> Test)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_SYN_001_PROXY_IMPL_20260101_020551.md



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
- scripts/test_cooldown_rule_isolated.py
- results/cooldown_rule_isolated_test.json

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
- Script syntaktisch korrekt (py_compile OK)
- JSON-Output validiert (results/cooldown_rule_isolated_test.json)
- Train/Test Split korrekt: 2022-2023 vs 2024
- Negative Control implementiert: random 30d windows ohne Jackpot-Bezug
- Chi2 + Mann-Whitney + Fisher's Exact Tests korrekt angewandt
- Ergebnis: 5/5 Train + 4/5 Test = Cooldown ROI < Normal ROI (CONFIRMED)
- 0 statistische Signifikanz (erwartet bei nur 11 Jackpots - geringe Power)
- Axiom-First Workflow eingehalten (A1+A7 -> Prediction -> Test)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_SYN_001_PROXY_IMPL_20260101_020551.md

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
task: SYN_001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki7_SYN_001_VALIDATOR_20260101_020751.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
