AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Telegram/Discord Bot
TASK-ID: TASK-P13
PRIORITY: LOW
PHASE: VALIDATOR

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
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

## [2025-12-28 09:54:45] TASK-P13 - PROXY_IMPL (ki0)

### Summary
- Bot module complete: 5 files (core.py, formatters.py, telegram_handler.py, discord_handler.py, __init__.py)
- BotCore with caching (TTL via bot.cache.ttl_seconds) and rate-limiting (bot.rate_limit.requests_per_minute)
- Integration with kenobase.prediction.recommendation verified (generate_recommendations, recommendations_to_dict)
- Config bot: section in default.yaml (lines 261-299) with proper structure
- Dependencies in requirements.txt (lines 43-46): python-telegram-bot>=21.0, discord.py>=2.3.0, schedule>=1.2.0
- 21 unit tests pass, all syntax checks pass
- scripts/run_bot.py provides CLI entry point with --platform telegram|discord|both
- No Known Bug patterns detected (BUG-001 to BUG-010 not applicable)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P13_PROXY_IMPL_20251228_095145.md




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
ROLLE: VALIDATOR
AUFGABE: Validiere die Implementation.

EFFIZIENZ-REGELN:
- Tests nur zielgerichtet (klein starten). Keine riesigen Logs in die Antwort; speichere nach AI_COLLABORATION/ARTIFACTS/ und verlinke.
- Vermeide Repo-weite Scans; nutze WORKING SET + gezielte Reads.

VORHERIGER OUTPUT (kurz):
- Bot module complete: 5 files (core.py, formatters.py, telegram_handler.py, discord_handler.py, __init__.py)
- BotCore with caching (TTL via bot.cache.ttl_seconds) and rate-limiting (bot.rate_limit.requests_per_minute)
- Integration with kenobase.prediction.recommendation verified (generate_recommendations, recommendations_to_dict)
- Config bot: section in default.yaml (lines 261-299) with proper structure
- Dependencies in requirements.txt (lines 43-46): python-telegram-bot>=21.0, discord.py>=2.3.0, schedule>=1.2.0
- 21 unit tests pass, all syntax checks pass
- scripts/run_bot.py provides CLI entry point with --platform telegram|discord|both
- No Known Bug patterns detected (BUG-001 to BUG-010 not applicable)

FULL HANDOFF:
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P13_PROXY_IMPL_20251228_095145.md

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
task: TASK-P13
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
- Datei: AI_COLLABORATION/HANDOFFS/ki3_TASK-P13_VALIDATOR_20251228_095445.md
- YAML mit status: APPROVED oder REJECTED
- Test-Ergebnisse (kurz)
