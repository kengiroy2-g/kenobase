AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Test HYP_013: Overlap-Birthday-Anteil nach Phase
TASK-ID: TASK_023
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 20:12:48] TASK_023 - EXECUTOR (ki2)

### Summary
- Implemented phase-stratified HYP_013 script and ran on 1,457 draws (2022-01-03..2025-12-29) using 17 jackpots from timeline_2025.csv.
- Overlap means by phase: PRE 5.79 (n=24, UNVERIFIED), POST 5.92 (n=38, UNVERIFIED), COOLDOWN 5.78 (n=274), NORMAL 5.73 (n=1120); all z-tests vs 5.714 non-significant after BH/Bonferroni.
- Birthday ratios by phase: PRE 0.476, POST 0.453, COOLDOWN 0.456, NORMAL 0.435 (sample sizes as above); all z-tests vs 0.443 non-significant after corrections.
- Global KW p-values: overlap 0.93, birthday_ratio 0.53; 6 pairwise MW tests per metric all p_adj >=0.87, no significant differences.
- Overall means: overlap 5.75 (n=1456), birthday_ratio 0.440 (n=1455); HYP_013 rejected (no corrected significance).
- Artifacts written to results/hyp013_overlap_birthday_phase.json and AI_COLLABORATION/ARTIFACTS/hyp013_overlap_birthday_phase.md; repro command added to results/REPRO_COMMANDS.md.

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_023_EXECUTOR_20251230_200548.md

## [2025-12-30 20:14:48] TASK_023 - PROXY_IMPL (ki0)

### Summary
- Script test_hyp013_overlap_birthday_phase.py compiles (py_compile OK)
- JSON output valid (json.load() success), 268 lines with complete structure
- Metadata correct: 1457 draws, date range 2022-01-03..2025-12-29, 17 jackpots
- Phase stats complete: PRE(n=24), POST(n=38), COOLDOWN(n=274), NORMAL(n=1120)
- Statistical tests with Bonferroni+BH corrections; no significant results
- Decision: HYP_013 REJECTED (support: false)
- REPRO_COMMANDS.md and artifact markdown correctly written

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_023_PROXY_IMPL_20251230_201248.md



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
- scripts/test_hyp013_overlap_birthday_phase.py
- results/hyp013_overlap_birthday_phase.json
- AI_COLLABORATION/ARTIFACTS/hyp013_overlap_birthday_phase.md
- results/REPRO_COMMANDS.md
- AI_COLLABORATION/HANDOFFS/ki2_TASK_023_EXECUTOR_20251230_200548.md

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
- Script test_hyp013_overlap_birthday_phase.py compiles (py_compile OK)
- JSON output valid (json.load() success), 268 lines with complete structure
- Metadata correct: 1457 draws, date range 2022-01-03..2025-12-29, 17 jackpots
- Phase stats complete: PRE(n=24), POST(n=38), COOLDOWN(n=274), NORMAL(n=1120)
- Statistical tests with Bonferroni+BH corrections; no significant results
- Decision: HYP_013 REJECTED (support: false)
- REPRO_COMMANDS.md and artifact markdown correctly written

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_023_PROXY_IMPL_20251230_201248.md

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
task: TASK_023
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK_023_VALIDATOR_20251230_201448.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
