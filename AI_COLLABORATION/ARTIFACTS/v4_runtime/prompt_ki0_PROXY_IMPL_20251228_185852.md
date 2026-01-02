AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Anti-Birthday Strategie Dokumentation
TASK-ID: DOC-001
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 18:51:52] DOC-001 - PROXY_FINAL (ki0)

### Summary
- Data claims (r=0.3921, Winner-Ratio 1.3x, 6.982 Ziehungen) in `docs/strategies/anti_birthday.md:9-33` with source ref at `docs/strategies/anti_birthday.md:343-345` lack required repro command/artifact path/filter/N â†’ reproducibility rule not met.
- Mandatory context check failed: `AI_COLLABORATION/SYSTEM_STATUS.json` not found, so Rule 1 only partially verified; CURRENT_STATUS remains UNVERIFIED.
- Proxy handoff recorded at `AI_COLLABORATION/HANDOFFS/ki0_DOC-001_PROXY_FINAL_20251228_184951.md` with status REJECTED.
- No additional tests executed (per efficiency rule; validator already ran `python scripts/backtest_anti_birthday.py --help`).

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DOC-001_PROXY_FINAL_20251228_184951.md


## [2025-12-28 18:58:52] DOC-001 - EXECUTOR (ki2)

### Summary
- Repro-Kommandos fuer Kernmetriken dokumentiert (Synthesizer) inkl. Datenquellen/Filter/N=769.
- Backtest-Abschnitt mit aktuellen Kennzahlen (1.0398x, 1.7217 Treffer, 18.8% vorteilhaft) und Repro-Pfad aktualisiert.
- Synthesizer- und Backtest-Skripte ausgefuehrt; Artefakte in results/* und AI_COLLABORATION/ARTIFACTS/* aktualisiert.
- SYSTEM_STATUS.json fehlt weiterhin, Rule 1 bleibt UNVERIFIED.

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_DOC-001_EXECUTOR_20251228_185152.md



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
- docs/strategies/anti_birthday.mdresults/anti_birthday_backtest.jsonresults/combined_keno_data.csvresults/synthesizer_analysis.jsonAI_COLLABORATION/ARTIFACTS/anti_birthday_backtest_exec_20251228.logAI_COLLABORATION/ARTIFACTS/synthesizer_analysis_exec_20251228.log

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
- Repro-Kommandos fuer Kernmetriken dokumentiert (Synthesizer) inkl. Datenquellen/Filter/N=769.
- Backtest-Abschnitt mit aktuellen Kennzahlen (1.0398x, 1.7217 Treffer, 18.8% vorteilhaft) und Repro-Pfad aktualisiert.
- Synthesizer- und Backtest-Skripte ausgefuehrt; Artefakte in results/* und AI_COLLABORATION/ARTIFACTS/* aktualisiert.
- SYSTEM_STATUS.json fehlt weiterhin, Rule 1 bleibt UNVERIFIED.

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_DOC-001_EXECUTOR_20251228_185152.md

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
task: DOC-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_DOC-001_PROXY_IMPL_20251228_185852.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
