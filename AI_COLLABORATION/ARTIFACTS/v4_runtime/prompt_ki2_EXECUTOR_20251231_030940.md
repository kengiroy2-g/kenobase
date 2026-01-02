AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Validierung: 2025 Ausreißer-Jahr
TASK-ID: TASK_042
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-31 03:07:40] TASK_042 - ARCHITECT (ki1)

### Summary
- Task: Validierung ob 2025 ein statistischer AusreiÃŸer ist vs 2018-2024
- 2025 zeigt +8.97% hÃ¶heren mean daily payout (91.004 vs 83.506)
- 2025 zeigt niedrigeren CV (0.972 vs 1.014) = stabilere Auszahlungen
- 2025 Jackpot-10 rate 4.70% vs 4.03% = hÃ¤ufigere Jackpots
- Implementierung: statistischer Vergleich via t-test, bootstrap CI, effect size
- Out: results/outlier_year_2025_validation.json mit p-values + CI

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_042_ARCHITECT_20251231_030540.md

## [2025-12-31 03:09:40] TASK_042 - PROXY_PLAN (ki0)

### Summary
- Plan is methodologically sound: t-test, bootstrap CI, Cohen's d, Chi2 for proportions
- All 4 data sources verified (KENO_ab_2022_bereinigt.csv, Keno_GQ_2025.csv, KENO_ab_2018.csv exist)
- Metrics cited in plan verified against distribution_analysis_2025.json + distribution_analysis_2022_2024.json
- Granularity correct: per-year comparison (2025 vs 2018-2024 baseline)
- Acceptance Criteria measurable and appropriate
- No Known Bugs triggered
- Script output path clear: results/outlier_year_2025_validation.json
- WORKING_SET_REQUEST appropriate for EXECUTOR

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_042_PROXY_PLAN_20251231_030740.md



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
- data/raw/keno/KENO_ab_2022_bereinigt.csv
- Keno_GPTs/Keno_GQ_2025.csv
- kenobase/core/data_loader.py
- results/distribution_analysis_2025.json
- results/distribution_analysis_2022_2024.json

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
- Plan is methodologically sound: t-test, bootstrap CI, Cohen's d, Chi2 for proportions
- All 4 data sources verified (KENO_ab_2022_bereinigt.csv, Keno_GQ_2025.csv, KENO_ab_2018.csv exist)
- Metrics cited in plan verified against distribution_analysis_2025.json + distribution_analysis_2022_2024.json
- Granularity correct: per-year comparison (2025 vs 2018-2024 baseline)
- Acceptance Criteria measurable and appropriate
- No Known Bugs triggered
- Script output path clear: results/outlier_year_2025_validation.json
- WORKING_SET_REQUEST appropriate for EXECUTOR

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_042_PROXY_PLAN_20251231_030740.md

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
task: TASK_042
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK_042_EXECUTOR_20251231_030940.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
