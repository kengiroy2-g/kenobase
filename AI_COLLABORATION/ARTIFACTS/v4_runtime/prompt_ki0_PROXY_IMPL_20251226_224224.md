AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P4-04: Output-Formate implementieren
TASK-ID: phase4_task04_output_formats
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-26 22:36:24] phase4_task04_output_formats - PROXY_PLAN (ki0)

### Summary
- Plan ist mechanisch vollstaendig - alle Schritte klar definiert
- Bestehende Implementierung in scripts/analyze.py:178-272 verifiziert (JSON/CSV/HTML)
- CSV-Limitierung korrekt identifiziert: nur frequency_results, keine Physics/Patterns
- Neues Modul kenobase/pipeline/output_formats.py ist sinnvoll (Separation of Concerns)
- Erweiterungen (Markdown, YAML) sind gut gewaehlt fuer verschiedene Use-Cases
- Integration in bestehende CLI via --format Option bereits vorhanden
- WORKING_SET_REQUEST ist vollstaendig fuer Executor-Arbeit
- Keine Red Flags (keine globalen Thresholds, keine Orchestrator-Integration noetig)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase4_task04_output_formats_PROXY_PLAN_20251226_223424.md

## [2025-12-26 22:42:24] phase4_task04_output_formats - EXECUTOR (ki2)

### Summary
- Neues Modul kenobase/pipeline/output_formats.py mit 5 Formaten implementiert
- OutputFormat Enum (JSON, CSV, HTML, MARKDOWN, YAML) erstellt
- OutputFormatter Klasse mit Registry-Pattern fuer Erweiterbarkeit
- CSV erweitert mit Physics-Section und Pair-Frequencies
- HTML mit Grid-Layout und Avalanche-State-Styling
- Markdown GFM-kompatibel mit Tables und Warnings
- CLI auf 5 Formate erweitert (--format json|csv|html|markdown|yaml)
- 40 Unit-Tests alle bestanden

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_phase4_task04_output_formats_EXECUTOR_20251226_223624.md



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
- kenobase/pipeline/output_formats.py (NEW - 450 lines)
- kenobase/pipeline/__init__.py (MODIFIED - exports added)
- scripts/analyze.py (MODIFIED - CLI extended, legacy code removed)
- tests/unit/test_output_formats.py (NEW - 40 tests)

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
- Neues Modul kenobase/pipeline/output_formats.py mit 5 Formaten implementiert
- OutputFormat Enum (JSON, CSV, HTML, MARKDOWN, YAML) erstellt
- OutputFormatter Klasse mit Registry-Pattern fuer Erweiterbarkeit
- CSV erweitert mit Physics-Section und Pair-Frequencies
- HTML mit Grid-Layout und Avalanche-State-Styling
- Markdown GFM-kompatibel mit Tables und Warnings
- CLI auf 5 Formate erweitert (--format json|csv|html|markdown|yaml)
- 40 Unit-Tests alle bestanden

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_phase4_task04_output_formats_EXECUTOR_20251226_223624.md

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
task: phase4_task04_output_formats
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_phase4_task04_output_formats_PROXY_IMPL_20251226_224224.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
