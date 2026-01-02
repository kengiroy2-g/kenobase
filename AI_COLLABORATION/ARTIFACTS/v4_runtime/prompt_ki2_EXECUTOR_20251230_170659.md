AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Test HYP_003: Wochentag-Effekt
TASK-ID: TASK_013
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 17:04:58] TASK_013 - ARCHITECT (ki1)

### Summary
- CORRECTED: Renamed from "HYP_003" to "Weekday-ROI Analysis" (avoids HYP-003 conflict)
- Script: scripts/analyze_weekday_roi.py (NOT analyze_hyp003_weekday.py)
- Output: results/weekday_roi_analysis.json (NOT hyp003_weekday_effect.json)
- REUSE existing temporal_cycles.analyze_dimension() for Chi-square (no reimplementation)
- NEW CODE ONLY: ROI stratification by weekday using V2-Tickets backtest
- Nullmodell: Weekday-preserving shuffle (compare shuffled draws within same weekday)
- Acceptance: ROI_diff >= 20% between best/worst weekday OR p<0.05 Chi-square
- Data: KENO_ab_2022_bereinigt.csv (348+ draws, sufficient for 7-weekday stratification)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_013_ARCHITECT_20251230_170158.md

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
- APPROVED: Architect correctly renamed to "Weekday-ROI Analysis" (avoids HYP-003 conflict)
- VERIFIED: temporal_cycles.analyze_dimension() exists at lines 96-212, supports weekday Chi-square
- DISCOVERED: scripts/analyze_cycles_deep.py already has weekday ROI stratification (lines 100-135)
- REUSE RECOMMENDATION: Executor should extract/refactor weekday ROI logic from analyze_cycles_deep.py
- Script name scripts/analyze_weekday_roi.py is correct (no collision with analyze_hyp003*.py)
- Output results/weekday_roi_analysis.json is distinct from any HYP-003 artifacts
- Acceptance criteria measurable: ROI_diff >= 20% OR p<0.05
- Nullmodell (weekday-preserving shuffle) is correctly specified

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_013_PROXY_PLAN_20251230_170459.md

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
task: TASK_013
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK_013_EXECUTOR_20251230_170659.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
