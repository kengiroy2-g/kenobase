AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Test HYP_008: Jahres-Zyklen
TASK-ID: TASK_018
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 18:27:03] TASK_018 - ARCHITECT (ki1)

### Summary
- Neue ID: HYP_YEAR_001 (statt HYP-008 wegen ID-Kollision)
- Orthogonalitaet zu HYP_CYC_001 klar definiert: Jahr/Quartal vs 28-Tage-Zyklus
- Script: scripts/test_hyp_year_001_cycles.py (Namensaenderung)
- Nullmodell: Jahr-Permutation (shuffle year-labels, preserve draw-order within year)
- Metriken: ROI pro Jahr/Quartal/Monat, Chi-Quadrat auf Hit-Distribution
- Train/Test: 2022-2024 Train, 2025 OOS
- Acceptance: p<0.05 (Bonferroni) UND ROI-Diff >20%
- Datenquelle: data/raw/keno/KENO_ab_2022_bereinigt.csv (N~1100)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_018_ARCHITECT_20251230_182403.md

## [2025-12-30 18:29:03] TASK_018 - PROXY_PLAN (ki0)

### Summary
- ID-Kollision behoben: HYP_YEAR_001 statt HYP-008 (111-Prinzip bereits vergeben, Zeile 50 HYPOTHESES_CATALOG.md)
- Orthogonalitaet zu HYP_CYC_001 klar: Jahr/Quartal/Monat vs 28-Tage-Zyklus (Jackpot-triggered)
- Datenquelle verifiziert: KENO_ab_2022_bereinigt.csv hat N=1456 Draws (2022-01-03 bis 2025-12-29)
- Train/Test Split 2022-2024 / 2025 OOS ist valide (~1100 Train, ~360 Test)
- Nullmodell sinnvoll: Jahr-Permutation bewahrt Draw-Order innerhalb Jahr
- Metriken vollstaendig: ROI pro Jahr/Quartal/Monat + Chi-Quadrat Hit-Distribution
- Acceptance Criteria messbar: p<0.05 (Bonferroni) UND ROI-Diff >20%
- Script-Name korrekt: scripts/test_hyp_year_001_cycles.py

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_018_PROXY_PLAN_20251230_182703.md



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
- kenobase/core/data_loader.py
- kenobase/core/keno_quotes.py
- scripts/analyze_cycles_comprehensive.py
- AI_COLLABORATION/KNOWLEDGE_BASE/HYPOTHESES_CATALOG.md

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
- ID-Kollision behoben: HYP_YEAR_001 statt HYP-008 (111-Prinzip bereits vergeben, Zeile 50 HYPOTHESES_CATALOG.md)
- Orthogonalitaet zu HYP_CYC_001 klar: Jahr/Quartal/Monat vs 28-Tage-Zyklus (Jackpot-triggered)
- Datenquelle verifiziert: KENO_ab_2022_bereinigt.csv hat N=1456 Draws (2022-01-03 bis 2025-12-29)
- Train/Test Split 2022-2024 / 2025 OOS ist valide (~1100 Train, ~360 Test)
- Nullmodell sinnvoll: Jahr-Permutation bewahrt Draw-Order innerhalb Jahr
- Metriken vollstaendig: ROI pro Jahr/Quartal/Monat + Chi-Quadrat Hit-Distribution
- Acceptance Criteria messbar: p<0.05 (Bonferroni) UND ROI-Diff >20%
- Script-Name korrekt: scripts/test_hyp_year_001_cycles.py

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_018_PROXY_PLAN_20251230_182703.md

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
task: TASK_018
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK_018_EXECUTOR_20251230_182903.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
