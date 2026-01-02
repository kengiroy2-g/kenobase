AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Regionale Daten Erweiterung
TASK-ID: DIST-004
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 22:33:10] DIST-004 - ARCHITECT (ki1)

### Summary
- Analysiert vorhandene Module: regions.py (106 LOC), regional_affinity.py (571 LOC), popularity_correlation.py (484 LOC)
- REGIONAL_DATA_RESEARCH.md dokumentiert Datenlage: direkte Regionaldaten NICHT verfuegbar
- Proxy-Methode via Gewinner-Anzahl (GQ-Daten) ist bereits konzipiert
- Pressemitteilungen als neue Datenquelle identifiziert (16 Landeslotterien)
- Lotto Hessen API entdeckt (services.lotto-hessen.de) - JSON-Endpunkte fuer KENO
- 3 Erweiterungs-Schritte definiert: Scraper, Popularity-Proxy, EuroJackpot-Mapping

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_DIST-004_ARCHITECT_20251228_223010.md

## [2025-12-28 22:35:10] DIST-004 - PROXY_PLAN (ki0)

### Summary (fallback)
- ---  **status: APPROVED**  **task: DIST-004**  **role: PROXY**  **phase: PROXY_PLAN**  **reviewed_handoff: ki1_DIST-004_ARCHITECT_20251228_223010.md**    ---    # Proxy Review Summary    Plan wurde als **APPROVED** bewertet. Hauptgruende:    1. **Fokussierter Scope:** Nur Phase B ...

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DIST-004_PROXY_PLAN_20251228_223310.md

## [2025-12-28 22:41:10] DIST-004 - EXECUTOR (ki2)

### Summary
- Added BirthdayCorrelationResult dataclass for birthday-winners correlation
- Added calculate_birthday_score() function (fraction of 1-31 numbers)
- Added correlate_birthday_with_winners() with rolling-window stability test
- Created scripts/analyze_popularity_proxy.py (296 LOC CLI tool)
- Added 10 new tests (5 for birthday_score, 5 for correlation)
- All 31 tests pass in test_popularity_correlation.py
- Output: results/popularity_proxy.json (NO_DATA - GQ files not available)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_DIST-004_EXECUTOR_20251228_223510.md



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
- kenobase/analysis/popularity_correlation.py
- scripts/analyze_popularity_proxy.py
- tests/unit/test_popularity_correlation.py
- results/popularity_proxy.json

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
- Added BirthdayCorrelationResult dataclass for birthday-winners correlation
- Added calculate_birthday_score() function (fraction of 1-31 numbers)
- Added correlate_birthday_with_winners() with rolling-window stability test
- Created scripts/analyze_popularity_proxy.py (296 LOC CLI tool)
- Added 10 new tests (5 for birthday_score, 5 for correlation)
- All 31 tests pass in test_popularity_correlation.py
- Output: results/popularity_proxy.json (NO_DATA - GQ files not available)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_DIST-004_EXECUTOR_20251228_223510.md

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
task: DIST-004
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_DIST-004_PROXY_IMPL_20251228_224110.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
