AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: V1 vs V2: Cooldown-Phase Test
TASK-ID: TASK_041
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-31 02:40:39] TASK_041 - PROXY_PLAN (ki0)

### Summary
- Plan is well-structured with clear gap analysis (existing scripts use 3-tier phases, not exact 30-day window)
- Key metric ROI delta (V2-V1) per phase is measurable and aligned with WL-003 hypothesis
- Cooldown semantics clearly defined: 0-30 days post-jackpot vs >30 days
- Existing backtest_post_jackpot.py provides reusable template code (is_in_cooldown pattern)
- compare_v1_v2_phases.py exists but uses different phase definitions (7/30 day tiers)
- New script justified: need exact 30-day window comparison for V1 vs V2
- Output path results/v1_v2_cooldown_comparison.json is consistent with existing naming
- Axiom-First compliant: builds on WL-003 hypothesis, frozen ticket comparison

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_041_PROXY_PLAN_20251231_023839.md

## [2025-12-31 02:43:39] TASK_041 - EXECUTOR (ki2)

### Summary
- Created scripts/backtest_v1_v2_cooldown.py for V1 vs V2 cooldown comparison
- Cooldown semantics: 0-30 days post-jackpot vs >30 days (WL-003 compliant)
- Tested on 11 Jackpots (2022-2024), 1877 draws, 296 cooldown / 1581 normal draws
- Key finding: V1 dominant in cooldown phase (2/3 Typen), V2 dominant in normal phase (3/3 Typen)
- ROI deltas: V2 better in normal (+2.66% to +5.50%), V1 better in cooldown for Typ9/10
- WL-003 hypothesis CONFIRMED: different model performance by phase
- Output saved to results/v1_v2_cooldown_comparison.json

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_041_EXECUTOR_20251231_024039.md



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
- scripts/super_model_v1_birthday.py
- scripts/super_model_v2_birthday_signal.py
- scripts/super_model_synthesis.py
- scripts/backtest_post_jackpot.py
- scripts/backtest_v1_v2_cooldown.py
- results/v1_v2_cooldown_comparison.json

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
- Created scripts/backtest_v1_v2_cooldown.py for V1 vs V2 cooldown comparison
- Cooldown semantics: 0-30 days post-jackpot vs >30 days (WL-003 compliant)
- Tested on 11 Jackpots (2022-2024), 1877 draws, 296 cooldown / 1581 normal draws
- Key finding: V1 dominant in cooldown phase (2/3 Typen), V2 dominant in normal phase (3/3 Typen)
- ROI deltas: V2 better in normal (+2.66% to +5.50%), V1 better in cooldown for Typ9/10
- WL-003 hypothesis CONFIRMED: different model performance by phase
- Output saved to results/v1_v2_cooldown_comparison.json

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_041_EXECUTOR_20251231_024039.md

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
task: TASK_041
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_041_PROXY_IMPL_20251231_024339.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
