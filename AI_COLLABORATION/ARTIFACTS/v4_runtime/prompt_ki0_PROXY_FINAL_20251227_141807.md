AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Kern-Hypothesen Validierung
TASK-ID: HYP-002
PRIORITY: HIGH
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 14:15:07] HYP-002 - PROXY_IMPL (ki0)

### Summary
- calendar_features.py: Syntax valid, all functions implemented (extract_calendar_features, analyze_calendar_correlation, predict_next_gk1, to_dict)
- __init__.py correctly exports all 5 new symbols (CalendarFeatures, CalendarAnalysisResult, extract_calendar_features, analyze_calendar_correlation, predict_next_gk1)
- validate_hypotheses.py:310-314 imports from calendar_features; :370-379 integrates calendar and prediction
- hyp002_jackpot_cycles.json: valid JSON with complete structure (calendar_analysis, prediction, status, interpretation)
- Chi-square tests use correct threshold check (P_VALUE_THRESHOLD from line 382/396/398)
- No global thresholds introduced (BUG-001 avoided)
- Module is isolated - no unintended dependencies or coupling
- Repro command verified in handoff matches implementation

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-002_PROXY_IMPL_20251227_141307.md

## [2025-12-27 14:18:07] HYP-002 - VALIDATOR (ki3)

### Summary
- All 4 unit tests PASSED (extract_calendar_features, analyze_calendar_correlation, predict_next_gk1, to_dict)
- Import test PASSED: direct module import and package-level import both work
- Syntax check PASSED (py_compile)
- Type hints verified: all 4 functions have return type annotations
- End-to-end test PASSED: `python scripts/validate_hypotheses.py --hypothesis HYP-002` completes successfully
- JSON output structure valid: calendar_analysis, prediction, status all present
- Chi-square threshold uses P_VALUE_THRESHOLD constant (line 29, 382, 396, 398) - BUG-001 avoided
- Results deterministic: same output as EXECUTOR handoff (N=20, mean=43.3, KS p=0.588, status=RANDOM)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_HYP-002_VALIDATOR_20251227_141507.md




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
- kenobase/analysis/calendar_features.py (NEW)
- kenobase/analysis/__init__.py (MODIFIED)
- scripts/validate_hypotheses.py (MODIFIED)
- data/results/hyp002_jackpot_cycles.json (NEW)

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
- All 4 unit tests PASSED (extract_calendar_features, analyze_calendar_correlation, predict_next_gk1, to_dict)
- Import test PASSED: direct module import and package-level import both work
- Syntax check PASSED (py_compile)
- Type hints verified: all 4 functions have return type annotations
- End-to-end test PASSED: `python scripts/validate_hypotheses.py --hypothesis HYP-002` completes successfully
- JSON output structure valid: calendar_analysis, prediction, status all present
- Chi-square threshold uses P_VALUE_THRESHOLD constant (line 29, 382, 396, 398) - BUG-001 avoided
- Results deterministic: same output as EXECUTOR handoff (N=20, mean=43.3, KS p=0.588, status=RANDOM)

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_HYP-002_VALIDATOR_20251227_141507.md

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
task: HYP-002
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_HYP-002_PROXY_FINAL_20251227_141807.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
