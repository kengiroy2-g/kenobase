AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Summen-Signatur
TASK-ID: TRANS-001
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 04:02:20] TRANS-001 - PROXY_IMPL (ki0)

### Summary
- Disabled Summen-Signatur path crashes because `summen_signatur_buckets`/`summen_signatur_path` stay undefined when the feature flag is off; any run with `analysis.summen_signatur.enabled=False` raises UnboundLocalError (kenobase/pipeline/runner.py:278-337).
- Ran sanity checks: py_compile on module/CLI/runner and targeted pytest all pass.
- KI profile `AI_COLLABORATION/KI_PROFILES/ki0_proxy.md` missing; unable to cross-check known bugs; CURRENT_STATUS still unchanged.
- Filed proxy handoff with REJECTED status at `AI_COLLABORATION/HANDOFFS/ki0_TRANS-001_PROXY_IMPL_20251230_035820.md`.

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TRANS-001_PROXY_IMPL_20251230_035820.md

## [2025-12-30 04:09:20] TRANS-001 - EXECUTOR (ki2)

### Summary
- Initialized Summen-Signatur outputs to None before the feature toggle to keep disabled runs from raising UnboundLocalError (kenobase/pipeline/runner.py:277).
- Added regression coverage to ensure PipelineRunner returns None Summen-Signatur outputs when the flag is disabled (tests/unit/test_summen_signatur.py:77).
- Checks: python -m py_compile kenobase/analysis/summen_signatur.py scripts/compute_summen_signatur.py kenobase/pipeline/runner.py; python -m pytest tests/unit/test_summen_signatur.py -q (PASS).

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TRANS-001_EXECUTOR_20251230_040220.md



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
- kenobase/analysis/__init__.py
- kenobase/core/config.py
- kenobase/core/__init__.py
- kenobase/pipeline/runner.py
- scripts/analyze.py
- scripts/compute_summen_signatur.py
- tests/unit/test_summen_signatur.py
- AI_COLLABORATION/HANDOFFS/ki2_TRANS-001_EXECUTOR_20251230_040220.md

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
- Initialized Summen-Signatur outputs to None before the feature toggle to keep disabled runs from raising UnboundLocalError (kenobase/pipeline/runner.py:277).
- Added regression coverage to ensure PipelineRunner returns None Summen-Signatur outputs when the flag is disabled (tests/unit/test_summen_signatur.py:77).
- Checks: python -m py_compile kenobase/analysis/summen_signatur.py scripts/compute_summen_signatur.py kenobase/pipeline/runner.py; python -m pytest tests/unit/test_summen_signatur.py -q (PASS).

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TRANS-001_EXECUTOR_20251230_040220.md

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
task: TRANS-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TRANS-001_PROXY_IMPL_20251230_041030.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
