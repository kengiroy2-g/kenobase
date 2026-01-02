AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Axiome + falsifizierbare Predictions definieren
TASK-ID: AXIOM-001
PRIORITY: P1
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 01:39:03] AXIOM-001 - ARCHITECT (ki5)

### Summary
- 7 Axiome (A1-A7) vollstaendig spezifiziert mit wirtschaftlicher Begruendung
- 21 falsifizierbare Predictions definiert (3 pro Axiom) mit konkreten Metriken
- Nullmodell-Strategie pro Prediction-Typ dokumentiert
- Train/Test-Split pre-2024 Train, 2024+ Test (frozen rules)
- EuroJackpot als externer Kontrollkanal (negative control)
- 5-Step Executor Checkliste mit Acceptance Criteria
- Repro-Commands fuer alle Validierungen

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki5_AXIOM-001_ARCHITECT_20251230_012803.md

## [2025-12-30 01:41:03] AXIOM-001 - PROXY_PLAN (ki0)

### Summary
- Handoff VOLLSTAENDIG (282 Zeilen) - alle 7 Axiome (A1-A7) mit 21 Predictions dokumentiert
- Vorherige PROXY-Iteration war fehlerhaft - Datei war damals truncated, jetzt komplett
- Train/Test-Split sauber definiert: pre-2024 Train, 2024+ Test (frozen rules)
- EuroJackpot als Negativ-Kontrollkanal korrekt spezifiziert
- Nullmodell-Strategie pro Prediction-Typ implementierbar (4 Typen)
- 5-Step Executor-Checkliste mit klaren Acceptance Criteria
- A6 (Regionale Verteilung) als DATAREQ-001 markiert - akzeptabel
- Risiko P-hacking durch FDR/BH-Korrektur mitigiert

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_AXIOM-001_PROXY_PLAN_20251230_013903.md



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
- AI_COLLABORATION/HANDOFFS/ki5_AXIOM-001_ARCHITECT_20251230_012102.md (NEU)AI_COLLABORATION/HANDOFFS/ki5_AXIOM-001_ARCHITECT_20251230_012803.md (NEU)kenobase/core/axioms.py (TO CREATE)tests/unit/test_axioms.py (TO CREATE)scripts/validate_axiom_predictions.py (TO CREATE)AI_COLLABORATION/HANDOFFS/ki5_AXIOM-001_ARCHITECT_20251230_012803.md (NEU)kenobase/core/axioms.py (TO CREATE)tests/unit/test_axioms.py (TO CREATE)scripts/validate_axiom_predictions.py (TO CREATE)

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
- Handoff VOLLSTAENDIG (282 Zeilen) - alle 7 Axiome (A1-A7) mit 21 Predictions dokumentiert
- Vorherige PROXY-Iteration war fehlerhaft - Datei war damals truncated, jetzt komplett
- Train/Test-Split sauber definiert: pre-2024 Train, 2024+ Test (frozen rules)
- EuroJackpot als Negativ-Kontrollkanal korrekt spezifiziert
- Nullmodell-Strategie pro Prediction-Typ implementierbar (4 Typen)
- 5-Step Executor-Checkliste mit klaren Acceptance Criteria
- A6 (Regionale Verteilung) als DATAREQ-001 markiert - akzeptabel
- Risiko P-hacking durch FDR/BH-Korrektur mitigiert

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_AXIOM-001_PROXY_PLAN_20251230_013903.md

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
task: AXIOM-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki6_AXIOM-001_EXECUTOR_20251230_014103.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
