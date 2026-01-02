AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: EuroJackpot separat + als externer Negativ-Kontrollkanal
TASK-ID: EJ-001
PRIORITY: P1
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 05:46:52] EJ-001 - PROXY_PLAN (ki0)

### Summary
- EuroJackpot als Negativ-Kontrollkanal korrekt konzipiert - EJ ist EXTERN (international), nicht Teil des DE-Oekosystems
- Bestehende Infrastruktur nutzbar: cross_lottery_coupling.py (GameDraws, conditional_lifts, bh_fdr)
- EJ-Daten vorhanden (data/raw/eurojackpot/EJ_ab_2022_bereinigt.csv)
- Implementierungsplan mit 6 Schritten ist mechanisch vollstaendig und messbar
- Falsifizierungs-Logik korrekt: EJ darf KEINE signifikanten Korrelationen zu KENO/LOTTO zeigen
- Acceptance Criteria (Train/Test-Split, q>0.05 fuer EJ-Trigger) sind testbar
- Kein BUG-001 (globale Thresholds) Risiko - per-game Semantik korrekt
- cross_lottery_coupling.py bereits EJ-kompatibel (Pool 1-50 Hauptzahlen, 1-12 Eurozahlen)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_EJ-001_PROXY_PLAN_20251230_054452.md

## [2025-12-30 05:52:52] EJ-001 - EXECUTOR (ki6)

### Summary
- Created scripts/validate_ej_negative_control.py implementing EJ as external negative control
- Implemented 6-step plan: Train/Test split (80/20), conditional lifts, pair overlap, FDR correction
- Created tests/unit/test_ej_negative_control.py with 15 unit tests (all passing)
- Executed validation on real data: KENO=1457, LOTTO=416, AW=207, EJ=404 draws
- DE Internal: 0 significant conditional lifts after FDR correction
- EJ External: 0 significant conditional lifts after FDR correction
- Unexpected finding: AW vs EJ pair overlap is significant (p=0.017)
- Verdict: WEAKENED - EJ shows unexpected correlation with DE (AW) via pair overlap

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_EJ-001_EXECUTOR_20251230_054652.md



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
- scripts/validate_ej_negative_control.py
- tests/unit/test_ej_negative_control.py
- results/ej_negative_control.json

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
- Created scripts/validate_ej_negative_control.py implementing EJ as external negative control
- Implemented 6-step plan: Train/Test split (80/20), conditional lifts, pair overlap, FDR correction
- Created tests/unit/test_ej_negative_control.py with 15 unit tests (all passing)
- Executed validation on real data: KENO=1457, LOTTO=416, AW=207, EJ=404 draws
- DE Internal: 0 significant conditional lifts after FDR correction
- EJ External: 0 significant conditional lifts after FDR correction
- Unexpected finding: AW vs EJ pair overlap is significant (p=0.017)
- Verdict: WEAKENED - EJ shows unexpected correlation with DE (AW) via pair overlap

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_EJ-001_EXECUTOR_20251230_054652.md

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
task: EJ-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_EJ-001_PROXY_IMPL_20251230_055252.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
