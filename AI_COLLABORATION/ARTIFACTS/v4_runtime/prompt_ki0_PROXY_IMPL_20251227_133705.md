AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Haeufigkeits-Anomalie validieren (Chi-Quadrat)
TASK-ID: HYP-009
PRIORITY: HIGH
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 13:33:05] HYP-009 - ARCHITECT (ki1)

### Summary
- Script existiert: scripts/validate_hypotheses.py mit Chi-Quadrat-Test
- Daten vorhanden: data/raw/keno/KENO_ab_2018.csv (2237 Ziehungen)
- Implementierung nutzt scipy.stats.chisquare gegen Gleichverteilung
- Acceptance Criteria: p-value < 0.05 -> Gleichverteilung abgelehnt
- EXECUTOR soll: Script ausfuehren, Ergebnis dokumentieren
- Erweiterung: Zeitfenster-Analyse (Hot/Cold Stabilitaet) empfohlen

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_HYP-009_ARCHITECT_20251227_133105.md

## [2025-12-27 13:35:05] HYP-009 - PROXY_PLAN (ki0)

### Summary
- Script scripts/validate_hypotheses.py existiert und ist korrekt implementiert
- Chi-Quadrat-Test gegen Gleichverteilung (scipy.stats.chisquare) korrekt
- Daten vorhanden: data/raw/keno/KENO_ab_2018.csv
- Acceptance Criteria klar definiert: p < 0.05 = REJECTED, p >= 0.05 = ACCEPTED
- EXECUTOR soll Script ausfuehren, Output speichern, Ergebnis dokumentieren
- Keine Architektur-Konflikte oder Known Bugs erkannt
- Plan ist einfach und fokussiert - kein Overengineering
- Repro-Command: python scripts/validate_hypotheses.py --hypothesis HYP-009

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-009_PROXY_PLAN_20251227_133305.md

## [2025-12-27 13:37:05] HYP-009 - EXECUTOR (ki2)

### Summary
- Executed scripts/validate_hypotheses.py --hypothesis HYP-009
- Data: data/raw/keno/KENO_ab_2018.csv (N=2237 Ziehungen, 44740 Zahlen)
- Chi-Quadrat: chi2=52.27, p=0.9333 >> threshold 0.05
- Result: ACCEPTED (Gleichverteilung NICHT abgelehnt)
- KENO-Zahlen erscheinen statistisch zufaellig verteilt
- JSON-Output: AI_COLLABORATION/ARTIFACTS/HYP-009_chi_quadrat_result.json
- Handoff: AI_COLLABORATION/HANDOFFS/ki2_HYP-009_EXECUTOR_20251227_133505.md

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HYP-009_EXECUTOR_20251227_133505.md



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
- AI_COLLABORATION/ARTIFACTS/HYP-009_chi_quadrat_result.json
- AI_COLLABORATION/HANDOFFS/ki2_HYP-009_EXECUTOR_20251227_133505.md

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
- Executed scripts/validate_hypotheses.py --hypothesis HYP-009
- Data: data/raw/keno/KENO_ab_2018.csv (N=2237 Ziehungen, 44740 Zahlen)
- Chi-Quadrat: chi2=52.27, p=0.9333 >> threshold 0.05
- Result: ACCEPTED (Gleichverteilung NICHT abgelehnt)
- KENO-Zahlen erscheinen statistisch zufaellig verteilt
- JSON-Output: AI_COLLABORATION/ARTIFACTS/HYP-009_chi_quadrat_result.json
- Handoff: AI_COLLABORATION/HANDOFFS/ki2_HYP-009_EXECUTOR_20251227_133505.md

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HYP-009_EXECUTOR_20251227_133505.md

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
task: HYP-009
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_HYP-009_PROXY_IMPL_20251227_133705.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
