AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Lag-Exploitation
TASK-ID: STRAT-003
PRIORITY: P2
PHASE: PROXY_PLAN

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 15:11:30] STRAT-003 - PROXY_FINAL (ki0)

### Summary
- STRAT-003 (Offene Hypothesen Analyse) vollstaendig abgeschlossen
- 4 Hypothesen analysiert mit robusten statistischen Methoden
- HYP-002 FALSIFIZIERT (CV=0.95/0.70, Wartezeiten zufaellig)
- HYP-005 FALSIFIZIERT (0/21 signifikante Dekaden-Paare, alle p>0.96)
- HYP-006 BESTAETIGT (100% Recurrence, 5.73 avg, stabile Paare)
- HYP-011 BESTAETIGT (Holiday Effect p=0.0001, 7.2% vs 9.6%)
- Alle Artefakte vorhanden und HYPOTHESES_CATALOG.md korrekt aktualisiert
- KENOBASE_ISSUES.md zeigt 28/33 DONE, 5 OFFEN - konsistent mit Ergebnissen

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_STRAT-003_PROXY_FINAL_20251228_150930.md

## [2025-12-30 06:41:46] STRAT-003 - ARCHITECT (ki1)

### Summary
- STRAT-003 Lag-Exploitation plan based on ecosystem_graph.json findings
- ONE robust edge found: KENO->AUSWAHLWETTE lag=7, lift=2.41x, q=0.027
- Strategy: When KENO draws number 11, bet number 25 in AUSWAHLWETTE 7 days later
- Baseline rate 14.1%, conditional rate 34.0% (2.41x improvement)
- Implementation requires backtest with train/test split + ROI calculation
- Null model: schedule-preserving permutation (weekday blocks)
- Risk: Single edge may be spurious; need multiple independent validation
- Acceptance: Positive ROI in test period with p<0.05 vs null

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_STRAT-003_ARCHITECT_20251230_063846.md




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
- results/hyp005_decade_affinity.json
- results/hyp006/wgz_analysis.json
- results/hyp011_temporal_cycles.json
- scripts/strategy_from_ecosystem.py
- scripts/analyze_cross_game_timing.py
- results/ecosystem_graph.json
- data/raw/keno/KENO_ab_2022_bereinigt.csv
- data/raw/auswahlwette/AW_ab_2022_bereinigt.csv

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
- STRAT-003 Lag-Exploitation plan based on ecosystem_graph.json findings
- ONE robust edge found: KENO->AUSWAHLWETTE lag=7, lift=2.41x, q=0.027
- Strategy: When KENO draws number 11, bet number 25 in AUSWAHLWETTE 7 days later
- Baseline rate 14.1%, conditional rate 34.0% (2.41x improvement)
- Implementation requires backtest with train/test split + ROI calculation
- Null model: schedule-preserving permutation (weekday blocks)
- Risk: Single edge may be spurious; need multiple independent validation
- Acceptance: Positive ROI in test period with p<0.05 vs null

FULL HANDOFF (nur bei Bedarf oeffnen):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_STRAT-003_ARCHITECT_20251230_063846.md

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
task: STRAT-003
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_STRAT-003_PROXY_PLAN_20251230_064146.md
- YAML Frontmatter mit status:
  - APPROVED: Plan ist gut, weiter zu Executor
  - REJECTED: Bug gefunden, zurueck zu Architect
  - ESCALATE: User-Entscheidung noetig (Architektur-Frage, Design-Wahl)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung (max 8 bullets)
