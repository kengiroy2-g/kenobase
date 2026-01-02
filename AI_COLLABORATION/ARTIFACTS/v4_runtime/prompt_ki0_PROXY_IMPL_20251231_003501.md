AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: V1 vs V2 PARALLEL: Gesamt-Performance
TASK-ID: TASK_038
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-31 00:33:01] TASK_038 - PROXY_PLAN (ki0)

### Summary
- Plan basiert auf existierenden Artefakten - keine neuen Berechnungen noetig
- Datenintegritaet verifiziert: backtest_v1_v2_comparison.json enthaelt N=2237 (2018-2024)
- ROI-Behauptungen korrekt: V2 Typ6 pair_focused +53.24%, V2 Typ7 pair_focused +28.79%
- Kritische Warnung im Plan: Overfitting-Risiko angemessen dokumentiert
- SYSTEM_STATUS.json zeigt keine stabile positive ROI nach Quoten-Korrektur
- Plan fordert nur Synthese-Report, kein neuer Code - akzeptabel
- Acceptance Criteria sind messbar und erfuellt
- EXECUTOR Aufgaben klar definiert: results/v1_v2_performance_synthesis.md erstellen

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_038_PROXY_PLAN_20251231_003101.md

## [2025-12-31 00:35:01] TASK_038 - EXECUTOR (ki2)

### Summary
- Synthese-Report erstellt: results/v1_v2_performance_synthesis.md
- V2 pair_focused zeigt beste ROI (+53.24% Typ6, +28.79% Typ7)
- V1 hat kein Ticket mit positiver ROI (beste: -0.18%)
- Overfitting-Warnung dokumentiert (kein Train/Test-Split)
- N=2237 Ziehungen (2018-01-01 bis 2024-02-15) verifiziert
- SYSTEM_STATUS.json-Konsistenz geprueft: keine stabile positive ROI nach Quoten-Korrektur
- Top 5 Tickets tabellarisch aufgefuehrt
- Repro-Command dokumentiert

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_038_EXECUTOR_20251231_003301.md



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
- results/backtest_v1_v2_comparison.json
- results/super_model_comparison_summary.md
- kenobase/core/keno_quotes.py (falls Quote-Verifikation noetig)
- AI_COLLABORATION/HANDOFFS/ki1_TASK_038_ARCHITECT_20251231_002901.md
- results/v1_v2_performance_synthesis.md

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
- Synthese-Report erstellt: results/v1_v2_performance_synthesis.md
- V2 pair_focused zeigt beste ROI (+53.24% Typ6, +28.79% Typ7)
- V1 hat kein Ticket mit positiver ROI (beste: -0.18%)
- Overfitting-Warnung dokumentiert (kein Train/Test-Split)
- N=2237 Ziehungen (2018-01-01 bis 2024-02-15) verifiziert
- SYSTEM_STATUS.json-Konsistenz geprueft: keine stabile positive ROI nach Quoten-Korrektur
- Top 5 Tickets tabellarisch aufgefuehrt
- Repro-Command dokumentiert

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_038_EXECUTOR_20251231_003301.md

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
task: TASK_038
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_038_PROXY_IMPL_20251231_003501.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
