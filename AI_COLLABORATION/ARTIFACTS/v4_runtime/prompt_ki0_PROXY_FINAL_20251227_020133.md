AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: DATA-03: Lotto-Daten migrieren
TASK-ID: data_migration_lotto
PRIORITY: P2
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 01:59:32] data_migration_lotto - PROXY_IMPL (ki0)

### Summary
- Implementation mechanically complete: _parse_lotto_archiv() added at data_loader.py:565-630
- Format detection in _parse_lotto() properly routes archiv format via first-line check
- Test fixture lotto_archiv_sample.csv has correct ISO8601+dash format (3 rows)
- All 38 tests pass including 5 new archiv tests (TestLottoArchivParser class)
- 3 files migrated to data/raw/lotto/ (141KB + 200KB + 122KB)
- Real data loads correctly: 4764 archiv, 4886 old, 638 new draws
- ~124 archiv rows have 7 numbers - source data issue, parser correctly skips them
- No architecture conflicts - follows existing _parse_lotto_* pattern

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_data_migration_lotto_PROXY_IMPL_20251227_015732.md

## [2025-12-27 02:01:33] data_migration_lotto - VALIDATOR (ki3)

### Summary
- All 38 unit tests pass (5 new tests for archiv format)
- _parse_lotto_archiv() at data_loader.py:565-630 correctly parses ISO8601+dash format
- Format detection at data_loader.py:414-417 routes archiv format correctly
- Test fixture lotto_archiv_sample.csv has 3 valid rows with expected format
- 3 files migrated to data/raw/lotto/ (141KB + 200KB + 122KB)
- Archiv data: 4764 rows loaded, 122 rows skipped (7 numbers = source data issue)
- Metadata correctly marks archiv format: metadata["format"]="archiv
- No regressions in existing parsers (KENO, EuroJackpot, Lotto old/new)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_data_migration_lotto_VALIDATOR_20251227_015933.md



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
- kenobase/core/data_loader.py
- tests/unit/test_data_loader.py
- tests/fixtures/lotto_archiv_sample.csv
- data/raw/lotto/Lotto_Archiv_ab-1955.csv
- data/raw/lotto/lotto_Stats_ab-2018.csv
- data/raw/lotto/Lotto_archiv_bereinigt.csv

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
- All 38 unit tests pass (5 new tests for archiv format)
- _parse_lotto_archiv() at data_loader.py:565-630 correctly parses ISO8601+dash format
- Format detection at data_loader.py:414-417 routes archiv format correctly
- Test fixture lotto_archiv_sample.csv has 3 valid rows with expected format
- 3 files migrated to data/raw/lotto/ (141KB + 200KB + 122KB)
- Archiv data: 4764 rows loaded, 122 rows skipped (7 numbers = source data issue)
- Metadata correctly marks archiv format: metadata["format"]="archiv
- No regressions in existing parsers (KENO, EuroJackpot, Lotto old/new)

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_data_migration_lotto_VALIDATOR_20251227_015933.md

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
task: data_migration_lotto
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_data_migration_lotto_PROXY_FINAL_20251227_020133.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
