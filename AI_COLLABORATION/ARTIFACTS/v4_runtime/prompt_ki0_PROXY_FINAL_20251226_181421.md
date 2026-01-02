AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P1-03: Data Loader refactoren
TASK-ID: phase1_task03_data_loader
PRIORITY: P0
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-26 18:12:20] phase1_task03_data_loader - PROXY_IMPL (ki0)

### Summary
- DataLoader module with auto-format detection fully implemented
- DrawResult Pydantic model validates numbers (positive, sorted) and bonus (non-negative)
- Four parsers: KENO (20 Zahlen), EuroJackpot (5+2), Lotto-Alt (6), Lotto-Neu (6+ZZ)
- Format detection based on header inspection (Keno_Z1, 5 aus 50, z1-z6, Gewinnzahlen)
- LegacyConfig compatibility: csv_delimiter, csv_date_format match DataLoader defaults
- DataFrame conversion with sorted date index implemented
- 33 unit tests all passing (0.49s), real data integration tests pass
- Exports in __init__.py korrekt: DataLoader, DrawResult, GameType, FormatInfo

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase1_task03_data_loader_PROXY_IMPL_20251226_181020.md


## [2025-12-26 18:14:21] phase1_task03_data_loader - VALIDATOR (ki3)

### Summary
- All 51 tests passing (33 DataLoader + 18 Config) in 0.51s
- Syntax valid (py_compile pass)
- Imports work correctly (DataLoader, DrawResult, GameType, FormatInfo)
- Acceptance Criteria #1 (CSV Support): PASS - all 4 formats load correctly
- Acceptance Criteria #2 (Auto Date Detection): PASS - %d.%m.%Y format detected
- Acceptance Criteria #3 (Schema Validation): PASS - Pydantic rejects negative numbers
- Acceptance Criteria #4 (Edge Cases): PASS - FileNotFoundError, forced game_type
- Real data integration: 2237 KENO, 4 CSV files all verified

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_phase1_task03_data_loader_VALIDATOR_20251226_181221.md



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
- AI_COLLABORATION/HANDOFFS/ki1_phase1_task03_data_loader_ARCHITECT_20251226_174920.mdKeno_GPTs/Daten/Lotto_Archiv_ab-1955.csv (erste 5 Zeilen)Keno_GPTs/Daten/lotto_Stats_ab-2018.csv (erste 5 Zeilen)kenobase/core/config.py (bereits gelesen)AI_COLLABORATION/HANDOFFS/ki1_phase1_task03_data_loader_ARCHITECT_20251226_175520.mdkenobase/core/data_loader.py (NEW)kenobase/core/__init__.py (MODIFIED)tests/unit/test_data_loader.py (NEW)tests/fixtures/keno_sample.csv (NEW)tests/fixtures/eurojackpot_sample.csv (NEW)tests/fixtures/lotto_old_sample.csv (NEW)tests/fixtures/lotto_new_sample.csv (NEW)

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
ROLLE: PROXY (User-Stellvertreter - Finale Freigabe)
AUFGABE: Finale Freigabe mit Projekt-Perspektive.

PFLICHTLEKTUERE (kurz):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Falls Zweifel an Integration

EFFIZIENZ-REGELN:
- Nutze VALIDATOR OUTPUT + dein Wissen aus vorherigen Proxy-Phasen
- Keine weiteren Tests, nur finale Entscheidung

VALIDATOR OUTPUT (kurz):
- All 51 tests passing (33 DataLoader + 18 Config) in 0.51s
- Syntax valid (py_compile pass)
- Imports work correctly (DataLoader, DrawResult, GameType, FormatInfo)
- Acceptance Criteria #1 (CSV Support): PASS - all 4 formats load correctly
- Acceptance Criteria #2 (Auto Date Detection): PASS - %d.%m.%Y format detected
- Acceptance Criteria #3 (Schema Validation): PASS - Pydantic rejects negative numbers
- Acceptance Criteria #4 (Edge Cases): PASS - FileNotFoundError, forced game_type
- Real data integration: 2237 KENO, 4 CSV files all verified

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_phase1_task03_data_loader_VALIDATOR_20251226_181221.md

FINALE PRUEFUNG:
1. Hat Validator alle kritischen Aspekte geprueft?
2. Wuerde der USER diese Aenderung akzeptieren?
3. Gibt es offene Architektur-Fragen die der User entscheiden sollte?

ESKALATION an User wenn:
- Architektur-Entscheidung noetig die nicht in ADRs dokumentiert ist
- Unsicherheit ueber globale vs spezifische Werte
- Potenzielle Breaking Changes

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: COMPLETE
task: phase1_task03_data_loader
role: PROXY
phase: PROXY_FINAL
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

# Proxy Final Review

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki0_phase1_task03_data_loader_PROXY_FINAL_20251226_181421.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
