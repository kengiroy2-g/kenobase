AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: P4-04: Output-Formate implementieren
TASK-ID: phase4_task04_output_formats
PRIORITY: P2
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-26 22:42:24] phase4_task04_output_formats - EXECUTOR (ki2)

### Summary
- Neues Modul kenobase/pipeline/output_formats.py mit 5 Formaten implementiert
- OutputFormat Enum (JSON, CSV, HTML, MARKDOWN, YAML) erstellt
- OutputFormatter Klasse mit Registry-Pattern fuer Erweiterbarkeit
- CSV erweitert mit Physics-Section und Pair-Frequencies
- HTML mit Grid-Layout und Avalanche-State-Styling
- Markdown GFM-kompatibel mit Tables und Warnings
- CLI auf 5 Formate erweitert (--format json|csv|html|markdown|yaml)
- 40 Unit-Tests alle bestanden

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_phase4_task04_output_formats_EXECUTOR_20251226_223624.md

## [2025-12-26 22:45:24] phase4_task04_output_formats - PROXY_IMPL (ki0)

### Summary
- Neues Modul output_formats.py (530 Zeilen) implementiert 5 Formate: JSON, CSV, HTML, Markdown, YAML
- OutputFormat Enum und OutputFormatter Klasse mit Registry-Pattern korrekt implementiert
- CSV erweitert mit Physics-Section und Pair-Frequencies (vorher nur frequency_results)
- HTML mit Grid-Layout, Avalanche-State-Styling (.avalanche-safe/moderate/warning/critical)
- Markdown GFM-kompatibel mit korrekten Tabellen-Separatoren (|

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase4_task04_output_formats_PROXY_IMPL_20251226_224224.md



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
- kenobase/pipeline/output_formats.py (NEW - 450 lines)
- kenobase/pipeline/__init__.py (MODIFIED - exports added)
- scripts/analyze.py (MODIFIED - CLI extended, legacy code removed)
- tests/unit/test_output_formats.py (NEW - 40 tests)

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
- Neues Modul output_formats.py (530 Zeilen) implementiert 5 Formate: JSON, CSV, HTML, Markdown, YAML
- OutputFormat Enum und OutputFormatter Klasse mit Registry-Pattern korrekt implementiert
- CSV erweitert mit Physics-Section und Pair-Frequencies (vorher nur frequency_results)
- HTML mit Grid-Layout, Avalanche-State-Styling (.avalanche-safe/moderate/warning/critical)
- Markdown GFM-kompatibel mit korrekten Tabellen-Separatoren (|

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_phase4_task04_output_formats_PROXY_IMPL_20251226_224224.md

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
task: phase4_task04_output_formats
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_phase4_task04_output_formats_VALIDATOR_20251226_224524.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
