AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Core Stable Numbers identifizieren
TASK-ID: TASK-H02
PRIORITY: HIGH
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 22:05:47] TASK-H02 - ARCHITECT (ki1)

### Summary
- Core Stable Numbers = Zahlen mit hoher Stabilitaet ueber Zeitfenster (Model Law A)
- Kombiniert frequency.py (Hot/Cold) + recurrence.py (Streaks) + physics/model_laws.py
- Stabilitaet = Rolling Frequency Varianz <= stability_threshold (0.90)
- Output: StableNumbersResult mit number, stability_score, is_stable, avg_frequency
- Neues Modul: kenobase/analysis/stable_numbers.py
- Integration in analyze.py CLI als --stable-numbers Flag
- Unit-Tests in tests/unit/test_stable_numbers.py
- Config: analysis.stable_numbers_window + physics.stability_threshold

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK-H02_ARCHITECT_20251227_220247.md

## [2025-12-27 22:07:47] TASK-H02 - PROXY_PLAN (ki0)

### Summary
- Plan ist konzeptionell solide: Core Stable Numbers via Rolling Frequency + Model Law A
- Stabilitaetsformel korrekt: stability_score = 1 - (std/mean) (per-number granularity)
- Config-Integration nutzt existierenden physics.stability_threshold (0.90) - kein neuer globaler Wert noetig
- WORKING_SET_REQUEST vollstaendig: frequency.py, __init__.py, analyze.py, default.yaml, data_loader.py
- CLI-Integration als neuer Click-Command (nicht --flag) empfohlen - konsistent mit bestehendem Pattern
- Keine BUG-001 Verletzung: nutzt game-specific config via cfg.get_active_game()
- Keine BUG-003 Verletzung: kenobase/analysis/__init__.py muss erweitert werden (explizit genannt)
- Output-Pfad results/stable_numbers_keno.json ist reproduzierbar

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-H02_PROXY_PLAN_20251227_220547.md



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
- Plan ist konzeptionell solide: Core Stable Numbers via Rolling Frequency + Model Law A
- Stabilitaetsformel korrekt: stability_score = 1 - (std/mean) (per-number granularity)
- Config-Integration nutzt existierenden physics.stability_threshold (0.90) - kein neuer globaler Wert noetig
- WORKING_SET_REQUEST vollstaendig: frequency.py, __init__.py, analyze.py, default.yaml, data_loader.py
- CLI-Integration als neuer Click-Command (nicht --flag) empfohlen - konsistent mit bestehendem Pattern
- Keine BUG-001 Verletzung: nutzt game-specific config via cfg.get_active_game()
- Keine BUG-003 Verletzung: kenobase/analysis/__init__.py muss erweitert werden (explizit genannt)
- Output-Pfad results/stable_numbers_keno.json ist reproduzierbar

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-H02_PROXY_PLAN_20251227_220547.md

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
task: TASK-H02
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK-H02_EXECUTOR_20251227_220747.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
