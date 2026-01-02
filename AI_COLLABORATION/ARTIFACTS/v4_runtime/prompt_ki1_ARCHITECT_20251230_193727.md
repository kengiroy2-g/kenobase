AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Test HYP_012: Overlap-Menge
TASK-ID: TASK_022
PRIORITY: P2
PHASE: ARCHITECT

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 19:34:16] TASK_022 - ARCHITECT (ki1)

### Summary
- SYSTEM_STATUS.json fehlt; SYSTEM_STATUS.md (2025-12-29, V2.2.2) als Kontext gelesen; git status erfasst.
- ADR_AXIOM_FIRST_FRAMEWORK.md (Axiom-first Guardrails) und README_CYCLES_ANALYSIS (Ticket-V1/V2, Phasenklassifikation, Datenpfade) geprÃ¼ft.
- HYP_012 misst overlap_count=|draw_t INTERSECT draw_{t-1}| (E=5.714 hypergeom) und overlap_birthday_ratio via scripts/analyze_cycles_comprehensive.py.
- Inputs: data/raw/keno/KENO_ab_2022_bereinigt.csv (~1457 Ziehungen), data/processed/ecosystem/timeline_2025.csv; Output: results/overlap_statistics.json.
- Fehlende Artefakte blockieren Compliance: AI_COLLABORATION/SYSTEM_STATUS.json und AI_COLLABORATION/KI_PROFILES/ki0_proxy.md mÃ¼ssen erstellt werden.
- Zielmetrik: Calibration der Overlap/Birthday z-Scores (Bonferroni alpha=0.0033) global und je Phase; bisher keine Signifikanz.

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK_022_ARCHITECT_20251230_193016.md

## [2025-12-30 19:37:27] TASK_022 - PROXY_PLAN (ki0)

### Summary
- SYSTEM_STATUS.json fehlt; Plan hat keinen Recovery-Step und verletzt die Kontext-Sync-Regel, daher nicht executor-fÃ¤hig.
- Pflichtprofil AI_COLLABORATION/KI_PROFILES/ki0_proxy.md fehlt; Known Bugs/Integrationspunkte kÃ¶nnen nicht angewendet werden.
- Plan-Logik fÃ¼r HYP_012 (overlap_count/overlap_birthday_ratio via scripts/analyze_cycles_comprehensive.py mit inputs raw/processed, output results/overlap_statistics.json) wirkt schlÃ¼ssig, aber Repro-Befehl ist nicht dokumentiert.
- Executor bleibt blockiert, bis beide Artefakte erstellt und der Status synchronisiert sind.

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_022_PROXY_PLAN_20251230_193526.md



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
- AI_COLLABORATION/SYSTEM_STATUS.md
- AI_COLLABORATION/KI_PROFILES/KI_1_LEAD_ARCHITECT.md
- scripts/analyze_cycles_comprehensive.py
- data/raw/keno/KENO_ab_2022_bereinigt.csv
- data/processed/ecosystem/timeline_2025.csv
- results/overlap_statistics.json

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
task: TASK_022
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
- Datei: AI_COLLABORATION/HANDOFFS/ki1_TASK_022_ARCHITECT_20251230_193727.md
- YAML mit status: COMPLETE
- YAML mit files_changed: [...]
