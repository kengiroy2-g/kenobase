AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Nullmodelle: schedule/block permutation
TASK-ID: NULL-001
PRIORITY: HOCH
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 02:44:06] NULL-001 - PROXY_IMPL (ki0)

### Summary
- Verified kenobase/analysis/null_models.py syntax OK (py_compile passed)
- Confirmed 27/27 unit tests pass in tests/unit/test_null_models.py
- NullModelType enum integration with axioms.py:17-26 is clean
- schedule_permutation() correctly preserves weekday structure
- block_permutation() correctly preserves weekly blocks
- benjamini_hochberg_fdr() implements FDR correction correctly
- analysis/__init__.py exports 10 new symbols correctly
- No Known Bugs (BUG-001 to BUG-010) reproduced

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_NULL-001_PROXY_IMPL_20251230_024206.md

## [2025-12-30 02:46:06] NULL-001 - VALIDATOR (ki7)

### Summary
- All 27 unit tests pass (pytest tests/unit/test_null_models.py -> 27 passed in 0.87s)
- Python syntax verified (py_compile passed)
- Module imports correctly with all 10 public symbols exported
- NullModelType enum integration verified (7 types available from axioms.py)
- schedule_permutation() preserves weekday structure (functional test passed)
- block_permutation() preserves weekly blocks (functional test passed)
- benjamini_hochberg_fdr() FDR correction functional (test passed)
- run_axiom_prediction_test() integrates with P1.3, P4.3, P6.3, P7.3 predictions

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki7_NULL-001_VALIDATOR_20251230_024406.md



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
- kenobase/analysis/null_models.py
- kenobase/analysis/__init__.py
- tests/unit/test_null_models.py

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
- All 27 unit tests pass (pytest tests/unit/test_null_models.py -> 27 passed in 0.87s)
- Python syntax verified (py_compile passed)
- Module imports correctly with all 10 public symbols exported
- NullModelType enum integration verified (7 types available from axioms.py)
- schedule_permutation() preserves weekday structure (functional test passed)
- block_permutation() preserves weekly blocks (functional test passed)
- benjamini_hochberg_fdr() FDR correction functional (test passed)
- run_axiom_prediction_test() integrates with P1.3, P4.3, P6.3, P7.3 predictions

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki7_NULL-001_VALIDATOR_20251230_024406.md

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
task: NULL-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_NULL-001_PROXY_FINAL_20251230_024606.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
