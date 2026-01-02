AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Summen-Fenster Analyse
TASK-ID: TASK-M04
PRIORITY: MEDIUM
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 00:44:54] TASK-M04 - EXECUTOR (ki2)

### Summary
- Neues Modul kenobase/analysis/sum_distribution.py implementiert
- Script scripts/analyze_sum_windows.py erstellt mit CLI-Interface
- Config erweitert um analysis.sum_windows Sektion
- Analyse auf 2237 KENO-Ziehungen durchgefuehrt: mean=711.1, std=77.6
- Chi-Quadrat-Test gegen Gleichverteilung: p=0.0 (signifikant)
- Ein Cluster identifiziert: [605-845] mit 87.2% Dichte
- JSON-Export nach results/sum_windows_analysis.json verifiziert
- Plot-Generierung nach results/sum_windows_histogram.png verifiziert

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-M04_EXECUTOR_20251228_003954.md

## [2025-12-28 00:46:54] TASK-M04 - PROXY_IMPL (ki0)

### Summary
- Neues Modul sum_distribution.py (557 Zeilen) - Syntax OK, Import OK
- Script analyze_sum_windows.py (227 Zeilen) - Syntax OK, CLI komplett
- Config erweitert: analysis.sum_windows Sektion (Zeilen 84-94) korrekt integriert
- __init__.py korrekt erweitert mit Alias-Imports (HistogramBin -> SumHistogramBin etc.)
- JSON-Export verifiziert: results/sum_windows_analysis.json (2237 draws, mean=711.1)
- Chi-Quadrat-Test korrekt: p=0.0 (signifikant vs Gleichverteilung)
- Ein Cluster [605-845] mit 87.2% Dichte identifiziert
- Keine Known Bugs (BUG-001 bis BUG-010) reproduziert

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-M04_PROXY_IMPL_20251228_004454.md



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
- kenobase/core/combination_engine.py
- kenobase/core/data_loader.py
- config/default.yaml
- data/raw/keno/KENO_ab_2018.csv (Daten)
- kenobase/analysis/sum_distribution.py (NEU - 493 Zeilen)
- scripts/analyze_sum_windows.py (NEU - 227 Zeilen)
- config/default.yaml (analysis.sum_windows hinzugefuegt)
- kenobase/analysis/__init__.py (sum_distribution exports hinzugefuegt)

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
- Neues Modul sum_distribution.py (557 Zeilen) - Syntax OK, Import OK
- Script analyze_sum_windows.py (227 Zeilen) - Syntax OK, CLI komplett
- Config erweitert: analysis.sum_windows Sektion (Zeilen 84-94) korrekt integriert
- __init__.py korrekt erweitert mit Alias-Imports (HistogramBin -> SumHistogramBin etc.)
- JSON-Export verifiziert: results/sum_windows_analysis.json (2237 draws, mean=711.1)
- Chi-Quadrat-Test korrekt: p=0.0 (signifikant vs Gleichverteilung)
- Ein Cluster [605-845] mit 87.2% Dichte identifiziert
- Keine Known Bugs (BUG-001 bis BUG-010) reproduziert

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-M04_PROXY_IMPL_20251228_004454.md

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
task: TASK-M04
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK-M04_VALIDATOR_20251228_004654.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
