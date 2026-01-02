AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Multi-Game Timeline (daily grid) bauen
TASK-ID: DATA-001
PRIORITY: P1
PHASE: ARCHITECT

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 01:46:54] DATA-001 - VALIDATOR (ki3)

### Summary
- All 24 unit tests passing (pytest tests/unit/test_timeline.py)
- Syntax validation OK for timeline.py, build_timeline_grid.py
- Parquet output verified: 1457 days x 45 columns (115KB)
- JSON summary valid: 3 games, correct coverage metrics
- KENO 7/week (100%), Lotto 2/week (28.5%), EuroJackpot 2/week (27.7%)
- Data_loader correctly parses Lotto bereinigt (L1-L6) and EJ (E1-E5/Euro1-2)
- CLI script works with --use-defaults and --json-summary <path>
- Ready for downstream COUPLE-001/002 integration

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_DATA-001_VALIDATOR_20251230_014454.md

## [2025-12-30 01:48:54] DATA-001 - PROXY_FINAL (ki0)

### Summary
- TimelineGrid module implements daily grid alignment for 3 lotteries
- KENO (7/wk), Lotto (2/wk Wed+Sat), EuroJackpot (2/wk Tue+Fri) correctly aligned
- 24 unit tests passing with good edge case coverage
- Parquet output: 1457 days x 46 columns (115KB) verified
- Coverage metrics correct: KENO 100%, Lotto 28.5%, EJ 27.7%
- CLI script with --use-defaults and --json-summary options functional
- Ready for downstream COUPLE-001/002 integration
- No architecture decisions require user escalation

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_DATA-001_PROXY_FINAL_20251230_014654.md




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
- kenobase/core/timeline.py (NEW - 378 lines)
- tests/unit/test_timeline.py (NEW - 401 lines)
- scripts/build_timeline_grid.py (NEW - 125 lines)
- kenobase/core/data_loader.py (MODIFIED - added Lotto bereinigt + EJ E-format parsers)
- data/processed/timeline_grid.parquet (NEW OUTPUT - 115KB)
- results/timeline_grid_summary.json (NEW OUTPUT)

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
task: DATA-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki5_DATA-001_ARCHITECT_20251230_021605.md
- YAML mit status: COMPLETE
- YAML mit files_changed: [...]
