AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Directed Coupling (Transfer Entropy / CMI) ueber Lags
TASK-ID: COUPLE-001
PRIORITY: HOCH
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 04:03:29] COUPLE-001 - ARCHITECT (ki5)

### Summary
- SYSTEM_STATUS.json missing (read error); ADR_AXIOM_FIRST_FRAMEWORK.md reviewed; git status captured.
- Aim: directed coupling via Transfer Entropy/Conditional MI across specified lags with train/test split and BH/FDR.
- Proposed working set: kenobase/analysis/alternative_coupling.py, scripts/analyze_alternative_methods.py, kenobase/analysis/number_representations.py, tests/unit/test_alternative_coupling.py.
- Plan adds kNN-based TE/CMI estimators with lagged conditioning + permutation nulls + FDR per pair/lag (ecosystem vs EuroJackpot control).
- CLI to surface config (lags, history length, representation) and write JSON results with q-values and metadata under results/.
- Validation via synthetic directionality tests, smoke run on sample data, and CURRENT_STATUS note post-implementation.

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki5_COUPLE-001_ARCHITECT_20251230_035929.md

## [2025-12-30 04:05:39] COUPLE-001 - PROXY_PLAN (ki0)

### Summary (fallback)
- --- status: APPROVED task: COUPLE-001 role: PROXY phase: PROXY_PLAN ---  ## Summary - Plan abdeckt TE/CMI mit kNN + Permutationsnullen, BH/FDR pro Paar/Lag, trennt Ecosystem vs EuroJackpot Control. - Arbeitsset klar (alternative_coupling.py, analyze_alternative_methods.py, number ...

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_COUPLE-001_PROXY_PLAN_20251230_040439.md



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
status: APPROVED
task: COUPLE-001
role: PROXY
phase: PROXY_PLAN
---

## Summary
- Plan abdeckt TE/CMI mit kNN + Permutationsnullen, BH/FDR pro Paar/Lag, trennt Ecosystem vs EuroJackpot Control.
- Arbeitsset klar (alternative_coupling.py, analyze_alternative_methods.py, number_representations.py, test_alternative_coupling.py) und CLI/Output-Anpassungen spezifiziert.
- Tests auf synthetisch gerichtete vs. unabhÃ¤ngige Signale vorgesehen, plus CLI-Smoke; CURRENT_STATUS Hinweis vorgesehen.
- Risiken: SYSTEM_STATUS.json fehlt; KI-Profil ki0_proxy.md nicht auffindbar -> Integrations-Stand UNVERIFIED.


FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_COUPLE-001_PROXY_PLAN_20251230_040439.md

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
task: COUPLE-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki6_COUPLE-001_EXECUTOR_20251230_040539.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
