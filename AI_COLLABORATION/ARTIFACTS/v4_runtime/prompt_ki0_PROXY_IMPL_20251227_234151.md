AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: 111-Prinzip Falsifikation
TASK-ID: TASK-H06
PRIORITY: HIGH
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 23:16:50] TASK-H06 - PROXY_PLAN (ki0)

### Summary
- Plan ist methodisch korrekt: Chi-Quadrat Test + Kontrollgruppe fuer 111-Prinzip Falsifikation
- Nullhypothese klar formuliert: H0 = 111-Filter hat keine bessere Trefferquote als Zufall
- Akzeptanzkriterien messbar: p-Wert > 0.05 = widerlegt, Hit-Rate Differenz < 5% = widerlegt
- Template (analyze_hyp007.py) existiert und ist geeignet - Monte Carlo + Permutationstest Methodik
- Datenbasis verifiziert: data/raw/keno/KENO_ab_2018.csv existiert
- WORKING_SET vollstaendig fuer Executor
- Risiko-Mitigation adaequat: Kombinationsgroesse variieren bei zu wenig 111-Kombinationen
- Aufwandsschaetzung (5h) realistisch basierend auf Template-Verfuegbarkeit

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-H06_PROXY_PLAN_20251227_231350.md

## [2025-12-27 23:41:51] TASK-H06 - EXECUTOR (ki2)

### Summary
- Script erstellt: scripts/falsify_hyp008_111.py - Monte Carlo basierte 111-Prinzip Falsifikation
- 111-Prinzip Algorithmus aus HYPOTHESES_CATALOG.md Lines 198-224 implementiert
- 50,000 Random Samples generiert: 42 erfuellen 111-Prinzip (0.084%)
- Hit-Rate 111: 0.225181 vs non-111: 0.225446 (Differenz: -0.0266%)
- Chi-Quadrat p-Wert: 0.960637 >> 0.05 (nicht signifikant)
- VERDICT: HYP-008 FALSIFIED - 111-Prinzip bietet keinen Vorteil gegenueber Zufall
- Alle 3 Acceptance Criteria PASSED
- JSON Report: results/hyp008_111_falsification.json

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-H06_EXECUTOR_20251227_231650.md



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
- all_code/Iteration111_V4.py
- AI_COLLABORATION/KNOWLEDGE_BASE/HYPOTHESES_CATALOG.md
- config/default.yaml
- kenobase/core/data_loader.py
- scripts/analyze_hyp007.py (als Template)
- scripts/falsify_hyp008_111.py
- results/hyp008_111_falsification.json

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
- Script erstellt: scripts/falsify_hyp008_111.py - Monte Carlo basierte 111-Prinzip Falsifikation
- 111-Prinzip Algorithmus aus HYPOTHESES_CATALOG.md Lines 198-224 implementiert
- 50,000 Random Samples generiert: 42 erfuellen 111-Prinzip (0.084%)
- Hit-Rate 111: 0.225181 vs non-111: 0.225446 (Differenz: -0.0266%)
- Chi-Quadrat p-Wert: 0.960637 >> 0.05 (nicht signifikant)
- VERDICT: HYP-008 FALSIFIED - 111-Prinzip bietet keinen Vorteil gegenueber Zufall
- Alle 3 Acceptance Criteria PASSED
- JSON Report: results/hyp008_111_falsification.json

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-H06_EXECUTOR_20251227_231650.md

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
task: TASK-H06
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK-H06_PROXY_IMPL_20251227_234151.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
