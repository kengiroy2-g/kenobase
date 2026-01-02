AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: A1-03: HZ-Delay isoliert testen (48-60d Wartezeit)
TASK-ID: SYN_003
PRIORITY: P0
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2026-01-01 04:02:55] SYN_003 - PROXY_PLAN (ki0)

### Summary
- Plan ist konzeptionell korrekt: HZ-Delay (48-60d) Test basiert auf find_ripe_hotzones.py Logik
- Template test_frueh_phase_isolated.py (SYN_002) ist gut geeignet - gleiche statistische Controls
- Hypothese klar definiert: 2. Jackpot nach 48-120 Tagen (optimal 48-60d), testbar via ROI/Jackpot-Rate
- Train/Test Split 2022-2023 vs 2024 ist konsistent mit vorherigen Tests
- cycle_phases.py hat passende Infrastruktur (SubCooldownPhase), aber HZ-Delay ist ANDERE Semantik
- ACHTUNG: HZ-Delay != SubCooldown (HZ = Hot-Zone-spezifischer 1. Jackpot, nicht globaler Jackpot)
- Controls adaequat: Random-Windows, Chi2, Mann-Whitney
- Keine Red Flags (keine globalen Thresholds, keine Integration-Luecken)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_SYN_003_PROXY_PLAN_20260101_040055.md

## [2026-01-01 07:18:00] SYN_003 - EXECUTOR (ki6)

### Summary
- Created test_hz_delay_isolated.py based on test_frueh_phase_isolated.py template
- Implemented HZ-Delay semantics (days since 1st HZ-specific Jackpot, NOT global 10/10)
- Delay phases: EARLY (0-47d), OPTIMAL (48-60d), LATE (61-120d), EXPIRED (>120d)
- Train/Test split: 2022-2023 vs 2024, N=1457 draws, 44 unique Hot-Zones
- Hypothesis NOT_CONFIRMED: OPTIMAL-Phase NOT consistently better than EARLY/LATE
- Typ-6 2024 Test shows +737% ROI in OPTIMAL (single jackpot event), but not generalizable
- Statistical power warning: Only 19 Hot-Zones with exactly 1 jackpot
- No statistically significant effects across types (p>0.05 in most comparisons)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_SYN_003_EXECUTOR_20260101_060258.md



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
- scripts/find_ripe_hotzones.py
- scripts/test_frueh_phase_isolated.py
- kenobase/analysis/cycle_phases.py
- kenobase/core/keno_quotes.py
- results/reife_hotzones.md
- scripts/test_hz_delay_isolated.py
- results/hz_delay_isolated_test.json

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
- Created test_hz_delay_isolated.py based on test_frueh_phase_isolated.py template
- Implemented HZ-Delay semantics (days since 1st HZ-specific Jackpot, NOT global 10/10)
- Delay phases: EARLY (0-47d), OPTIMAL (48-60d), LATE (61-120d), EXPIRED (>120d)
- Train/Test split: 2022-2023 vs 2024, N=1457 draws, 44 unique Hot-Zones
- Hypothesis NOT_CONFIRMED: OPTIMAL-Phase NOT consistently better than EARLY/LATE
- Typ-6 2024 Test shows +737% ROI in OPTIMAL (single jackpot event), but not generalizable
- Statistical power warning: Only 19 Hot-Zones with exactly 1 jackpot
- No statistically significant effects across types (p>0.05 in most comparisons)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_SYN_003_EXECUTOR_20260101_060258.md

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
task: SYN_003
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_SYN_003_PROXY_IMPL_20260101_071800.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
