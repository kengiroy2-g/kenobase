AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Regionale Daten Erweiterung
TASK-ID: DIST-004
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 22:35:10] DIST-004 - PROXY_PLAN (ki0)

### Summary (fallback)
- ---  **status: APPROVED**  **task: DIST-004**  **role: PROXY**  **phase: PROXY_PLAN**  **reviewed_handoff: ki1_DIST-004_ARCHITECT_20251228_223010.md**    ---    # Proxy Review Summary    Plan wurde als **APPROVED** bewertet. Hauptgruende:    1. **Fokussierter Scope:** Nur Phase B ...

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DIST-004_PROXY_PLAN_20251228_223310.md

## [2025-12-28 22:41:10] DIST-004 - EXECUTOR (ki2)

### Summary
- Added BirthdayCorrelationResult dataclass for birthday-winners correlation
- Added calculate_birthday_score() function (fraction of 1-31 numbers)
- Added correlate_birthday_with_winners() with rolling-window stability test
- Created scripts/analyze_popularity_proxy.py (296 LOC CLI tool)
- Added 10 new tests (5 for birthday_score, 5 for correlation)
- All 31 tests pass in test_popularity_correlation.py
- Output: results/popularity_proxy.json (NO_DATA - GQ files not available)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_DIST-004_EXECUTOR_20251228_223510.md

## [2025-12-28 22:44:10] DIST-004 - PROXY_IMPL (ki0)

### Summary
- All 31 tests pass including 10 new birthday-correlation tests
- Syntax check OK for popularity_correlation.py and analyze_popularity_proxy.py
- New functions properly exported in __all__ list
- BirthdayCorrelationResult dataclass correctly implements per-draw granularity
- CLI script correctly handles NO_DATA case when GQ files unavailable
- Rolling-window stability test implements Law A (stability threshold check)
- No integration issues - module is self-contained analysis helper
- Acceptance criteria evaluation logic is correct (r > 0.3, p < 0.05)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DIST-004_PROXY_IMPL_20251228_224110.md



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
- kenobase/analysis/popularity_correlation.py
- scripts/analyze_popularity_proxy.py
- tests/unit/test_popularity_correlation.py
- results/popularity_proxy.json

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
ROLLE: VALIDATOR
AUFGABE: Validiere die Implementation.

EFFIZIENZ-REGELN:
- Tests nur zielgerichtet (klein starten). Keine riesigen Logs in die Antwort; speichere nach AI_COLLABORATION/ARTIFACTS/ und verlinke.
- Vermeide Repo-weite Scans; nutze WORKING SET + gezielte Reads.

VORHERIGER OUTPUT (kurz):
- All 31 tests pass including 10 new birthday-correlation tests
- Syntax check OK for popularity_correlation.py and analyze_popularity_proxy.py
- New functions properly exported in __all__ list
- BirthdayCorrelationResult dataclass correctly implements per-draw granularity
- CLI script correctly handles NO_DATA case when GQ files unavailable
- Rolling-window stability test implements Law A (stability threshold check)
- No integration issues - module is self-contained analysis helper
- Acceptance criteria evaluation logic is correct (r > 0.3, p < 0.05)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DIST-004_PROXY_IMPL_20251228_224110.md

VALIDIERUNG:
1. Fuehre minimale Tests aus (zielgerichtet)
2. Pruefe Code-Qualitaet
3. Verifiziere Acceptance Criteria

TOKEN HYGIENE:
- Bei Test FAIL: nur Command + kurze Fehlermeldung (max 20 Zeilen)
- Mehr Log noetig? Speichere in AI_COLLABORATION/ARTIFACTS/ und referenziere Pfad

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: APPROVED
task: DIST-004
role: VALIDATOR
phase: VALIDATOR
validated_handoff: "<nur filename oder leer>"
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

# Validation

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki3_DIST-004_VALIDATOR_20251228_224410.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
