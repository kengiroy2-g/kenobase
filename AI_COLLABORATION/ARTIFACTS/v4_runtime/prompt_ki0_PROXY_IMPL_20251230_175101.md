AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Test HYP_006: Ticket-Alterung
TASK-ID: TASK_016
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 17:46:01] TASK_016 - ARCHITECT (ki1)

### Summary
- HYP_006 Ticket-Alterung bereits implementiert: scripts/analyze_ticket_lifecycle.py
- Walk-Forward Simulation vorhanden (365d Train, 90d Test, 90d Step)
- Aging-Analyse mit 28-Tage-Bloecken implementiert
- Jahres-Transfer-Matrix verfuegbar (Train Jahr X -> Test Jahr Y)
- Ergebnis-JSON unvollstaendig (truncated bei Line 750) - muss neu generiert werden
- Drei Strategien getestet: frequency, frequency_high, v2_style
- EMPFEHLUNG: Script ausfuehren + Ergebnisse in Hypothesen-Katalog dokumentieren

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_016_ARCHITECT_20251230_174401.md

## [2025-12-30 17:48:01] TASK_016 - PROXY_PLAN (ki0)

### Summary
- HYP_006 Implementation vollstaendig: scripts/analyze_ticket_lifecycle.py (530 LOC)
- Ergebnis-JSON existiert und ist NICHT truncated (walk_forward mit 12 Iterationen)
- Walk-Forward korrekt implementiert (365d Train, 90d Test, 90d Step)
- 3 Strategien getestet: frequency, frequency_high, v2_style
- Aging-Analyse mit 28-Tage-Bloecken + Trend-Berechnung vorhanden
- ROI durchgaengig negativ, ein Outlier (+1037% durch einzelnen 8-Treffer)
- EMPFEHLUNG: Executor soll nur Hypothesen-Katalog dokumentieren
- Kein Code-Aenderung noetig

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_016_PROXY_PLAN_20251230_174601.md

## [2025-12-30 17:51:01] TASK_016 - EXECUTOR (ki2)

### Summary
- JSON-Serialisierungs-Bug in Script gefixt (int32 Keys -> int())
- Script erfolgreich ausgefuehrt (12 Walk-Forward Iterationen)
- HYP_006 als NICHT SIGNIFIKANT dokumentiert
- Walk-Forward Avg ROI: frequency +30.9%, freq_high -59.6%, v2_style -51.8%
- Aging-Trends negativ aber Varianz hoch (Outlier +1037%)
- Hypothesen-Katalog aktualisiert mit vollstaendiger Analyse
- Changelog ergaenzt

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_016_EXECUTOR_20251230_174801.md



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
- scripts/analyze_ticket_lifecycle.py
- AI_COLLABORATION/KNOWLEDGE_BASE/HYPOTHESES_CATALOG.md
- results/ticket_lifecycle_analysis.json

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
- JSON-Serialisierungs-Bug in Script gefixt (int32 Keys -> int())
- Script erfolgreich ausgefuehrt (12 Walk-Forward Iterationen)
- HYP_006 als NICHT SIGNIFIKANT dokumentiert
- Walk-Forward Avg ROI: frequency +30.9%, freq_high -59.6%, v2_style -51.8%
- Aging-Trends negativ aber Varianz hoch (Outlier +1037%)
- Hypothesen-Katalog aktualisiert mit vollstaendiger Analyse
- Changelog ergaenzt

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_016_EXECUTOR_20251230_174801.md

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
task: TASK_016
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_016_PROXY_IMPL_20251230_175101.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
