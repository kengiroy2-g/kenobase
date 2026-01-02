AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Gewinnquoten mit gezogenen Zahlen korrelieren
TASK-ID: HYP-010
PRIORITY: MEDIUM
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 15:58:12] HYP-010 - ARCHITECT (ki1)

### Summary
- Analyzed HYP-010: Correlate winner counts per draw class with drawn numbers
- Data sources: Keno_GQ_2022_2023-2024.csv (27,685 rows) + KENO_ab_2018.csv (draws)
- Create kenobase/analysis/odds_correlation.py module
- Join GQ data with draws on date, aggregate winner counts per number
- Calculate Pearson/Spearman correlation between draw frequency and winner counts
- Identify "safe" (low winners) vs "popular" (high winners) numbers
- Target metric: correlation coefficient with p-value

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_HYP-010_ARCHITECT_20251227_155512.md

## [2025-12-27 16:00:12] HYP-010 - PROXY_PLAN (ki0)

### Summary
- Plan is well-structured with clear 4-step implementation
- Correctly leverages existing popularity_correlation.py pattern (484 lines, similar GQ handling)
- Data sources identified: GQ (27,685 rows) + draws - overlap 2022-2024 properly noted
- German number format handling documented (1.443 = 1443)
- Pearson + Spearman dual correlation approach is sound
- Safe/popular classification uses median +/- 1 std (reasonable threshold)
- WORKING_SET_REQUEST includes all relevant reference files
- Acceptance criteria are measurable and verifiable

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-010_PROXY_PLAN_20251227_155812.md



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
- (leer)

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
- Plan is well-structured with clear 4-step implementation
- Correctly leverages existing popularity_correlation.py pattern (484 lines, similar GQ handling)
- Data sources identified: GQ (27,685 rows) + draws - overlap 2022-2024 properly noted
- German number format handling documented (1.443 = 1443)
- Pearson + Spearman dual correlation approach is sound
- Safe/popular classification uses median +/- 1 std (reasonable threshold)
- WORKING_SET_REQUEST includes all relevant reference files
- Acceptance criteria are measurable and verifiable

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-010_PROXY_PLAN_20251227_155812.md

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
task: HYP-010
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_HYP-010_EXECUTOR_20251227_160012.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
