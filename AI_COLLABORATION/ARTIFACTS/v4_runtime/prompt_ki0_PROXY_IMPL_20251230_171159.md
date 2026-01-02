AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Test HYP_003: Wochentag-Effekt
TASK-ID: TASK_013
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 17:06:59] TASK_013 - PROXY_PLAN (ki0)

### Summary
- APPROVED: Architect correctly renamed to "Weekday-ROI Analysis" (avoids HYP-003 conflict)
- VERIFIED: temporal_cycles.analyze_dimension() exists at lines 96-212, supports weekday Chi-square
- DISCOVERED: scripts/analyze_cycles_deep.py already has weekday ROI stratification (lines 100-135)
- REUSE RECOMMENDATION: Executor should extract/refactor weekday ROI logic from analyze_cycles_deep.py
- Script name scripts/analyze_weekday_roi.py is correct (no collision with analyze_hyp003*.py)
- Output results/weekday_roi_analysis.json is distinct from any HYP-003 artifacts
- Acceptance criteria measurable: ROI_diff >= 20% OR p<0.05
- Nullmodell (weekday-preserving shuffle) is correctly specified

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_013_PROXY_PLAN_20251230_170459.md

## [2025-12-30 17:11:59] TASK_013 - EXECUTOR (ki2)

### Summary
- Created scripts/analyze_weekday_roi.py with weekday ROI stratification for V2-Ticket Type 9
- Reused temporal_cycles.analyze_dimension() for Chi-square test (verified at lines 96-212)
- Implemented weekday-shuffle nullmodell (shuffles weekday assignments, 1000 permutations)
- Output saved to results/weekday_roi_analysis.json (1457 draws, 2022-2025)
- Result: ROI-Spread 490.1% (best=Di +423.1%, worst=Mo -67.0%) passes >= 20% criterion
- Chi-square p=1.0 (draws perfectly uniform across weekdays, KENO daily)
- Nullmodell p=0.374 -> Spread NOT SIGNIFICANT (single jackpot hit on Tuesday)
- VERDICT: CONFIRMED (ROI criterion) but NOT_SIGNIFICANT (nullmodell says due to chance)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_013_EXECUTOR_20251230_170659.md




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
- scripts/analyze_weekday_roi.py (NEW)
- results/weekday_roi_analysis.json (NEW)

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
- Created scripts/analyze_weekday_roi.py with weekday ROI stratification for V2-Ticket Type 9
- Reused temporal_cycles.analyze_dimension() for Chi-square test (verified at lines 96-212)
- Implemented weekday-shuffle nullmodell (shuffles weekday assignments, 1000 permutations)
- Output saved to results/weekday_roi_analysis.json (1457 draws, 2022-2025)
- Result: ROI-Spread 490.1% (best=Di +423.1%, worst=Mo -67.0%) passes >= 20% criterion
- Chi-square p=1.0 (draws perfectly uniform across weekdays, KENO daily)
- Nullmodell p=0.374 -> Spread NOT SIGNIFICANT (single jackpot hit on Tuesday)
- VERDICT: CONFIRMED (ROI criterion) but NOT_SIGNIFICANT (nullmodell says due to chance)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_013_EXECUTOR_20251230_170659.md

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
task: TASK_013
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_013_PROXY_IMPL_20251230_171159.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
