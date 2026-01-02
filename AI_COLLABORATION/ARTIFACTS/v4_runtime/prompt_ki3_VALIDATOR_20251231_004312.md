AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: V1 vs V2 PARALLEL: Gesamt-Performance
TASK-ID: TASK_038
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-31 00:37:02] TASK_038 - PROXY_IMPL (ki0)

### Summary
- Synthese-Report verifiziert: results/v1_v2_performance_synthesis.md korrekt erstellt
- ROI-Werte aus Quelle bestaetigt: V2 Typ6 pair_focused +53.24%, V2 Typ7 pair_focused +28.79%
- N=2237 und date_range 2018-01-01 bis 2024-02-15 verifiziert
- Overfitting-Warnung korrekt und prominent dokumentiert (keine Train/Test-Split)
- SYSTEM_STATUS.json Konsistenz geprueft: negative ROI bei korrigierten Quoten dokumentiert
- Top 5 Tabelle stimmt exakt mit best_by_roi aus JSON ueberein
- Repro-Command funktional verifiziert
- Keine Architektur-Widersprueche eingefuehrt (nur Report-Datei)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_038_PROXY_IMPL_20251231_003501.md

## [2025-12-31 00:42:12] TASK_038 - VALIDATOR (ki3)

### Summary
- Reported average ROI values do not match source JSON (v1 -48.33%/v2 -35.43% vs -43.5%/-32.4% documented).
- Provided repro command in synthesis report fails with SyntaxError in current shell.

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK_038_VALIDATOR_20251231_003812.md

## [2025-12-31 00:43:12] TASK_038 - VALIDATOR (ki3)

### Summary
- Durchschnitts-ROI in `results/v1_v2_performance_synthesis.md:27` weicht vom Roh-Artefakt ab (tatsaechlich v1 -48.33%, v2 -35.43% per `results/backtest_v1_v2_comparison.json` N=2237).
- Repro-Command im Report (`results/v1_v2_performance_synthesis.md:93`) erzeugt SyntaxError im aktuellen PowerShell-Setup.
- Proxy-Handoff `AI_COLLABORATION/HANDOFFS/ki0_TASK_038_PROXY_IMPL_20251231_003501.md:1` enthaelt nur den Text "You've hit your limit..." (keine YAML/Ergebnisse).
- Validator-Handoff `AI_COLLABORATION/HANDOFFS/ki3_TASK_038_VALIDATOR_20251231_003812.md` erstellt (Status REJECTED, Tests protokolliert).

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK_038_VALIDATOR_20251231_003812.md




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
- results/backtest_v1_v2_comparison.json
- results/super_model_comparison_summary.md
- kenobase/core/keno_quotes.py (falls Quote-Verifikation noetig)
- AI_COLLABORATION/HANDOFFS/ki1_TASK_038_ARCHITECT_20251231_002901.md
- results/v1_v2_performance_synthesis.md

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
- Durchschnitts-ROI in `results/v1_v2_performance_synthesis.md:27` weicht vom Roh-Artefakt ab (tatsaechlich v1 -48.33%, v2 -35.43% per `results/backtest_v1_v2_comparison.json` N=2237).
- Repro-Command im Report (`results/v1_v2_performance_synthesis.md:93`) erzeugt SyntaxError im aktuellen PowerShell-Setup.
- Proxy-Handoff `AI_COLLABORATION/HANDOFFS/ki0_TASK_038_PROXY_IMPL_20251231_003501.md:1` enthaelt nur den Text "You've hit your limit..." (keine YAML/Ergebnisse).
- Validator-Handoff `AI_COLLABORATION/HANDOFFS/ki3_TASK_038_VALIDATOR_20251231_003812.md` erstellt (Status REJECTED, Tests protokolliert).

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK_038_VALIDATOR_20251231_003812.md

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
task: TASK_038
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK_038_VALIDATOR_20251231_004312.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
