AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Inverse/periodische Kopplung (Cross-Spectrum, Phase)
TASK-ID: COUPLE-002
PRIORITY: MITTEL
PHASE: PROXY_FINAL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-30 05:15:51] COUPLE-002 - PROXY_IMPL (ki0)

### Summary
- Implementation matches architecture plan: CPSD/coherence/phase-lag via scipy.signal
- Phase-randomized and block-permutation surrogates correctly preserve amplitude spectrum / block structure
- BH/FDR correction applied per-band across both coherence and PLV p-values
- CLI supports KENO/Lotto/EuroJackpot with configurable representations and frequency bands
- All 23 unit tests pass: synth-sinus detection, null-control, schema checks verified
- EuroJackpot correctly treated as negative control (flagged in output)
- Module exports correctly added to analysis/__init__.py (8 symbols)
- No integration issues found; bh_fdr and GameDraws dependencies verified

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_COUPLE-002_PROXY_IMPL_20251230_051251.md

## [2025-12-30 05:18:51] COUPLE-002 - VALIDATOR (ki7)

### Summary
- All 23 unit tests pass (2.68s) covering PLV, circular mean, surrogates, spectral computation, synthetic sinusoids, null control, and CLI schema
- CLI help verified: analyze_cross_spectrum_coupling.py with all parameters
- Module exports verified: 8 public symbols correctly exported from kenobase.analysis
- Acceptance criteria met: BH-corrected q-values, negative_control flag, tests pass, repro commands documented
- Architecture plan verified: CPSD/coherence via scipy.signal, phase-randomized and block surrogates
- EuroJackpot correctly treated as negative control per CLAUDE.md section 1.2
- Code quality: 722 lines main module, 467 lines tests, clean dataclass design

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki7_COUPLE-002_VALIDATOR_20251230_051551.md




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
- AI_COLLABORATION/HANDOFFS/ki5_COUPLE-002_ARCHITECT_20251230_043400.mdkenobase/analysis/cross_spectrum_coupling.pykenobase/analysis/__init__.pyscripts/analyze_cross_spectrum_coupling.pytests/unit/test_cross_spectrum_coupling.py

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
ROLLE: PROXY (User-Stellvertreter - Finale Freigabe)
AUFGABE: Finale Freigabe mit Projekt-Perspektive.

PFLICHTLEKTUERE (kurz):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Falls Zweifel an Integration

EFFIZIENZ-REGELN:
- Nutze VALIDATOR OUTPUT + dein Wissen aus vorherigen Proxy-Phasen
- Keine weiteren Tests, nur finale Entscheidung

VALIDATOR OUTPUT (kurz):
- All 23 unit tests pass (2.68s) covering PLV, circular mean, surrogates, spectral computation, synthetic sinusoids, null control, and CLI schema
- CLI help verified: analyze_cross_spectrum_coupling.py with all parameters
- Module exports verified: 8 public symbols correctly exported from kenobase.analysis
- Acceptance criteria met: BH-corrected q-values, negative_control flag, tests pass, repro commands documented
- Architecture plan verified: CPSD/coherence via scipy.signal, phase-randomized and block surrogates
- EuroJackpot correctly treated as negative control per CLAUDE.md section 1.2
- Code quality: 722 lines main module, 467 lines tests, clean dataclass design

FULL VALIDATOR HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki7_COUPLE-002_VALIDATOR_20251230_051551.md

FINALE PRUEFUNG:
1. Hat Validator alle kritischen Aspekte geprueft?
2. Wuerde der USER diese Aenderung akzeptieren?
3. Gibt es offene Architektur-Fragen die der User entscheiden sollte?

ESKALATION an User wenn:
- Architektur-Entscheidung noetig die nicht in ADRs dokumentiert ist
- Unsicherheit ueber globale vs spezifische Werte
- Potenzielle Breaking Changes

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: COMPLETE
task: COUPLE-002
role: PROXY
phase: PROXY_FINAL
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

# Proxy Final Review

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki0_COUPLE-002_PROXY_FINAL_20251230_051851.md
- YAML mit status:
  - COMPLETE: Task fertig, alles gut
  - REJECTED: Problem gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig vor Finalisierung
- Kurze finale Zusammenfassung
