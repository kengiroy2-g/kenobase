AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: A1-02: FRUEH-Phase isoliert testen (Tag 1-14)
TASK-ID: SYN_002
PRIORITY: P0
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2026-01-01 02:16:52] SYN_002 - PROXY_PLAN (ki0)

### Summary
- Plan folgt exakt SYN_001 Vorlage (test_cooldown_rule_isolated.py)
- FRUEH (1-14d) vs SPAET (15-30d) vs NORMAL (>30d) klar definiert
- Neue Funktion get_sub_cooldown_phase() in cycle_phases.py
- Train/Test-Split, Chi2, Mann-Whitney, Negative Control spezifiziert
- Keine globalen Thresholds (BUG-001 vermieden)
- WORKING_SET vollstaendig
- Output: results/frueh_phase_isolated_test.json
- Hypothese: FRUEH < SPAET ROI (wirtschaftlich plausibel)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_SYN_002_PROXY_PLAN_20260101_021452.md

## [2026-01-01 02:21:52] SYN_002 - EXECUTOR (ki6)

### Summary
- Added SubCooldownPhase enum (FRUEH/SPAET/NORMAL/UNKNOWN) to cycle_phases.py
- Added get_sub_cooldown_phase() function with FRUEH=1-14d, SPAET=15-30d, NORMAL=>30d
- Created test_frueh_phase_isolated.py script analog to test_cooldown_rule_isolated.py
- Train/Test split (2022-2023/2024), Chi2-Test, Mann-Whitney U implemented
- Negative Control with random 14d windows (excluding jackpot periods)
- Hypothesis CONFIRMED: FRUEH worse than SPAET in 5/5 train, 5/5 test
- Train FRUEH worse vs NORMAL: 5/5, Test: 4/5
- Output saved to results/frueh_phase_isolated_test.json (15KB)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_SYN_002_EXECUTOR_20260101_021652.md



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
- kenobase/analysis/cycle_phases.py
- scripts/test_frueh_phase_isolated.py
- results/frueh_phase_isolated_test.json

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
- Added SubCooldownPhase enum (FRUEH/SPAET/NORMAL/UNKNOWN) to cycle_phases.py
- Added get_sub_cooldown_phase() function with FRUEH=1-14d, SPAET=15-30d, NORMAL=>30d
- Created test_frueh_phase_isolated.py script analog to test_cooldown_rule_isolated.py
- Train/Test split (2022-2023/2024), Chi2-Test, Mann-Whitney U implemented
- Negative Control with random 14d windows (excluding jackpot periods)
- Hypothesis CONFIRMED: FRUEH worse than SPAET in 5/5 train, 5/5 test
- Train FRUEH worse vs NORMAL: 5/5, Test: 4/5
- Output saved to results/frueh_phase_isolated_test.json (15KB)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_SYN_002_EXECUTOR_20260101_021652.md

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
task: SYN_002
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_SYN_002_PROXY_IMPL_20260101_022152.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
