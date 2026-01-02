AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Index-Reset nach GK1 Analyse
TASK-ID: HYP005-001
PRIORITY: HOCH
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 15:25:31] HYP005-001 - ARCHITECT (ki1)

### Summary
- Index-Reset nach GK1 analysiert: number_index.py bereits implementiert
- Korrelationsanalyse calculate_index_correlation() vorhanden mit t-Test
- GK1-Events aus 10-9_KGDaten_gefiltert.csv oder 10-9_Liste_GK1_Treffer.csv
- Analyse-Script scripts/analyze_index_reset.py fehlt (NEU zu erstellen)
- Acceptance Criteria: p < 0.05 fuer Index-Vorhersagekraft
- 7 Dateien im Working Set identifiziert
- Implementierungsplan mit 5 Schritten erstellt

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_HYP005-001_ARCHITECT_20251228_152231.md

## [2025-12-28 15:27:31] HYP005-001 - PROXY_PLAN (ki0)

### Summary
- Plan ist vollstaendig: 5 Schritte mit klaren Deliverables
- Acceptance Criteria messbar: p < 0.05 fuer Index-Vorhersagekraft
- number_index.py:166-328 bereits implementiert mit calculate_index_correlation()
- data_loader.py:743-807 hat _parse_gk1_summary() fuer GK1-Events
- Keine globalen Thresholds - per-number Granularitaet korrekt
- Tests und Script fehlen - beide im Plan enthalten
- Risiko LOW: Kernlogik existiert, nur Wrapper fehlt
- Empfehlung: APPROVED fuer Executor

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP005-001_PROXY_PLAN_20251228_152531.md

## [2025-12-28 15:32:31] HYP005-001 - EXECUTOR (ki2)

### Summary
- Created scripts/analyze_index_reset.py for HYP-005 Index-Reset analysis
- Created tests/unit/test_number_index.py with 18 unit tests (all passing)
- Script loads KENO draws + GK1 events via DataLoader
- Uses existing calculate_index_correlation() from number_index.py
- Output format: JSON with full statistical results
- Ran successfully: p=0.0419 < 0.05 -> SUPPORTED
- Acceptance Criteria MET: Index shows significant predictive power

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HYP005-001_EXECUTOR_20251228_152731.md



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
- kenobase/analysis/number_index.py
- kenobase/core/data_loader.py
- kenobase/analysis/gk1_waiting.py
- scripts/analyze_hyp005.py
- Keno_GPTs/10-9_KGDaten_gefiltert.csv (Schema)
- data/raw/keno/KENO_ab_2018.csv (Schema)
- scripts/analyze_index_reset.py (NEW)
- tests/unit/test_number_index.py (NEW)

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
- Created scripts/analyze_index_reset.py for HYP-005 Index-Reset analysis
- Created tests/unit/test_number_index.py with 18 unit tests (all passing)
- Script loads KENO draws + GK1 events via DataLoader
- Uses existing calculate_index_correlation() from number_index.py
- Output format: JSON with full statistical results
- Ran successfully: p=0.0419 < 0.05 -> SUPPORTED
- Acceptance Criteria MET: Index shows significant predictive power

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HYP005-001_EXECUTOR_20251228_152731.md

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
task: HYP005-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_HYP005-001_PROXY_IMPL_20251228_153231.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
