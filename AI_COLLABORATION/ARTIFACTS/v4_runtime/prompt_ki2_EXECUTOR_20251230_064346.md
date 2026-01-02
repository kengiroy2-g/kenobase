AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Lag-Exploitation
TASK-ID: STRAT-003
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 06:41:46] STRAT-003 - ARCHITECT (ki1)

### Summary
- STRAT-003 Lag-Exploitation plan based on ecosystem_graph.json findings
- ONE robust edge found: KENO->AUSWAHLWETTE lag=7, lift=2.41x, q=0.027
- Strategy: When KENO draws number 11, bet number 25 in AUSWAHLWETTE 7 days later
- Baseline rate 14.1%, conditional rate 34.0% (2.41x improvement)
- Implementation requires backtest with train/test split + ROI calculation
- Null model: schedule-preserving permutation (weekday blocks)
- Risk: Single edge may be spurious; need multiple independent validation
- Acceptance: Positive ROI in test period with p<0.05 vs null

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_STRAT-003_ARCHITECT_20251230_063846.md


## [2025-12-30 06:43:46] STRAT-003 - PROXY_PLAN (ki0)

### Summary
- Plan is mechanically complete with 6 EXECUTOR steps and 4 VALIDATOR checks
- Edge data VERIFIED: results/ecosystem_graph.json shows KENO->AUSWAHLWETTE lag=7, lift=2.41, q=0.027
- Data files EXIST: AW_ab_2022_bereinigt.csv has 207 draws, columns A1-A6,Zusatzzahl
- Train/Test split reasonable (2022-2023 train, 2024-2025 test)
- Acceptance criteria AC1-AC6 are measurable and appropriate
- Risk of spurious correlation correctly identified (single edge, support=53)
- Null model (schedule-preserving permutation) is appropriate for weekday structure
- AUSWAHLWETTE has weekly draws (Saturdays) - plan correctly accounts for lag=7 alignment

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_STRAT-003_PROXY_PLAN_20251230_064146.md



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
- results/hyp005_decade_affinity.json
- results/hyp006/wgz_analysis.json
- results/hyp011_temporal_cycles.json
- scripts/strategy_from_ecosystem.py
- scripts/analyze_cross_game_timing.py
- results/ecosystem_graph.json
- data/raw/keno/KENO_ab_2022_bereinigt.csv
- data/raw/auswahlwette/AW_ab_2022_bereinigt.csv

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
- Plan is mechanically complete with 6 EXECUTOR steps and 4 VALIDATOR checks
- Edge data VERIFIED: results/ecosystem_graph.json shows KENO->AUSWAHLWETTE lag=7, lift=2.41, q=0.027
- Data files EXIST: AW_ab_2022_bereinigt.csv has 207 draws, columns A1-A6,Zusatzzahl
- Train/Test split reasonable (2022-2023 train, 2024-2025 test)
- Acceptance criteria AC1-AC6 are measurable and appropriate
- Risk of spurious correlation correctly identified (single edge, support=53)
- Null model (schedule-preserving permutation) is appropriate for weekday structure
- AUSWAHLWETTE has weekly draws (Saturdays) - plan correctly accounts for lag=7 alignment

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_STRAT-003_PROXY_PLAN_20251230_064146.md

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
task: STRAT-003
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_STRAT-003_EXECUTOR_20251230_064346.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
