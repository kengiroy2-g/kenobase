AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Jackpot-Hoehe vs. Zahlentyp Korrelation
TASK-ID: HOUSE-001
PRIORITY: P1
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 20:14:04] HOUSE-001 - PROXY_PLAN (ki0)

### Summary
- Plan folgt bewaehrtem Muster von odds_correlation.py (HYP-010)
- Datenquelle 10-9_KGDaten_gefiltert.csv hat korrektes Format
- Jackpot=0 Gewinner bei 10/10 ist korrekter Proxy fuer hohe Jackpots
- Zahlentypen Birthday(1-31), Hoch(32-70) konsistent mit Projekt
- __init__.py muss erweitert werden (Integration Point beachtet)
- Acceptance Criteria (|r|>0.2, p<0.05, Chi-Quadrat) sind messbar
- Script-Name: scripts/analyze_hyp015_jackpot.py (Konsistenz)
- APPROVED - weiter zu EXECUTOR

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HOUSE-001_PROXY_PLAN_20251228_201203.md

## [2025-12-28 20:20:04] HOUSE-001 - EXECUTOR (ki2)

### Summary
- Created jackpot_correlation.py module (557 lines) following odds_correlation.py pattern
- Implemented GK1Event, NumberTypeStats, JackpotCorrelationResult, JackpotAnalysisSummary dataclasses
- Functions: load_gk1_events, analyze_jackpot_correlation, chi_square_test, run_hyp015_analysis
- Created test_jackpot_correlation.py with 32 unit tests (all passing)
- Created analyze_hyp015_jackpot.py CLI script
- Updated __init__.py with 22 new exports for HYP-015
- Analysis ran successfully: N=737 draws, 18 jackpot, 719 normal
- Result: NO significant correlation (Pearson r=0.017, p=0.65, Chi2 p=0.74)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HOUSE-001_EXECUTOR_20251228_201404.md



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
- kenobase/core/data_loader.py
- config/default.yaml
- Keno_GPTs/10-9_KGDaten_gefiltert.csv
- data/raw/keno/KENO_ab_2018.csv
- kenobase/analysis/jackpot_correlation.py
- tests/unit/test_jackpot_correlation.py
- scripts/analyze_hyp015_jackpot.py
- results/hyp015_jackpot_correlation.json

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
- Created jackpot_correlation.py module (557 lines) following odds_correlation.py pattern
- Implemented GK1Event, NumberTypeStats, JackpotCorrelationResult, JackpotAnalysisSummary dataclasses
- Functions: load_gk1_events, analyze_jackpot_correlation, chi_square_test, run_hyp015_analysis
- Created test_jackpot_correlation.py with 32 unit tests (all passing)
- Created analyze_hyp015_jackpot.py CLI script
- Updated __init__.py with 22 new exports for HYP-015
- Analysis ran successfully: N=737 draws, 18 jackpot, 719 normal
- Result: NO significant correlation (Pearson r=0.017, p=0.65, Chi2 p=0.74)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HOUSE-001_EXECUTOR_20251228_201404.md

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
task: HOUSE-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_HOUSE-001_PROXY_IMPL_20251228_202004.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
