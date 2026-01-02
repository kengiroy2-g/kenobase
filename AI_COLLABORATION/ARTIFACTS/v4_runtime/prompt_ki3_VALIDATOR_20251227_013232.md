AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: DATA-02: EuroJackpot-Daten migrieren
TASK-ID: data_migration_eurojackpot
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 01:30:31] data_migration_eurojackpot - EXECUTOR (ki2)

### Summary
- Created target directory data/raw/eurojackpot/
- Copied eurojackpot_archiv_bereinigt.csv from Keno_GPTs/ to target (527 data rows)
- Fixed DataLoader._detect_format() to recognize bereinigt format (S1;S2;z1-z5 header)
- Fixed DataLoader._parse_eurojackpot() to handle both standard and bereinigt formats
- Bereinigt format: S1,S2=EuroZahlen (bonus), z1-z5=Hauptzahlen (inverted from standard)
- Verified: 526 draws loaded correctly with proper number/bonus separation
- All 33 DataLoader unit tests pass

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_data_migration_eurojackpot_EXECUTOR_20251227_012631.md

## [2025-12-27 01:32:32] data_migration_eurojackpot - PROXY_IMPL (ki0)

### Summary
- File migration verified: Keno_GPTs/ -> data/raw/eurojackpot/ (identical, N=528 lines, 527 data rows)
- DataLoader._detect_format() correctly identifies bereinigt format via S1+z1 header check (line 200-202)
- DataLoader._parse_eurojackpot() handles both standard and bereinigt formats (line 336-346)
- Bereinigt column mapping: S1,S2=EuroZahlen (bonus), z1-z5=Hauptzahlen (main) - CORRECT
- Integration test verified: 526 draws loaded, first draw 27.10.2023 numbers=[6,13,15,20,40] bonus=[2,8]
- Config path matches: legacy.eurojackpot_file = "eurojackpot/eurojackpot_archiv_bereinigt.csv" (line 117)
- All 33 DataLoader unit tests pass (pytest 0.48s)
- Syntax check: py_compile PASSED

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_data_migration_eurojackpot_PROXY_IMPL_20251227_013031.md



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
- kenobase/core/data_loader.py
- Keno_GPTs/eurojackpot_archiv_bereinigt.csv
- config/default.yaml
- tests/fixtures/eurojackpot_sample.csv
- data/raw/eurojackpot/eurojackpot_archiv_bereinigt.csv (new)

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
- File migration verified: Keno_GPTs/ -> data/raw/eurojackpot/ (identical, N=528 lines, 527 data rows)
- DataLoader._detect_format() correctly identifies bereinigt format via S1+z1 header check (line 200-202)
- DataLoader._parse_eurojackpot() handles both standard and bereinigt formats (line 336-346)
- Bereinigt column mapping: S1,S2=EuroZahlen (bonus), z1-z5=Hauptzahlen (main) - CORRECT
- Integration test verified: 526 draws loaded, first draw 27.10.2023 numbers=[6,13,15,20,40] bonus=[2,8]
- Config path matches: legacy.eurojackpot_file = "eurojackpot/eurojackpot_archiv_bereinigt.csv" (line 117)
- All 33 DataLoader unit tests pass (pytest 0.48s)
- Syntax check: py_compile PASSED

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_data_migration_eurojackpot_PROXY_IMPL_20251227_013031.md

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
task: data_migration_eurojackpot
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_data_migration_eurojackpot_VALIDATOR_20251227_013232.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
