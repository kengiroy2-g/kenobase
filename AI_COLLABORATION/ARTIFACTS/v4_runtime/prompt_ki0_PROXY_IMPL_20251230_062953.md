AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Bundesland-Zyklus: Datenbedarf + Ingestion Plan
TASK-ID: DATAREQ-001
PRIORITY: P1
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 06:23:53] DATAREQ-001 - PROXY_PLAN (ki0)

### Summary
- A6 (Regionale Verteilung) Datenbedarf korrekt identifiziert
- REGIONAL_DATA_RESEARCH.md zeigt DATENQUELLEN sind vorhanden (nicht fehlend!)
- Pressemitteilungen 16 Bundeslaender = primaere Quelle (URLs dokumentiert)
- Lotto Hessen API = automatisierbare JSON-Quelle (entdeckt!)
- 5-Phasen Pipeline ist sinnvoll (8h Gesamtaufwand)
- Proxy-Methode (popularity_proxy.py) bereits als Fallback dokumentiert
- Vorheriger ESCALATE war FEHLINTERPRETATION des Research-Dokuments
- Plan kann starten mit Hybrid-Ansatz: Hessen API + 2-3 Bundeslaender Scraping

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DATAREQ-001_PROXY_PLAN_20251230_062153.md

## [2025-12-30 06:29:53] DATAREQ-001 - EXECUTOR (ki6)

### Summary
- A6 validation script created (scripts/validate_a6_regional.py)
- Implements P6.1 (population correlation), P6.2 (jackpot per capita), P6.3 (temporal uniformity)
- Lotto Hessen API client added (kenobase/scraper/lotto_hessen_api.py)
- Tests added and passing (7/7)
- Existing scraper infrastructure already complete (16 Landeslotterien configured)
- Current data: only 2 records (Brandenburg) - insufficient for full validation
- Recommendation: Run full scrape with `python scripts/scrape_press.py --all`

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_DATAREQ-001_EXECUTOR_20251230_062353.md



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
- scripts/validate_a6_regional.py
- kenobase/scraper/lotto_hessen_api.py
- kenobase/scraper/__init__.py
- tests/unit/test_a6_validation.py
- results/a6_validation.json

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
- A6 validation script created (scripts/validate_a6_regional.py)
- Implements P6.1 (population correlation), P6.2 (jackpot per capita), P6.3 (temporal uniformity)
- Lotto Hessen API client added (kenobase/scraper/lotto_hessen_api.py)
- Tests added and passing (7/7)
- Existing scraper infrastructure already complete (16 Landeslotterien configured)
- Current data: only 2 records (Brandenburg) - insufficient for full validation
- Recommendation: Run full scrape with `python scripts/scrape_press.py --all`

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_DATAREQ-001_EXECUTOR_20251230_062353.md

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
task: DATAREQ-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_DATAREQ-001_PROXY_IMPL_20251230_062953.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
