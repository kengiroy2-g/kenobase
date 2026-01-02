AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P1-03: Data Loader refactoren
TASK-ID: phase1_task03_data_loader
PRIORITY: P0
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-26 18:02:20] phase1_task03_data_loader - ARCHITECT (ki1)

### Summary
- KENO 22 Spalten semicolon dd.mm.yyyy Keno_Z1 to Keno_Z20 Plus5 Spieleinsatz
- EuroJackpot Komplex-Format mit 5 aus 50 String-Spalte plus EZ-Spalten semicolon
- Lotto_Archiv_ab-1955 7 Spalten KOMMA-Delimiter dd.mm.yyyy z1 to z6
- lotto_Stats_ab-2018 28plus Spalten semicolon Gewinnzahlen als String braucht Split
- Drei Parser-Klassen KenoParser EuroJackpotParser LottoParser
- Auto-Format-Erkennung via Header-Inspection
- Output DrawResult date numbers bonus game_type metadata
- Pydantic-Validation plus Pandas DataFrame Output

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_phase1_task03_data_loader_ARCHITECT_20251226_175520.md

## [2025-12-26 18:04:20] phase1_task03_data_loader - PROXY_PLAN (ki0)

### Summary
- KENO Format verifiziert: 22 Spalten, Semikolon, Zahlen separiert (Keno_Z1-Z20)
- EuroJackpot KRITISCH KORRIGIERT: Zahlen in Spalten 1-7 nach Datum, NICHT String
- EuroJackpot Spalten: Datum;Z1;Z2;Z3;Z4;Z5;EZ1;EZ2;Spieleinsatz;...
- Lotto Alt (ab-1955): Komma-Delimiter, 7 Spalten (Datum,z1-z6), einfachstes Format
- Lotto Neu (ab-2018): Semikolon, Spalte "Gewinnzahlen" als String braucht Split
- Plan passt zu config.py LegacyConfig (csv_delimiter, csv_date_format)
- Auto-Format-Erkennung via Header-Inspektion ist korrekt konzipiert
- DrawResult Pydantic-Model mit date/numbers/bonus/game_type sinnvoll

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase1_task03_data_loader_PROXY_PLAN_20251226_180220.md



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
- AI_COLLABORATION/HANDOFFS/ki1_phase1_task03_data_loader_ARCHITECT_20251226_174920.mdKeno_GPTs/Daten/Lotto_Archiv_ab-1955.csv (erste 5 Zeilen)Keno_GPTs/Daten/lotto_Stats_ab-2018.csv (erste 5 Zeilen)kenobase/core/config.py (bereits gelesen)AI_COLLABORATION/HANDOFFS/ki1_phase1_task03_data_loader_ARCHITECT_20251226_175520.md

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
- KENO Format verifiziert: 22 Spalten, Semikolon, Zahlen separiert (Keno_Z1-Z20)
- EuroJackpot KRITISCH KORRIGIERT: Zahlen in Spalten 1-7 nach Datum, NICHT String
- EuroJackpot Spalten: Datum;Z1;Z2;Z3;Z4;Z5;EZ1;EZ2;Spieleinsatz;...
- Lotto Alt (ab-1955): Komma-Delimiter, 7 Spalten (Datum,z1-z6), einfachstes Format
- Lotto Neu (ab-2018): Semikolon, Spalte "Gewinnzahlen" als String braucht Split
- Plan passt zu config.py LegacyConfig (csv_delimiter, csv_date_format)
- Auto-Format-Erkennung via Header-Inspektion ist korrekt konzipiert
- DrawResult Pydantic-Model mit date/numbers/bonus/game_type sinnvoll

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase1_task03_data_loader_PROXY_PLAN_20251226_180220.md

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
task: phase1_task03_data_loader
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_phase1_task03_data_loader_EXECUTOR_20251226_180420.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
