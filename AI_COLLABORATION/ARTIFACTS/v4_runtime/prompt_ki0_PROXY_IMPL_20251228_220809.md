AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Auszahlung-Gewinner Ratio Analyse
TASK-ID: DIST-002
PRIORITY: P1
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 22:01:08] DIST-002 - ARCHITECT (ki1)

### Summary
- Auszahlung-Gewinner Ratio Analyse erweitert HYP-001 Distribution
- Datenquelle: Keno_GPTs/KENO_Quote_details_2023.csv (mit Auszahlung-Spalte)
- Neue Metrik: payout_per_winner = Auszahlung / Anzahl der Gewinner
- Erkennt Anomalien bei ungewoehnlichem Auszahlungs-Verhaeltnis
- Erweiterung des bestehenden distribution.py Moduls
- Acceptance Criteria: 6 Testfaelle definiert

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_DIST-002_ARCHITECT_20251228_215808.md

## [2025-12-28 22:03:08] DIST-002 - PROXY_PLAN (ki0)

### Summary
- Plan konzeptionell korrekt: payout_per_winner = Auszahlung / Anzahl der Gewinner
- Datenquelle verifiziert: KENO_Quote_details_2023.csv hat native Auszahlung-Spalte
- Granularitaet per-gewinnklasse (Keno-Typ x Richtige) ist korrekt
- CSV-Spalte heisst "Gewinn/1Eur" nicht "1 Euro Gewinn" - beachten
- Erweiterung distribution.py statt neues Modul - architektonisch sauber
- Working Set vollstaendig: 5 Dateien korrekt identifiziert
- Tests (test_distribution.py) muessen erweitert werden fuer neue Metrik
- Division by zero bei Gewinner=0 behandeln

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DIST-002_PROXY_PLAN_20251228_220108.md

## [2025-12-28 22:08:09] DIST-002 - EXECUTOR (ki2)

### Summary
- Added PayoutRatioResult dataclass to distribution.py
- Implemented analyze_payout_ratio() with division-by-zero handling
- Implemented load_quote_details_data() for semicolon-separated CSV
- Implemented detect_payout_ratio_anomalies() for CV and zero-draw detection
- Added 6 unit tests in TestPayoutRatioAnalysis - all 6 PASSED
- Extended analyze_distribution.py with --mode payout-ratio CLI option
- Ran end-to-end test with real data - results saved to results/dist002_payout_ratio.json

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_DIST-002_EXECUTOR_20251228_220309.md



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
- kenobase/analysis/distribution.py
- scripts/analyze_distribution.py
- tests/unit/test_distribution.py
- Keno_GPTs/KENO_Quote_details_2023.csv
- config/default.yaml
- results/dist002_payout_ratio.json

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
- Added PayoutRatioResult dataclass to distribution.py
- Implemented analyze_payout_ratio() with division-by-zero handling
- Implemented load_quote_details_data() for semicolon-separated CSV
- Implemented detect_payout_ratio_anomalies() for CV and zero-draw detection
- Added 6 unit tests in TestPayoutRatioAnalysis - all 6 PASSED
- Extended analyze_distribution.py with --mode payout-ratio CLI option
- Ran end-to-end test with real data - results saved to results/dist002_payout_ratio.json

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_DIST-002_EXECUTOR_20251228_220309.md

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
task: DIST-002
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_DIST-002_PROXY_IMPL_20251228_220809.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
