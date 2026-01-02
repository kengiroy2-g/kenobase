AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Anti-Cluster Reset-Regel
TASK-ID: TASK-H03
PRIORITY: HIGH
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 22:23:48] TASK-H03 - PROXY_PLAN (ki0)

### Summary
- Plan folgt etabliertem Modul-Pattern (Dataclass + Analyse-Funktionen)
- Architektur konsistent mit recurrence.py Struktur
- Cluster-Threshold (5) ist sinnvoll fuer Keno-Kontext
- CLI-Integration in analyze_hyp003.py (neues Script, korrekt)
- Unit-Tests geplant
- Backtest-Validierung vorgesehen
- WARNUNG: Reset-Wahrscheinlichkeit 60% ist Annahme, muss validiert werden
- HINWEIS: Pruefe ob recurrence.py Funktionen wiederverwendbar sind

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-H03_PROXY_PLAN_20251227_222148.md

## [2025-12-27 22:29:48] TASK-H03 - EXECUTOR (ki2)

### Summary
- Created cluster_reset.py with ClusterEvent, ClusterResetResult, TradingSignal dataclasses
- Implemented detect_cluster_events() - finds clusters >= threshold (default 5)
- Implemented analyze_reset_probability() - calculates P(reset | cluster) empirically
- Implemented generate_trading_signals() - generates NO-BET signals for active clusters
- Implemented generate_cluster_reset_report() - full JSON report generation
- Added exports to kenobase/analysis/__init__.py
- Created CLI script scripts/analyze_hyp003.py with argparse interface
- Created 26 unit tests in tests/unit/test_cluster_reset.py - ALL PASSING

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-H03_EXECUTOR_20251227_222348.md



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
- kenobase/analysis/cluster_reset.py (NEW)
- kenobase/analysis/__init__.py (UPDATED)
- scripts/analyze_hyp003.py (NEW)
- tests/unit/test_cluster_reset.py (NEW)

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
- Created cluster_reset.py with ClusterEvent, ClusterResetResult, TradingSignal dataclasses
- Implemented detect_cluster_events() - finds clusters >= threshold (default 5)
- Implemented analyze_reset_probability() - calculates P(reset | cluster) empirically
- Implemented generate_trading_signals() - generates NO-BET signals for active clusters
- Implemented generate_cluster_reset_report() - full JSON report generation
- Added exports to kenobase/analysis/__init__.py
- Created CLI script scripts/analyze_hyp003.py with argparse interface
- Created 26 unit tests in tests/unit/test_cluster_reset.py - ALL PASSING

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-H03_EXECUTOR_20251227_222348.md

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
task: TASK-H03
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK-H03_PROXY_IMPL_20251227_222948.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
