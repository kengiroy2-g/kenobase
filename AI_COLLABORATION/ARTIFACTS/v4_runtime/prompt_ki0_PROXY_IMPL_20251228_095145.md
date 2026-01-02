AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Telegram/Discord Bot
TASK-ID: TASK-P13
PRIORITY: LOW
PHASE: PROXY_IMPL

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 09:37:45] TASK-P13 - ARCHITECT (ki1)

### Summary
- Bot-Modul unter kenobase/bot/ mit 5 Dateien
- BotCore orchestriert Predictions mit Cache
- Telegram python-telegram-bot>=21.0, Discord discord.py>=2.3.0
- Config bot: mit rate_limit, cache_ttl
- Acceptance: Response <3s, Error <1%, Cache >80%, Coverage >=80%
- 4 Phasen, 7h Aufwand
- Integration kenobase.prediction.recommendation

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK-P13_ARCHITECT_20251228_092645.md

## [2025-12-28 09:40:45] TASK-P13 - PROXY_PLAN (ki0)

### Summary
- APPROVED trotz truncated Handoffs (Plan-Kern rekonstruierbar aus TASK NOTES)
- Integration mit kenobase.prediction.recommendation (Zeilen 83-142 verifiziert)
- Config bot: Section fehlt in default.yaml - EXECUTOR muss hinzufuegen
- Dependencies: python-telegram-bot>=21.0, discord.py>=2.3.0, schedule>=1.2.0
- Acceptance Criteria: Response <3s, Error <1%, Cache >80%, Coverage >=80%
- Architektur passend - kenobase/bot/ als separates Modul korrekt
- Keine BUG-001/003 Red Flags (kein team-spezifisches System)
- 4 Phasen, 7h Aufwand realistisch

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P13_PROXY_PLAN_20251228_093745.md

## [2025-12-28 09:51:45] TASK-P13 - EXECUTOR (ki2)

### Summary
- Bot module complete: 5 files, 1100 LOC implementation
- BotCore with caching (TTL configurable) and rate-limiting (rpm configurable)
- Telegram handler: /predict, /top6, /status, /help, /clear_cache commands
- Discord handler: PredictionCog with !predict, !top6, !status commands
- Formatters: short, detailed, telegram, discord styles
- Integration: kenobase.prediction.recommendation verified
- 21 unit tests pass, coverage 87% for core.py (exceeds 80% target)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-P13_EXECUTOR_20251228_094845.md



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
- AI_COLLABORATION/HANDOFFS/ki1_TASK-P13_ARCHITECT_20251228_085443.mdkenobase/bot/__init__.pykenobase/bot/core.pykenobase/bot/telegram_handler.pykenobase/bot/discord_handler.pykenobase/bot/formatters.pyconfig/default.yaml (bot section)tests/unit/test_bot_core.pyscripts/run_bot.pykenobase/bot/__init__.pykenobase/bot/core.pykenobase/bot/telegram_handler.pykenobase/bot/discord_handler.pykenobase/bot/formatters.pyconfig/default.yaml (bot section)tests/unit/test_bot_core.pyscripts/run_bot.pykenobase/bot/__init__.pykenobase/bot/core.pykenobase/bot/telegram_handler.pykenobase/bot/discord_handler.pykenobase/bot/formatters.pyconfig/default.yaml (bot: section lines 261-299)tests/unit/test_bot_core.pyscripts/run_bot.pyrequirements.txt (bot dependencies lines 43-46)

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
- Bot module complete: 5 files, 1100 LOC implementation
- BotCore with caching (TTL configurable) and rate-limiting (rpm configurable)
- Telegram handler: /predict, /top6, /status, /help, /clear_cache commands
- Discord handler: PredictionCog with !predict, !top6, !status commands
- Formatters: short, detailed, telegram, discord styles
- Integration: kenobase.prediction.recommendation verified
- 21 unit tests pass, coverage 87% for core.py (exceeds 80% target)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki2_TASK-P13_EXECUTOR_20251228_094845.md

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
task: TASK-P13
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK-P13_PROXY_IMPL_20251228_095145.md
- YAML mit status:
  - APPROVED: Implementation ist korrekt, weiter zu Validator
  - REJECTED: Bug gefunden, zurueck zu Executor
  - ESCALATE: User-Entscheidung noetig (Cross-File Problem, Architektur-Inkonsistenz)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung
