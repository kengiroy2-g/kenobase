AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Summen-Fenster Analyse
TASK-ID: TASK-M04
PRIORITY: MEDIUM
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 00:37:54] TASK-M04 - ARCHITECT (ki1)

### Summary
- Summen-Fenster Analyse basiert auf Hypothese: Summen clustern in [140-170] und [190-220]
- CombinationEngine bereits implementiert mit min_sum/max_sum Filtern (combination_engine.py:97-98, 202-215)
- Neues Analyse-Script erforderlich: scripts/analyze_sum_windows.py
- Neues Modul: kenobase/analysis/sum_distribution.py fuer Histogramm-Analyse
- Integration in config/default.yaml unter analysis.sum_windows
- Visualisierung via matplotlib (bereits in requirements.txt)
- Acceptance Criteria: Verteilung plotten, Cluster identifizieren, Filter anwenden

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK-M04_ARCHITECT_20251228_003554.md

## [2025-12-28 00:39:54] TASK-M04 - PROXY_PLAN (ki0)

### Summary
- Plan ist vollstaendig und gut strukturiert
- Line-Referenzen verifiziert: combination_engine.py:97-98 (min_sum/max_sum) und :202-215 (_passes_sum_filter)
- Erwartungswert E[sum]=710 korrekt fuer 20 Zahlen aus [1,70]
- Chi-Quadrat-Test als Signifikanzmetrik angemessen
- Config-Integration unter analysis.sum_windows passt zur bestehenden Struktur
- matplotlib bereits in requirements.txt vorhanden
- KENO-spezifisch (20 Zahlen pro Ziehung) - keine globalen Thresholds fuer andere Spiele
- Keine Architektur-Konflikte mit bestehenden Modulen

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-M04_PROXY_PLAN_20251228_003754.md



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
- kenobase/analysis/sum_distribution.py (NEU)
- scripts/analyze_sum_windows.py (NEU)
- kenobase/core/combination_engine.py
- kenobase/core/data_loader.py
- config/default.yaml
- data/raw/keno/KENO_ab_2018.csv (Daten)

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
- Plan ist vollstaendig und gut strukturiert
- Line-Referenzen verifiziert: combination_engine.py:97-98 (min_sum/max_sum) und :202-215 (_passes_sum_filter)
- Erwartungswert E[sum]=710 korrekt fuer 20 Zahlen aus [1,70]
- Chi-Quadrat-Test als Signifikanzmetrik angemessen
- Config-Integration unter analysis.sum_windows passt zur bestehenden Struktur
- matplotlib bereits in requirements.txt vorhanden
- KENO-spezifisch (20 Zahlen pro Ziehung) - keine globalen Thresholds fuer andere Spiele
- Keine Architektur-Konflikte mit bestehenden Modulen

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-M04_PROXY_PLAN_20251228_003754.md

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
task: TASK-M04
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_TASK-M04_EXECUTOR_20251228_003954.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
