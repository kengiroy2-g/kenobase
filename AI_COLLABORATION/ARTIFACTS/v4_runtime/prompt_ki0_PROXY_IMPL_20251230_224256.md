AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Verlust-Serien Analyse
TASK-ID: TASK_033
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 22:34:56] TASK_033 - ARCHITECT (ki1)

### Summary
- Verlust-Serien (Loss Streak) Analyse fuer KENO-Backtests
- Neue Metriken max_loss_streak, max_drawdown_pct, drawdown_duration
- Null-Model Vergleich (random tickets) zur Validierung
- Neue Script scripts/analyze_loss_streaks.py
- Unit-Tests in tests/unit/test_loss_streaks.py
- Axiom-First Nutzt A1 (House-Edge) plus A7 (Reset-Zyklen)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_033_ARCHITECT_20251230_222956.md

## [2025-12-30 22:36:56] TASK_033 - PROXY_PLAN (ki0)

### Summary
- Plan ist mechanisch vollstaendig (Script, Unit-Tests, Output-Pfad)
- Granularitaet per-ticket-type passt zu SYSTEM_STATUS pair_based_tickets
- Null-Model Vergleich (random tickets) integriert existierendes null_models.py
- Metriken max_loss_streak, max_drawdown_pct sind klar definiert
- Axiom-Verknuepfung A1+A7 korrekt (House-Edge + Reset-Zyklen)
- Kein Konflikt mit bestehender ticket_backtester.py Architektur
- Repro-Kommando vollstaendig und ausfuehrbar
- Keine RED FLAGS gefunden

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_033_PROXY_PLAN_20251230_223456.md

## [2025-12-30 22:42:56] TASK_033 - EXECUTOR (ki2)

### Summary
- Created scripts/analyze_loss_streaks.py with loss streak, drawdown, recovery metrics
- Implemented is_payout() for KENO payout rules (Typ-2 to Typ-10)
- Created tests/unit/test_loss_streaks.py with 21 passing unit tests
- Null model comparison using 100 random ticket seeds
- Output saved to results/loss_streak_analysis.json (N=1457 draws)
- All keno types within null model 95th percentile (no anomalies detected)
- Axiom notes: A1 (house edge) and A7 (reset cycles) integrated

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_033_EXECUTOR_20251230_223656.md



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
- scripts/analyze_loss_streaks.py
- tests/unit/test_loss_streaks.py
- results/loss_streak_analysis.json

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
- Created scripts/analyze_loss_streaks.py with loss streak, drawdown, recovery metrics
- Implemented is_payout() for KENO payout rules (Typ-2 to Typ-10)
- Created tests/unit/test_loss_streaks.py with 21 passing unit tests
- Null model comparison using 100 random ticket seeds
- Output saved to results/loss_streak_analysis.json (N=1457 draws)
- All keno types within null model 95th percentile (no anomalies detected)
- Axiom notes: A1 (house edge) and A7 (reset cycles) integrated

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_033_EXECUTOR_20251230_223656.md

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
task: TASK_033
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_033_PROXY_IMPL_20251230_224256.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
