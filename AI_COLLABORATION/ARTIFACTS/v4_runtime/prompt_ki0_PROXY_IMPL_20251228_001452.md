AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Zehnergruppen-Regel Validierung
TASK-ID: TASK-M02
PRIORITY: MEDIUM
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 00:10:52] TASK-M02 - PROXY_PLAN (ki0)

### Summary
- ARCHITECT Plan ist konzeptionell solide: A/B-Test mit/ohne Zehnergruppen-Filter
- combination_engine.py:181-200 implementiert bereits _passes_decade_filter() - kann fuer A/B wiederverwendet werden
- backtest.py existiert mit F1-Metriken - validate_zehnergruppen.py kann diese Logik importieren
- Grid-Search fuer max_per_decade (1-5) ist sinnvoll - CLAUDE.md sagt default=3 (Zeile 75)
- Statistischer Test (paired t-test) ist angemessen fuer Signifikanzpruefung
- Keine BUG-001 Verletzung: max_per_decade ist per-game in config/default.yaml definiert
- Repro-Befehl ist klar und ausfuehrbar
- KEIN neues Modul noetig - nur neues Script in scripts/

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-M02_PROXY_PLAN_20251228_000852.md

## [2025-12-28 00:14:52] TASK-M02 - EXECUTOR (ki2)

### Summary
- Neues Script scripts/validate_zehnergruppen.py erstellt (A/B-Test + Grid-Search)
- 6 Varianten getestet: no_filter, max_1, max_2, max_3, max_4, max_5
- A/B-Test max_3 vs no_filter zeigt keinen signifikanten Unterschied (delta=0.0)
- Grid-Search: max_2-5 gleichwertig (F1=0.0293), max_1 schlechter (F1=0.0269)
- Paired t-test implementiert via scipy.stats.ttest_rel
- JSON-Output nach results/zehnergruppen_validation.json
- _safe_value() fuer nan/numpy Typ-Handling implementiert

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-M02_EXECUTOR_20251228_001052.md



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
- scripts/validate_zehnergruppen.py
- results/zehnergruppen_validation.json

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
- Neues Script scripts/validate_zehnergruppen.py erstellt (A/B-Test + Grid-Search)
- 6 Varianten getestet: no_filter, max_1, max_2, max_3, max_4, max_5
- A/B-Test max_3 vs no_filter zeigt keinen signifikanten Unterschied (delta=0.0)
- Grid-Search: max_2-5 gleichwertig (F1=0.0293), max_1 schlechter (F1=0.0269)
- Paired t-test implementiert via scipy.stats.ttest_rel
- JSON-Output nach results/zehnergruppen_validation.json
- _safe_value() fuer nan/numpy Typ-Handling implementiert

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-M02_EXECUTOR_20251228_001052.md

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
task: TASK-M02
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK-M02_PROXY_IMPL_20251228_001452.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
