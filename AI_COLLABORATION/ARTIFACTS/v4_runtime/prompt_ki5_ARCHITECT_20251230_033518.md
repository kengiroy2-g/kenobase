AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Regime/State Detection (Change-Points, HMM)
TASK-ID: STATE-001
PRIORITY: HOCH
PHASE: ARCHITECT

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 03:31:08] STATE-001 - ARCHITECT (ki5)

### Summary
- Design Regime/State Detection module using Change-Point detection + HMM
- Integrate with existing EconomicState (kenobase/core/economic_state.py)
- Use ruptures for change-point detection, hmmlearn for Hidden Markov Models
- Two-stage approach - Change-points segment data, HMM labels regimes
- Target output - per-draw state labels (COOLDOWN/HOT/RECOVERY/NORMAL)
- Validation - Train/Test split per axioms.py protocol
- New file - kenobase/analysis/regime_detection.py
- Config section - economic_state + new regime_detection block

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki5_STATE-001_ARCHITECT_20251230_032608.md

## [2025-12-30 03:35:18] STATE-001 - PROXY_PLAN (ki0)

### Summary
- KI0 proxy profile missing in repo; SYSTEM_STATUS.json absent (read SYSTEM_STATUS.md instead) so guardrails/known integration points unverified.
- Plan lacks orchestrator/pipeline wiring for the regime module (only new file/config mentioned), risking BUG-003 orphan feature.
- Observables for change-points/HMM undefined (numbers vs economic proxies), leaving state_label semantics misaligned with `kenobase/core/economic_state.py`.
- Acceptance criteria and reproducibility not operationalized (placeholder validation script, no metric/threshold or data split details).
- Dependency/config details missing (ruptures/hmmlearn versions, config keys, train/test windows, data_loader touchpoints).
- Proxy handoff saved to `AI_COLLABORATION/HANDOFFS/ki0_STATE-001_PROXY_PLAN_20251230_033218.md`; CURRENT_STATUS not updated pending revised plan.

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_STATE-001_PROXY_PLAN_20251230_033218.md



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
- kenobase/core/economic_state.py
- kenobase/core/data_loader.py
- kenobase/analysis/__init__.py
- config/default.yaml
- requirements.txt

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
ROLLE: ARCHITECT
AUFGABE: Erstelle detaillierten Implementierungsplan.

EFFIZIENZ-REGELN (wie normal CLI):
- Kein Repo-weiter Scan (kein rekursives Listing, kein breitflÃ¤chiges Grep).
- Arbeite primÃ¤r mit WORKING SET + TASK NOTES; wenn leer: max 2 gezielte Datei-Finder-Queries, dann stoppen und fehlende Pfade anfordern.
- Keine Status-/Messaging-Dateien lesen/schreiben (queue/CURRENT_STATUS) ausser explizit verlangt.
- Keine langen Tool-Outputs im Handoff; grosse Logs nach AI_COLLABORATION/ARTIFACTS/ auslagern und verlinken.

SCHRITTE:
1. Analysiere Anforderungen
2. Identifiziere betroffene Dateien
3. Erstelle Schritt-fuer-Schritt Checkliste
4. Definiere Acceptance Criteria

TOKEN HYGIENE:
- Output muss direkt das Handoff-Markdown sein (keine Diffs, keine Zusatztexte).
- Schreibe Handoff mit YAML Frontmatter (---\nstatus: COMPLETE\n...\n---)
- Max 8 summary bullets
- Keine langen Logs/Diffs im Body (nur Pfade)

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: COMPLETE
task: STATE-001
role: ARCHITECT
phase: ARCHITECT
files_changed: []
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

# Implementierungsplan

WICHTIG: Erstelle Handoff-Datei wenn fertig:
- Datei: AI_COLLABORATION/HANDOFFS/ki5_STATE-001_ARCHITECT_20251230_033518.md
- YAML mit status: COMPLETE
- YAML mit files_changed: [...]
