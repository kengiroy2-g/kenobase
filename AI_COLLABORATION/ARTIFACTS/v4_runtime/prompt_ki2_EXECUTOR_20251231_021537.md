AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: V1 vs V2 PARALLEL: Jackknife Leave-One-Out
TASK-ID: TASK_039e
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-31 02:13:37] TASK_039e - ARCHITECT (ki1)

### Summary
- Jackknife LOO fÃ¼r V1 vs V2: VarianzschÃ¤tzung der ROI-Differenz
- V1/V2 sind frozen (keine Hyperparameter) - LOO dient Konfidenzintervall-Berechnung
- Nutzt bestehende 68 Zyklen aus compare_v1_v2_cycles.py
- Script: scripts/jackknife_v1_v2_loo.py
- Output: results/jackknife_v1_v2_loo.json
- Metriken: Mean ROI-Delta, SE, 95% CI, Signifikanz-Test

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_039e_ARCHITECT_20251231_021037.md

## [2025-12-31 02:15:37] TASK_039e - PROXY_PLAN (ki0)

### Summary
- Plan ist mechanisch vollstaendig mit klaren 6 Acceptance Criteria
- Jackknife-LOO Algorithmus mathematisch korrekt (Formel Zeile 77-80)
- Nutzt existierende v1_v2_cycle_comparison.json mit 68 Zyklen (VERIFIED)
- Keine globalen Thresholds (BUG-001 nicht applicable - reine Statistik)
- Kein Hyperparameter-Tuning (V1/V2 frozen) - LOO nur fuer Varianzschaetzung
- Output-Schema klar definiert mit per-type + combined Metriken
- Repro-Command spezifiziert: python scripts/jackknife_v1_v2_loo.py
- Integration minimal: eigenstaendiges Script, laedt nur existierende JSON

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_039e_PROXY_PLAN_20251231_021337.md



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
- scripts/compare_v1_v2_cycles.py
- results/v1_v2_cycle_comparison.json (erste 100 Zeilen reichen)
- scripts/super_model_synthesis.py (fÃ¼r KENO_QUOTES falls nÃ¶tig)

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
- Plan ist mechanisch vollstaendig mit klaren 6 Acceptance Criteria
- Jackknife-LOO Algorithmus mathematisch korrekt (Formel Zeile 77-80)
- Nutzt existierende v1_v2_cycle_comparison.json mit 68 Zyklen (VERIFIED)
- Keine globalen Thresholds (BUG-001 nicht applicable - reine Statistik)
- Kein Hyperparameter-Tuning (V1/V2 frozen) - LOO nur fuer Varianzschaetzung
- Output-Schema klar definiert mit per-type + combined Metriken
- Repro-Command spezifiziert: python scripts/jackknife_v1_v2_loo.py
- Integration minimal: eigenstaendiges Script, laedt nur existierende JSON

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_039e_PROXY_PLAN_20251231_021337.md

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
task: TASK_039e
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK_039e_EXECUTOR_20251231_021537.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
