AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Daten laden und validieren
TASK-ID: TASK_001
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 13:47:48] TASK_001 - ARCHITECT (ki1)

### Summary
- DataLoader existiert in kenobase/core/data_loader.py (1082 Zeilen)
- Unterstuetzt KENO, EuroJackpot, Lotto (alt/neu/bereinigt/archiv), GK1Summary, GK1Hit
- Auto-Erkennung via Header-Patterns; Pydantic-Validierung via DrawResult/GK1-Models
- Unit-Tests vorhanden in tests/unit/test_data_loader.py (491 Zeilen, ~30 Tests)
- Daten verfuegbar: 17 CSV-Dateien unter data/raw/** (KENO_ab_2022_bereinigt.csv primaer)
- Config definiert Pfade in config/default.yaml (legacy.keno_file, etc.)
- Validierung: Schema-Check + Feld-Validatoren (positive Zahlen, Bonus non-negativ)
- EXECUTOR soll: Daten laden, Validierung pruefen, N+Format dokumentieren

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_001_ARCHITECT_20251230_134548.md

## [2025-12-30 13:49:49] TASK_001 - PROXY_PLAN (ki0)

### Summary (fallback)
- Handoff erstellt: `AI_COLLABORATION/HANDOFFS/ki0_TASK_001_PROXY_PLAN_20251230_134749.md`    **Status: APPROVED**    Plan ist vollstaendig und kann vom EXECUTOR ausgefuehrt werden. Keine Red Flags oder konzeptionellen Probleme erkannt.

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_001_PROXY_PLAN_20251230_134749.md

## [2025-12-30 13:52:49] TASK_001 - EXECUTOR (ki2)

### Summary
- DataLoader validated with 4 datasets: KENO (1457), EuroJackpot (404), Lotto (416), KENO historical (2237)
- All 39 unit tests in tests/unit/test_data_loader.py PASSED
- Primary KENO file: data/raw/keno/KENO_ab_2022_bereinigt.csv (2022-01-03 to 2025-12-29)
- Pydantic validation (DrawResult/GK1 models) working correctly - 0 validation errors
- Auto-format detection confirmed for KENO, EuroJackpot, Lotto formats
- Validation artifact saved to AI_COLLABORATION/ARTIFACTS/TASK_001_data_validation.json

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_001_EXECUTOR_20251230_134949.md



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
- AI_COLLABORATION/ARTIFACTS/TASK_001_data_validation.json

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
- DataLoader validated with 4 datasets: KENO (1457), EuroJackpot (404), Lotto (416), KENO historical (2237)
- All 39 unit tests in tests/unit/test_data_loader.py PASSED
- Primary KENO file: data/raw/keno/KENO_ab_2022_bereinigt.csv (2022-01-03 to 2025-12-29)
- Pydantic validation (DrawResult/GK1 models) working correctly - 0 validation errors
- Auto-format detection confirmed for KENO, EuroJackpot, Lotto formats
- Validation artifact saved to AI_COLLABORATION/ARTIFACTS/TASK_001_data_validation.json

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_001_EXECUTOR_20251230_134949.md

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
task: TASK_001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_001_PROXY_IMPL_20251230_135249.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
