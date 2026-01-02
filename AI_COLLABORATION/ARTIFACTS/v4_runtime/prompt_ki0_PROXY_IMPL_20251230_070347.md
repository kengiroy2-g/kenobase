AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Zyklus-Surfen
TASK-ID: STRAT-004
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 06:59:47] STRAT-004 - PROXY_PLAN (ki0)

### Summary
- Plan korrekt: regime_detection.py + temporal_cycles.py existieren beide
- Train/Test Split via RegimeDetectionConfig.train_split_date = 2024-01-01 bestaetigt (Zeile 45)
- HMM-basierte Regime-Erkennung mit 4 States, mapping zu economic_state Labels
- temporal_cycles.py bietet weekday_analysis, month_analysis, holiday_proximity
- Benoetigter Output: Orchestrierungs-Script scripts/backtest_cycle_surfing.py
- Acceptance Criteria messbar: ROI vs. Baseline + Mann-Whitney U p<0.05
- Integration: Keine bestehenden Dateien muessen geaendert werden (nur neues Script)
- Kein BUG-001 (globale Thresholds) - verwendet per-draw Granularitaet

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_STRAT-004_PROXY_PLAN_20251230_065747.md

## [2025-12-30 07:03:47] STRAT-004 - EXECUTOR (ki2)

### Summary
- Created scripts/backtest_cycle_surfing.py combining regime_detection.py + temporal_cycles.py
- Implements HMM-based regime detection with train/test split at 2024-01-01 (configurable)
- Adds temporal filters: weekday bias (derived from train chi2) + holiday proximity (3-day window)
- Decision logic: PLAY if regime is favorable AND weekday passes AND not near holiday
- Hit metric: fraction of popular numbers (1-31) as ROI proxy
- Statistical test: Mann-Whitney U (one-sided) for strategy vs baseline comparison
- Output: results/cycle_surfing_backtest.json with full metrics and acceptance criteria
- Backtest result: NO_IMPROVEMENT (p=0.58) - strategy shows no significant edge

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_STRAT-004_EXECUTOR_20251230_070258.md



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
- scripts/backtest_cycle_surfing.py

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
- Created scripts/backtest_cycle_surfing.py combining regime_detection.py + temporal_cycles.py
- Implements HMM-based regime detection with train/test split at 2024-01-01 (configurable)
- Adds temporal filters: weekday bias (derived from train chi2) + holiday proximity (3-day window)
- Decision logic: PLAY if regime is favorable AND weekday passes AND not near holiday
- Hit metric: fraction of popular numbers (1-31) as ROI proxy
- Statistical test: Mann-Whitney U (one-sided) for strategy vs baseline comparison
- Output: results/cycle_surfing_backtest.json with full metrics and acceptance criteria
- Backtest result: NO_IMPROVEMENT (p=0.58) - strategy shows no significant edge

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_STRAT-004_EXECUTOR_20251230_070258.md

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
task: STRAT-004
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_STRAT-004_PROXY_IMPL_20251230_070347.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
