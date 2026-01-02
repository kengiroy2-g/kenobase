AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: V1 vs V2: Alle Typen Parallel-Vergleich
TASK-ID: TASK_056
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2026-01-01 03:29:13] TASK_056 - ARCHITECT (ki1)

### Summary
- Existing V1/V2 comparison covers Typ 5-10 in results/v1_v2_typ6_10_comparison.json
- V2 wins 5/5 Typen with avg ROI-Delta of +24.69% (data from 2237 draws, 2018-2024)
- Gap identified: Typ 2-4 not yet included in parallel comparison
- Plan: extend backtest_v1_v2_comparison.json to include Typ 2-4
- New script: scripts/compare_v1_v2_all_typen.py (Typ 2-10 parallel)
- Output: results/v1_v2_all_typen_comparison.json
- Acceptance: all Typen covered, ROI-Delta per Typ, winner summary

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_056_ARCHITECT_20260101_032713.md

## [2026-01-01 04:01:14] TASK_056 - PROXY_PLAN (ki0)

### Summary
- Plan is sound: extend Typ 6-10 comparison to include Typ 2-4
- Source data backtest_v1_v2_comparison.json already contains Typ 5 data
- Existing script compare_v1_v2_typ6_10.py provides clean template (162 lines)
- Output file naming consistent: v1_v2_all_typen_comparison.json
- Acceptance criteria clear: all Typen covered, ROI-Delta per Typ, winner summary
- Working set request reasonable (3 files)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_056_PROXY_PLAN_20260101_035914.md

## [2026-01-01 04:37:15] TASK_056 - EXECUTOR (ki2)

### Summary
- Created scripts/compare_v1_v2_all_typen.py extending Typ 6-10 comparison to include Typ 5
- Source backtest_v1_v2_comparison.json contains Typ 5-10 only (Typ 2-4 not generated)
- Script dynamically detects available Typen and documents missing ones
- Generated results/v1_v2_all_typen_comparison.json with 6 Typen (5-10)
- V2 wins 6/6 Typen with avg ROI-Delta of +22.81%
- Best V2 performance Typ 6 pair_focused +53.24% ROI vs V1 -20.52% (delta +73.76%)
- Missing Typ 2-4 documented in output JSON for future backtest generation

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_056_EXECUTOR_20260101_040114.md



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
- scripts/compare_v1_v2_all_typen.py
- results/v1_v2_all_typen_comparison.json

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
- Created scripts/compare_v1_v2_all_typen.py extending Typ 6-10 comparison to include Typ 5
- Source backtest_v1_v2_comparison.json contains Typ 5-10 only (Typ 2-4 not generated)
- Script dynamically detects available Typen and documents missing ones
- Generated results/v1_v2_all_typen_comparison.json with 6 Typen (5-10)
- V2 wins 6/6 Typen with avg ROI-Delta of +22.81%
- Best V2 performance Typ 6 pair_focused +53.24% ROI vs V1 -20.52% (delta +73.76%)
- Missing Typ 2-4 documented in output JSON for future backtest generation

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_056_EXECUTOR_20260101_040114.md

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
task: TASK_056
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_056_PROXY_IMPL_20260101_060717.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
