AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Integration und Dokumentation
TASK-ID: QUOTE-001
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 18:25:40] QUOTE-001 - VALIDATOR (ki3)

### Summary
- Document docs/keno_quotes.md Line 34 uses WRONG formula
- Wrong: C(20,k)*C(50,n-k)/C(70,20)
- Correct: C(n,k)*C(70-n,20-k)/C(70,20)
- 8/9 KENO types have ROI errors (only Typ 10 within 0.3pp tolerance)
- Typ 7 worst error: -23.91pp (doc 25.66% vs correct 49.57%)
- Typ 8 error: -21.94pp (doc 21.31% vs correct 43.25%)
- AC2 (Probabilities) FAIL, AC4 (ROI) FAIL
- Return to EXECUTOR for complete recalculation

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_QUOTE-001_VALIDATOR_20251228_182240.md

## [2025-12-28 18:26:40] QUOTE-001 - VALIDATOR (ki3)

### Summary
- Formula Line 34 WRONG: uses C(20,k)*C(50,n-k) instead of C(n,k)*C(70-n,20-k)
- 8/9 KENO types have ROI errors exceeding 1pp tolerance
- Error range: -23.91pp (Typ 7) to +6.36pp (Typ 9)
- Only Typ 10 within tolerance: Doc 49.66% vs Correct 49.40% (+0.26pp)
- AC2 (Probabilities) FAIL
- AC4 (ROI) FAIL
- Document requires complete recalculation before approval
- Handoff: AI_COLLABORATION/HANDOFFS/ki3_QUOTE-001_VALIDATOR_20251228_182440.md

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_QUOTE-001_VALIDATOR_20251228_182440.md


## [2025-12-28 18:28:40] QUOTE-001 - VALIDATOR (ki3)

### Summary
- Formula Line 34 is CORRECT: P(k|n) = C(n,k)*C(70-n,20-k)/C(70,20)
- All probability values in tables are WRONG (miscalculated)
- All ROI values are WRONG (derived from wrong probabilities)
- 8/9 KENO types exceed 1pp tolerance (only Typ 10 within tolerance)
- Correct ROI should be ~50% for all types (German lottery house edge)
- Document shows impossible range 21%-56% (indicates calculation error)
- AC2 (Probabilities) FAIL
- AC4 (ROI) FAIL - requires complete recalculation

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_QUOTE-001_VALIDATOR_20251228_182640.md



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
- docs/keno_quotes.md (NEU - zu erstellen)
- AI_COLLABORATION/KNOWLEDGE_BASE/LOTTERY_STATISTICS_2024_2025.md (Referenz)
- AI_COLLABORATION/BACKLOG/KENOBASE_ISSUES.md (Task-Definition QUOTE-001)
- docs/keno_quotes.md

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
ROLLE: VALIDATOR
AUFGABE: Validiere die Implementation.

EFFIZIENZ-REGELN:
- Tests nur zielgerichtet (klein starten). Keine riesigen Logs in die Antwort; speichere nach AI_COLLABORATION/ARTIFACTS/ und verlinke.
- Vermeide Repo-weite Scans; nutze WORKING SET + gezielte Reads.

VORHERIGER OUTPUT (kurz):
- Formula Line 34 is CORRECT: P(k|n) = C(n,k)*C(70-n,20-k)/C(70,20)
- All probability values in tables are WRONG (miscalculated)
- All ROI values are WRONG (derived from wrong probabilities)
- 8/9 KENO types exceed 1pp tolerance (only Typ 10 within tolerance)
- Correct ROI should be ~50% for all types (German lottery house edge)
- Document shows impossible range 21%-56% (indicates calculation error)
- AC2 (Probabilities) FAIL
- AC4 (ROI) FAIL - requires complete recalculation

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki3_QUOTE-001_VALIDATOR_20251228_182640.md

VALIDIERUNG:
1. Fuehre minimale Tests aus (zielgerichtet)
2. Pruefe Code-Qualitaet
3. Verifiziere Acceptance Criteria

TOKEN HYGIENE:
- Bei Test FAIL: nur Command + kurze Fehlermeldung (max 20 Zeilen)
- Mehr Log noetig? Speichere in AI_COLLABORATION/ARTIFACTS/ und referenziere Pfad

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: APPROVED
task: QUOTE-001
role: VALIDATOR
phase: VALIDATOR
validated_handoff: "<nur filename oder leer>"
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

# Validation

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki3_QUOTE-001_VALIDATOR_20251228_182840.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
