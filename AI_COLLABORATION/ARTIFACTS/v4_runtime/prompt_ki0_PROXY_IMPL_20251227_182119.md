AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Ergebnis-Synthese und Vorhersage-Modell
TASK-ID: ISSUE-006
PRIORITY: HIGH
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 18:15:18] ISSUE-006 - PROXY_PLAN (ki0)

### Summary
- Plan ist architektonisch sauber: kenobase/prediction/ als neues Modul
- Verfuegbare HYP-Ergebnisse: HYP-007, HYP-010, HYP-011, HYP-012 (4 Dateien)
- Fehlend: HYP-001, HYP-004, HYP-006 Ergebnisse (Scripts existieren, aber keine JSON)
- Synthese-Ansatz valide: combined_score aus heterogenen Hypothesen
- Granularitaet per-number ist korrekt fuer KENO (70 Zahlen)
- Keine globalen Thresholds noetig - Scores normalisiert 0-1
- Integration klar: synthesizer.py liest results/*.json, predict.py nutzt Synthesizer
- Aufwand realistisch: 4-6h bei 4 verfuegbaren Hypothesen

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_ISSUE-006_PROXY_PLAN_20251227_181318.md

## [2025-12-27 18:21:19] ISSUE-006 - EXECUTOR (ki2)

### Summary
- Created kenobase/prediction/ module with HypothesisSynthesizer
- Implemented synthesizer.py: loads HYP-007/010/011/012, computes per-number combined_score
- Implemented recommendation.py: Tier A/B/C with decade filter + avalanche warning
- Created scripts/predict.py CLI with --top, --max-per-decade, --output options
- All 13 unit tests pass
- Verified: 4 hypotheses loaded, 6 recommendations generated
- Top: Zahl 36 (0.754 Tier A), Zahl 64 (0.718 Tier A)
- Anti-Avalanche warning integrated (theta = 88% for 6 numbers)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_ISSUE-006_EXECUTOR_20251227_181518.md



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
- kenobase/prediction/__init__.py
- kenobase/prediction/synthesizer.py
- kenobase/prediction/recommendation.py
- scripts/predict.py
- tests/unit/test_synthesizer.py
- results/prediction_synthesis.json

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
- Created kenobase/prediction/ module with HypothesisSynthesizer
- Implemented synthesizer.py: loads HYP-007/010/011/012, computes per-number combined_score
- Implemented recommendation.py: Tier A/B/C with decade filter + avalanche warning
- Created scripts/predict.py CLI with --top, --max-per-decade, --output options
- All 13 unit tests pass
- Verified: 4 hypotheses loaded, 6 recommendations generated
- Top: Zahl 36 (0.754 Tier A), Zahl 64 (0.718 Tier A)
- Anti-Avalanche warning integrated (theta = 88% for 6 numbers)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_ISSUE-006_EXECUTOR_20251227_181518.md

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
task: ISSUE-006
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_ISSUE-006_PROXY_IMPL_20251227_182119.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
