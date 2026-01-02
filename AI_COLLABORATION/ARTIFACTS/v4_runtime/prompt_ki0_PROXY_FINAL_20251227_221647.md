AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Core Stable Numbers identifizieren
TASK-ID: TASK-H02
PRIORITY: HIGH
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-27 22:13:47] TASK-H02 - PROXY_IMPL (ki0)

### Summary
- stable_numbers.py implements Model Law A correctly (stability = 1 - std/mean, clamped [0,1])
- Config integration uses physics.stability_threshold (0.90) - no new global threshold
- CLI command `stable-numbers` added to analyze.py with proper options (--window, --threshold, --all)
- Exports added to kenobase/analysis/__init__.py (5 items: StableNumberResult, calculate_stability_score, analyze_stable_numbers, get_stable_numbers, export_stable_numbers)
- All 19 unit tests pass (test_stable_numbers.py)
- Syntax validation passes for all modified files
- Game-specific number_range from cfg.get_active_game() - no BUG-001 violation
- Import chain verified: kenobase.analysis -> stable_numbers OK

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-H02_PROXY_IMPL_20251227_221147.md

## [2025-12-27 22:16:47] TASK-H02 - VALIDATOR (ki3)

### Summary
- All 19 unit tests pass (test_stable_numbers.py) - 0.83s
- Model Law A formula verified: stability = 1 - (std/mean), clamped [0,1]
- Config uses physics.stability_threshold = 0.90 from default.yaml:30
- CLI command `stable-numbers` with --window, --threshold, --all options
- Import chain OK: kenobase.analysis -> stable_numbers (5 exports)
- Syntax validation passes for all 3 modified files
- Formula correctness verified with numeric test (0.974702 == expected)
- StableNumberResult dataclass frozen with 7 fields

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK-H02_VALIDATOR_20251227_221347.md




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
- kenobase/analysis/stable_numbers.py (NEW)
- kenobase/analysis/__init__.py (MODIFIED)
- scripts/analyze.py (MODIFIED)
- tests/unit/test_stable_numbers.py (NEW)

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
- All 19 unit tests pass (test_stable_numbers.py) - 0.83s
- Model Law A formula verified: stability = 1 - (std/mean), clamped [0,1]
- Config uses physics.stability_threshold = 0.90 from default.yaml:30
- CLI command `stable-numbers` with --window, --threshold, --all options
- Import chain OK: kenobase.analysis -> stable_numbers (5 exports)
- Syntax validation passes for all 3 modified files
- Formula correctness verified with numeric test (0.974702 == expected)
- StableNumberResult dataclass frozen with 7 fields

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_TASK-H02_VALIDATOR_20251227_221347.md

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
task: TASK-H02
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK-H02_PROXY_FINAL_20251227_221647.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
