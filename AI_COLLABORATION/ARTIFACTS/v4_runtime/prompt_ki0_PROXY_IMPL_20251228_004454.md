AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Summen-Fenster Analyse
TASK-ID: TASK-M04
PRIORITY: MEDIUM
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
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

## [2025-12-28 00:44:54] TASK-M04 - EXECUTOR (ki2)

### Summary
- Neues Modul kenobase/analysis/sum_distribution.py implementiert
- Script scripts/analyze_sum_windows.py erstellt mit CLI-Interface
- Config erweitert um analysis.sum_windows Sektion
- Analyse auf 2237 KENO-Ziehungen durchgefuehrt: mean=711.1, std=77.6
- Chi-Quadrat-Test gegen Gleichverteilung: p=0.0 (signifikant)
- Ein Cluster identifiziert: [605-845] mit 87.2% Dichte
- JSON-Export nach results/sum_windows_analysis.json verifiziert
- Plot-Generierung nach results/sum_windows_histogram.png verifiziert

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-M04_EXECUTOR_20251228_003954.md



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
- kenobase/core/combination_engine.py
- kenobase/core/data_loader.py
- config/default.yaml
- data/raw/keno/KENO_ab_2018.csv (Daten)
- kenobase/analysis/sum_distribution.py (NEU - 493 Zeilen)
- scripts/analyze_sum_windows.py (NEU - 227 Zeilen)
- config/default.yaml (analysis.sum_windows hinzugefuegt)
- kenobase/analysis/__init__.py (sum_distribution exports hinzugefuegt)

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
ROLLE: PROXY (User-Stellvertreter mit Projekt-Kontext)
AUFGABE: Pruefe die Implementation - NICHT nur mechanisch, sondern auf Architektur-Konsistenz.

PFLICHTLEKTUERE (vor Review):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Known Bugs & Integration Points
2. AI_COLLABORATION/SYSTEM_STATUS.json - Bei Architektur-Fragen

EFFIZIENZ-REGELN:
- Arbeite mit VORHERIGER OUTPUT + WORKING SET + Profil-Wissen
- Maximal 3-4 gezielte Reads
- Minimaler Sanity-Check (python -m py_compile, JSON-Validierung)

VORHERIGER OUTPUT (kurz):
- Neues Modul kenobase/analysis/sum_distribution.py implementiert
- Script scripts/analyze_sum_windows.py erstellt mit CLI-Interface
- Config erweitert um analysis.sum_windows Sektion
- Analyse auf 2237 KENO-Ziehungen durchgefuehrt: mean=711.1, std=77.6
- Chi-Quadrat-Test gegen Gleichverteilung: p=0.0 (signifikant)
- Ein Cluster identifiziert: [605-845] mit 87.2% Dichte
- JSON-Export nach results/sum_windows_analysis.json verifiziert
- Plot-Generierung nach results/sum_windows_histogram.png verifiziert

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-M04_EXECUTOR_20251228_003954.md

PRUEFKRITERIEN (4 Dimensionen):
1. MECHANISCH: Alle Schritte ausgefuehrt? Syntax OK? Acceptance Criteria erfuellt?
2. ARCHITEKTUR: Implementation passt zu ADRs? Keine Widersprueche eingefuehrt?
3. INTEGRATION: ALLE betroffenen Dateien geaendert? (siehe Known Integration Points)
   - hybrid_prediction_engine.py geaendert? -> production_orchestrator.py pruefen!
   - Config geaendert? -> Code der Config liest pruefen!
   - Threshold geaendert? -> Ist er global oder spezifisch?
4. KNOWN BUGS: Keiner der 10 Known Bugs reproduziert? (BUG-001 bis BUG-010)

RED FLAGS (sofort REJECTED):
- Aenderung in Datei A ohne korrespondierende Aenderung in Datei B
- Globale Werte wo spezifische noetig (BUG-001)
- Feature implementiert aber nicht im Orchestrator eingebunden (BUG-003)
- Config-Pfad im Code stimmt nicht mit YAML-Struktur (BUG-002)

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: APPROVED
task: TASK-M04
role: PROXY
phase: PROXY_IMPL
reviewed_handoff: "<nur filename oder leer>"
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

# Proxy Review (Implementation)

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK-M04_PROXY_IMPL_20251228_004454.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
