AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P1-03: Data Loader refactoren
TASK-ID: phase1_task03_data_loader
PRIORITY: P0
PHASE: PROXY_PLAN

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
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
ROLLE: PROXY (User-Stellvertreter mit Projekt-Kontext)
AUFGABE: Pruefe den Plan vom ARCHITECT - NICHT nur mechanisch, sondern konzeptionell.

PFLICHTLEKTUERE (vor Review lesen):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Dein vollstaendiges Profil mit Known Bugs
2. AI_COLLABORATION/SYSTEM_STATUS.json - Aktueller Projektstatus
3. CLAUDE.md - Projektkontext (bei Architektur-Fragen)

EFFIZIENZ-REGELN:
- Arbeite mit VORHERIGER OUTPUT + TASK NOTES + Profil-Wissen
- Maximal 3-4 gezielte Reads (Profil, Status, relevante Dateien)
- Keine breiten Repo-Scans

VORHERIGER OUTPUT (kurz, no logs):
- KENO 22 Spalten semicolon dd.mm.yyyy Keno_Z1 to Keno_Z20 Plus5 Spieleinsatz
- EuroJackpot Komplex-Format mit 5 aus 50 String-Spalte plus EZ-Spalten semicolon
- Lotto_Archiv_ab-1955 7 Spalten KOMMA-Delimiter dd.mm.yyyy z1 to z6
- lotto_Stats_ab-2018 28plus Spalten semicolon Gewinnzahlen als String braucht Split
- Drei Parser-Klassen KenoParser EuroJackpotParser LottoParser
- Auto-Format-Erkennung via Header-Inspection
- Output DrawResult date numbers bonus game_type metadata
- Pydantic-Validation plus Pandas DataFrame Output

FULL HANDOFF (nur bei Bedarf oeffnen):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_phase1_task03_data_loader_ARCHITECT_20251226_175520.md

PRUEFKRITERIEN (4 Dimensionen):
1. MECHANISCH: Plan vollstaendig? Schritte klar? Acceptance Criteria messbar?
2. ARCHITEKTUR: Passt zu ADRs? Keine Widersprueche?
3. INTEGRATION: Werden alle betroffenen Dateien genannt? (siehe Known Integration Points im Profil)
4. KONZEPTIONELL: Globale Werte wo spezifische noetig? Known Bugs vermieden?

RED FLAGS (sofort REJECTED):
- Globale Thresholds in team-spezifischem System (BUG-001)
- Feature ohne Orchestrator-Integration (BUG-003)
- Cross-File Aenderung ohne alle Dateien (Known Integration Points)

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: APPROVED
task: phase1_task03_data_loader
role: PROXY
phase: PROXY_PLAN
reviewed_handoff: "<nur filename oder leer>"
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

# Proxy Review

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki0_phase1_task03_data_loader_PROXY_PLAN_20251226_180220.md
- YAML Frontmatter mit status:
  - APPROVED: Plan ist gut, weiter zu Executor
  - REJECTED: Bug gefunden, zurueck zu Architect
  - ESCALATE: User-Entscheidung noetig (Architektur-Frage, Design-Wahl)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung (max 8 bullets)
