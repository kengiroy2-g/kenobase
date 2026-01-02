AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: A1-01: Cooldown-Regel isoliert testen (30d nach 10/10)
TASK-ID: SYN_001
PRIORITY: P0
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2026-01-01 01:29:50] SYN_001 - ARCHITECT (ki5)

### Summary
- Task: A1-01: Cooldown-Regel isoliert testen (30d nach 10/10)
- Existing analysis found in results/post_jackpot_backtest.json (11 Jackpots, 30d window)
- V1 vs V2 Cooldown comparison exists in results/v1_v2_cooldown_comparison.json
- Cooldown-Semantik: 0-30 Tage nach Jackpot = System spart (WL-003)
- Current findings: V1 dominates cooldown (2/3), V2 dominates normal (3/3)
- Plan: Create isolated Cooldown-Rule test script with proper null-model controls
- Required: Train/Test split, Chi2-Test, Negative Control (non-jackpot 30d windows)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki5_SYN_001_ARCHITECT_20260101_012650.md

## [2026-01-01 01:31:50] SYN_001 - PROXY_PLAN (ki0)

### Summary
- Plan ist technisch vollstaendig mit 7 EXECUTOR-Aufgaben
- Train/Test Split (2022-2023 vs 2024) korrekt definiert
- Negative Control (random 30d windows) entspricht Axiom-First
- ACHTUNG: Existierende Daten zeigen p=1.0 (NOT_SIGNIFICANT) - neuer Test wird voraussichtlich aehnlich
- 11 Jackpots = geringe statistische Power fuer Chi2-Test
- WORKING_SET_REQUEST enthaelt alle relevanten Dateien
- Output-Pfad definiert: results/cooldown_rule_isolated_test.json
- EMPFEHLUNG: Executor soll trotzdem durchfuehren fuer saubere Dokumentation

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_SYN_001_PROXY_PLAN_20260101_012950.md



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
- Plan ist technisch vollstaendig mit 7 EXECUTOR-Aufgaben
- Train/Test Split (2022-2023 vs 2024) korrekt definiert
- Negative Control (random 30d windows) entspricht Axiom-First
- ACHTUNG: Existierende Daten zeigen p=1.0 (NOT_SIGNIFICANT) - neuer Test wird voraussichtlich aehnlich
- 11 Jackpots = geringe statistische Power fuer Chi2-Test
- WORKING_SET_REQUEST enthaelt alle relevanten Dateien
- Output-Pfad definiert: results/cooldown_rule_isolated_test.json
- EMPFEHLUNG: Executor soll trotzdem durchfuehren fuer saubere Dokumentation

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_SYN_001_PROXY_PLAN_20260101_012950.md

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
task: SYN_001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki6_SYN_001_EXECUTOR_20260101_013150.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
