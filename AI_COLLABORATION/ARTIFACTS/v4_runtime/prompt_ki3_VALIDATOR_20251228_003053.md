AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: EuroJackpot Cross-Validation
TASK-ID: TASK-M03
PRIORITY: MEDIUM
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 00:28:53] TASK-M03 - EXECUTOR (ki2)

### Summary
- Backtest erfolgreich auf 526 EuroJackpot-Ziehungen (2012-2023)
- 6 Walk-Forward Perioden, Avg F1=0.1466 (std 0.0185)
- Best Period #3 (F1=0.1696), Worst Period #6 (F1=0.1235)
- Avg Stability 0.6533 - unter 0.9 (kein Gesetz A)
- 4/6 Perioden CRITICAL Criticality
- Per-game Thresholds korrekt angewandt
- Pipeline laeuft, keine signifikante Vorhersagekraft (erwartbar)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-M03_EXECUTOR_20251228_002653.md

## [2025-12-28 00:30:53] TASK-M03 - PROXY_IMPL (ki0)

### Summary
- Backtest JSON valid und vollstaendig (204 Zeilen, 6 Perioden)
- 526 Ziehungen korrekt (528 Zeilen - 1 Header - 1 trailing = 526)
- Avg F1=0.1466, std=0.0185 - konsistent mit Random-Baseline (~0.10)
- Per-game Thresholds verifiziert: hot=0.13, cold=0.07 (config/default.yaml:124-125)
- Stability avg 0.6533 < 0.9 - kein Gesetz A (korrekt dokumentiert)
- 4/6 CRITICAL Perioden korrekt gezaehlt
- Keine Code-Aenderungen (nur Execution Task) - keine BUG-001 Gefahr
- Repro-Command syntaktisch korrekt, Output-Pfad existiert

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-M03_PROXY_IMPL_20251228_002853.md



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
- results/eurojackpot_backtest.json

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
- Backtest JSON valid und vollstaendig (204 Zeilen, 6 Perioden)
- 526 Ziehungen korrekt (528 Zeilen - 1 Header - 1 trailing = 526)
- Avg F1=0.1466, std=0.0185 - konsistent mit Random-Baseline (~0.10)
- Per-game Thresholds verifiziert: hot=0.13, cold=0.07 (config/default.yaml:124-125)
- Stability avg 0.6533 < 0.9 - kein Gesetz A (korrekt dokumentiert)
- 4/6 CRITICAL Perioden korrekt gezaehlt
- Keine Code-Aenderungen (nur Execution Task) - keine BUG-001 Gefahr
- Repro-Command syntaktisch korrekt, Output-Pfad existiert

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-M03_PROXY_IMPL_20251228_002853.md

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
task: TASK-M03
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK-M03_VALIDATOR_20251228_003053.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
