AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: V1 vs V2 PARALLEL: Per Phase Vergleich
TASK-ID: TASK_039
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-31 01:10:34] TASK_039 - ARCHITECT (ki1)

### Summary
- V1 vs V2 Per-Phase Vergleich geplant - V2 hat bereits mode_roi (normal/conservative/jackpot)
- V1 fehlt Phase-Breakdown - muss in super_model_v1_birthday.py erweitert werden
- Phasen-Definition basiert auf Cooldown nach GK1 (Jackpot) Events
- Haupterkenntnis aus V2: normal-Modus outperformt (-37% vs -62% in jackpot-Modus)
- Implementierung benoetigt Phase-Tracking in V1 Backtest-Script
- Ziel: Identifiziere welche Phase bei welchem Modell funktioniert
- Output: results/v1_v2_phase_comparison.json mit pro-Phase ROI
- Repro-Commands definiert fuer Nachvollziehbarkeit

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_039_ARCHITECT_20251231_010834.md

## [2025-12-31 01:12:34] TASK_039 - PROXY_PLAN (ki0)

### Summary
- V2 hat mode_roi per Phase (normal/conservative/jackpot) - VERIFIED in results/super_model_v2_comparison.json
- V1 (super_model_v1_birthday.py) hat kein Phase-Tracking - VERIFIED via grep (0 matches)
- Script scripts/compare_v1_v2_phases.py muss NEU erstellt werden - NOT EXISTS yet
- Phasen-Semantik klar: normal (kein Cooldown), conservative (leichter Cooldown), jackpot (GK1 Cooldown)
- V2-Daten zeigen: normal-Modus outperformt (typ_8: -49.3% vs -70.2% jackpot) - CONFIRMED
- Plan ist technisch korrekt und Axiom-First konform (Phase als wirtschaftlicher Constraint)
- Executor muss: (1) V1 Phase-Tracking hinzufuegen, (2) Vergleichsscript erstellen

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_039_PROXY_PLAN_20251231_011034.md



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
- V2 hat mode_roi per Phase (normal/conservative/jackpot) - VERIFIED in results/super_model_v2_comparison.json
- V1 (super_model_v1_birthday.py) hat kein Phase-Tracking - VERIFIED via grep (0 matches)
- Script scripts/compare_v1_v2_phases.py muss NEU erstellt werden - NOT EXISTS yet
- Phasen-Semantik klar: normal (kein Cooldown), conservative (leichter Cooldown), jackpot (GK1 Cooldown)
- V2-Daten zeigen: normal-Modus outperformt (typ_8: -49.3% vs -70.2% jackpot) - CONFIRMED
- Plan ist technisch korrekt und Axiom-First konform (Phase als wirtschaftlicher Constraint)
- Executor muss: (1) V1 Phase-Tracking hinzufuegen, (2) Vergleichsscript erstellen

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_039_PROXY_PLAN_20251231_011034.md

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
task: TASK_039
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK_039_EXECUTOR_20251231_011234.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
