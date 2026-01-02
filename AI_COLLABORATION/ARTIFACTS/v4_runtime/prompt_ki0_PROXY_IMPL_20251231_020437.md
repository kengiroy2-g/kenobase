AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: V1 vs V2 PARALLEL: High-Win Forensik
TASK-ID: TASK_039d
PRIORITY: P2
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-31 02:01:36] TASK_039d - PROXY_PLAN (ki0)

### Summary
- ARCHITECT correctly identified existing forensik infrastructure (scripts/analyze_high_win_forensik.py)
- Current artifact results/high_win_forensik.json contains 14 events with strategy breakdown
- V1/V2 semantics confirmed: V1={near_miss,jackpot,balanced}=8 events; V2={pair_focused}=6 events
- Permutation test p=0.571 already validates no significant clustering (nullmodel compliant)
- OOS data available in data/raw/keno/KENO_ab_2022_bereinigt.csv for 2025 validation
- Plan lacks explicit implementation steps but existing script can be extended
- Birthday_ratio_mean=0.446 (near expected 0.443 for uniform) - no strong V1/V2 delta expected
- APPROVED: Existing infrastructure sufficient; Executor should add V1/V2 comparison output

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK_039d_PROXY_PLAN_20251231_015936.md

## [2025-12-31 02:04:37] TASK_039d - EXECUTOR (ki2)

### Summary
- Extended analyze_high_win_forensik.py with V1/V2 comparison (lines 226-305)
- V1={near_miss,jackpot,balanced}: 8 events, birthday_ratio=0.456, avg_payout=625 EUR
- V2={pair_focused}: 6 events, birthday_ratio=0.433, avg_payout=583.33 EUR
- Delta birthday_ratio=-0.023 (V2 slightly lower, near expected uniform 0.443)
- Delta avg_payout=-41.67 EUR (V2 lower due to more Typ-6 vs Typ-7 mix)
- Permutation test p=0.591 confirms no significant clustering (nullmodel compliant)
- Updated results/high_win_forensik.json with v1_v2_comparison section
- No OOS 2025 high-win events in current backtest to compare (would require new run)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_039d_EXECUTOR_20251231_020136.md



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
- scripts/analyze_high_win_forensik.py
- results/high_win_forensik.json
- results/high_win_forensik_v1v2.json

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
AUFGABE: Pruefe die Implementation - NICHT nur mechanisch, sondern auf Architektur-Konsistenz.

PFLICHTLEKTUERE (vor Review):
1. AI_COLLABORATION/KI_PROFILES/ki0_proxy.md - Known Bugs & Integration Points
2. AI_COLLABORATION/SYSTEM_STATUS.json - Bei Architektur-Fragen

EFFIZIENZ-REGELN:
- Arbeite mit VORHERIGER OUTPUT + WORKING SET + Profil-Wissen
- Maximal 3-4 gezielte Reads
- Minimaler Sanity-Check (python -m py_compile, JSON-Validierung)

VORHERIGER OUTPUT (kurz):
- Extended analyze_high_win_forensik.py with V1/V2 comparison (lines 226-305)
- V1={near_miss,jackpot,balanced}: 8 events, birthday_ratio=0.456, avg_payout=625 EUR
- V2={pair_focused}: 6 events, birthday_ratio=0.433, avg_payout=583.33 EUR
- Delta birthday_ratio=-0.023 (V2 slightly lower, near expected uniform 0.443)
- Delta avg_payout=-41.67 EUR (V2 lower due to more Typ-6 vs Typ-7 mix)
- Permutation test p=0.591 confirms no significant clustering (nullmodel compliant)
- Updated results/high_win_forensik.json with v1_v2_comparison section
- No OOS 2025 high-win events in current backtest to compare (would require new run)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK_039d_EXECUTOR_20251231_020136.md

PRUEFKRITERIEN (4 Dimensionen):
1. MECHANISCH: Alle Schritte ausgefuehrt? Syntax OK? Acceptance Criteria erfuellt?
2. ARCHITEKTUR: Implementation passt zu ADRs? Keine Widersprueche eingefuehrt?
3. INTEGRATION: ALLE betroffenen Dateien geaendert? (siehe Known Integration Points)
   - hybrid_prediction_engine.py geaendert? -> production_orchestrator.py pruefen!
   - Config geaendert? -> Code der Config liest pruefen!
   - Threshold geaendert? -> Ist er global oder spezifisch?
4. KNOWN BUGS: Keiner der 10 Known Bugs reproduziert? (BUG-001 bis BUG-010)

RED FLAGS (sofort REJECTED):
- Aenderung in Datei A ohne korrespondierende Aenderung in Datei B
- Globale Werte wo spezifische noetig (BUG-001)
- Feature implementiert aber nicht im Orchestrator eingebunden (BUG-003)
- Config-Pfad im Code stimmt nicht mit YAML-Struktur (BUG-002)

OUTPUT TEMPLATE (muss exakt so starten, dann ausfuellen):
---
status: APPROVED
task: TASK_039d
role: PROXY
phase: PROXY_IMPL
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

# Proxy Review (Implementation)

WICHTIG: Erstelle Handoff-Datei mit Ergebnis:
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK_039d_PROXY_IMPL_20251231_020437.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
