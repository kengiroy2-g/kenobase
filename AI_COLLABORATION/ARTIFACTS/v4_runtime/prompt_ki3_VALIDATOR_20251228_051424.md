AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Lotto 6aus49 Model Transfer
TASK-ID: TASK-P09
PRIORITY: MEDIUM
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 05:12:24] TASK-P09 - EXECUTOR (ki2)

### Summary
- Lotto 6aus49 backtest executed successfully with 12 periods
- Archive data (1955-2024, N=4764): F1=0.0405, std=0.0154
- Recent data (2018+, N=638): F1=0.1740, std=0.0317 (4x better)
- All 12 periods show CRITICAL criticality level (expected for lottery)
- Stability scores consistently ~0.85 across periods
- Game-specific thresholds (hot=0.16, cold=0.09) correctly applied
- Results saved to results/lotto_backtest.json and results/lotto_backtest_2018.json
- No code changes required - infrastructure already complete

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-P09_EXECUTOR_20251228_051024.md

## [2025-12-28 05:14:24] TASK-P09 - PROXY_IMPL (ki0)

### Summary
- Archive backtest verified: N=4764, F1=0.0405, std=0.0154 (correct)
- Recent backtest verified: N=638, F1=0.1740, std=0.0317 (correct)
- Game-specific thresholds confirmed: hot=0.16, cold=0.09 (no BUG-001)
- Both result files exist and contain valid JSON
- Minor doc error: 2018+ shows LOW/MEDIUM criticality, not CRITICAL (expected)
- No code changes required - infrastructure was already complete
- 4x F1 improvement on recent data vs archive is reasonable
- APPROVED for Validator phase

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P09_PROXY_IMPL_20251228_051224.md



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
- (leer)

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
- Archive backtest verified: N=4764, F1=0.0405, std=0.0154 (correct)
- Recent backtest verified: N=638, F1=0.1740, std=0.0317 (correct)
- Game-specific thresholds confirmed: hot=0.16, cold=0.09 (no BUG-001)
- Both result files exist and contain valid JSON
- Minor doc error: 2018+ shows LOW/MEDIUM criticality, not CRITICAL (expected)
- No code changes required - infrastructure was already complete
- 4x F1 improvement on recent data vs archive is reasonable
- APPROVED for Validator phase

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P09_PROXY_IMPL_20251228_051224.md

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
task: TASK-P09
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK-P09_VALIDATOR_20251228_051424.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
