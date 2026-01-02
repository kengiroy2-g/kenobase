AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: DATA-01: KENO-Daten migrieren
TASK-ID: data_migration_keno
PRIORITY: P1
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 01:16:31] data_migration_keno - EXECUTOR (ki2)

### Summary
- Created target directory data/raw/keno/
- Copied Keno_GPTs/Daten/KENO_Stats_ab-2018.csv to data/raw/keno/KENO_ab_2018.csv
- Verified source file: 2238 lines (1 header + 2237 data rows)
- Verified target file: identical 2238 lines, 193275 bytes
- Format verified: 22-col semicolon (Datum;Keno_Z1-Z20;Keno_Plus5;Keno_Spieleinsatz)
- DataLoader.load() validation: 2237 DrawResult objects loaded successfully
- No schema transformation required - format matches DataLoader._parse_keno()

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_data_migration_keno_EXECUTOR_20251227_011431.md

## [2025-12-27 01:18:31] data_migration_keno - PROXY_IMPL (ki0)

### Summary
- Target file exists: data/raw/keno/KENO_ab_2018.csv
- Line count verified: 2238 (1 header + 2237 data rows)
- Header format correct: 22-col semicolon Datum Keno_Z1-Z20 Keno_Plus5 Keno_Spieleinsatz
- DataLoader.load validation: 2237 DrawResult objects loaded successfully
- First record verified: 2018-01-01 numbers 1 6 11 19 21
- Config path match: config/default.yaml line 116 keno_file matches target location
- No architectural concerns - straightforward data migration
- No Known Bugs triggered BUG-001 to BUG-010 not applicable to data migration

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_data_migration_keno_PROXY_IMPL_20251227_011631.md



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
- data/raw/keno/KENO_ab_2018.csv

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
- Target file exists: data/raw/keno/KENO_ab_2018.csv
- Line count verified: 2238 (1 header + 2237 data rows)
- Header format correct: 22-col semicolon Datum Keno_Z1-Z20 Keno_Plus5 Keno_Spieleinsatz
- DataLoader.load validation: 2237 DrawResult objects loaded successfully
- First record verified: 2018-01-01 numbers 1 6 11 19 21
- Config path match: config/default.yaml line 116 keno_file matches target location
- No architectural concerns - straightforward data migration
- No Known Bugs triggered BUG-001 to BUG-010 not applicable to data migration

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_data_migration_keno_PROXY_IMPL_20251227_011631.md

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
task: data_migration_keno
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_data_migration_keno_VALIDATOR_20251227_011831.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
