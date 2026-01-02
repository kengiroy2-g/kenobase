AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: A1-04: Payout-Correlation Regel testen (7d nach hoher Auszahlung)
TASK-ID: SYN_004
PRIORITY: P1
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2026-01-01 07:28:01] SYN_004 - ARCHITECT (ki5)

### Summary
- Task: Test Payout-Correlation Rule (7d after high payout >= 400 EUR)
- Axiom: A7 Reset-Cycles - system may "save" after large payouts
- Existing artifacts: high_payout_backtest_2018_2024.json contains 15 high-payout events with dates
- Hypothesis: ROI in 7 days after high payout differs from baseline
- Approach: Tag draws by "days_since_last_high_payout" and compare ROI windows
- Train/Test split required: 2018-2024 Train, 2025 OOS Test
- Null model: Permutation of high-payout dates (block-preserving)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki5_SYN_004_ARCHITECT_20260101_072501.md

## [2026-01-01 07:59:02] SYN_004 - PROXY_PLAN (ki0)

### Summary
- Plan tests Axiom A7 (Reset-Cycles): ROI in 7d window after high payout >= 400 EUR
- Artifact exists: results/high_payout_backtest_2018_2024.json (2237 draws, 48 tickets, 15 high-payout events)
- High-payout events from artifact: 2018-05-12 through 2023-10-10 (sparse, ~2-3/year)
- Train/Test split correctly specified: 2018-2024 Train, 2025 OOS
- Null model: block-preserving permutation of high-payout dates (correct approach)
- CLARIFICATION: high-payout events are ticket-level in artifact; plan must aggregate to get global event dates
- Repro commands well-defined; output paths specified
- Acceptance criteria implicit: effect size + p-value needed

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_SYN_004_PROXY_PLAN_20260101_072801.md



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
- Plan tests Axiom A7 (Reset-Cycles): ROI in 7d window after high payout >= 400 EUR
- Artifact exists: results/high_payout_backtest_2018_2024.json (2237 draws, 48 tickets, 15 high-payout events)
- High-payout events from artifact: 2018-05-12 through 2023-10-10 (sparse, ~2-3/year)
- Train/Test split correctly specified: 2018-2024 Train, 2025 OOS
- Null model: block-preserving permutation of high-payout dates (correct approach)
- CLARIFICATION: high-payout events are ticket-level in artifact; plan must aggregate to get global event dates
- Repro commands well-defined; output paths specified
- Acceptance criteria implicit: effect size + p-value needed

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_SYN_004_PROXY_PLAN_20260101_072801.md

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
task: SYN_004
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
- Datei: AI_COLLABORATION/HANDOFFS/ki6_SYN_004_EXECUTOR_20260101_075902.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
