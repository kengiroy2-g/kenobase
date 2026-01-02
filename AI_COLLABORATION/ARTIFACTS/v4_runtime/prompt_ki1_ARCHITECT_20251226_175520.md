AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P1-03: Data Loader refactoren
TASK-ID: phase1_task03_data_loader
PRIORITY: P0
PHASE: ARCHITECT

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-26 17:52:20] phase1_task03_data_loader - ARCHITECT (ki1)

### Summary
- DataLoader muss CSV/JSON mit Schema-Validierung unterstuetzen
- Drei CSV-Formate identifiziert: KENO (22 cols), EuroJackpot (7 cols), Lotto (8+ cols)
- Delimiter ';', Datumsformat '%d.%m.%Y' aus LegacyConfig nutzen
- Pydantic-basierte Schema-Validierung analog zu config.py
- Integration mit KenobaseConfig.legacy fuer Dateipfade
- Output: DataFrame mit standardisierten Spalten (date, numbers[], bonus[])
- Unit-Tests: Schema-Fehler, leere Dateien, ungueltige Daten
- Ziel: kenobase/core/data_loader.py mit >80% Coverage

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_phase1_task03_data_loader_ARCHITECT_20251226_174920.md

## [2025-12-26 17:55:20] phase1_task03_data_loader - PROXY_PLAN (ki0)

### Summary
- KENO CSV-Format korrekt analysiert (22 cols, ';', dd.mm.yyyy)
- EuroJackpot hat 8 Spalten nicht 7: Datum;S1;S2;z1;z2;z3;z4;z5 (Bonus zuerst!)
- KRITISCH: Lotto-Format komplett falsch! Ist: "ISO-Datum,zahlen-mit-bindestrich
- Lotto_archiv_bereinigt.csv nutzt NICHT Semikolon sondern Komma und Bindestriche
- Plan muss Lotto-Parser komplett ueberarbeiten (Format-Erkennung noetig)
- Integration mit LegacyConfig prinzipiell korrekt konzipiert
- Pydantic-basierte Validierung passend zu config.py
- Working-Set-Request: Lotto-Alternativ-Datei pruefen (s. Daten/Lotto_Archiv_ab-1955.csv)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase1_task03_data_loader_PROXY_PLAN_20251226_175220.md



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
- AI_COLLABORATION/HANDOFFS/ki1_phase1_task03_data_loader_ARCHITECT_20251226_174920.mdKeno_GPTs/Daten/Lotto_Archiv_ab-1955.csv (erste 5 Zeilen)Keno_GPTs/Daten/lotto_Stats_ab-2018.csv (erste 5 Zeilen)kenobase/core/config.py (bereits gelesen)

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
ROLLE: ARCHITECT
AUFGABE: Erstelle detaillierten Implementierungsplan.

EFFIZIENZ-REGELN (wie normal CLI):
- Kein Repo-weiter Scan (kein rekursives Listing, kein breitflÃ¤chiges Grep).
- Arbeite primÃ¤r mit WORKING SET + TASK NOTES; wenn leer: max 2 gezielte Datei-Finder-Queries, dann stoppen und fehlende Pfade anfordern.
- Keine Status-/Messaging-Dateien lesen/schreiben (queue/CURRENT_STATUS) ausser explizit verlangt.
- Keine langen Tool-Outputs im Handoff; grosse Logs nach AI_COLLABORATION/ARTIFACTS/ auslagern und verlinken.

SCHRITTE:
1. Analysiere Anforderungen
2. Identifiziere betroffene Dateien
3. Erstelle Schritt-fuer-Schritt Checkliste
4. Definiere Acceptance Criteria

TOKEN HYGIENE:
- Output muss direkt das Handoff-Markdown sein (keine Diffs, keine Zusatztexte).
- Schreibe Handoff mit YAML Frontmatter (---\nstatus: COMPLETE\n...\n---)
- Max 8 summary bullets
- Keine langen Logs/Diffs im Body (nur Pfade)

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: COMPLETE
task: phase1_task03_data_loader
role: ARCHITECT
phase: ARCHITECT
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

# Implementierungsplan

WICHTIG: Erstelle Handoff-Datei wenn fertig:
- Datei: AI_COLLABORATION/HANDOFFS/ki1_phase1_task03_data_loader_ARCHITECT_20251226_175520.md
- YAML mit status: COMPLETE
- YAML mit files_changed: [...]
