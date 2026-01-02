AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Regionale Verteilungs-Framework
TASK-ID: TASK-R00
PRIORITY: CRITICAL
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 02:30:17] TASK-R00 - EXECUTOR (ki2)

### Summary
- Task-Schliessung verifiziert - keine Code-Aenderungen erforderlich
- HYP-003 bereits als WON'T FIX in KENOBASE_ISSUES.md:711-741 dokumentiert
- Keine regionalen Daten in verfuegbaren Quellen (Keno_GQ_*.csv nur aggregiert)
- Proxy-Approval bestaetigt Task-Schliessung ohne Implementation
- Kein Executor-Code notwendig - reine Dokumentations-Task
- Verwandte Analyse HYP-010 nutzt bereits verfuegbare aggregierte Daten

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-R00_EXECUTOR_20251228_022917.md

## [2025-12-28 02:32:17] TASK-R00 - PROXY_IMPL (ki0)

### Summary
- Task-Schliessung korrekt - HYP-003 als WON'T FIX dokumentiert
- Dokumentation verifiziert in KENOBASE_ISSUES.md:711-741
- WON'T FIX Begruendung ist faktenbasiert und vollstaendig
- Keine Code-Aenderungen erforderlich - files_changed: [] ist korrekt
- Daten-Analyse bestaetigt: Keno_GQ_*.csv nur aggregierte nationale Daten
- Alternative (Web-Scraping) korrekt als Out of Scope bewertet
- Verweis auf HYP-010 als verwandte Analyse ist korrekt
- Keine Integration-Issues - reine Dokumentations-Task

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-R00_PROXY_IMPL_20251228_023017.md



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
- Daten-Analyse bestaetigt: Keno_GQ_*.csv nur aggregierte nationale Daten
- Alternative (Web-Scraping) korrekt als Out of Scope bewertet
- Verweis auf HYP-010 als verwandte Analyse ist korrekt
- Keine Integration-Issues - reine Dokumentations-Task

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
- Task-Schliessung korrekt - HYP-003 als WON'T FIX dokumentiert
- Dokumentation verifiziert in KENOBASE_ISSUES.md:711-741
- WON'T FIX Begruendung ist faktenbasiert und vollstaendig
- Keine Code-Aenderungen erforderlich - files_changed: [] ist korrekt
- Daten-Analyse bestaetigt: Keno_GQ_*.csv nur aggregierte nationale Daten
- Alternative (Web-Scraping) korrekt als Out of Scope bewertet
- Verweis auf HYP-010 als verwandte Analyse ist korrekt
- Keine Integration-Issues - reine Dokumentations-Task

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-R00_PROXY_IMPL_20251228_023017.md

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
task: TASK-R00
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK-R00_VALIDATOR_20251228_023217.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
