AUTONOMOUS LOOP V4 - Plan-Based Execution (Token Hygiene Enabled)
==================================================================
TASK: Telegram/Discord Bot
TASK-ID: TASK-P13
PRIORITY: LOW
PHASE: PROXY_PLAN

TASK DESCRIPTION (Plan excerpt, kurz):


TASK NOTES (kurz, autoritativ):
## [2025-12-28 08:57:43] TASK-P13 - ARCHITECT (ki1)

### Summary
- Telegram/Discord Bot fuer Kenobase Prediction-Output
- Nutzt bestehende predict.py und HypothesisSynthesizer
- Zwei Bot-Varianten: telegram_bot.py + discord_bot.py
- Gemeinsamer Bot-Core in kenobase/bot/core.py
- Konfig-Erweiterung in config/default.yaml unter 'bot:
- Keine DB erforderlich - nutzt results/ JSON-Dateien direkt
- Rate-Limiting und Error-Handling eingebaut
- Daily-Cron optional via Schedule-Library

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK-P13_ARCHITECT_20251228_085443.md

## [2025-12-28 08:59:44] TASK-P13 - PROXY_PLAN (ki0)

### Summary (fallback)
- Handoff erfolgreich erstellt. Hier die Zusammenfassung:    ---    **PROXY REVIEW COMPLETE**    ```  status: REJECTED  task: TASK-P13  role: PROXY  phase: PROXY_PLAN  reviewed_handoff: ki1_TASK-P13_ARCHITECT_20251228_085443.md  ```    **Befund:** Plan ist unvollständig und nicht e ...

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_TASK-P13_PROXY_PLAN_20251228_085743.md

## [2025-12-28 09:05:44] TASK-P13 - ARCHITECT (ki1)

### Summary (fallback)
- Handoff erfolgreich erstellt. Hier die Zusammenfassung:    ---    **ARCHITECT PHASE COMPLETE**    ```  status: COMPLETE  task: TASK-P13  role: ARCHITECT  phase: ARCHITECT  ```    **Handoff erstellt:**  `AI_COLLABORATION/HANDOFFS/ki1_TASK-P13_ARCHITECT_20251228_085944.md`    **Beh ...

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK-P13_ARCHITECT_20251228_085944.md



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
- AI_COLLABORATION/HANDOFFS/ki1_TASK-P13_ARCHITECT_20251228_085443.md

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
Handoff erfolgreich erstellt. Hier die Zusammenfassung:

---

**ARCHITECT PHASE COMPLETE**

```
status: COMPLETE
task: TASK-P13
role: ARCHITECT
phase: ARCHITECT
```

**Handoff erstellt:**
`AI_COLLABORATION/HANDOFFS/ki1_TASK-P13_ARCHITECT_20251228_085944.md`

**Behobene PROXY-Kritikpunkte aus vorherigem Durchlauf:**

1. **Detaillierte Dateistruktur:** 8 Dateien mit vollstaendiger Spezifikation
2. **Config-Schema:** `bot:` Section mit telegram/discord/daily_push/rate_limit
3. **Dependencies mit Versionen:** python-telegram-bot>=21.0, discord.py>=2.3.0, schedule>=1.2.0
4. **Messbare Acceptance Criteria:** 4 Kriterien (Response Time <3s, Error Rate <1%, Cache Hit >80%, Coverage >=80%)
5. **API-Design:** BotCore.get_prediction() returns PredictionResult dataclass

**Implementierungs-Checkliste (4 Phasen, 7h):**
- Phase 1: Bot-Modul (kenobase/bot/) - 2h
- Phase 2: Telegram Bot - 2h
- Phase 3: Discord Bot - 1.5h
- Phase 4: Config + Integration - 1.5h

**Next:** PROXY validiert Plan, dann EXECUTOR implementiert


FULL HANDOFF (nur bei Bedarf oeffnen):
C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki1_TASK-P13_ARCHITECT_20251228_085944.md

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
task: TASK-P13
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
- Datei: AI_COLLABORATION/HANDOFFS/ki0_TASK-P13_PROXY_PLAN_20251228_090544.md
- YAML Frontmatter mit status:
  - APPROVED: Plan ist gut, weiter zu Executor
  - REJECTED: Bug gefunden, zurueck zu Architect
  - ESCALATE: User-Entscheidung noetig (Architektur-Frage, Design-Wahl)
- Bei ESCALATE: PROBLEM, OPTIONEN, EMPFEHLUNG angeben
- Kurze Begruendung (max 8 bullets)
