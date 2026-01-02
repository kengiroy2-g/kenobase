AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Inverse/periodische Kopplung (Cross-Spectrum, Phase)
TASK-ID: COUPLE-002
PRIORITY: MITTEL
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
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

## [2025-12-30 05:15:51] COUPLE-002 - PROXY_IMPL (ki0)

### Summary
- Implementation matches architecture plan: CPSD/coherence/phase-lag via scipy.signal
- Phase-randomized and block-permutation surrogates correctly preserve amplitude spectrum / block structure
- BH/FDR correction applied per-band across both coherence and PLV p-values
- CLI supports KENO/Lotto/EuroJackpot with configurable representations and frequency bands
- All 23 unit tests pass: synth-sinus detection, null-control, schema checks verified
- EuroJackpot correctly treated as negative control (flagged in output)
- Module exports correctly added to analysis/__init__.py (8 symbols)
- No integration issues found; bh_fdr and GameDraws dependencies verified

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_COUPLE-002_PROXY_IMPL_20251230_051251.md



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
ROLLE: VALIDATOR
AUFGABE: Validiere die Implementation.

EFFIZIENZ-REGELN:
- Tests nur zielgerichtet (klein starten). Keine riesigen Logs in die Antwort; speichere nach AI_COLLABORATION/ARTIFACTS/ und verlinke.
- Vermeide Repo-weite Scans; nutze WORKING SET + gezielte Reads.

VORHERIGER OUTPUT (kurz):
- Implementation matches architecture plan: CPSD/coherence/phase-lag via scipy.signal
- Phase-randomized and block-permutation surrogates correctly preserve amplitude spectrum / block structure
- BH/FDR correction applied per-band across both coherence and PLV p-values
- CLI supports KENO/Lotto/EuroJackpot with configurable representations and frequency bands
- All 23 unit tests pass: synth-sinus detection, null-control, schema checks verified
- EuroJackpot correctly treated as negative control (flagged in output)
- Module exports correctly added to analysis/__init__.py (8 symbols)
- No integration issues found; bh_fdr and GameDraws dependencies verified

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_COUPLE-002_PROXY_IMPL_20251230_051251.md

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
task: COUPLE-002
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
- Datei: AI_COLLABORATION/HANDOFFS/ki7_COUPLE-002_VALIDATOR_20251230_051551.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
