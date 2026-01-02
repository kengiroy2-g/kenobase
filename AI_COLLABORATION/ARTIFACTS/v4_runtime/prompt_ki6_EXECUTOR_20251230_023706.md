AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Nullmodelle: schedule/block permutation
TASK-ID: NULL-001
PRIORITY: HOCH
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 02:35:06] NULL-001 - ARCHITECT (ki5)

### Summary
- Define new module kenobase/analysis/null_models.py for permutation-based null models
- Implement schedule_permutation() preserving draw-schedule structure (same weekdays)
- Implement block_permutation() preserving temporal blocks (weekly autocorrelation)
- Add NullModelRunner class integrating with existing NullModelType enum in axioms.py
- Add FDR-corrected p-value computation for each null model type
- Create unit tests in tests/unit/test_null_models.py with synthetic data validation
- Integrate null models with existing axiom predictions (P1.3, P4.3, P6.3, P7.3)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki5_NULL-001_ARCHITECT_20251230_023206.md

## [2025-12-30 02:37:06] NULL-001 - PROXY_PLAN (ki0)

### Summary
- NullModelType enum already exists in kenobase/core/axioms.py:17-25
- BLOCK_PERMUTATION and SCHEDULE_PRESERVING types pre-defined
- 4 predictions require these null models: P1.3, P4.3, P6.3, P7.3
- New module kenobase/analysis/null_models.py fits existing 35 analysis modules
- FDR correction via statsmodels.stats.multitest is standard approach
- Integration with axioms.py via NullModelType enum is clean
- No architecture conflicts or BUG patterns detected

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_NULL-001_PROXY_PLAN_20251230_023506.md



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
- NullModelType enum already exists in kenobase/core/axioms.py:17-25
- BLOCK_PERMUTATION and SCHEDULE_PRESERVING types pre-defined
- 4 predictions require these null models: P1.3, P4.3, P6.3, P7.3
- New module kenobase/analysis/null_models.py fits existing 35 analysis modules
- FDR correction via statsmodels.stats.multitest is standard approach
- Integration with axioms.py via NullModelType enum is clean
- No architecture conflicts or BUG patterns detected

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_NULL-001_PROXY_PLAN_20251230_023506.md

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
task: NULL-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki6_NULL-001_EXECUTOR_20251230_023706.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
