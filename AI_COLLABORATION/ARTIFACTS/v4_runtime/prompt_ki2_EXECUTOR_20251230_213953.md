AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Nullmodell: Permutationstest
TASK-ID: TASK_029
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 21:37:53] TASK_029 - ARCHITECT (ki1)

### Summary
- TASK_029 (Nullmodell Permutationstest) bereits vollstaendig implementiert
- Modul kenobase/analysis/null_models.py (523 Zeilen) vorhanden
- Tests tests/unit/test_null_models.py (429 Zeilen) vorhanden
- NullModelType Enum in kenobase/core/axioms.py definiert
- NullModelRunner Klasse mit run_test() und run_multiple_tests() + FDR Korrektur
- Drei Permutationsmethoden: schedule_permutation, block_permutation, iid_permutation

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_029_ARCHITECT_20251230_213553.md

## [2025-12-30 21:39:53] TASK_029 - PROXY_PLAN (ki0)

### Summary (fallback)
- ---    **PROXY REVIEW COMPLETE**    ---  status: APPROVED  task: TASK_029  role: PROXY  phase: PROXY_PLAN  reviewed_handoff: "ki1_TASK_029_ARCHITECT_20251230_213553.md"  summary:    - TASK_029 (Nullmodell Permutationstest) ist bereits vollstaendig implementiert    - Modul kenobas ...

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_029_PROXY_PLAN_20251230_213753.md



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
---

**PROXY REVIEW COMPLETE**

---
status: APPROVED
task: TASK_029
role: PROXY
phase: PROXY_PLAN
reviewed_handoff: "ki1_TASK_029_ARCHITECT_20251230_213553.md"
summary:
  - TASK_029 (Nullmodell Permutationstest) ist bereits vollstaendig implementiert
  - Modul kenobase/analysis/null_models.py vorhanden (522 Zeilen)
  - Unit-Tests tests/unit/test_null_models.py vorhanden (428 Zeilen)
  - Alle 27 Unit-Tests bestanden (pytest verified)
  - NullModelType Enum in kenobase/core/axioms.py korrekt definiert (Zeile 17-26)
  - Drei Permutationsmethoden implementiert (schedule, block, iid)
  - FDR-Korrektur via benjamini_hochberg_fdr() vorhanden
  - Task sollte als DONE markiert werden - keine Executor-Phase noetig
---

# Rule Confirmation

- Rule 1 (SYSTEM_STATUS + ADR/Docs + git status): CONFIRMED
- Rule 2 (granularity stated): global
- Rule 3 (semantics defined): NullModelType enum, NullModelRunner class
- Rule 4 (target metric): calibration
- Rule 5 (helper-only boundaries): CONFIRMED
- Rule 6 (reproducibility): `python -m pytest tests/unit/test_null_models.py -v` -> 27 passed in 1.81s

## Handoff erstellt

`AI_COLLABORATION/HANDOFFS/ki0_TASK_029_PROXY_PLAN_20251230_213753.md`

**Empfehlung:** Task als DONE markieren - Implementation ist vollstaendig.


FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_029_PROXY_PLAN_20251230_213753.md

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
task: TASK_029
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK_029_EXECUTOR_20251230_213953.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
