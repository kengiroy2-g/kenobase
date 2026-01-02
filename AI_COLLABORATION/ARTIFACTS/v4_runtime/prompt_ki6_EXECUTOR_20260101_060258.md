AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: A1-03: HZ-Delay isoliert testen (48-60d Wartezeit)
TASK-ID: SYN_003
PRIORITY: P0
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2026-01-01 02:30:52] SYN_003 - ARCHITECT (ki5)

### Summary
- Plan fuer HZ-Delay isolierten Test (48-60d Wartezeit nach 1. Jackpot)
- Basiert auf Template test_frueh_phase_isolated.py (SYN_002)
- Hot-Zone = Top-7 Zahlen aus 50-Tage Fenster (find_ripe_hotzones.py)
- Hypothese: 2. Jackpot kommt 48-120 Tage nach 1. Jackpot (OPTIMAL: 48-60d)
- Train/Test Split: 2022-2023 vs 2024
- Controls: Random-Windows + Chi2 + Mann-Whitney

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki5_SYN_003_ARCHITECT_20260101_022752.md

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
ROLLE: EXECUTOR
AUFGABE: Fuehre den genehmigten Plan aus.

EFFIZIENZ-REGELN:
- Starte mit WORKING SET; vermeide Repo-weite Scans. Wenn du suchen musst: 1 gezieltes Grep pro Subtask, nicht breit.
- Schreibe nur kurze, entscheidungsrelevante Logs; grosse Logs nach AI_COLLABORATION/ARTIFACTS/ auslagern und verlinken.
- Aktualisiere Status ausschliesslich ueber den Handoff (keine CURRENT_STATUS edits im Body).
- Aendere niemals AI_COLLABORATION/MESSAGE_QUEUE/* oder AI_COLLABORATION/RESULTS/CURRENT_STATUS.md (nur Handoff-Ausgabe).
- Vermeide das Ausgeben von Diffs (diff --git, Patch-BlÃ¶cke). In der Antwort nur Summary + Pfade.

PLAN (kurz):
- Plan ist konzeptionell korrekt: HZ-Delay (48-60d) Test basiert auf find_ripe_hotzones.py Logik
- Template test_frueh_phase_isolated.py (SYN_002) ist gut geeignet - gleiche statistische Controls
- Hypothese klar definiert: 2. Jackpot nach 48-120 Tagen (optimal 48-60d), testbar via ROI/Jackpot-Rate
- Train/Test Split 2022-2023 vs 2024 ist konsistent mit vorherigen Tests
- cycle_phases.py hat passende Infrastruktur (SubCooldownPhase), aber HZ-Delay ist ANDERE Semantik
- ACHTUNG: HZ-Delay != SubCooldown (HZ = Hot-Zone-spezifischer 1. Jackpot, nicht globaler Jackpot)
- Controls adaequat: Random-Windows, Chi2, Mann-Whitney
- Keine Red Flags (keine globalen Thresholds, keine Integration-Luecken)

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_SYN_003_PROXY_PLAN_20260101_040055.md

REGELN:
1. Folge Checkliste exakt
2. Keine eigenen Interpretationen
3. Dokumentiere jeden Schritt
4. WICHTIG: Fuege files_changed: [...] im YAML hinzu

TOKEN HYGIENE:
- Final Output muss direkt das Handoff-Markdown sein (keine Diffs, keine Zusatztexte).
- Keine langen Command-Outputs im Handoff
- Bei Fehlern: nur Command + 20 Zeilen excerpt
- Lange Logs: speichere in AI_COLLABORATION/ARTIFACTS/ und referenziere nur Pfad

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: COMPLETE
task: SYN_003
role: EXECUTOR
phase: EXECUTOR
files_changed: []
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

# Umsetzung

WICHTIG: Erstelle Handoff-Datei wenn fertig:
- Datei: AI_COLLABORATION/HANDOFFS/ki6_SYN_003_EXECUTOR_20260101_060258.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
