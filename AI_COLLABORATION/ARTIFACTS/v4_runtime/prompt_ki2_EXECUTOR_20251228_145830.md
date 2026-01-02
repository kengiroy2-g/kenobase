AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Offene Hypothesen Analyse
TASK-ID: STRAT-003
PRIORITY: P1
PHASE: EXECUTOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 14:55:30] STRAT-003 - ARCHITECT (ki1)

### Summary
- Analysiert: 14 Hypothesen im HYPOTHESES_CATALOG.md
- BESTAETIGT (4): HYP-001, HYP-004, HYP-010, HYP-013
- FALSIFIZIERT (6): HYP-008, RE02, M02, HYP-007, HYP-010/Odds, HYP-012
- OFFEN (6): HYP-002, HYP-003, HYP-005, HYP-006, HYP-009, HYP-014
- Priorisierung: HYP-009 > HYP-005 > HYP-002 > HYP-003
- 10 analyze_hyp*.py Scripts vorhanden
- Naechste Aktion: Scripts fuer offene Hypothesen ausfuehren

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_STRAT-003_ARCHITECT_20251228_145318.md

## [2025-12-28 14:58:30] STRAT-003 - PROXY_PLAN (ki0)

### Summary (fallback)
- ---    ## PROXY Review abgeschlossen    **status: APPROVED**    | Pruefung | Ergebnis |  |----------|----------|  | Mechanisch | Plan vollstaendig, Acceptance Criteria messbar |  | Architektur | Keine ADR-Widersprueche |  | Integration | Alle benoetigten Dateien/Scripts existiere ...

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_STRAT-003_PROXY_PLAN_20251228_145530.md



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
- scripts/analyze_hyp002.py
- scripts/analyze_hyp005.py
- scripts/analyze_hyp006.py
- scripts/analyze_hyp011.py
- AI_COLLABORATION/KNOWLEDGE_BASE/HYPOTHESES_CATALOG.md
- AI_COLLABORATION/BACKLOG/KENOBASE_ISSUES.md

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
ROLLE: EXECUTOR
AUFGABE: Fuehre den genehmigten Plan aus.

EFFIZIENZ-REGELN:
- Starte mit WORKING SET; vermeide Repo-weite Scans. Wenn du suchen musst: 1 gezieltes Grep pro Subtask, nicht breit.
- Schreibe nur kurze, entscheidungsrelevante Logs; grosse Logs nach AI_COLLABORATION/ARTIFACTS/ auslagern und verlinken.
- Aktualisiere Status ausschliesslich ueber den Handoff (keine CURRENT_STATUS edits im Body).
- Aendere niemals AI_COLLABORATION/MESSAGE_QUEUE/* oder AI_COLLABORATION/RESULTS/CURRENT_STATUS.md (nur Handoff-Ausgabe).
- Vermeide das Ausgeben von Diffs (diff --git, Patch-BlÃ¶cke). In der Antwort nur Summary + Pfade.

PLAN (kurz):
---

## PROXY Review abgeschlossen

**status: APPROVED**

| Pruefung | Ergebnis |
|----------|----------|
| Mechanisch | Plan vollstaendig, Acceptance Criteria messbar |
| Architektur | Keine ADR-Widersprueche |
| Integration | Alle benoetigten Dateien/Scripts existieren |
| Konzeptionell | Keine Known Bugs (BUG-001/003) |

**Handoff erstellt:**
`AI_COLLABORATION/HANDOFFS/ki0_STRAT-003_PROXY_PLAN_20251228_145530.md`

**Naechster Schritt:** Plan geht an EXECUTOR zur Ausfuehrung der Hypothesen-Scripts.


FULL PLAN (nur bei Bedarf):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_STRAT-003_PROXY_PLAN_20251228_145530.md

REGELN:
1. Folge Checkliste exakt
2. Keine eigenen Interpretationen
3. Dokumentiere jeden Schritt
4. WICHTIG: Fuege files_changed: [...] im YAML hinzu

TOKEN HYGIENE:
- Final Output muss direkt das Handoff-Markdown sein (keine Diffs, keine Zusatztexte).
- Keine langen Command-Outputs im Handoff
- Bei Fehlern: nur Command + 20 Zeilen excerpt
- Lange Logs: speichere in AI_COLLABORATION/ARTIFACTS/ und referenziere nur Pfad

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: COMPLETE
task: STRAT-003
role: EXECUTOR
phase: EXECUTOR
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

# Umsetzung

WICHTIG: Erstelle Handoff-Datei wenn fertig:
- Datei: AI_COLLABORATION/HANDOFFS/ki2_STRAT-003_EXECUTOR_20251228_145830.md
- YAML mit status: COMPLETE oder BLOCKED
- YAML mit files_changed: [...]
