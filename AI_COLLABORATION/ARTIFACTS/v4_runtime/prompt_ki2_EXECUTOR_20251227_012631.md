AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: DATA-02: EuroJackpot-Daten migrieren
TASK-ID: data_migration_eurojackpot
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 01:24:31] data_migration_eurojackpot - ARCHITECT (ki1)

### Summary
- Source data: Keno_GPTs/eurojackpot_archiv_bereinigt.csv (bereinigtes Format, N=~300 rows)
- Target location: data/raw/eurojackpot/eurojackpot_archiv_bereinigt.csv
- DataLoader already supports EuroJackpot via _parse_eurojackpot() method
- Config default.yaml already has eurojackpot_file path configured
- Two source formats detected: raw (ISO dates) and bereinigt (DD.MM.YYYY, columns S1,S2,z1-z5)
- Bereinigt format matches expected schema: Datum;S1;S2;z1;z2;z3;z4;z5
- DataLoader needs minor fix: expects columns 1-5 for main nums, 6-7 for euro, but bereinigt has S1,S2 first
- test fixture exists at tests/fixtures/eurojackpot_sample.csv (different format with header "5 aus 50")

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_data_migration_eurojackpot_ARCHITECT_20251227_012231.md

## [2025-12-27 01:26:31] data_migration_eurojackpot - PROXY_PLAN (ki0)

### Summary
- ARCHITECT correctly identified column order mismatch in bereinigt format
- Source: Keno_GPTs/eurojackpot_archiv_bereinigt.csv (N=527 data rows, header: Datum;S1;S2;z1;z2;z3;z4;z5)
- Bereinigt format: S1,S2=EuroZahlen (cols 1-2), z1-z5=Hauptzahlen (cols 3-7)
- Current DataLoader expects: cols 1-5=main, cols 6-7=euro (INVERTED)
- Test fixture has different format (5 aus 50;EZ headers, 7 numbers inline)
- Target directory data/raw/eurojackpot/ does not exist yet
- Fix requires: (1) copy file to target, (2) fix DataLoader column mapping for bereinigt format
- No architectural red flags - straightforward data migration with parser fix

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_data_migration_eurojackpot_PROXY_PLAN_20251227_012431.md



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
ROLLE: EXECUTOR
AUFGABE: Fuehre den genehmigten Plan aus.

EFFIZIENZ-REGELN:
- Starte mit WORKING SET; vermeide Repo-weite Scans. Wenn du suchen musst: 1 gezieltes Grep pro Subtask, nicht breit.
- Schreibe nur kurze, entscheidungsrelevante Logs; grosse Logs nach AI_COLLABORATION/ARTIFACTS/ auslagern und verlinken.
- Aktualisiere Status ausschliesslich ueber den Handoff (keine CURRENT_STATUS edits im Body).
- Aendere niemals AI_COLLABORATION/MESSAGE_QUEUE/* oder AI_COLLABORATION/RESULTS/CURRENT_STATUS.md (nur Handoff-Ausgabe).
- Vermeide das Ausgeben von Diffs (diff --git, Patch-BlÃ¶cke). In der Antwort nur Summary + Pfade.

PLAN (kurz):
- ARCHITECT correctly identified column order mismatch in bereinigt format
- Source: Keno_GPTs/eurojackpot_archiv_bereinigt.csv (N=527 data rows, header: Datum;S1;S2;z1;z2;z3;z4;z5)
- Bereinigt format: S1,S2=EuroZahlen (cols 1-2), z1-z5=Hauptzahlen (cols 3-7)
- Current DataLoader expects: cols 1-5=main, cols 6-7=euro (INVERTED)
- Test fixture has different format (5 aus 50;EZ headers, 7 numbers inline)
- Target directory data/raw/eurojackpot/ does not exist yet
- Fix requires: (1) copy file to target, (2) fix DataLoader column mapping for bereinigt format
- No architectural red flags - straightforward data migration with parser fix

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_data_migration_eurojackpot_PROXY_PLAN_20251227_012431.md

REGELN:
1. Folge Checkliste exakt
2. Keine eigenen Interpretationen
3. Dokumentiere jeden Schritt
4. WICHTIG: Fuege files_changed: [...] im YAML hinzu

TOKEN HYGIENE:
- Final Output muss direkt das Handoff-Markdown sein (keine Diffs, keine Zusatztexte).
- Keine langen Command-Outputs im Handoff
- Bei Fehlern: nur Command + 20 Zeilen excerpt
- Lange Logs: speichere in AI_COLLABORATION/ARTIFACTS/ und referenziere nur Pfad

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: COMPLETE
task: data_migration_eurojackpot
role: EXECUTOR
phase: EXECUTOR
files_changed: []
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

# Umsetzung

WICHTIG: Erstelle Handoff-Datei wenn fertig:
- Datei: AI_COLLABORATION/HANDOFFS/ki2_data_migration_eurojackpot_EXECUTOR_20251227_012631.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
