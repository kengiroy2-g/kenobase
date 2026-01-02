AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Jackpot-Hoehe vs. Zahlentyp Korrelation
TASK-ID: HOUSE-001
PRIORITY: P1
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 20:12:03] HOUSE-001 - ARCHITECT (ki1)

### Summary
- Analysiere Korrelation zwischen Jackpot-Hoehe und gezogenen Zahlentypen
- Zahlentypen: Birthday(1-31), Hoch(32-70), Gerade/Ungerade, Dekaden
- Daten: Keno_GQ_*.csv (Jackpot=0 Gewinner bei 10/10) + KENO_ab_2018.csv
- Neues Modul: kenobase/analysis/jackpot_correlation.py
- Output: results/hyp015_jackpot_correlation.json
- Test: tests/unit/test_jackpot_correlation.py
- Acceptance: Pearson r, p-Wert, Chi-Quadrat pro Zahlentyp

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_HOUSE-001_ARCHITECT_20251228_200903.md

## [2025-12-28 20:14:04] HOUSE-001 - PROXY_PLAN (ki0)

### Summary
- Plan folgt bewaehrtem Muster von odds_correlation.py (HYP-010)
- Datenquelle 10-9_KGDaten_gefiltert.csv hat korrektes Format
- Jackpot=0 Gewinner bei 10/10 ist korrekter Proxy fuer hohe Jackpots
- Zahlentypen Birthday(1-31), Hoch(32-70) konsistent mit Projekt
- __init__.py muss erweitert werden (Integration Point beachtet)
- Acceptance Criteria (|r|>0.2, p<0.05, Chi-Quadrat) sind messbar
- Script-Name: scripts/analyze_hyp015_jackpot.py (Konsistenz)
- APPROVED - weiter zu EXECUTOR

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HOUSE-001_PROXY_PLAN_20251228_201203.md



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
- kenobase/analysis/odds_correlation.py (Referenz-Implementation)
- kenobase/analysis/__init__.py
- kenobase/core/data_loader.py
- config/default.yaml
- Keno_GPTs/10-9_KGDaten_gefiltert.csv
- data/raw/keno/KENO_ab_2018.csv

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
- Plan folgt bewaehrtem Muster von odds_correlation.py (HYP-010)
- Datenquelle 10-9_KGDaten_gefiltert.csv hat korrektes Format
- Jackpot=0 Gewinner bei 10/10 ist korrekter Proxy fuer hohe Jackpots
- Zahlentypen Birthday(1-31), Hoch(32-70) konsistent mit Projekt
- __init__.py muss erweitert werden (Integration Point beachtet)
- Acceptance Criteria (|r|>0.2, p<0.05, Chi-Quadrat) sind messbar
- Script-Name: scripts/analyze_hyp015_jackpot.py (Konsistenz)
- APPROVED - weiter zu EXECUTOR

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HOUSE-001_PROXY_PLAN_20251228_201203.md

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
task: HOUSE-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_HOUSE-001_EXECUTOR_20251228_201404.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
