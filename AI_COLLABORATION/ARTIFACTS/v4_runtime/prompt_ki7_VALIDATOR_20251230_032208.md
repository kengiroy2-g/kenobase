AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Spieler-Popularitaet als Risiko-Proxy modellieren (Birthday/Pattern-Risk)
TASK-ID: POP-001
PRIORITY: MITTEL
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 03:20:07] POP-001 - EXECUTOR (ki6)

### Summary
- Neues Modul popularity_risk.py mit PopularityRiskScore, calculate_pattern_risk_score(), estimate_competition_factor(), should_play()
- Wiederverwendung von calculate_birthday_score() Logik aus popularity_correlation.py
- 43 Unit Tests, alle bestanden (AC-1 bis AC-5 abgedeckt)
- Integration in analysis/__init__.py mit allen Exports
- Backtest-Script scripts/backtest_popularity_risk.py erstellt
- Axiom-First basiert auf A2 (Dauerscheine) und A3 (Attraktivitaet)
- Competition-Factor Berechnung auf empirischen Daten (HYP-004 r=0.3921, 1.3x Winner-Ratio)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_POP-001_EXECUTOR_20251230_031307.md

## [2025-12-30 03:22:08] POP-001 - PROXY_IMPL (ki0)

### Summary
- Modul popularity_risk.py syntaktisch korrekt, alle 43 Unit Tests bestanden
- Integration in analysis/__init__.py vollstaendig (alle Exports vorhanden)
- Backtest-Script syntaktisch korrekt und lauffaehig
- AC-1 bis AC-5 durch Tests abgedeckt (Score 0-1, Monotonie, Integration, Null-Model, Coverage)
- BIRTHDAY_NUMBERS dupliziert in popularity_risk.py und popularity_correlation.py - akzeptabel (keine Cross-Import)
- Keine globalen Thresholds (BUG-001 avoided) - Parameter sind konfigurierbar
- Axiom-First Basis dokumentiert (A2/A3)
- Kein Architektur-Konflikt mit bestehenden Modulen

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_POP-001_PROXY_IMPL_20251230_032008.md



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
- kenobase/analysis/popularity_risk.py
- kenobase/analysis/__init__.py
- tests/unit/test_popularity_risk.py
- scripts/backtest_popularity_risk.py

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
- Modul popularity_risk.py syntaktisch korrekt, alle 43 Unit Tests bestanden
- Integration in analysis/__init__.py vollstaendig (alle Exports vorhanden)
- Backtest-Script syntaktisch korrekt und lauffaehig
- AC-1 bis AC-5 durch Tests abgedeckt (Score 0-1, Monotonie, Integration, Null-Model, Coverage)
- BIRTHDAY_NUMBERS dupliziert in popularity_risk.py und popularity_correlation.py - akzeptabel (keine Cross-Import)
- Keine globalen Thresholds (BUG-001 avoided) - Parameter sind konfigurierbar
- Axiom-First Basis dokumentiert (A2/A3)
- Kein Architektur-Konflikt mit bestehenden Modulen

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_POP-001_PROXY_IMPL_20251230_032008.md

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
task: POP-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki7_POP-001_VALIDATOR_20251230_032208.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
