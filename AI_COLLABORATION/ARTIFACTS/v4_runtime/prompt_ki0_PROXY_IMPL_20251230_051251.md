AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Inverse/periodische Kopplung (Cross-Spectrum, Phase)
TASK-ID: COUPLE-002
PRIORITY: MITTEL
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 04:39:00] COUPLE-002 - PROXY_PLAN (ki0)

### Summary
- Plan ist per-market/pro Darstellung/Frequenzband definiert, deckt Alignment, CPSD/Coherence/Phase-Lags, Surrogates (Block/Phase) und BH-FDR ab.
- Tests enthalten Synth-Sinus mit bekanntem Lag, Nullkontrolle (EuroJackpot) und CLI-Schema-Check; Acceptance-Kriterien messbar formuliert.
- Keine Red Flags gefunden; Empfehlung: im Executor Orchestrator/Config-Anbindung (Runner/Results) explizit einplanen.
- SYSTEM_STATUS.json fehlt; KI0-Profil nicht auffindbar -> Integrationshinweise als UNVERIFIED markieren; CURRENT_STATUS nicht angepasst (Plan-Review).
- Ergebnis-Handoff geschrieben: `AI_COLLABORATION/HANDOFFS/ki0_COUPLE-002_PROXY_PLAN_20251230_043700.md`.

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_COUPLE-002_PROXY_PLAN_20251230_043700.md

## [2025-12-30 05:12:51] COUPLE-002 - EXECUTOR (ki6)

### Summary
- Created cross_spectrum_coupling.py with CPSD/coherence/phase-lag analysis via scipy.signal
- Implemented phase-randomized and block-permutation surrogates for null distribution
- Added BH/FDR correction per band across coherence and PLV p-values
- CLI supports KENO/Lotto/EuroJackpot inputs with configurable representations and bands
- 23 unit tests all pass covering synth-sinus detection, null-control, schema checks
- EuroJackpot treated as negative control (should not show spurious coupling)
- Exported new symbols in analysis/__init__.py for module integration

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_COUPLE-002_EXECUTOR_20251230_050551.md



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
- AI_COLLABORATION/HANDOFFS/ki5_COUPLE-002_ARCHITECT_20251230_043400.mdkenobase/analysis/cross_spectrum_coupling.pykenobase/analysis/__init__.pyscripts/analyze_cross_spectrum_coupling.pytests/unit/test_cross_spectrum_coupling.py

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
- Created cross_spectrum_coupling.py with CPSD/coherence/phase-lag analysis via scipy.signal
- Implemented phase-randomized and block-permutation surrogates for null distribution
- Added BH/FDR correction per band across coherence and PLV p-values
- CLI supports KENO/Lotto/EuroJackpot inputs with configurable representations and bands
- 23 unit tests all pass covering synth-sinus detection, null-control, schema checks
- EuroJackpot treated as negative control (should not show spurious coupling)
- Exported new symbols in analysis/__init__.py for module integration

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki6_COUPLE-002_EXECUTOR_20251230_050551.md

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
task: COUPLE-002
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_COUPLE-002_PROXY_IMPL_20251230_051251.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
