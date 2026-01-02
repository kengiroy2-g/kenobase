AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Gewinnverteilungs-Optimierung analysieren
TASK-ID: HYP-001
PRIORITY: HIGH
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 14:27:07] HYP-001 - ARCHITECT (ki1)

### Summary
- HYP-001 Gewinnverteilungs-Optimierung analysieren
- Datenbasis Keno_GQ_*.csv (27.685 Zeilen) + Restbetrag CSV (365 Zeilen 2023)
- 3 Analyse-Module geplant distribution, near_miss, reinforcement
- Neues Script scripts/analyze_hyp001.py
- Output AI_COLLABORATION/ARTIFACTS/HYP-001_report.json
- Acceptance Criteria 4 Metriken definiert
- Geschaetzter Aufwand 4-5 Stunden
- Keine externen Abhaengigkeiten

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_HYP-001_ARCHITECT_20251227_142307.md

## [2025-12-27 14:29:08] HYP-001 - PROXY_PLAN (ki0)

### Summary
- Plan ist vollstaendig mit 5 Phasen (A-E) und 25 Checkpoints
- Datenbasis verifiziert (Keno_GQ_*.csv + Restbetrag CSV)
- 3 neue Module distribution, near_miss, reinforcement sind architekturkonform
- Acceptance Criteria messbar (4 Metriken mit Schwellwerten)
- Integration in kenobase/analysis/__init__.py korrekt geplant
- Working Set Request vollstaendig (4 Dateien)
- Keine Known Bugs (BUG-001/003) betroffen
- Risiken identifiziert mit Mitigationen

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP-001_PROXY_PLAN_20251227_142707.md

## [2025-12-27 14:35:08] HYP-001 - EXECUTOR (ki2)

### Summary
- 3 neue Analyse-Module erstellt (distribution, near_miss, reinforcement)
- Script scripts/analyze_hyp001.py implementiert und getestet
- Report generiert mit 4/4 Acceptance Criteria passed
- 8 signifikante Near-Miss Anomalien gefunden (Keno-Typen 3-10)
- 17 Verteilungs-Anomalien identifiziert (hohe CV/Schiefe)
- Regularity Score 0.458 (unter Schwelle 0.5)
- Hypothese HYP-001 supported (alle Kriterien erfuellt)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HYP-001_EXECUTOR_20251227_142908.md



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
- Keno_GPTs/Keno_Ziehung2023_+_Restbetrag_v2.CSV
- kenobase/analysis/__init__.py
- kenobase/core/data_loader.py
- kenobase/analysis/distribution.py
- kenobase/analysis/near_miss.py
- kenobase/analysis/reinforcement.py
- scripts/analyze_hyp001.py
- AI_COLLABORATION/ARTIFACTS/HYP-001_report.json

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
- 3 neue Analyse-Module erstellt (distribution, near_miss, reinforcement)
- Script scripts/analyze_hyp001.py implementiert und getestet
- Report generiert mit 4/4 Acceptance Criteria passed
- 8 signifikante Near-Miss Anomalien gefunden (Keno-Typen 3-10)
- 17 Verteilungs-Anomalien identifiziert (hohe CV/Schiefe)
- Regularity Score 0.458 (unter Schwelle 0.5)
- Hypothese HYP-001 supported (alle Kriterien erfuellt)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_HYP-001_EXECUTOR_20251227_142908.md

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
task: HYP-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_HYP-001_PROXY_IMPL_20251227_143508.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
