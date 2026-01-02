AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Langzeit-Zahlen-Balance mit Trigger-Analyse
TASK-ID: TASK-R05
PRIORITY: HIGH
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 08:25:42] TASK-R05 - EXECUTOR (ki2)

### Summary
- Neues Modul longterm_balance.py mit Balance-Score und Trigger-Erkennung
- Dataclasses: NumberBalanceStats, BalanceTrigger, BalanceResult
- Kernfunktionen: calculate_balance_score, detect_balance_triggers, analyze_longterm_balance
- CLI-Script analyze_longterm_balance.py mit --data, --window, --output
- 29 Unit-Tests alle PASSED
- Export in __init__.py hinzugefuegt
- Folgt Modul-Pattern aus cluster_reset.py

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-R05_EXECUTOR_20251228_082042.md

## [2025-12-28 08:27:42] TASK-R05 - PROXY_IMPL (ki0)

### Summary
- MECHANISCH: Alle 4 Dateien erstellt/modifiziert, Syntax OK (py_compile passed)
- MECHANISCH: 29/29 Unit-Tests PASSED
- ARCHITEKTUR: Folgt etabliertem Pattern aus cluster_reset.py
- ARCHITEKTUR: Dataclasses NumberBalanceStats, BalanceTrigger, BalanceResult korrekt definiert
- INTEGRATION: __init__.py Export vollstaendig (Zeilen 187-199 imports, 368-379 __all__)
- INTEGRATION: CLI-Script nutzt korrekten DataLoader + GameType.KENO
- KNOWN BUGS: Kein BUG-001 (per-number Granularitaet, nicht global)
- KNOWN BUGS: Kein BUG-002 (keine hardcodierte Config-Pfade)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-R05_PROXY_IMPL_20251228_082542.md

## [2025-12-28 08:30:42] TASK-R05 - VALIDATOR (ki3)

### Summary
- TESTS: 29/29 Unit-Tests PASSED (0.87s)
- SYNTAX: Alle 4 Dateien syntaktisch korrekt (py_compile passed)
- EXPORTS: Imports aus kenobase.analysis funktionieren
- CLI: analyze_longterm_balance.py --help funktioniert
- ARCHITECTURE: Dataclasses + Functions Pattern korrekt
- INTEGRATION: __init__.py Zeilen 187-199 (imports), 376-379 (__all__)
- EDGE-CASES: Getestet (single draw, exact window, biased data)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK-R05_VALIDATOR_20251228_082742.md



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
- kenobase/analysis/longterm_balance.py (NEW)
- kenobase/analysis/__init__.py (MODIFIED)
- scripts/analyze_longterm_balance.py (NEW)
- tests/unit/test_longterm_balance.py (NEW)

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
- TESTS: 29/29 Unit-Tests PASSED (0.87s)
- SYNTAX: Alle 4 Dateien syntaktisch korrekt (py_compile passed)
- EXPORTS: Imports aus kenobase.analysis funktionieren
- CLI: analyze_longterm_balance.py --help funktioniert
- ARCHITECTURE: Dataclasses + Functions Pattern korrekt
- INTEGRATION: __init__.py Zeilen 187-199 (imports), 376-379 (__all__)
- EDGE-CASES: Getestet (single draw, exact window, biased data)

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK-R05_VALIDATOR_20251228_082742.md

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
task: TASK-R05
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK-R05_PROXY_FINAL_20251228_083042.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
