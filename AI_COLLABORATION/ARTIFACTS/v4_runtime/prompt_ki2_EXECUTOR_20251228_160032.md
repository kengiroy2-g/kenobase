AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Hot/Cold Numbers Stabilität
TASK-ID: HYP009-001
PRIORITY: HOCH
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 15:58:32] HYP009-001 - ARCHITECT (ki1)

### Summary
- DUPLIKAT: HYP-009 wurde am 2025-12-27 vollstaendig abgeschlossen
- Vorheriger Status: COMPLETE in ki0_HYP-009_PROXY_FINAL_20251227_134106.md
- Chi-Quadrat-Test: chi2=52.27, p=0.9333, N=2237 - ACCEPTED
- Artifact existiert: AI_COLLABORATION/ARTIFACTS/HYP-009_chi_quadrat_result.json
- stable_numbers.py existiert (268 Zeilen implementiert)
- test_stable_numbers.py existiert (9 Test-Klassen)
- Kein weiterer Implementierungsaufwand noetig
- Task soll aus Plan entfernt oder als DONE markiert werden

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_HYP009-001_ARCHITECT_20251228_155632.md

## [2025-12-28 16:00:32] HYP009-001 - PROXY_PLAN (ki0)

### Summary
- ARCHITECT korrekt: Task ist DUPLIKAT von HYP-009 (abgeschlossen 2025-12-27)
- Artifact verifiziert: AI_COLLABORATION/ARTIFACTS/HYP-009_chi_quadrat_result.json
- Chi2=52.27, p=0.9333, N=2237 - ACCEPTED (Gleichverteilung bestaetigt)
- stable_numbers.py existiert (Model Law A implementiert)
- test_stable_numbers.py existiert (9 Test-Klassen)
- SKIP-Status korrekt - kein weiterer Implementierungsaufwand
- Plan-Update noetig: Task aus Plan entfernen oder DONE markieren
- APPROVED weil ARCHITECT-Analyse stimmt

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP009-001_PROXY_PLAN_20251228_155832.md



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
- ARCHITECT korrekt: Task ist DUPLIKAT von HYP-009 (abgeschlossen 2025-12-27)
- Artifact verifiziert: AI_COLLABORATION/ARTIFACTS/HYP-009_chi_quadrat_result.json
- Chi2=52.27, p=0.9333, N=2237 - ACCEPTED (Gleichverteilung bestaetigt)
- stable_numbers.py existiert (Model Law A implementiert)
- test_stable_numbers.py existiert (9 Test-Klassen)
- SKIP-Status korrekt - kein weiterer Implementierungsaufwand
- Plan-Update noetig: Task aus Plan entfernen oder DONE markieren
- APPROVED weil ARCHITECT-Analyse stimmt

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP009-001_PROXY_PLAN_20251228_155832.md

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
task: HYP009-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_HYP009-001_EXECUTOR_20251228_160032.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
