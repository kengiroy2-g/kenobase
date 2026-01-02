AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Basis-Zahlenpool und Index-System ermitteln
TASK-ID: HYP-005
PRIORITY: HIGH
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 13:48:06] HYP-005 - PROXY_PLAN (ki0)

### Summary
- Plan ist konzeptionell solide: Index = Haeufigkeit seit letztem GK1-Event
- Datenquellen verifiziert: KENO_ab_2018.csv (N=2237 Zeilen), 10-9_KGDaten_gefiltert.csv (N=20 GK1-Events)
- Integration in frequency.py-Architektur passt (bestehende FrequencyResult-Muster nutzbar)
- Neues Modul number_index.py korrekt isoliert (keine Cross-File-Probleme)
- GK1-Events sind heterogen (Keno-Typ 9 und 10 gemischt) - kein Blocker, aber bei Reset-Logik beachten
- validate_hypotheses.py existiert bereits als Stub - Integration moeglich
- Output-Pfad data/results/hyp005_index_table.json muss noch erstellt werden
- Keine globalen Thresholds wo spezifische noetig - CLEAN

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-005_PROXY_PLAN_20251227_134506.md

## [2025-12-27 13:54:06] HYP-005 - EXECUTOR (ki2)

### Summary
- Neues Modul number_index.py mit Index-Berechnung seit GK1-Reset implementiert
- calculate_index_table() berechnet Index fuer alle 70 Zahlen seit letztem GK1-Event
- calculate_index_correlation() analysiert Korrelation zwischen Index und Trefferrate
- GK1-Events heterogen (Keno-Typ 9 und 10) - beide werden als Reset behandelt
- Integration in validate_hypotheses.py als HYP-005-GK1
- Index-Tabelle exportiert nach data/results/hyp005_index_table.json
- HYP-005-GK1 CONFIRMED: p=0.0419, High-Index 3.17 vs. Low-Index 3.08
- Effect Size gering (0.06) - statistisch signifikant, praktisch marginal

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HYP-005_EXECUTOR_20251227_134806.md



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
- kenobase/analysis/number_index.py (NEW)
- kenobase/analysis/__init__.py
- scripts/validate_hypotheses.py
- data/results/hyp005_index_table.json (NEW)

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
- Neues Modul number_index.py mit Index-Berechnung seit GK1-Reset implementiert
- calculate_index_table() berechnet Index fuer alle 70 Zahlen seit letztem GK1-Event
- calculate_index_correlation() analysiert Korrelation zwischen Index und Trefferrate
- GK1-Events heterogen (Keno-Typ 9 und 10) - beide werden als Reset behandelt
- Integration in validate_hypotheses.py als HYP-005-GK1
- Index-Tabelle exportiert nach data/results/hyp005_index_table.json
- HYP-005-GK1 CONFIRMED: p=0.0419, High-Index 3.17 vs. Low-Index 3.08
- Effect Size gering (0.06) - statistisch signifikant, praktisch marginal

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HYP-005_EXECUTOR_20251227_134806.md

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
task: HYP-005
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_HYP-005_PROXY_IMPL_20251227_135406.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
