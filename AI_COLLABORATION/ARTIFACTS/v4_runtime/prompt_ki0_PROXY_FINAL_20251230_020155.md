AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Zahlenraum-Normalisierung
TASK-ID: DATA-002
PRIORITY: P2
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 01:59:55] DATA-002 - PROXY_IMPL (ki0)

### Summary
- normalizer.py implementiert korrekt (n-min)/(max-min) Formel
- Alle 43 Unit-Tests bestanden (pytest 0.40s)
- Syntax-Check fuer beide Dateien OK
- __init__.py korrekt um Normalizer-Exports erweitert
- Game ranges konsistent mit config/default.yaml (KENO 1-70, Lotto 1-49, EuroJackpot 1-50)
- Bonus-Handling korrekt: EuroZahlen 1-12, Superzahl 0-9, KENO Plus5 skipped
- cross_game_distance verwendet MAE - mathematisch korrekt
- Keine Known Bugs reproduziert, keine Architektur-Verletzungen

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DATA-002_PROXY_IMPL_20251230_015755.md

## [2025-12-30 02:01:55] DATA-002 - VALIDATOR (ki3)

### Summary
- All 43 unit tests passed (pytest 0.39s)
- Syntax check passed for normalizer.py and __init__.py
- Imports verified working from kenobase.core
- GAME_RANGES correct: KENO 1-70, Lotto 1-49, EuroJackpot 1-50
- Formula (n-min)/(max-min) correctly implemented with roundtrip verification
- Bonus handling: EuroZahlen 1-12, Superzahl 0-9, KENO Plus5 skipped (correct)
- cross_game_distance uses MAE - mathematically correct
- __init__.py exports all 11 normalizer symbols correctly

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_DATA-002_VALIDATOR_20251230_015955.md



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
- kenobase/core/normalizer.py
- kenobase/core/__init__.py
- tests/unit/test_normalizer.py

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
- All 43 unit tests passed (pytest 0.39s)
- Syntax check passed for normalizer.py and __init__.py
- Imports verified working from kenobase.core
- GAME_RANGES correct: KENO 1-70, Lotto 1-49, EuroJackpot 1-50
- Formula (n-min)/(max-min) correctly implemented with roundtrip verification
- Bonus handling: EuroZahlen 1-12, Superzahl 0-9, KENO Plus5 skipped (correct)
- cross_game_distance uses MAE - mathematically correct
- __init__.py exports all 11 normalizer symbols correctly

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_DATA-002_VALIDATOR_20251230_015955.md

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
task: DATA-002
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_DATA-002_PROXY_FINAL_20251230_020155.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
