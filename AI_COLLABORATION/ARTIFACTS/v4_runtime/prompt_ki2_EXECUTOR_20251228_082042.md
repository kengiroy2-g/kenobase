AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Langzeit-Zahlen-Balance mit Trigger-Analyse
TASK-ID: TASK-R05
PRIORITY: HIGH
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 08:18:42] TASK-R05 - ARCHITECT (ki1)

### Summary
- TASK-R05 ist eine Langzeit-Zahlen-Balance Analyse mit Trigger-Erkennung
- Ziel: Identifiziere Zahlen die langfristig unter-/ueberrepraesentiert sind
- Trigger: Erkenne wann Balance-Ausgleich wahrscheinlich wird
- Baut auf frequency.py (Rolling-Frequenz) und cluster_reset.py (Pattern) auf
- Neues Modul: kenobase/analysis/longterm_balance.py
- Neues Script: scripts/analyze_longterm_balance.py
- Output: results/longterm_balance.json
- Geschaetzter Aufwand: 3-4 Stunden

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK-R05_ARCHITECT_20251228_081342.md

## [2025-12-28 08:20:42] TASK-R05 - PROXY_PLAN (ki0)

### Summary
- Plan ist konzeptionell solide - Langzeit-Balance Analyse mit Trigger-Erkennung
- Granularitaet per-number ist korrekt gewaehlt (kein BUG-001 Risiko)
- Integration mit bestehenden Modulen (frequency.py, cluster_reset.py) logisch
- Neues Modul longterm_balance.py folgt etabliertem Pattern aus cluster_reset.py
- __init__.py Export erforderlich - explizit im Plan genannt
- Tests geplant (8+ Unit-Tests) - entspricht Projekt-Standard
- Output-Format (JSON nach results/) konsistent mit anderen Analysen
- Aufwandsschaetzung 3-4h realistisch basierend auf cluster_reset.py als Referenz

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-R05_PROXY_PLAN_20251228_081842.md



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
- Plan ist konzeptionell solide - Langzeit-Balance Analyse mit Trigger-Erkennung
- Granularitaet per-number ist korrekt gewaehlt (kein BUG-001 Risiko)
- Integration mit bestehenden Modulen (frequency.py, cluster_reset.py) logisch
- Neues Modul longterm_balance.py folgt etabliertem Pattern aus cluster_reset.py
- __init__.py Export erforderlich - explizit im Plan genannt
- Tests geplant (8+ Unit-Tests) - entspricht Projekt-Standard
- Output-Format (JSON nach results/) konsistent mit anderen Analysen
- Aufwandsschaetzung 3-4h realistisch basierend auf cluster_reset.py als Referenz

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-R05_PROXY_PLAN_20251228_081842.md

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
task: TASK-R05
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK-R05_EXECUTOR_20251228_082042.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
