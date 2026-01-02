AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Spieler-Popularitaet als Risiko-Proxy modellieren (Birthday/Pattern-Risk)
TASK-ID: POP-001
PRIORITY: MITTEL
PHASE: PROXY_PLAN

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 03:11:07] POP-001 - ARCHITECT (ki5)

### Summary (fallback)
- Handoff-Datei erfolgreich erstellt.    ---    **ARCHITECT COMPLETE**    ---  status: COMPLETE  task: POP-001  role: ARCHITECT  phase: ARCHITECT  files_changed: []  summary:    - Spieler-Popularitaet als Risiko-Proxy modellieren (Birthday/Pattern-Risk)    - Bestehende Module ident ...

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki5_POP-001_ARCHITECT_20251230_030807.md



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
- (leer)

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
Handoff-Datei erfolgreich erstellt.

---

**ARCHITECT COMPLETE**

---
status: COMPLETE
task: POP-001
role: ARCHITECT
phase: ARCHITECT
files_changed: []
summary:
  - Spieler-Popularitaet als Risiko-Proxy modellieren (Birthday/Pattern-Risk)
  - Bestehende Module identifiziert: anti_birthday.py + popularity_correlation.py
  - Neues Modul: kenobase/analysis/popularity_risk.py (Risiko-Score-Kombinator)
  - Integration in prediction/recommendation.py fuer Spielentscheidungen
  - Backtest-Erweiterung fuer ROI-Impact-Messung
  - Null-Model Validierung mit permutiertem Birthday-Score
---

**Handoff-Datei**: `AI_COLLABORATION/HANDOFFS/ki5_POP-001_ARCHITECT_20251230_030807.md`

**Key Deliverables fuer EXECUTOR**:
1. `kenobase/analysis/popularity_risk.py` - Neues Modul mit `PopularityRiskScore`, `calculate_pattern_risk_score()`, `estimate_competition_factor()`, `should_play()`
2. `tests/unit/test_popularity_risk.py` - Unit Tests
3. `scripts/backtest_popularity_risk.py` - ROI-Backtest
4. Integration in `recommendation.py`

**Acceptance Criteria**: AC-1 bis AC-5 definiert (0-1 Range, Monotonie, >10% ROI-Verbesserung, Null-Model <0.1, >80% Coverage)


FULL HANDOFF (nur bei Bedarf oeffnen):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki5_POP-001_ARCHITECT_20251230_030807.md

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
task: POP-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_POP-001_PROXY_PLAN_20251230_031107.md
- YAML Frontmatter mit status:
  - APPROVED: Plan ist gut, weiter zu Executor
  - REJECTED: Bug gefunden, zurueck zu Architect
  - ESCALATE: User-Entscheidung noetig (Architektur-Frage, Design-Wahl)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung (max 8 bullets)
