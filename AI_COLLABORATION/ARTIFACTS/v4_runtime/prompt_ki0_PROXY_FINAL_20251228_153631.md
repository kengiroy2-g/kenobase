AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Index-Reset nach GK1 Analyse
TASK-ID: HYP005-001
PRIORITY: HOCH
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 15:34:31] HYP005-001 - PROXY_IMPL (ki0)

### Summary
- Created files verified: scripts/analyze_index_reset.py (275 lines), tests/unit/test_number_index.py (351 lines)
- Syntax check PASSED for both files
- All 18 unit tests PASSED (pytest run confirmed)
- Results JSON validated - properly formatted with full statistical output
- p-Value 0.0419 < 0.05 - Acceptance Criteria MET
- Uses existing calculate_index_correlation() from number_index.py (lines 166-328)
- Per-number granularity correctly maintained (no global thresholds)
- No integration issues detected - script is standalone analysis tool

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HYP005-001_PROXY_IMPL_20251228_153231.md

## [2025-12-28 15:36:31] HYP005-001 - VALIDATOR (ki3)

### Summary
- All 18 unit tests PASSED (pytest verified)
- Syntax check PASSED for scripts/analyze_index_reset.py
- Script runs end-to-end successfully with real data (2237 draws, 20 GK1 events)
- p-Value 0.0419 < 0.05 - Acceptance Criteria MET
- JSON output validated - proper structure with full statistical results
- Uses calculate_index_correlation() from number_index.py:166-328
- Per-number granularity maintained (70 numbers individually tracked)
- Effect size (Cohen's d = 0.063) indicates small but significant effect

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_HYP005-001_VALIDATOR_20251228_153431.md



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
- kenobase/analysis/number_index.py
- kenobase/core/data_loader.py
- kenobase/analysis/gk1_waiting.py
- scripts/analyze_hyp005.py
- Keno_GPTs/10-9_KGDaten_gefiltert.csv (Schema)
- data/raw/keno/KENO_ab_2018.csv (Schema)
- scripts/analyze_index_reset.py (NEW)
- tests/unit/test_number_index.py (NEW)

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
- All 18 unit tests PASSED (pytest verified)
- Syntax check PASSED for scripts/analyze_index_reset.py
- Script runs end-to-end successfully with real data (2237 draws, 20 GK1 events)
- p-Value 0.0419 < 0.05 - Acceptance Criteria MET
- JSON output validated - proper structure with full statistical results
- Uses calculate_index_correlation() from number_index.py:166-328
- Per-number granularity maintained (70 numbers individually tracked)
- Effect size (Cohen's d = 0.063) indicates small but significant effect

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_HYP005-001_VALIDATOR_20251228_153431.md

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
task: HYP005-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_HYP005-001_PROXY_FINAL_20251228_153631.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
