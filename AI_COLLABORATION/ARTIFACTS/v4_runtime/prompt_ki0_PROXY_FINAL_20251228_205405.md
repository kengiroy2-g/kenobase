AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Rolling House-Edge Stabilitaet
TASK-ID: HOUSE-003
PRIORITY: P1
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 20:52:05] HOUSE-003 - PROXY_IMPL (ki0)

### Summary
- Implementation is mechanically complete with all 5 files created/modified
- CV calculation (std/mean) mathematically correct in calculate_rolling_cv()
- Rolling windows 7/14/30 days correctly implemented
- Result shows NOT SUPPORTED (CV mean 45-54% vs threshold 15%) - scientifically valid negative result
- All 14 unit tests pass (verified via pytest)
- JSON output valid and properly serialized
- Exports correctly added to analysis/__init__.py (lines 248-255, 490)
- Reuse of StakeDrawRecord from stake_correlation.py is appropriate

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HOUSE-003_PROXY_IMPL_20251228_205005.md

## [2025-12-28 20:54:05] HOUSE-003 - VALIDATOR (ki3)

### Summary
- All 14 unit tests pass (pytest verified)
- CV calculation mathematically correct (manual verification: CV = std/mean matches module output)
- Rolling windows 7/14/30 days correctly produce n-window+1 positions
- Result NOT SUPPORTED is scientifically valid (CV mean 45-54% vs 15% threshold)
- JSON output valid with all required fields (results/house003_rolling_stability.json)
- Exports in __init__.py verified at lines 248-258 (imports) and 484-490 (__all__)
- Script analyze_house003.py runs successfully and produces correct output
- Code quality good: type hints, docstrings, frozen dataclasses

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_HOUSE-003_VALIDATOR_20251228_205205.md



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
- kenobase/analysis/house_edge_stability.py
- kenobase/analysis/__init__.py
- scripts/analyze_house003.py
- tests/unit/test_house_edge_stability.py
- results/house003_rolling_stability.json

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
- All 14 unit tests pass (pytest verified)
- CV calculation mathematically correct (manual verification: CV = std/mean matches module output)
- Rolling windows 7/14/30 days correctly produce n-window+1 positions
- Result NOT SUPPORTED is scientifically valid (CV mean 45-54% vs 15% threshold)
- JSON output valid with all required fields (results/house003_rolling_stability.json)
- Exports in __init__.py verified at lines 248-258 (imports) and 484-490 (__all__)
- Script analyze_house003.py runs successfully and produces correct output
- Code quality good: type hints, docstrings, frozen dataclasses

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_HOUSE-003_VALIDATOR_20251228_205205.md

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
task: HOUSE-003
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_HOUSE-003_PROXY_FINAL_20251228_205405.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
