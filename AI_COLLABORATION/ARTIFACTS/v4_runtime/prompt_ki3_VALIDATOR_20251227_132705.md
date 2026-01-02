AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Schnelle Hypothesen-Validierungen
TASK-ID: TASK-F03
PRIORITY: HIGH
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 13:25:05] TASK-F03 - EXECUTOR (ki2)

### Summary
- scripts/validate_hypotheses.py erstellt mit Chi-Quadrat, Zahlenpool-Index und Jackpot-Zyklen Tests
- HYP-009 (Chi-Quadrat): ACCEPTED - Zahlen gleichverteilt (p=0.9333), keine Manipulation detektiert
- HYP-005 (Zahlenpool-Index): REJECTED - 3.15 vs. 3.14 Treffer (Cohen's d=0.004), kein Vorhersagewert
- HYP-002 (Jackpot-Zyklen): RANDOM - Intervalle exponentiell (KS p=0.5878), keine Muster
- 2237 Ziehungen analysiert, 20 GK1-Events geprueft
- Alle 3 Hypothesen zeigen: KENO-Daten verhalten sich wie echter Zufall
- JSON-Ergebnisse in AI_COLLABORATION/ARTIFACTS/hypotheses_validation_results.json

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-F03_EXECUTOR_20251227_132105.md

## [2025-12-27 13:27:05] TASK-F03 - PROXY_IMPL (ki0)

### Summary
- scripts/validate_hypotheses.py syntaktisch korrekt (py_compile OK)
- JSON-Ergebnisdatei valide (AI_COLLABORATION/ARTIFACTS/hypotheses_validation_results.json)
- 3 Hypothesen korrekt implementiert: Chi-Quadrat, Zahlenpool-Index, Jackpot-Zyklen
- Acceptance Criteria erfuellt: p-Wert Threshold 0.05, statistische Tests korrekt angewandt
- HYP-009 nutzt scipy.stats.chisquare wie empfohlen
- HYP-005 verwendet t-Test mit Cohen's d Effect Size
- HYP-002 verwendet KS-Test gegen Exponentialverteilung + Runs-Test

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-F03_PROXY_IMPL_20251227_132505.md



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
- kenobase/analysis/frequency.py
- Keno_GPTs/10-9_KGDaten_gefiltert.csv
- data/raw/keno/KENO_ab_2018.csv
- requirements.txt
- scripts/validate_hypotheses.py
- AI_COLLABORATION/ARTIFACTS/hypotheses_validation_results.json

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
- scripts/validate_hypotheses.py syntaktisch korrekt (py_compile OK)
- JSON-Ergebnisdatei valide (AI_COLLABORATION/ARTIFACTS/hypotheses_validation_results.json)
- 3 Hypothesen korrekt implementiert: Chi-Quadrat, Zahlenpool-Index, Jackpot-Zyklen
- Acceptance Criteria erfuellt: p-Wert Threshold 0.05, statistische Tests korrekt angewandt
- HYP-009 nutzt scipy.stats.chisquare wie empfohlen
- HYP-005 verwendet t-Test mit Cohen's d Effect Size
- HYP-002 verwendet KS-Test gegen Exponentialverteilung + Runs-Test

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-F03_PROXY_IMPL_20251227_132505.md

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
task: TASK-F03
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK-F03_VALIDATOR_20251227_132705.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
