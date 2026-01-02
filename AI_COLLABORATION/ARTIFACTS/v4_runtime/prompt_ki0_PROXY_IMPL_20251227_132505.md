AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Schnelle Hypothesen-Validierungen
TASK-ID: TASK-F03
PRIORITY: HIGH
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 13:21:04] TASK-F03 - PROXY_PLAN (ki0)

### Summary
- Plan konzeptionell geprueft - 3 Hypothesen sinnvoll priorisiert
- HYP-009 (Chi-Quadrat) schnellste Validierung - frequency.py vorhanden aber Chi-Quadrat fehlt
- HYP-005 (Zahlenpool-Index) erfordert neue Logik - Index seit GK1-Reset nicht implementiert
- HYP-002 (Jackpot-Zyklen) erfordert Zeitintervall-Analyse zwischen GK1-Events
- scripts/validate_hypotheses.py als zentrales Script sinnvoll
- Acceptance Criteria klar: p-Wert < 0.05, Korrelation r > 0.3
- scipy.stats.chisquare fuer Chi-Quadrat-Test empfohlen
- Keine architekturellen Red Flags erkannt

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-F03_PROXY_PLAN_20251227_131904.md

## [2025-12-27 13:25:05] TASK-F03 - EXECUTOR (ki2)

### Summary
- scripts/validate_hypotheses.py erstellt mit Chi-Quadrat, Zahlenpool-Index und Jackpot-Zyklen Tests
- HYP-009 (Chi-Quadrat): ACCEPTED - Zahlen gleichverteilt (p=0.9333), keine Manipulation detektiert
- HYP-005 (Zahlenpool-Index): REJECTED - 3.15 vs. 3.14 Treffer (Cohen's d=0.004), kein Vorhersagewert
- HYP-002 (Jackpot-Zyklen): RANDOM - Intervalle exponentiell (KS p=0.5878), keine Muster
- 2237 Ziehungen analysiert, 20 GK1-Events geprueft
- Alle 3 Hypothesen zeigen: KENO-Daten verhalten sich wie echter Zufall
- JSON-Ergebnisse in AI_COLLABORATION/ARTIFACTS/hypotheses_validation_results.json

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-F03_EXECUTOR_20251227_132105.md



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
- kenobase/analysis/frequency.py
- Keno_GPTs/10-9_KGDaten_gefiltert.csv
- data/raw/keno/KENO_ab_2018.csv
- requirements.txt
- scripts/validate_hypotheses.py
- AI_COLLABORATION/ARTIFACTS/hypotheses_validation_results.json

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
- scripts/validate_hypotheses.py erstellt mit Chi-Quadrat, Zahlenpool-Index und Jackpot-Zyklen Tests
- HYP-009 (Chi-Quadrat): ACCEPTED - Zahlen gleichverteilt (p=0.9333), keine Manipulation detektiert
- HYP-005 (Zahlenpool-Index): REJECTED - 3.15 vs. 3.14 Treffer (Cohen's d=0.004), kein Vorhersagewert
- HYP-002 (Jackpot-Zyklen): RANDOM - Intervalle exponentiell (KS p=0.5878), keine Muster
- 2237 Ziehungen analysiert, 20 GK1-Events geprueft
- Alle 3 Hypothesen zeigen: KENO-Daten verhalten sich wie echter Zufall
- JSON-Ergebnisse in AI_COLLABORATION/ARTIFACTS/hypotheses_validation_results.json

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-F03_EXECUTOR_20251227_132105.md

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
task: TASK-F03
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK-F03_PROXY_IMPL_20251227_132505.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
