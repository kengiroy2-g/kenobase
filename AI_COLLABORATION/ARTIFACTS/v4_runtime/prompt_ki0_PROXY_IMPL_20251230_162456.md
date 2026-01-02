AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Gewinnklassen-Verteilung
TASK-ID: TASK_010
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 16:21:56] TASK_010 - ARCHITECT (ki1)

### Summary
- Gewinnklassen-System bereits vollstaendig implementiert in kenobase/prediction/win_class_calculator.py
- Single Source of Truth fuer Quoten in kenobase/core/keno_quotes.py (Zeilen 16-26)
- GK_LABELS_BY_TYPE Mapping generiert GK1-GKn automatisch aus Quoten-Tabelle
- Dataclasses WinClassResult + TicketEvaluation fuer strukturierte Ergebnisse
- Unit Tests vorhanden in tests/unit/test_win_class_calculator.py (234 Zeilen)
- Kein neuer Code erforderlich - Task ist Feature-Complete

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_010_ARCHITECT_20251230_161956.md

## [2025-12-30 16:23:56] TASK_010 - PROXY_PLAN (ki0)

### Summary
- Gewinnklassen-System vollstaendig implementiert und verifiziert
- Single Source of Truth (keno_quotes.py:16-26) korrekt referenziert
- GK_LABELS_BY_TYPE automatisch generiert aus Quoten-Tabelle
- Dataclasses WinClassResult + TicketEvaluation sauber definiert
- Unit Tests: 20 Tests, alle PASSED (pytest run live verifiziert)
- Integration mit V1/V2 Tickets funktional
- Kein neuer Code erforderlich - Task ist Feature-Complete
- ARCHITECT-Empfehlung "COMPLETE" ist korrekt

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_010_PROXY_PLAN_20251230_162156.md

## [2025-12-30 16:24:56] TASK_010 - EXECUTOR (ki2)

### Summary
- Gewinnklassen-System vollstaendig implementiert (win_class_calculator.py: 221 Zeilen)
- Single Source of Truth verifiziert (keno_quotes.py:16-26)
- Unit Tests 20/20 PASSED (pytest run verifiziert)
- GK_LABELS_BY_TYPE automatisch generiert aus KENO_FIXED_QUOTES_BY_TYPE
- Dataclasses WinClassResult + TicketEvaluation vorhanden
- Kein neuer Code erforderlich - Task war bereits Feature-Complete

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_010_EXECUTOR_20251230_162356.md



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
- (leer)

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
- Gewinnklassen-System vollstaendig implementiert (win_class_calculator.py: 221 Zeilen)
- Single Source of Truth verifiziert (keno_quotes.py:16-26)
- Unit Tests 20/20 PASSED (pytest run verifiziert)
- GK_LABELS_BY_TYPE automatisch generiert aus KENO_FIXED_QUOTES_BY_TYPE
- Dataclasses WinClassResult + TicketEvaluation vorhanden
- Kein neuer Code erforderlich - Task war bereits Feature-Complete

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_010_EXECUTOR_20251230_162356.md

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
task: TASK_010
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_010_PROXY_IMPL_20251230_162456.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
