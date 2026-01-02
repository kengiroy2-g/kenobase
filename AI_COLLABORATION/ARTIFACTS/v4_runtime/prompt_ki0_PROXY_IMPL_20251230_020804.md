AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Economic State Variablen/Proxies (Spieleinsatz, Jackpot, Rolling CV)
TASK-ID: ECON-001
PRIORITY: P1
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 02:03:04] ECON-001 - PROXY_PLAN (ki0)

### Summary
- Plan erstellt neues Modul `kenobase/core/economic_state.py` mit 3 Proxies
- DataLoader parsed bereits spieleinsatz/jackpot in metadata (verified: data_loader.py:382-385, 488-491)
- Train/Test Split korrekt referenziert aus axioms.py:458-463
- Integration mit Axiom A7 (Reset-Zyklen) passt zu SYSTEM_STATUS.md
- Config-Integration in default.yaml geplant - kein Konflikt mit existierender Struktur
- WORKING_SET vollstaendig: economic_state.py (neu), __init__.py, default.yaml, test_economic_state.py
- Keine globalen Thresholds wo spezifische noetig (BUG-001 vermieden)
- Kein Feature ohne Orchestrator-Integration (BUG-003 nicht relevant - helper-only)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_ECON-001_PROXY_PLAN_20251230_020104.md

## [2025-12-30 02:08:04] ECON-001 - EXECUTOR (ki6)

### Summary
- Created kenobase/core/economic_state.py with 3 Economic Proxies
- Proxy 1: parse_spieleinsatz() - extracts betting volume from metadata
- Proxy 2: parse_jackpot() - extracts jackpot level from metadata
- Proxy 3: compute_rolling_cv() - computes coefficient of variation of hit distribution
- State classifier: classify_economic_state() maps proxies to NORMAL/COOLDOWN/HOT/RECOVERY
- Integration: extract_economic_states() processes DrawResult list
- Bet recommendation: get_bet_recommendation() returns action based on Axiom A7
- All 27 new unit tests pass; 1172 total tests pass

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_ECON-001_EXECUTOR_20251230_020304.md



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
- kenobase/core/economic_state.py (neu zu erstellen)
- kenobase/core/__init__.py
- config/default.yaml
- tests/unit/test_economic_state.py (neu zu erstellen)
- kenobase/core/economic_state.py (new)
- tests/unit/test_economic_state.py (new)

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
- Created kenobase/core/economic_state.py with 3 Economic Proxies
- Proxy 1: parse_spieleinsatz() - extracts betting volume from metadata
- Proxy 2: parse_jackpot() - extracts jackpot level from metadata
- Proxy 3: compute_rolling_cv() - computes coefficient of variation of hit distribution
- State classifier: classify_economic_state() maps proxies to NORMAL/COOLDOWN/HOT/RECOVERY
- Integration: extract_economic_states() processes DrawResult list
- Bet recommendation: get_bet_recommendation() returns action based on Axiom A7
- All 27 new unit tests pass; 1172 total tests pass

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_ECON-001_EXECUTOR_20251230_020304.md

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
task: ECON-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_ECON-001_PROXY_IMPL_20251230_020804.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
