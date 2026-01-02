AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Test HYP_013: Overlap-Birthday-Anteil nach Phase
TASK-ID: TASK_023
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 20:05:48] TASK_023 - PROXY_PLAN (ki0)

### Summary (fallback)
- --- status: APPROVED task: TASK_023 role: PROXY phase: PROXY_PLAN --- - Plan deckt End-to-End ab (Definitionen, Datenpfade, Feature-Build, Stats, Artefakte, CURRENT_STATUS/REPRO). - Tests/Signifikanz sauber umrissen (z/z+KW/MW, Bonferroni/FDR, Sample>=50 oder UNVERIFIED). - Repro ...

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_023_PROXY_PLAN_20251230_200448.md

## [2025-12-30 20:12:48] TASK_023 - EXECUTOR (ki2)

### Summary
- Implemented phase-stratified HYP_013 script and ran on 1,457 draws (2022-01-03..2025-12-29) using 17 jackpots from timeline_2025.csv.
- Overlap means by phase: PRE 5.79 (n=24, UNVERIFIED), POST 5.92 (n=38, UNVERIFIED), COOLDOWN 5.78 (n=274), NORMAL 5.73 (n=1120); all z-tests vs 5.714 non-significant after BH/Bonferroni.
- Birthday ratios by phase: PRE 0.476, POST 0.453, COOLDOWN 0.456, NORMAL 0.435 (sample sizes as above); all z-tests vs 0.443 non-significant after corrections.
- Global KW p-values: overlap 0.93, birthday_ratio 0.53; 6 pairwise MW tests per metric all p_adj >=0.87, no significant differences.
- Overall means: overlap 5.75 (n=1456), birthday_ratio 0.440 (n=1455); HYP_013 rejected (no corrected significance).
- Artifacts written to results/hyp013_overlap_birthday_phase.json and AI_COLLABORATION/ARTIFACTS/hyp013_overlap_birthday_phase.md; repro command added to results/REPRO_COMMANDS.md.

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_023_EXECUTOR_20251230_200548.md



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
- scripts/test_hyp013_overlap_birthday_phase.py
- results/hyp013_overlap_birthday_phase.json
- AI_COLLABORATION/ARTIFACTS/hyp013_overlap_birthday_phase.md
- results/REPRO_COMMANDS.md
- AI_COLLABORATION/HANDOFFS/ki2_TASK_023_EXECUTOR_20251230_200548.md

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
- Implemented phase-stratified HYP_013 script and ran on 1,457 draws (2022-01-03..2025-12-29) using 17 jackpots from timeline_2025.csv.
- Overlap means by phase: PRE 5.79 (n=24, UNVERIFIED), POST 5.92 (n=38, UNVERIFIED), COOLDOWN 5.78 (n=274), NORMAL 5.73 (n=1120); all z-tests vs 5.714 non-significant after BH/Bonferroni.
- Birthday ratios by phase: PRE 0.476, POST 0.453, COOLDOWN 0.456, NORMAL 0.435 (sample sizes as above); all z-tests vs 0.443 non-significant after corrections.
- Global KW p-values: overlap 0.93, birthday_ratio 0.53; 6 pairwise MW tests per metric all p_adj >=0.87, no significant differences.
- Overall means: overlap 5.75 (n=1456), birthday_ratio 0.440 (n=1455); HYP_013 rejected (no corrected significance).
- Artifacts written to results/hyp013_overlap_birthday_phase.json and AI_COLLABORATION/ARTIFACTS/hyp013_overlap_birthday_phase.md; repro command added to results/REPRO_COMMANDS.md.

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_023_EXECUTOR_20251230_200548.md

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
task: TASK_023
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_023_PROXY_IMPL_20251230_201248.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
