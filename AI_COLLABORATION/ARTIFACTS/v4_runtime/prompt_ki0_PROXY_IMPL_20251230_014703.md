AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Axiome + falsifizierbare Predictions definieren
TASK-ID: AXIOM-001
PRIORITY: P1
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 01:41:03] AXIOM-001 - PROXY_PLAN (ki0)

### Summary
- Handoff VOLLSTAENDIG (282 Zeilen) - alle 7 Axiome (A1-A7) mit 21 Predictions dokumentiert
- Vorherige PROXY-Iteration war fehlerhaft - Datei war damals truncated, jetzt komplett
- Train/Test-Split sauber definiert: pre-2024 Train, 2024+ Test (frozen rules)
- EuroJackpot als Negativ-Kontrollkanal korrekt spezifiziert
- Nullmodell-Strategie pro Prediction-Typ implementierbar (4 Typen)
- 5-Step Executor-Checkliste mit klaren Acceptance Criteria
- A6 (Regionale Verteilung) als DATAREQ-001 markiert - akzeptabel
- Risiko P-hacking durch FDR/BH-Korrektur mitigiert

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_AXIOM-001_PROXY_PLAN_20251230_013903.md

## [2025-12-30 01:47:03] AXIOM-001 - EXECUTOR (ki6)

### Summary
- ADR_AXIOM_FIRST_FRAMEWORK.md erstellt mit vollstaendiger Dokumentation
- kenobase/core/axioms.py implementiert mit 7 Axiomen (A1-A7) und 21 Predictions
- 100% Test-Coverage fuer axioms.py (72 statements, 0 missing)
- 28 Unit-Tests alle bestanden in 0.47s
- CLI-Script validate_axiom_predictions.py funktioniert mit --list, --all, --output
- Train/Test Split konfiguriert (pre-2024 Train, 2024+ Test)
- EuroJackpot als Negativ-Kontrollkanal implementiert (A2, A4, A6 excluded)
- DATAREQ-001 fuer A6 (Regionale Verteilung) dokumentiert

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_AXIOM-001_EXECUTOR_20251230_014103.md




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
- AI_COLLABORATION/HANDOFFS/ki5_AXIOM-001_ARCHITECT_20251230_012102.md (NEU)AI_COLLABORATION/HANDOFFS/ki5_AXIOM-001_ARCHITECT_20251230_012803.md (NEU)kenobase/core/axioms.py (TO CREATE)tests/unit/test_axioms.py (TO CREATE)scripts/validate_axiom_predictions.py (TO CREATE)AI_COLLABORATION/HANDOFFS/ki5_AXIOM-001_ARCHITECT_20251230_012803.md (NEU)kenobase/core/axioms.py (TO CREATE)tests/unit/test_axioms.py (TO CREATE)scripts/validate_axiom_predictions.py (TO CREATE)AI_COLLABORATION/ARCHITECTURE/ADR_AXIOM_FIRST_FRAMEWORK.md (NEU)kenobase/core/axioms.py (NEU)kenobase/core/__init__.py (MODIFIED)tests/unit/test_axioms.py (NEU)scripts/validate_axiom_predictions.py (NEU)results/axiom_validation.json (NEU)

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
- ADR_AXIOM_FIRST_FRAMEWORK.md erstellt mit vollstaendiger Dokumentation
- kenobase/core/axioms.py implementiert mit 7 Axiomen (A1-A7) und 21 Predictions
- 100% Test-Coverage fuer axioms.py (72 statements, 0 missing)
- 28 Unit-Tests alle bestanden in 0.47s
- CLI-Script validate_axiom_predictions.py funktioniert mit --list, --all, --output
- Train/Test Split konfiguriert (pre-2024 Train, 2024+ Test)
- EuroJackpot als Negativ-Kontrollkanal implementiert (A2, A4, A6 excluded)
- DATAREQ-001 fuer A6 (Regionale Verteilung) dokumentiert

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_AXIOM-001_EXECUTOR_20251230_014103.md

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
task: AXIOM-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_AXIOM-001_PROXY_IMPL_20251230_014703.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
