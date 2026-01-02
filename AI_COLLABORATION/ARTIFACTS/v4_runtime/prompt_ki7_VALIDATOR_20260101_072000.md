AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: A1-03: HZ-Delay isoliert testen (48-60d Wartezeit)
TASK-ID: SYN_003
PRIORITY: P0
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
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

## [2026-01-01 07:20:00] SYN_003 - PROXY_IMPL (ki0)

### Summary
- HZ-Delay Test korrekt implementiert mit korrekter Semantik (1. HZ-spezifischer Jackpot, NICHT global 10/10)
- Alle 4 Phasen definiert: EARLY (0-47d), OPTIMAL (48-60d), LATE (61-120d), EXPIRED (>120d)
- Train/Test Split 2022-2023 vs 2024 konsistent mit SYN_002 (Frueh-Phase)
- Negative Controls (Random Windows) korrekt implementiert, ohne Overlap mit HZ-Jackpot Fenstern
- Statistische Tests (Chi2, Mann-Whitney) vollstaendig integriert
- Hypothese NOT_CONFIRMED: OPTIMAL-Phase zeigt KEINE konsistente Verbesserung vs EARLY/LATE
- Typ-6 2024 +737% ROI anomaly basiert auf single Jackpot event (61 draws) - nicht generalisierbar
- Statistische Power-Warnung korrekt dokumentiert (nur 19 HZ mit 1 Jackpot)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_SYN_003_PROXY_IMPL_20260101_071800.md



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
ROLLE: VALIDATOR
AUFGABE: Validiere die Implementation.

EFFIZIENZ-REGELN:
- Tests nur zielgerichtet (klein starten). Keine riesigen Logs in die Antwort; speichere nach AI_COLLABORATION/ARTIFACTS/ und verlinke.
- Vermeide Repo-weite Scans; nutze WORKING SET + gezielte Reads.

VORHERIGER OUTPUT (kurz):
- HZ-Delay Test korrekt implementiert mit korrekter Semantik (1. HZ-spezifischer Jackpot, NICHT global 10/10)
- Alle 4 Phasen definiert: EARLY (0-47d), OPTIMAL (48-60d), LATE (61-120d), EXPIRED (>120d)
- Train/Test Split 2022-2023 vs 2024 konsistent mit SYN_002 (Frueh-Phase)
- Negative Controls (Random Windows) korrekt implementiert, ohne Overlap mit HZ-Jackpot Fenstern
- Statistische Tests (Chi2, Mann-Whitney) vollstaendig integriert
- Hypothese NOT_CONFIRMED: OPTIMAL-Phase zeigt KEINE konsistente Verbesserung vs EARLY/LATE
- Typ-6 2024 +737% ROI anomaly basiert auf single Jackpot event (61 draws) - nicht generalisierbar
- Statistische Power-Warnung korrekt dokumentiert (nur 19 HZ mit 1 Jackpot)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_SYN_003_PROXY_IMPL_20260101_071800.md

VALIDIERUNG:
1. Fuehre minimale Tests aus (zielgerichtet)
2. Pruefe Code-Qualitaet
3. Verifiziere Acceptance Criteria

TOKEN HYGIENE:
- Bei Test FAIL: nur Command + kurze Fehlermeldung (max 20 Zeilen)
- Mehr Log noetig? Speichere in AI_COLLABORATION/ARTIFACTS/ und referenziere Pfad

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: APPROVED
task: SYN_003
role: VALIDATOR
phase: VALIDATOR
validated_handoff: "<nur filename oder leer>"
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

# Validation

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki7_SYN_003_VALIDATOR_20260101_072000.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
