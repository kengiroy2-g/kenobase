AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: V1 vs V2 PARALLEL: Per Wochentag Vergleich
TASK-ID: TASK_039b
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-31 01:28:35] TASK_039b - PROXY_PLAN (ki0)

### Summary
- Plan ist vollstaendig mit klarer Implementierungs-Checkliste (A1-D3)
- V1/V2 Ticket-Definitionen verifiziert in backtest_birthday_cooldown.py lines 37-52
- Granularitaet korrekt: per-weekday (7 Kategorien)
- Nullmodell spezifiziert (weekday-preserving shuffle, Permutationstest)
- Multiple-Testing-Korrektur (BH) erwaehnt - wichtig bei 7 Wochentagen
- Output-Schema klar definiert mit Acceptance Criteria
- WORKING_SET ist ausreichend fuer Implementation
- Keine Red Flags (globale Thresholds, fehlende Integration)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_039b_PROXY_PLAN_20251231_012635.md

## [2025-12-31 01:34:35] TASK_039b - EXECUTOR (ki2)

### Summary
- Created scripts/compare_v1_v2_weekday.py for V1 vs V2 weekday comparison
- V1 Tickets from backtest_birthday_cooldown.py lines 37-43, V2 from lines 46-52
- Compares ROI per weekday (7 Kategorien) for 5 Keno types (Typ 6-10)
- Nullmodell: weekday-preserving shuffle permutation test (1000 permutations)
- Benjamini-Hochberg correction applied across 5 types
- Result: V2 trend better (+8.53% avg), but NOT significant (0/5 BH-corrected)
- Output: results/v1_v2_weekday_comparison.json (887 lines, valid JSON)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_039b_EXECUTOR_20251231_012835.md



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
- scripts/analyze_weekday_roi.py
- scripts/backtest_birthday_cooldown.py
- results/weekday_roi_analysis.json
- kenobase/core/keno_quotes.py
- scripts/compare_v1_v2_weekday.py
- results/v1_v2_weekday_comparison.json

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
- Created scripts/compare_v1_v2_weekday.py for V1 vs V2 weekday comparison
- V1 Tickets from backtest_birthday_cooldown.py lines 37-43, V2 from lines 46-52
- Compares ROI per weekday (7 Kategorien) for 5 Keno types (Typ 6-10)
- Nullmodell: weekday-preserving shuffle permutation test (1000 permutations)
- Benjamini-Hochberg correction applied across 5 types
- Result: V2 trend better (+8.53% avg), but NOT significant (0/5 BH-corrected)
- Output: results/v1_v2_weekday_comparison.json (887 lines, valid JSON)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_039b_EXECUTOR_20251231_012835.md

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
task: TASK_039b
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_039b_PROXY_IMPL_20251231_013435.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
