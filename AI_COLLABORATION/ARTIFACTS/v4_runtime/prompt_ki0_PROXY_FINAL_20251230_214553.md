AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Nullmodell: Permutationstest
TASK-ID: TASK_029
PRIORITY: P2
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
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

## [2025-12-30 21:45:53] TASK_029 - VALIDATOR (ki3)

### Summary
- TASK_029 (Nullmodell Permutationstest) VALIDATED and APPROVED
- kenobase/analysis/null_models.py (522 lines) - All functions verified
- tests/unit/test_null_models.py - 27/27 tests PASSED (1.74s)
- All module exports importable (NullModelRunner, schedule_permutation, block_permutation, iid_permutation, benjamini_hochberg_fdr)
- NullModelType enum (7 types) confirmed in kenobase/core/axioms.py
- Smoke test verified: NullModelRunner + FDR correction working
- Implementation complete - Task ready for DONE status

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK_029_VALIDATOR_20251230_214253.md



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
ROLLE: PROXY (User-Stellvertreter - Finale Freigabe)
AUFGABE: Finale Freigabe mit Projekt-Perspektive.

PFLICHTLEKTUERE (kurz):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Falls Zweifel an Integration

EFFIZIENZ-REGELN:
- Nutze VALIDATOR OUTPUT + dein Wissen aus vorherigen Proxy-Phasen
- Keine weiteren Tests, nur finale Entscheidung

VALIDATOR OUTPUT (kurz):
- TASK_029 (Nullmodell Permutationstest) VALIDATED and APPROVED
- kenobase/analysis/null_models.py (522 lines) - All functions verified
- tests/unit/test_null_models.py - 27/27 tests PASSED (1.74s)
- All module exports importable (NullModelRunner, schedule_permutation, block_permutation, iid_permutation, benjamini_hochberg_fdr)
- NullModelType enum (7 types) confirmed in kenobase/core/axioms.py
- Smoke test verified: NullModelRunner + FDR correction working
- Implementation complete - Task ready for DONE status

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK_029_VALIDATOR_20251230_214253.md

FINALE PRUEFUNG:
1. Hat Validator alle kritischen Aspekte geprueft?
2. Wuerde der USER diese Aenderung akzeptieren?
3. Gibt es offene Architektur-Fragen die der User entscheiden sollte?

ESKALATION an User wenn:
- Architektur-Entscheidung noetig die nicht in ADRs dokumentiert ist
- Unsicherheit ueber globale vs spezifische Werte
- Potenzielle Breaking Changes

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: COMPLETE
task: TASK_029
role: PROXY
phase: PROXY_FINAL
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

# Proxy Final Review

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_029_PROXY_FINAL_20251230_214553.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
