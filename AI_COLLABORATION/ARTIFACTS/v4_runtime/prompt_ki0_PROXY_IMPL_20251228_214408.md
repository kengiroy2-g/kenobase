AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Gewinnklassen-Verteilungsmuster
TASK-ID: DIST-001
PRIORITY: P1
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 21:38:07] DIST-001 - ARCHITECT (ki1)

### Summary
- Task HYP-001 Gewinnklassen-Verteilungsmuster vollstaendig analysieren
- Datenquelle Keno_GPTs/Keno_GQ_2022_2023-2024.csv
- Existierend kenobase/analysis/distribution.py scripts/analyze_distribution.py
- Offen Near-Miss Analyse Gewinnklassen-Matrix Zeitliche Korrelation
- Neuer Task scripts/analyze_hyp001_complete.py erstellen
- Output results/hyp001_distribution_complete.json
- Zeitraum 2022-2024 ca 800 Ziehungstage

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_DIST-001_ARCHITECT_20251228_213307.md

## [2025-12-28 21:40:07] DIST-001 - PROXY_PLAN (ki0)

### Summary
- Plan vollstaendig und mechanisch korrekt
- Datenquelle Keno_GPTs/Keno_GQ_2022_2023-2024.csv existiert (verifiziert via Glob)
- Existierende Module nutzen: kenobase/analysis/distribution.py + near_miss.py
- Near-Miss Logik bereits implementiert in near_miss.py (Zeilen 87-148) - wiederverwenden
- Gewinnklassen-Matrix (9x11) ist sinnvoll, passt zu DistributionResult Struktur
- Zeitliche Korrelation fehlt in bisherigen Modulen - muss neu implementiert werden
- Unit-Tests vorhanden: tests/unit/test_near_miss.py (untracked)
- Akzeptanzkriterien sind messbar und klar definiert

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DIST-001_PROXY_PLAN_20251228_213807.md

## [2025-12-28 21:44:08] DIST-001 - EXECUTOR (ki2)

### Summary
- Script scripts/analyze_hyp001_complete.py erstellt mit 4 Analysen
- Near-Miss fuer Typ 8/9/10 berechnet (AC1 PASS)
- Gewinnklassen-Matrix mit 36 Eintraegen erstellt (AC2 PASS)
- Zeitliche Korrelation mit 7 Lags dokumentiert (AC3 PASS)
- Hypothese bewertet als TEILWEISE (AC4 PASS)
- Report gespeichert in results/hyp001_distribution_complete.json (AC5 PASS)
- 12 Unit-Tests alle PASSED (AC6 PASS)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_DIST-001_EXECUTOR_20251228_214007.md



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
- scripts/analyze_hyp001_complete.py (NEU, 382 Zeilen)
- tests/unit/test_distribution.py (NEU, 286 Zeilen)

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
- Script scripts/analyze_hyp001_complete.py erstellt mit 4 Analysen
- Near-Miss fuer Typ 8/9/10 berechnet (AC1 PASS)
- Gewinnklassen-Matrix mit 36 Eintraegen erstellt (AC2 PASS)
- Zeitliche Korrelation mit 7 Lags dokumentiert (AC3 PASS)
- Hypothese bewertet als TEILWEISE (AC4 PASS)
- Report gespeichert in results/hyp001_distribution_complete.json (AC5 PASS)
- 12 Unit-Tests alle PASSED (AC6 PASS)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_DIST-001_EXECUTOR_20251228_214007.md

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
task: DIST-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_DIST-001_PROXY_IMPL_20251228_214408.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
