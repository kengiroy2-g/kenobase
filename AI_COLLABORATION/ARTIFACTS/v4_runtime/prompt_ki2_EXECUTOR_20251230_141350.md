AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Zyklus-Phasen markieren
TASK-ID: TASK_003
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 14:11:50] TASK_003 - ARCHITECT (ki1)

### Summary
- Zyklus-Phasen (COOLDOWN/GROWTH/HOT) basierend auf Jackpot-Events markieren
- Nutzt vorhandene Jackpot-Events aus Keno_GPTs/10-9_KGDaten_gefiltert.csv (20 Events)
- Phasen-Definition: COOLDOWN=0-30d nach Jackpot, GROWTH=31-60d, HOT=>60d
- Output: phase-annotierte DrawResult-Liste oder separates phase_labels dict
- Funktion in kenobase/analysis/cycle_phases.py oder als Helper in bestehender Datei
- Unit-Tests fuer Edge-Cases (kein Jackpot, mehrere Jackpots nah beieinander)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_003_ARCHITECT_20251230_140850.md

## [2025-12-30 14:13:50] TASK_003 - PROXY_PLAN (ki0)

### Summary
- Plan ist vollstaendig und klar strukturiert mit 6 Implementierungsschritten
- Phase-Semantik (COOLDOWN/GROWTH/HOT/UNKNOWN) korrekt definiert mit Boundaries 30/60 Tage
- Acceptance Criteria sind messbar (100% Coverage, Unit-Tests)
- WICHTIG: jackpot_correlation.py hat bereits load_gk1_events() und get_jackpot_dates() - REUSE statt duplizieren!
- Jackpot-CSV verifiziert: 20 Events 2022-02-2024, Format Datum/Keno-Typ/Gewinner/Tage
- Unit-Test Edge-Cases sinnvoll: Boundaries, kein Jackpot, mehrere Jackpots
- Integration in analysis/__init__.py korrekt geplant
- Keine BUG-001/BUG-003 Red Flags (keine globalen Thresholds, kein Orchestrator noetig)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_003_PROXY_PLAN_20251230_141150.md



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
- kenobase/analysis/__init__.py
- Keno_GPTs/10-9_KGDaten_gefiltert.csv
- kenobase/core/data_loader.py
- tests/unit/test_distribution.py (als Template fuer Test-Struktur)

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
- Plan ist vollstaendig und klar strukturiert mit 6 Implementierungsschritten
- Phase-Semantik (COOLDOWN/GROWTH/HOT/UNKNOWN) korrekt definiert mit Boundaries 30/60 Tage
- Acceptance Criteria sind messbar (100% Coverage, Unit-Tests)
- WICHTIG: jackpot_correlation.py hat bereits load_gk1_events() und get_jackpot_dates() - REUSE statt duplizieren!
- Jackpot-CSV verifiziert: 20 Events 2022-02-2024, Format Datum/Keno-Typ/Gewinner/Tage
- Unit-Test Edge-Cases sinnvoll: Boundaries, kein Jackpot, mehrere Jackpots
- Integration in analysis/__init__.py korrekt geplant
- Keine BUG-001/BUG-003 Red Flags (keine globalen Thresholds, kein Orchestrator noetig)

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_003_PROXY_PLAN_20251230_141150.md

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
task: TASK_003
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK_003_EXECUTOR_20251230_141350.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
