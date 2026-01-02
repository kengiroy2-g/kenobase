AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Datenquellen validieren und Qualitaet pruefen
TASK-ID: TASK-F02
PRIORITY: HIGH
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 13:09:04] TASK-F02 - EXECUTOR (ki2)

### Summary
- Datenquellen-Validierung abgeschlossen: KENO, EuroJackpot, Lotto verifiziert
- KENO Hauptdatei (data/raw/keno): 2238 Zeilen, 23 Spalten, Schema konsistent
- KENO Gewinnquoten (Keno_GPTs): 27685 Zeilen, BOM-Encoding bestaetigt (utf-8-sig)
- EuroJackpot: 528 Zeilen, Schema S1;S2;z1-z5 verifiziert
- Lotto Archiv: 4887 Zeilen (ab 1955), sauberes Schema Datum,z1-z6
- Schema-Heterogenitaet: 4 verschiedene Konventionen dokumentiert
- Alle Dateien haben Windows-Zeilenenden (CRLF) - konsistent
- Keine Code-Aenderungen erforderlich (Validierungs-Task)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-F02_EXECUTOR_20251227_130604.md

## [2025-12-27 13:11:04] TASK-F02 - PROXY_IMPL (ki0)

### Summary
- Alle Daten-Claims des Executors verifiziert
- KENO: 2238 Zeilen (bestaetigt), 23 Spalten, BOM-Encoding (ef bb bf = UTF-8 BOM)
- KENO Gewinnquoten: 27685 Zeilen (bestaetigt), BOM-Issue mit utf-8-sig dokumentiert
- EuroJackpot: 528 Zeilen (bestaetigt), Schema Datum;S1;S2;z1-z5 korrekt
- Lotto Archiv: 4887 Zeilen (bestaetigt), Schema Datum,z1-z6 korrekt
- Schema-Heterogenitaet: 4 Konventionen (Semikolon vs Komma, S1/S2 vs nur z-Spalten)
- Keine Code-Aenderungen (Validierungs-Task) - korrekt
- Keine RED FLAGS: keine fehlenden Integrationen, keine globalen Thresholds

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-F02_PROXY_IMPL_20251227_130904.md



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
- [x] Keine neuen Bugs eingefuehrt
- [x] BUG-001 bis BUG-010 nicht relevant (keine Code-Aenderungen)
- KENO: 2238 Zeilen, 22 Spalten
- Lotto: 639 Zeilen
- KENO: 2238 Zeilen, 23 Spalten
- Lotto Archiv: 4887 Zeilen (nicht 639)

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
- Alle Daten-Claims des Executors verifiziert
- KENO: 2238 Zeilen (bestaetigt), 23 Spalten, BOM-Encoding (ef bb bf = UTF-8 BOM)
- KENO Gewinnquoten: 27685 Zeilen (bestaetigt), BOM-Issue mit utf-8-sig dokumentiert
- EuroJackpot: 528 Zeilen (bestaetigt), Schema Datum;S1;S2;z1-z5 korrekt
- Lotto Archiv: 4887 Zeilen (bestaetigt), Schema Datum,z1-z6 korrekt
- Schema-Heterogenitaet: 4 Konventionen (Semikolon vs Komma, S1/S2 vs nur z-Spalten)
- Keine Code-Aenderungen (Validierungs-Task) - korrekt
- Keine RED FLAGS: keine fehlenden Integrationen, keine globalen Thresholds

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-F02_PROXY_IMPL_20251227_130904.md

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
task: TASK-F02
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK-F02_VALIDATOR_20251227_131104.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
