AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Train->Test: frozen Couplings im Test validieren
TASK-ID: VALID-001
PRIORITY: HOCH
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 06:03:52] VALID-001 - PROXY_PLAN (ki0)

### Summary
- ARCHITECT correctly identified existing Train->Test infrastructure in scripts/backtest_cross_game_rule_layer_train_test.py
- Script implements proper frozen rules pattern: _mine_rules_train() called ONLY on train slices (lines 478-499)
- Rules are stored in rules_train, then passed to backtest WITHOUT re-mining (lines 526-539)
- Current result shows 0 rules mined at alpha=0.05 (train period 2022-2023 has no significant couplings)
- Validation gap is real: no unit test asserts the frozen-rules invariant
- Plan is actionable: add test that verifies rules passed to backtest are NOT re-fitted
- EuroJackpot correctly included as source but NOT treated as ecosystem member (consistent with CLAUDE.md)
- Repro command verified: output file exists with expected structure

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_VALID-001_PROXY_PLAN_20251230_060152.md

## [2025-12-30 06:07:53] VALID-001 - EXECUTOR (ki6)

### Summary
- Created tests/unit/test_frozen_rules_invariant.py with 6 unit tests
- Test 1: backtest_uses_rules_externally_no_mining - verifies backtest receives rules externally
- Test 2: rules_mined_on_train_are_frozen_on_test - validates Train->Test frozen rules workflow
- Test 3: frozen_rules_dataclass_is_immutable - confirms CrossGameRule is frozen=True
- Test 4: backtest_does_not_call_mining_functions - structural check no mining params in signature
- Test 5: train_test_split_no_data_leakage - verifies train dates never exceed train_end
- Test 6: same_rules_applied_to_all_test_draws - confirms consistent rule application
- All 6 tests pass (pytest 2.55s)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_VALID-001_EXECUTOR_20251230_060353.md



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
- tests/unit/test_frozen_rules_invariant.py

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
ROLLE: PROXY (User-Stellvertreter mit Projekt-Kontext)
AUFGABE: Pruefe die Implementation - NICHT nur mechanisch, sondern auf Architektur-Konsistenz.

PFLICHTLEKTUERE (vor Review):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Known Bugs & Integration Points
2. AI_COLLABORATION/SYSTEM_STATUS.json - Bei Architektur-Fragen

EFFIZIENZ-REGELN:
- Arbeite mit VORHERIGER OUTPUT + WORKING SET + Profil-Wissen
- Maximal 3-4 gezielte Reads
- Minimaler Sanity-Check (python -m py_compile, JSON-Validierung)

VORHERIGER OUTPUT (kurz):
- Created tests/unit/test_frozen_rules_invariant.py with 6 unit tests
- Test 1: backtest_uses_rules_externally_no_mining - verifies backtest receives rules externally
- Test 2: rules_mined_on_train_are_frozen_on_test - validates Train->Test frozen rules workflow
- Test 3: frozen_rules_dataclass_is_immutable - confirms CrossGameRule is frozen=True
- Test 4: backtest_does_not_call_mining_functions - structural check no mining params in signature
- Test 5: train_test_split_no_data_leakage - verifies train dates never exceed train_end
- Test 6: same_rules_applied_to_all_test_draws - confirms consistent rule application
- All 6 tests pass (pytest 2.55s)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_VALID-001_EXECUTOR_20251230_060353.md

PRUEFKRITERIEN (4 Dimensionen):
1. MECHANISCH: Alle Schritte ausgefuehrt? Syntax OK? Acceptance Criteria erfuellt?
2. ARCHITEKTUR: Implementation passt zu ADRs? Keine Widersprueche eingefuehrt?
3. INTEGRATION: ALLE betroffenen Dateien geaendert? (siehe Known Integration Points)
   - hybrid_prediction_engine.py geaendert? -> production_orchestrator.py pruefen!
   - Config geaendert? -> Code der Config liest pruefen!
   - Threshold geaendert? -> Ist er global oder spezifisch?
4. KNOWN BUGS: Keiner der 10 Known Bugs reproduziert? (BUG-001 bis BUG-010)

RED FLAGS (sofort REJECTED):
- Aenderung in Datei A ohne korrespondierende Aenderung in Datei B
- Globale Werte wo spezifische noetig (BUG-001)
- Feature implementiert aber nicht im Orchestrator eingebunden (BUG-003)
- Config-Pfad im Code stimmt nicht mit YAML-Struktur (BUG-002)

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: APPROVED
task: VALID-001
role: PROXY
phase: PROXY_IMPL
reviewed_handoff: "<nur filename oder leer>"
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

# Proxy Review (Implementation)

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki0_VALID-001_PROXY_IMPL_20251230_060753.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
