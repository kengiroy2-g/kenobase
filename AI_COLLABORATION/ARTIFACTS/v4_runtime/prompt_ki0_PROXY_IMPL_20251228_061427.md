AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Jackpot-Timing Analyse
TASK-ID: TASK-R02
PRIORITY: HIGH
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 06:12:27] TASK-R02 - PROXY_PLAN (ki0)

### Summary
- Plan vollstaendig: Script + Modul + Daten vorhanden
- Acceptance Criteria klar: Chi-Square p > 0.05 = random, p < 0.05 = pattern
- Repro-Befehl verifiziert
- Datenquelle existiert: Keno_GPTs/10-9_KGDaten_gefiltert.csv
- Granularitaet korrekt: per-game (Keno-9 vs Keno-10)
- Keine Integration Bugs: standalone HYP-002 Analyse
- Chi-Square Test bei n < 20 korrekt abgelehnt
- EXECUTOR muss nur Script ausfuehren und JSON validieren

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-R02_PROXY_PLAN_20251228_061027.md

## [2025-12-28 06:14:27] TASK-R02 - EXECUTOR (ki2)

### Summary
- Script ausgefuehrt: python scripts/analyze_hyp002.py --data-path Keno_GPTs/10-9_KGDaten_gefiltert.csv --output results/hyp002_gk1_waiting.json
- 20 GK1-Records geladen (9 Keno-9, 11 Keno-10)
- Chi-Quadrat Test korrekt abgelehnt (n < 20 pro Typ)
- Keno-9 Statistik: mean=19.2 Tage, CV=0.95, 1 Outlier (57 Tage)
- Keno-10 Statistik: mean=51.2 Tage, CV=0.70, 0 Outliers
- HYP-002 NICHT BESTAETIGT: Wartezeiten folgen Zufallsverteilung
- acceptance_criteria_met: true (wg. insufficient data fuer Chi-Square)
- JSON-Output validiert: alle erwarteten Felder vorhanden

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-R02_EXECUTOR_20251228_061227.md



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
- scripts/analyze_hyp002.py
- kenobase/analysis/gk1_waiting.py
- kenobase/core/data_loader.py
- Keno_GPTs/10-9_KGDaten_gefiltert.csv
- AI_COLLABORATION/BACKLOG/KENOBASE_ISSUES.md
- results/hyp002_gk1_waiting.json

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
- Script ausgefuehrt: python scripts/analyze_hyp002.py --data-path Keno_GPTs/10-9_KGDaten_gefiltert.csv --output results/hyp002_gk1_waiting.json
- 20 GK1-Records geladen (9 Keno-9, 11 Keno-10)
- Chi-Quadrat Test korrekt abgelehnt (n < 20 pro Typ)
- Keno-9 Statistik: mean=19.2 Tage, CV=0.95, 1 Outlier (57 Tage)
- Keno-10 Statistik: mean=51.2 Tage, CV=0.70, 0 Outliers
- HYP-002 NICHT BESTAETIGT: Wartezeiten folgen Zufallsverteilung
- acceptance_criteria_met: true (wg. insufficient data fuer Chi-Square)
- JSON-Output validiert: alle erwarteten Felder vorhanden

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-R02_EXECUTOR_20251228_061227.md

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
task: TASK-R02
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK-R02_PROXY_IMPL_20251228_061427.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
