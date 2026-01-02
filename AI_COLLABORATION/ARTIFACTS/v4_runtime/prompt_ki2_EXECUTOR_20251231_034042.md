AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Validierung: Regime-Wechsel nach Jackpot
TASK-ID: TASK_044
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-31 03:38:42] TASK_044 - ARCHITECT (ki1)

### Summary
- Validierungsaufgabe fuer HYP-007 (Regime-Wechsel nach Jackpot)
- Bestehende Infrastruktur identifiziert: regime_detection.py, backtest_post_jackpot.py, test_hyp007_regime_switch.py
- WL-003 bereits BESTAETIGT (-66% ROI nach Jackpot vs Normal)
- HYP_002 (High-Wins Cooldown) NICHT_SIGNIFIKANT wegen geringer Sample Size
- HYP_007 testet 28-Tage-Block-Autokorrelation (Lag=1)
- Validierung erfordert: OOS-Test 2025, Stabilitaetscheck, Nullmodell-Vergleich
- Implementierungsplan mit 6 Schritten erstellt

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_044_ARCHITECT_20251231_033542.md

## [2025-12-31 03:40:42] TASK_044 - PROXY_PLAN (ki0)

### Summary
- HYP-007 Test bereits implementiert und ausgefuehrt (test_hyp007_regime_switch.py)
- Ergebnis bereits in results/hyp007_regime_switch.json (100% confirmation_rate, 5/5 Typen)
- Alle Typen zeigen |autocorr| < 0.3 => REGIME_WECHSEL bestaetigt
- Block-Permutation Nullmodell korrekt implementiert (1000 Permutationen)
- p-values zwischen 0.529-0.889 (niedrige Autokorrelation nicht signifikant anders als Zufall)
- Plan ist valid, Task bereits DONE - Executor muss dokumentieren

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_044_PROXY_PLAN_20251231_033842.md



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
- HYP-007 Test bereits implementiert und ausgefuehrt (test_hyp007_regime_switch.py)
- Ergebnis bereits in results/hyp007_regime_switch.json (100% confirmation_rate, 5/5 Typen)
- Alle Typen zeigen |autocorr| < 0.3 => REGIME_WECHSEL bestaetigt
- Block-Permutation Nullmodell korrekt implementiert (1000 Permutationen)
- p-values zwischen 0.529-0.889 (niedrige Autokorrelation nicht signifikant anders als Zufall)
- Plan ist valid, Task bereits DONE - Executor muss dokumentieren

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_044_PROXY_PLAN_20251231_033842.md

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
task: TASK_044
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK_044_EXECUTOR_20251231_034042.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
