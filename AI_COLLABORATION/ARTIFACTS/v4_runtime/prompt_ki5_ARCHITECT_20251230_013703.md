AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Axiome + falsifizierbare Predictions definieren
TASK-ID: AXIOM-001
PRIORITY: P1
PHASE: ARCHITECT

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 01:28:03] AXIOM-001 - PROXY_PLAN (ki0)

### Summary
- Handoff-Datei ist unvollstaendig (nur Stub mit Summary, keine Details)
- 21 Predictions erwÃ¤hnt aber nicht dokumentiert
- Keine Acceptance Criteria fuer die 5 Executor-Steps
- Keine konkreten Repro-Commands oder Artefakt-Pfade
- Nullmodell-Strategie nur genannt, nicht spezifiziert
- Train/Test-Split genannt aber keine Window-Groessen
- EuroJackpot-Kontrollkanal nur erwaehnt, nicht definiert
- ARCHITECT muss vollstaendige Spezifikation liefern

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_AXIOM-001_PROXY_PLAN_20251230_012603.md

## [2025-12-30 01:35:03] AXIOM-001 - ARCHITECT (ki5)

### Summary
- 7 Axiome (A1-A7) vollstaendig spezifiziert mit wirtschaftlicher Begruendung
- 21 falsifizierbare Predictions definiert (3 pro Axiom) mit konkreten Metriken
- Nullmodell-Strategie pro Prediction-Typ dokumentiert
- Train/Test-Split pre-2024 Train, 2024+ Test (frozen rules)
- EuroJackpot als externer Kontrollkanal (negative control)
- 5-Step Executor Checkliste mit Acceptance Criteria
- Repro-Commands fuer alle Validierungen

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki5_AXIOM-001_ARCHITECT_20251230_012803.md

## [2025-12-30 01:37:03] AXIOM-001 - PROXY_PLAN (ki0)

### Summary
- Handoff-Datei ist UNVOLLSTAENDIG - endet bei Zeile 106 (Axiom A4-P3)
- Axiome A5, A6, A7 fehlen komplett (nur 12 von 21 Predictions dokumentiert)
- 5-Step Executor Checkliste mit Acceptance Criteria fehlt komplett
- Keine Code-Spezifikation fuer kenobase/core/axioms.py
- Train/Test-Split nur erwaehnt aber keine Window-Details
- Kein EuroJackpot-Kontrollkanal-Spezifikation
- Repro-Command referenziert nicht existierendes Script
- ARCHITECT muss vollstaendiges Dokument mit allen 7 Axiomen liefern

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_AXIOM-001_PROXY_PLAN_20251230_013503.md



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
- AI_COLLABORATION/HANDOFFS/ki5_AXIOM-001_ARCHITECT_20251230_012102.md (NEU)AI_COLLABORATION/HANDOFFS/ki5_AXIOM-001_ARCHITECT_20251230_012803.md (NEU)kenobase/core/axioms.py (TO CREATE)tests/unit/test_axioms.py (TO CREATE)scripts/validate_axiom_predictions.py (TO CREATE)

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
task: AXIOM-001
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
- Datei: AI_COLLABORATION/HANDOFFS/ki5_AXIOM-001_ARCHITECT_20251230_013703.md
- YAML mit status: COMPLETE
- YAML mit files_changed: [...]
