AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Test HYP_008: Jahres-Zyklen
TASK-ID: TASK_018
PRIORITY: P2
PHASE: ARCHITECT

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 18:13:02] TASK_018 - ARCHITECT (ki1)

### Summary
- HYP_008 Jahres-Zyklen: Test ob ROI signifikant zwischen Jahren/Quartalen variiert
- Bestehende Infrastruktur nutzbar: cycle_phases.py, frequency.py, analyze_cycles_comprehensive.py
- Neues Script scripts/test_hyp008_year_cycles.py zu erstellen
- Nullmodell: Jahr-Permutation (shuffle year-labels preserving draw-order within year)
- Metriken: ROI pro Jahr, pro Quartal, pro Monat; Chi-Quadrat auf Hit-Distribution
- Train/Test Split: 2022-2024 Train, 2025 OOS Test
- Acceptance: p<0.05 (Bonferroni-korrigiert) UND ROI-Differenz >20% zwischen Perioden

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_018_ARCHITECT_20251230_181102.md

## [2025-12-30 18:15:02] TASK_018 - PROXY_PLAN (ki0)

### Summary (fallback)
- ---    ## PROXY Review Summary    **status: REJECTED**  **task: TASK_018**  **role: PROXY**  **phase: PROXY_PLAN**  **reviewed_handoff: ki1_TASK_018_ARCHITECT_20251230_181102.md**    ### Gruende fuer REJECTED    1. **ID-Kollision:** HYP-008 ist bereits in HYPOTHESES_CATALOG.md al ...

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_018_PROXY_PLAN_20251230_181302.md



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
- kenobase/core/keno_quotes.py
- scripts/analyze_cycles_comprehensive.py
- AI_COLLABORATION/KNOWLEDGE_BASE/HYPOTHESES_CATALOG.md

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
task: TASK_018
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
- Datei: AI_COLLABORATION/HANDOFFS/ki1_TASK_018_ARCHITECT_20251230_181803.md
- YAML mit status: COMPLETE
- YAML mit files_changed: [...]
