AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Korrelations-Analysen
TASK-ID: ISSUE-004
PRIORITY: MEDIUM
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 15:51:11] ISSUE-004 - PROXY_IMPL (ki0)

### Summary
- BUG-FIX verifiziert: parallel if-Statements (pattern.py:118-131) korrekt
- 16/16 Unit-Tests PASSED (mathematisch korrekt: C(n,k) Formeln)
- Neue Funktionen (calculate_pattern_lift, calculate_feature_importance, get_significant_patterns) importierbar
- Backtest-Script syntaktisch OK (py_compile passed)
- Backtest-Artefakt vorhanden: 218 Folds, 2237 Ziehungen, JSON valide
- ADR-002 dokumentiert Bug-Fix mit Validierungsmatrix
- Acceptance Criteria: 2/3 passed (Lift ~1.0 entspricht Zufall - statistisch korrekt)
- KEINE Integration-Issues: Modul ist Standalone-Analyse ohne Orchestrator-Kopplung

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_ISSUE-004_PROXY_IMPL_20251227_154811.md

## [2025-12-27 15:53:11] ISSUE-004 - VALIDATOR (ki3)

### Summary
- Unit-Tests: 16/16 PASSED (test_pattern.py, 0.79s)
- BUG-FIX verifiziert: parallel if-Statements (pattern.py:118-131)
- Neue Funktionen importierbar: calculate_pattern_lift, calculate_feature_importance, get_significant_patterns
- Backtest-Script: py_compile PASSED
- ADR-002: Vollstaendig dokumentiert mit Validation-Matrix
- Artefakt: pattern_backtest_test.json (218 Folds, 2237 Ziehungen)
- Statistisches Ergebnis: Lift ~1.0 (KENO-RNG funktioniert korrekt)
- Acceptance Criteria: 2/3 passed (korrekt)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_ISSUE-004_VALIDATOR_20251227_155111.md



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
- scripts/backtest_patterns.py (NEU, 450 LOC)
- kenobase/analysis/pattern.py (ERWEITERUNG, +150 LOC)
- docs/adr/ADR-002-PATTERN-BUGFIX.md (NEU)
- AI_COLLABORATION/ARTIFACTS/pattern_backtest_test.json (OUTPUT)

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
- Unit-Tests: 16/16 PASSED (test_pattern.py, 0.79s)
- BUG-FIX verifiziert: parallel if-Statements (pattern.py:118-131)
- Neue Funktionen importierbar: calculate_pattern_lift, calculate_feature_importance, get_significant_patterns
- Backtest-Script: py_compile PASSED
- ADR-002: Vollstaendig dokumentiert mit Validation-Matrix
- Artefakt: pattern_backtest_test.json (218 Folds, 2237 Ziehungen)
- Statistisches Ergebnis: Lift ~1.0 (KENO-RNG funktioniert korrekt)
- Acceptance Criteria: 2/3 passed (korrekt)

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_ISSUE-004_VALIDATOR_20251227_155111.md

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
task: ISSUE-004
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_ISSUE-004_PROXY_FINAL_20251227_155311.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
