AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: High-Win Forensik: Alle >450 EUR Events
TASK-ID: TASK_055
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2026-01-01 01:17:10] TASK_055 - PROXY_PLAN (ki0)

### Summary
- Two-step workflow verified: backtest (threshold filter) -> forensik (reads events)
- Step 1: backtest_high_payout_tickets.py --threshold 451 generates filtered events
- Step 2: analyze_high_win_forensik.py --backtest <step1_output> runs forensik
- forensik script extracts all high_payout_events from backtest JSON (no internal filter)
- ARCHITECT correctly identified --threshold 451 (>450, not >=450)
- Output artifact: results/high_win_forensik_gt450.json
- Data source: Keno_GPTs/Kenogpts_2/Basis_Tab/KENO_ab_2018.csv (2018-2024)
- Existing backtest files use threshold=400 - new backtest required

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_055_PROXY_PLAN_20260101_011510.md

## [2026-01-01 01:19:11] TASK_055 - EXECUTOR (ki2)

### Summary
- Step 1: Ran backtest_high_payout_tickets.py --threshold 451 on 2018-2024 data (2242 draws)
- Step 2: Ran analyze_high_win_forensik.py on filtered events
- Total high-win events >450 EUR: 14 (12 unique dates)
- Birthday ratio: 0.446 (expected 0.443, no anomaly)
- Permutation test p=0.558 (no significant clustering)
- Top ticket: typ_6:pair_focused with 5 high-win events (+52.90% ROI)
- V1 vs V2: V1=8 events, V2=6 events; V2 has lower birthday ratio (0.433 vs 0.456)
- Forensik complete, handoff at AI_COLLABORATION/HANDOFFS/ki2_TASK_055_EXECUTOR_20260101_011710.md

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_055_EXECUTOR_20260101_011710.md



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
- results/high_payout_backtest_gt450.json
- results/high_win_forensik_gt450.json

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
- Step 1: Ran backtest_high_payout_tickets.py --threshold 451 on 2018-2024 data (2242 draws)
- Step 2: Ran analyze_high_win_forensik.py on filtered events
- Total high-win events >450 EUR: 14 (12 unique dates)
- Birthday ratio: 0.446 (expected 0.443, no anomaly)
- Permutation test p=0.558 (no significant clustering)
- Top ticket: typ_6:pair_focused with 5 high-win events (+52.90% ROI)
- V1 vs V2: V1=8 events, V2=6 events; V2 has lower birthday ratio (0.433 vs 0.456)
- Forensik complete, handoff at AI_COLLABORATION/HANDOFFS/ki2_TASK_055_EXECUTOR_20260101_011710.md

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_055_EXECUTOR_20260101_011710.md

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
task: TASK_055
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_055_PROXY_IMPL_20260101_011911.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
