AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Inverse Korrelation beliebte vs. gezogene Zahlen
TASK-ID: HYP-004
PRIORITY: HIGH
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 14:48:08] HYP-004 - PROXY_PLAN (ki0)

### Summary
- Plan ist konzeptionell korrekt: Inverse Korrelation beliebte vs. gezogene Zahlen
- GQ-Daten VORHANDEN in Keno_GPTs/: Keno_GQ_2022_2023-2024.csv (27.685 Zeilen)
- Architect-Aussage "GQ-Daten fehlen" ist FALSCH - Daten existieren, nur nicht in data/raw kopiert
- Fallback-Heuristik (Geburtstage 1-31, schoene Zahlen) ist guter Plan B
- frequency.py existiert mit solider Basis (calculate_frequency, rolling_frequency)
- Spearman-Korrelation r < -0.2 mit p < 0.05 ist messbares Akzeptanzkriterium
- Rolling 30-Tage Windows fuer Walk-Forward Validation ist methodisch korrekt
- Neues Modul popularity_correlation.py ist korrekter Ansatz

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-004_PROXY_PLAN_20251227_144608.md

## [2025-12-27 14:54:09] HYP-004 - EXECUTOR (ki2)

### Summary
- Created kenobase/analysis/popularity_correlation.py with Spearman correlation analysis
- Implemented load_gq_popularity() using GQ data from Keno_GPTs/Keno_GQ_2022_2023-2024.csv
- 21 unit tests created and passing
- HYP-004 NOT SUPPORTED: r=0.0497, p=0.683 (need r<-0.2, p<0.05)
- Only 2% of rolling windows show supporting evidence
- Handoff: AI_COLLABORATION/HANDOFFS/ki2_HYP-004_EXECUTOR_20251227_144808.md

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HYP-004_EXECUTOR_20251227_144808.md



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
- kenobase/analysis/popularity_correlation.py (NEW)
- kenobase/analysis/__init__.py (MODIFIED)
- scripts/analyze_hyp004.py (NEW)
- tests/unit/test_popularity_correlation.py (NEW)
- data/results/hyp004_correlation.json (GENERATED)

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
- Created kenobase/analysis/popularity_correlation.py with Spearman correlation analysis
- Implemented load_gq_popularity() using GQ data from Keno_GPTs/Keno_GQ_2022_2023-2024.csv
- 21 unit tests created and passing
- HYP-004 NOT SUPPORTED: r=0.0497, p=0.683 (need r<-0.2, p<0.05)
- Only 2% of rolling windows show supporting evidence
- Handoff: AI_COLLABORATION/HANDOFFS/ki2_HYP-004_EXECUTOR_20251227_144808.md

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HYP-004_EXECUTOR_20251227_144808.md

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
task: HYP-004
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_HYP-004_PROXY_IMPL_20251227_145409.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
