AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Zahlen-Arbitrage
TASK-ID: STRAT-002
PRIORITY: P2
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 06:21:45] STRAT-002 - ARCHITECT (ki1)

### Summary
- Zahlen-Arbitrage = Cross-Lottery Number Exploitation basierend auf Lag-Korrelationen
- Einzige robuste Edge aus ecosystem_graph: KENO->AUSWAHLWETTE lag=7, lift=2.41, q=0.027
- Strategie-Konzept: Wenn Zahl X bei Spiel A, dann Zahl Y bei Spiel B nach N Tagen wahrscheinlicher
- Train/Test Split erforderlich (Train vor 2024-01-01, Test danach)
- Backtest mit Schedule-preserving Permutation als Nullmodell
- Modul zu erstellen: kenobase/analysis/number_arbitrage.py
- Script zu erstellen: scripts/backtest_number_arbitrage.py
- EuroJackpot als Negativ-Kontrolle (sollte KEINE Korrelation zeigen)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_STRAT-002_ARCHITECT_20251230_061745.md

## [2025-12-30 06:23:45] STRAT-002 - PROXY_PLAN (ki0)

### Summary
- Plan korrekt strukturiert mit 4 Phasen und klaren Acceptance Criteria
- Granularitaet per-number-pair ist richtig (nicht global)
- Train/Test Split 2022-2023 vs 2024+ korrekt spezifiziert
- EuroJackpot als Negativ-Kontrolle eingebaut (Axiom-First konform)
- Bestehende cross_lottery_coupling.py Funktionen werden korrekt genutzt
- Einzige robuste Edge (KENO->AUSWAHLWETTE, lag=7, lift=2.41, q=0.027) ist gut dokumentiert
- Frozen-Rules im Test-Set garantiert (keine Parameter-Aenderungen)
- ROI-Warnung bei >0% eingebaut (physisch unplausibel wg Axiom A1)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_STRAT-002_PROXY_PLAN_20251230_062145.md



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
- kenobase/analysis/cross_lottery_coupling.py
- kenobase/core/normalizer.py
- results/ecosystem_graph.json
- scripts/analyze_cross_lottery_coupling.py
- tests/unit/test_cross_lottery_coupling.py

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
- Plan korrekt strukturiert mit 4 Phasen und klaren Acceptance Criteria
- Granularitaet per-number-pair ist richtig (nicht global)
- Train/Test Split 2022-2023 vs 2024+ korrekt spezifiziert
- EuroJackpot als Negativ-Kontrolle eingebaut (Axiom-First konform)
- Bestehende cross_lottery_coupling.py Funktionen werden korrekt genutzt
- Einzige robuste Edge (KENO->AUSWAHLWETTE, lag=7, lift=2.41, q=0.027) ist gut dokumentiert
- Frozen-Rules im Test-Set garantiert (keine Parameter-Aenderungen)
- ROI-Warnung bei >0% eingebaut (physisch unplausibel wg Axiom A1)

FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_STRAT-002_PROXY_PLAN_20251230_062145.md

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
task: STRAT-002
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
- Datei: AI_COLLABORATION/HANDOFFS/ki2_STRAT-002_EXECUTOR_20251230_062345.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
