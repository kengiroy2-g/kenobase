AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Basis-Zahlenpool und Index-System ermitteln
TASK-ID: HYP-005
PRIORITY: HIGH
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
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

## [2025-12-27 13:59:06] HYP-005 - VALIDATOR (ki3)

### Summary
- Module import OK: 6 symbols exportiert (NumberIndex, IndexResult, CorrelationResult, calculate_index_table, calculate_index_correlation, export_index_table)
- __init__.py exports OK: Alle Symbole via kenobase.analysis importierbar
- calculate_index_table PASS: Index-Berechnung korrekt (Zaehlung, Reset-Logik)
- calculate_index_correlation PASS: Edge-case "Insufficient data" korrekt behandelt
- JSON-Output valide: 70 Indices, last_reset_date, draws_since_reset, gk1_event_type vorhanden
- Syntax + Type Hints: PASS
- CLI Validation HYP-005-GK1: CONFIRMED (p=0.0419, High-Index 3.17 vs Low-Index 3.08)
- Effect Size gering (0.06) - wissenschaftlich korrekt dokumentiert

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_HYP-005_VALIDATOR_20251227_135606.md



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
ROLLE: PROXY (User-Stellvertreter - Finale Freigabe)
AUFGABE: Finale Freigabe mit Projekt-Perspektive.

PFLICHTLEKTUERE (kurz):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Falls Zweifel an Integration

EFFIZIENZ-REGELN:
- Nutze VALIDATOR OUTPUT + dein Wissen aus vorherigen Proxy-Phasen
- Keine weiteren Tests, nur finale Entscheidung

VALIDATOR OUTPUT (kurz):
- Module import OK: 6 symbols exportiert (NumberIndex, IndexResult, CorrelationResult, calculate_index_table, calculate_index_correlation, export_index_table)
- __init__.py exports OK: Alle Symbole via kenobase.analysis importierbar
- calculate_index_table PASS: Index-Berechnung korrekt (Zaehlung, Reset-Logik)
- calculate_index_correlation PASS: Edge-case "Insufficient data" korrekt behandelt
- JSON-Output valide: 70 Indices, last_reset_date, draws_since_reset, gk1_event_type vorhanden
- Syntax + Type Hints: PASS
- CLI Validation HYP-005-GK1: CONFIRMED (p=0.0419, High-Index 3.17 vs Low-Index 3.08)
- Effect Size gering (0.06) - wissenschaftlich korrekt dokumentiert

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_HYP-005_VALIDATOR_20251227_135606.md

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
task: HYP-005
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_HYP-005_PROXY_FINAL_20251227_135906.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
