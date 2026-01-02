AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Top-Pool Size Optimierung
TASK-ID: TASK-M01
PRIORITY: MEDIUM
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 23:53:51] TASK-M01 - PROXY_PLAN (ki0)

### Summary
- Plan ist technisch korrekt und umsetzbar
- top_n_per_period=11 default in NumberPoolGenerator BESTAETIGT (number_pool.py:78)
- Parameter via Konstruktor konfigurierbar BESTAETIGT (Zeilen 78-79, 274-275)
- backtest.py existiert mit vollstaendigem Walk-Forward Framework (561 Zeilen)
- Config default.yaml enthaelt KEINEN top_n_per_period Eintrag - muss hinzugefuegt werden
- Neues Script optimize_pool_size.py soll Pool-Sizes [5,11,15,20] vergleichen
- Zielmetrik F1-Score ist korrekt (harmonisches Mittel P/R)
- ACHTUNG: backtest.py nutzt get_hot_numbers(), nicht NumberPoolGenerator direkt

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-M01_PROXY_PLAN_20251227_235151.md

## [2025-12-27 23:57:52] TASK-M01 - EXECUTOR (ki2)

### Summary
- Created scripts/optimize_pool_size.py (340 lines) - Walk-Forward optimization for top_n_per_period
- Added number_pool section to config/default.yaml with n_periods, draws_per_period, top_n_per_period, top_n_total
- Script tests pool sizes [5,11,15,20] via Walk-Forward backtest using F1-Score metric
- Optimization result (12 periods, 2237 draws): top_n=20 marginally best (F1=0.2469), top_n=11 close (F1=0.2424)
- Default top_n_per_period=11 retained (difference <2% F1, statistically insignificant)
- Results saved to results/pool_optimization.json with full metrics
- CLI verified: --help works, optimization runs successfully

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-M01_EXECUTOR_20251227_235351.md



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
- scripts/optimize_pool_size.py
- config/default.yaml
- results/pool_optimization.json

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
- Created scripts/optimize_pool_size.py (340 lines) - Walk-Forward optimization for top_n_per_period
- Added number_pool section to config/default.yaml with n_periods, draws_per_period, top_n_per_period, top_n_total
- Script tests pool sizes [5,11,15,20] via Walk-Forward backtest using F1-Score metric
- Optimization result (12 periods, 2237 draws): top_n=20 marginally best (F1=0.2469), top_n=11 close (F1=0.2424)
- Default top_n_per_period=11 retained (difference <2% F1, statistically insignificant)
- Results saved to results/pool_optimization.json with full metrics
- CLI verified: --help works, optimization runs successfully

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-M01_EXECUTOR_20251227_235351.md

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
task: TASK-M01
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK-M01_PROXY_IMPL_20251227_235752.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
