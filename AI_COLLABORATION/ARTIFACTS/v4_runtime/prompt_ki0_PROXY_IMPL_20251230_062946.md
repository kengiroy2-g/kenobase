AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Zahlen-Arbitrage
TASK-ID: STRAT-002
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 06:23:45] STRAT-002 - PROXY_PLAN (ki0)

### Summary
- Plan korrekt strukturiert mit 4 Phasen und klaren Acceptance Criteria
- Granularitaet per-number-pair ist richtig (nicht global)
- Train/Test Split 2022-2023 vs 2024+ korrekt spezifiziert
- EuroJackpot als Negativ-Kontrolle eingebaut (Axiom-First konform)
- Bestehende cross_lottery_coupling.py Funktionen werden korrekt genutzt
- Einzige robuste Edge (KENO->AUSWAHLWETTE, lag=7, lift=2.41, q=0.027) ist gut dokumentiert
- Frozen-Rules im Test-Set garantiert (keine Parameter-Aenderungen)
- ROI-Warnung bei >0% eingebaut (physisch unplausibel wg Axiom A1)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_STRAT-002_PROXY_PLAN_20251230_062145.md

## [2025-12-30 06:29:46] STRAT-002 - EXECUTOR (ki2)

### Summary
- Created kenobase/analysis/number_arbitrage.py with Train/Test split, frozen-rules, null model
- Created scripts/backtest_number_arbitrage.py with full backtest workflow
- Created tests/unit/test_number_arbitrage.py with 13 passing unit tests
- Backtest result: 0 rules discovered in train, 0 significant in test (edge does not persist)
- EuroJackpot negative control correctly shows 0 rules (Axiom-First compliant)
- ROI sanity check with Axiom A1 warning implemented
- Null model baseline: mean_max_lift=0.93, 95th_pctl=3.05

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_STRAT-002_EXECUTOR_20251230_062345.md



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
- kenobase/core/normalizer.py
- results/ecosystem_graph.json
- scripts/analyze_cross_lottery_coupling.py
- tests/unit/test_cross_lottery_coupling.py
- kenobase/analysis/number_arbitrage.py
- scripts/backtest_number_arbitrage.py
- tests/unit/test_number_arbitrage.py
- results/number_arbitrage_backtest.json

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
- Created kenobase/analysis/number_arbitrage.py with Train/Test split, frozen-rules, null model
- Created scripts/backtest_number_arbitrage.py with full backtest workflow
- Created tests/unit/test_number_arbitrage.py with 13 passing unit tests
- Backtest result: 0 rules discovered in train, 0 significant in test (edge does not persist)
- EuroJackpot negative control correctly shows 0 rules (Axiom-First compliant)
- ROI sanity check with Axiom A1 warning implemented
- Null model baseline: mean_max_lift=0.93, 95th_pctl=3.05

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_STRAT-002_EXECUTOR_20251230_062345.md

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
task: STRAT-002
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_STRAT-002_PROXY_IMPL_20251230_062946.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
