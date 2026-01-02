AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Basis-Zahlenpool und Index-System ermitteln
TASK-ID: HYP-005
PRIORITY: HIGH
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 13:54:06] HYP-005 - EXECUTOR (ki2)

### Summary
- Neues Modul number_index.py mit Index-Berechnung seit GK1-Reset implementiert
- calculate_index_table() berechnet Index fuer alle 70 Zahlen seit letztem GK1-Event
- calculate_index_correlation() analysiert Korrelation zwischen Index und Trefferrate
- GK1-Events heterogen (Keno-Typ 9 und 10) - beide werden als Reset behandelt
- Integration in validate_hypotheses.py als HYP-005-GK1
- Index-Tabelle exportiert nach data/results/hyp005_index_table.json
- HYP-005-GK1 CONFIRMED: p=0.0419, High-Index 3.17 vs. Low-Index 3.08
- Effect Size gering (0.06) - statistisch signifikant, praktisch marginal

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HYP-005_EXECUTOR_20251227_134806.md

## [2025-12-27 13:56:06] HYP-005 - PROXY_IMPL (ki0)

### Summary
- Neues Modul number_index.py korrekt implementiert mit Type Hints und Docstrings
- __init__.py Export aktualisiert mit allen 6 neuen Symbolen
- validate_hypotheses.py um HYP-005-GK1 erweitert mit korrekter Integration
- JSON-Output hyp005_index_table.json valide (70 Indices, last_reset_date vorhanden)
- Keine globalen Thresholds wo spezifische noetig (BUG-001 CLEAN)
- Eigenstaendiges Modul ohne Cross-File Dependencies (BUG-003 CLEAN)
- GK1-Events heterogen behandelt (Typ 9 und 10 beide als Reset) - korrekt
- Effect Size gering (0.06) aber statistisch signifikant - wissenschaftlich korrekt dokumentiert

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-005_PROXY_IMPL_20251227_135406.md



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
- kenobase/analysis/number_index.py (NEW)
- kenobase/analysis/__init__.py
- scripts/validate_hypotheses.py
- data/results/hyp005_index_table.json (NEW)

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
- Neues Modul number_index.py korrekt implementiert mit Type Hints und Docstrings
- __init__.py Export aktualisiert mit allen 6 neuen Symbolen
- validate_hypotheses.py um HYP-005-GK1 erweitert mit korrekter Integration
- JSON-Output hyp005_index_table.json valide (70 Indices, last_reset_date vorhanden)
- Keine globalen Thresholds wo spezifische noetig (BUG-001 CLEAN)
- Eigenstaendiges Modul ohne Cross-File Dependencies (BUG-003 CLEAN)
- GK1-Events heterogen behandelt (Typ 9 und 10 beide als Reset) - korrekt
- Effect Size gering (0.06) aber statistisch signifikant - wissenschaftlich korrekt dokumentiert

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-005_PROXY_IMPL_20251227_135406.md

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
task: HYP-005
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_HYP-005_VALIDATOR_20251227_135606.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
