AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Konzept-Synthese erstellen
TASK-ID: TASK-F01
PRIORITY: CRITICAL
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 12:49:03] TASK-F01 - PROXY_PLAN (ki0)

### Summary
- V2.0 Modernisierung COMPLETE: kenobase/ mit 18 .py Dateien in core/, analysis/, physics/, pipeline/
- Backlog: 20 Issues (2 DONE, 18 OFFEN) - strukturiert nach HOCH/MITTEL/NIEDRIG
- Physics Layer vollstaendig implementiert: model_laws.py, avalanche.py, metrics.py
- Thresholds: per-game bereits umgesetzt (ISSUE-002 DONE)
- Naechste Prioritaet korrekt: HYP-009 (Chi-Quadrat) -> HYP-005 (Zahlenpool)
- Datenquellen dokumentiert in DATA_SOURCES.md, Master-Script vorhanden
- Keine RED FLAGS: Keine globalen Werte wo spielspezifische noetig
- Plan ist konsistent mit CLAUDE.md Architektur

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-F01_PROXY_PLAN_20251227_124703.md

## [2025-12-27 12:51:03] TASK-F01 - EXECUTOR (ki2)

### Summary
- Konzept-Synthese COMPLETE: Kenobase V2.0 vollstaendig dokumentiert
- Struktur verifiziert: 18 Python-Module in 4 Packages (core, analysis, physics, pipeline)
- Backlog analysiert: 20 Issues (2 DONE, 18 OFFEN), Prioritaeten klar definiert
- Hypothesen-Katalog: 12 Hypothesen, empfohlene Reihenfolge HYP-009 -> HYP-005
- Physics Layer COMPLETE: model_laws.py, avalanche.py, metrics.py implementiert
- Per-Game Thresholds DONE (ISSUE-002): F1 31x Verbesserung bei EuroJackpot
- Datenquellen dokumentiert: DATA_SOURCES.md + master_update.py vorhanden
- Naechster Schritt: HYP-009 Chi-Quadrat Test starten

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-F01_EXECUTOR_20251227_124903.md



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
- AI_COLLABORATION/HANDOFFS/ki2_TASK-F01_EXECUTOR_20251227_124903.md

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
AUFGABE: Pruefe die Implementation - NICHT nur mechanisch, sondern auf Architektur-Konsistenz.

PFLICHTLEKTUERE (vor Review):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Known Bugs & Integration Points
2. AI_COLLABORATION/SYSTEM_STATUS.json - Bei Architektur-Fragen

EFFIZIENZ-REGELN:
- Arbeite mit VORHERIGER OUTPUT + WORKING SET + Profil-Wissen
- Maximal 3-4 gezielte Reads
- Minimaler Sanity-Check (python -m py_compile, JSON-Validierung)

VORHERIGER OUTPUT (kurz):
- Konzept-Synthese COMPLETE: Kenobase V2.0 vollstaendig dokumentiert
- Struktur verifiziert: 18 Python-Module in 4 Packages (core, analysis, physics, pipeline)
- Backlog analysiert: 20 Issues (2 DONE, 18 OFFEN), Prioritaeten klar definiert
- Hypothesen-Katalog: 12 Hypothesen, empfohlene Reihenfolge HYP-009 -> HYP-005
- Physics Layer COMPLETE: model_laws.py, avalanche.py, metrics.py implementiert
- Per-Game Thresholds DONE (ISSUE-002): F1 31x Verbesserung bei EuroJackpot
- Datenquellen dokumentiert: DATA_SOURCES.md + master_update.py vorhanden
- Naechster Schritt: HYP-009 Chi-Quadrat Test starten

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-F01_EXECUTOR_20251227_124903.md

PRUEFKRITERIEN (4 Dimensionen):
1. MECHANISCH: Alle Schritte ausgefuehrt? Syntax OK? Acceptance Criteria erfuellt?
2. ARCHITEKTUR: Implementation passt zu ADRs? Keine Widersprueche eingefuehrt?
3. INTEGRATION: ALLE betroffenen Dateien geaendert? (siehe Known Integration Points)
   - hybrid_prediction_engine.py geaendert? -> production_orchestrator.py pruefen!
   - Config geaendert? -> Code der Config liest pruefen!
   - Threshold geaendert? -> Ist er global oder spezifisch?
4. KNOWN BUGS: Keiner der 10 Known Bugs reproduziert? (BUG-001 bis BUG-010)

RED FLAGS (sofort REJECTED):
- Aenderung in Datei A ohne korrespondierende Aenderung in Datei B
- Globale Werte wo spezifische noetig (BUG-001)
- Feature implementiert aber nicht im Orchestrator eingebunden (BUG-003)
- Config-Pfad im Code stimmt nicht mit YAML-Struktur (BUG-002)

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: APPROVED
task: TASK-F01
role: PROXY
phase: PROXY_IMPL
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

# Proxy Review (Implementation)

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK-F01_PROXY_IMPL_20251227_125103.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
