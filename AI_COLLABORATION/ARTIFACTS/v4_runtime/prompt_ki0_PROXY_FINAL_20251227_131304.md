AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Datenquellen validieren und Qualitaet pruefen
TASK-ID: TASK-F02
PRIORITY: HIGH
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
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

## [2025-12-27 13:13:04] TASK-F02 - VALIDATOR (ki3)

### Summary
- Alle Daten-Claims unabhaengig verifiziert
- KENO: 2238 Zeilen (bestaetigt), 23 Spalten (bestaetigt), kein BOM im Hauptfile
- KENO Gewinnquoten: 27685 Zeilen (bestaetigt), UTF-8 BOM (ef bb bf) bestaetigt
- EuroJackpot: 528 Zeilen (bestaetigt), Schema Datum;S1;S2;z1-z5 (bestaetigt)
- Lotto Archiv: 4887 Zeilen (bestaetigt), Schema Datum,z1-z6 (bestaetigt)
- Schema-Heterogenitaet: Semikolon (KENO/EJ) vs Komma (Lotto/GQ)
- Keine Code-Aenderungen erforderlich (Validierungs-Task)
- Task APPROVED - Datenquellen dokumentiert und validiert

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK-F02_VALIDATOR_20251227_131104.md



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
ROLLE: PROXY (User-Stellvertreter - Finale Freigabe)
AUFGABE: Finale Freigabe mit Projekt-Perspektive.

PFLICHTLEKTUERE (kurz):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Falls Zweifel an Integration

EFFIZIENZ-REGELN:
- Nutze VALIDATOR OUTPUT + dein Wissen aus vorherigen Proxy-Phasen
- Keine weiteren Tests, nur finale Entscheidung

VALIDATOR OUTPUT (kurz):
- Alle Daten-Claims unabhaengig verifiziert
- KENO: 2238 Zeilen (bestaetigt), 23 Spalten (bestaetigt), kein BOM im Hauptfile
- KENO Gewinnquoten: 27685 Zeilen (bestaetigt), UTF-8 BOM (ef bb bf) bestaetigt
- EuroJackpot: 528 Zeilen (bestaetigt), Schema Datum;S1;S2;z1-z5 (bestaetigt)
- Lotto Archiv: 4887 Zeilen (bestaetigt), Schema Datum,z1-z6 (bestaetigt)
- Schema-Heterogenitaet: Semikolon (KENO/EJ) vs Komma (Lotto/GQ)
- Keine Code-Aenderungen erforderlich (Validierungs-Task)
- Task APPROVED - Datenquellen dokumentiert und validiert

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK-F02_VALIDATOR_20251227_131104.md

FINALE PRUEFUNG:
1. Hat Validator alle kritischen Aspekte geprueft?
2. Wuerde der USER diese Aenderung akzeptieren?
3. Gibt es offene Architektur-Fragen die der User entscheiden sollte?

ESKALATION an User wenn:
- Architektur-Entscheidung noetig die nicht in ADRs dokumentiert ist
- Unsicherheit ueber globale vs spezifische Werte
- Potenzielle Breaking Changes

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: COMPLETE
task: TASK-F02
role: PROXY
phase: PROXY_FINAL
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

# Proxy Final Review

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK-F02_PROXY_FINAL_20251227_131304.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
