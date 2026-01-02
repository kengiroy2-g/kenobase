AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Near-Miss Analyse bei hohem Jackpot
TASK-ID: HOUSE-004
PRIORITY: P1
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 21:06:06] HOUSE-004 - PROXY_IMPL (ki0)

### Summary
- All 3 files created (near_miss_jackpot.py, analyze_house004.py, test_near_miss_jackpot.py)
- Syntax validation passed for all files (py_compile OK)
- All 20 unit tests passing (pytest 0.88s)
- Module imports work correctly from kenobase.analysis
- CLI --help verified working
- Imports from dependency modules (jackpot_correlation, near_miss) verified
- No global threshold issues - uses standard p<0.05 significance
- Architecture consistent with existing house002/house003 patterns

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_HOUSE-004_PROXY_IMPL_20251228_210406.md

## [2025-12-28 21:08:06] HOUSE-004 - VALIDATOR (ki3)

### Summary
- All 20 unit tests pass (pytest 0.89s)
- CLI --help verified working with correct arguments
- Module imports correctly (P_VALUE_THRESHOLD=0.05, MIN_SIGNIFICANT_TYPES=3)
- Syntax validation OK (py_compile all 3 files)
- Code follows dataclass pattern consistent with HYP modules
- Chi-square test correctly implemented with scipy.stats.chi2_contingency
- Acceptance criteria logic correct (>= 3 significant types = SUPPORTED)
- No global threshold violations - uses standard p < 0.05

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_HOUSE-004_VALIDATOR_20251228_210606.md



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
- kenobase/analysis/near_miss_jackpot.py
- scripts/analyze_house004.py
- tests/unit/test_near_miss_jackpot.py

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
- All 20 unit tests pass (pytest 0.89s)
- CLI --help verified working with correct arguments
- Module imports correctly (P_VALUE_THRESHOLD=0.05, MIN_SIGNIFICANT_TYPES=3)
- Syntax validation OK (py_compile all 3 files)
- Code follows dataclass pattern consistent with HYP modules
- Chi-square test correctly implemented with scipy.stats.chi2_contingency
- Acceptance criteria logic correct (>= 3 significant types = SUPPORTED)
- No global threshold violations - uses standard p < 0.05

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_HOUSE-004_VALIDATOR_20251228_210606.md

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
task: HOUSE-004
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_HOUSE-004_PROXY_FINAL_20251228_210806.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
