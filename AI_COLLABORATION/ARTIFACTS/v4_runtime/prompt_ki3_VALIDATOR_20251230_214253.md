AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Nullmodell: Permutationstest
TASK-ID: TASK_029
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 21:40:53] TASK_029 - EXECUTOR (ki2)

### Summary
- TASK_029 (Nullmodell Permutationstest) bereits vollstaendig implementiert
- kenobase/analysis/null_models.py (522 Zeilen) vorhanden und funktional
- tests/unit/test_null_models.py (428 Zeilen) mit 27 Unit-Tests
- Alle 27 Tests bestanden (pytest verified: 27 passed in 1.73s)
- NullModelType Enum in kenobase/core/axioms.py definiert
- Drei Permutationsmethoden: schedule_permutation, block_permutation, iid_permutation
- FDR-Korrektur via benjamini_hochberg_fdr() implementiert
- Task als DONE markieren - keine weitere Executor-Arbeit noetig

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_029_EXECUTOR_20251230_213953.md

## [2025-12-30 21:42:53] TASK_029 - PROXY_IMPL (ki0)

### Summary
- TASK_029 (Nullmodell Permutationstest) bereits vollstaendig implementiert
- kenobase/analysis/null_models.py (522 Zeilen) - Syntax verifiziert (py_compile OK)
- tests/unit/test_null_models.py mit 27 Unit-Tests - ALLE 27 PASSED (1.75s)
- NullModelType Enum in kenobase/core/axioms.py korrekt definiert und importiert
- Drei Permutationsmethoden: schedule_permutation, block_permutation, iid_permutation
- FDR-Korrektur via benjamini_hochberg_fdr() implementiert
- Module korrekt in kenobase/analysis/__init__.py exponiert (Import verifiziert)
- Task kann als DONE markiert werden - Implementation vollstaendig

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_029_PROXY_IMPL_20251230_214053.md



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
- TASK_029 (Nullmodell Permutationstest) bereits vollstaendig implementiert
- kenobase/analysis/null_models.py (522 Zeilen) - Syntax verifiziert (py_compile OK)
- tests/unit/test_null_models.py mit 27 Unit-Tests - ALLE 27 PASSED (1.75s)
- NullModelType Enum in kenobase/core/axioms.py korrekt definiert und importiert
- Drei Permutationsmethoden: schedule_permutation, block_permutation, iid_permutation
- FDR-Korrektur via benjamini_hochberg_fdr() implementiert
- Module korrekt in kenobase/analysis/__init__.py exponiert (Import verifiziert)
- Task kann als DONE markiert werden - Implementation vollstaendig

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_029_PROXY_IMPL_20251230_214053.md

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
task: TASK_029
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK_029_VALIDATOR_20251230_214253.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
