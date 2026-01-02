AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Ensemble Prediction Model
TASK-ID: TASK-P06
PRIORITY: HIGH
PHASE: PROXY_PLAN

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 04:21:22] TASK-P06 - ARCHITECT (ki1)

### Summary (fallback)
- Handoff file created successfully. Here's the summary:    ---  **status: COMPLETE**  **task: TASK-P06**  **role: ARCHITECT**  **phase: ARCHITECT**  **files_changed: []**    ## Summary  - Analyzed TASK-P06 Ensemble Prediction Model (4h, HOCH priority)  - Ensemble combines Rule-Bas ...

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK-P06_ARCHITECT_20251228_041622.md



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
- Analyzed TASK-P06 Ensemble Prediction Model (4h, HOCH priority)
- Ensemble combines Rule-Based (0.4 wt) + ML Model (0.6 wt)
- Rule-Based HypothesisSynthesizer exists (`synthesizer.py`)
- ML Model KenoPredictor + KenoTrainer exist (`model.py`, `trainer.py`)
- Gap: No EnsemblePredictor class to combine both approaches
- Target F1 >= 0.50 (improvement from 0.4434 baseline)
- New file needed: `kenobase/prediction/ensemble.py`

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
AUFGABE: Pruefe den Plan vom ARCHITECT - NICHT nur mechanisch, sondern konzeptionell.

PFLICHTLEKTUERE (vor Review lesen):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Dein vollstaendiges Profil mit Known Bugs
2. AI_COLLABORATION/SYSTEM_STATUS.json - Aktueller Projektstatus
3. CLAUDE.md - Projektkontext (bei Architektur-Fragen)

EFFIZIENZ-REGELN:
- Arbeite mit VORHERIGER OUTPUT + TASK NOTES + Profil-Wissen
- Maximal 3-4 gezielte Reads (Profil, Status, relevante Dateien)
- Keine breiten Repo-Scans

VORHERIGER OUTPUT (kurz, no logs):
Handoff file created successfully. Here's the summary:

---
**status: COMPLETE**
**task: TASK-P06**
**role: ARCHITECT**
**phase: ARCHITECT**
**files_changed: []**

## Summary
- Analyzed TASK-P06 Ensemble Prediction Model (4h, HOCH priority)
- Ensemble combines Rule-Based (0.4 wt) + ML Model (0.6 wt)
- Rule-Based HypothesisSynthesizer exists (`synthesizer.py`)
- ML Model KenoPredictor + KenoTrainer exist (`model.py`, `trainer.py`)
- Gap: No EnsemblePredictor class to combine both approaches
- Target F1 >= 0.50 (improvement from 0.4434 baseline)
- New file needed: `kenobase/prediction/ensemble.py`

## Key Deliverables for EXECUTOR

**New files to create:**
1. `kenobase/prediction/ensemble.py` - EnsemblePredictor class
2. `tests/unit/test_ensemble.py` - Unit tests

**Files to modify:**
1. `kenobase/prediction/__init__.py` - Add exports
2. `scripts/predict.py` - Add `--ensemble` flag

## Architecture
```
EnsemblePredictor = alpha * HypothesisSynthesizer + (1-alpha) * KenoPredictor
Default: alpha = 0.4 (rule), 0.6 (ml)
```

## Handoff Location
`AI_COLLABORATION/HANDOFFS/ki1_TASK-P06_ARCHITECT_20251228_041622.md`


FULL HANDOFF (nur bei Bedarf oeffnen):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK-P06_ARCHITECT_20251228_041622.md

PRUEFKRITERIEN (4 Dimensionen):
1. MECHANISCH: Plan vollstaendig? Schritte klar? Acceptance Criteria messbar?
2. ARCHITEKTUR: Passt zu ADRs? Keine Widersprueche?
3. INTEGRATION: Werden alle betroffenen Dateien genannt? (siehe Known Integration Points im Profil)
4. KONZEPTIONELL: Globale Werte wo spezifische noetig? Known Bugs vermieden?

RED FLAGS (sofort REJECTED):
- Globale Thresholds in team-spezifischem System (BUG-001)
- Feature ohne Orchestrator-Integration (BUG-003)
- Cross-File Aenderung ohne alle Dateien (Known Integration Points)

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: APPROVED
task: TASK-P06
role: PROXY
phase: PROXY_PLAN
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

# Proxy Review

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK-P06_PROXY_PLAN_20251228_042122.md
- YAML Frontmatter mit status:
  - APPROVED: Plan ist gut, weiter zu Executor
  - REJECTED: Bug gefunden, zurueck zu Architect
  - ESCALATE: User-Entscheidung noetig (Architektur-Frage, Design-Wahl)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung (max 8 bullets)
