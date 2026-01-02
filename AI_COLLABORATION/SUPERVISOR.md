# Kenobase V2.0 - Supervisor Guide

## Verfuegbare Scripts

| Script | Beschreibung |
|--------|--------------|
| `autonomous_loop_v4.ps1` | Haupt-Loop Engine |
| `supervisor_agent.ps1` | Supervisor fuer Monitoring |
| `v4_monitor.ps1` | Live-Status Monitor |
| `send_message.ps1` | Nachrichten senden |
| `read_inbox.ps1` | Inbox lesen |
| `check_task_status.ps1` | Task-Status pruefen |
| `start_external_task.ps1` | Externe Tasks starten |
| `check_resources.ps1` | RAM/CPU pruefen |
| `task_wrapper.ps1` | Task-Wrapper mit Heartbeat |
| `dry_run_check.ps1` | Befehl validieren |

## Loop V4 Quick Start

```powershell
# Standard-Start (Alpha Team, alle Claude)
.\scripts\autonomous_loop_v4.ps1 `
  -Team alpha `
  -PlanFile "AI_COLLABORATION/PLANS/kenobase_v2_complete_plan.yaml"

# Mit Codex Backend
.\scripts\autonomous_loop_v4.ps1 `
  -Team alpha `
  -PlanFile "AI_COLLABORATION/PLANS/kenobase_v2_complete_plan.yaml" `
  -KiBackends "ki0=claude,ki1=codex,ki2=codex,ki3=codex"

# Schneller Modus (ohne Proxy)
.\scripts\autonomous_loop_v4.ps1 `
  -Team alpha `
  -PlanFile "AI_COLLABORATION/PLANS/kenobase_v2_complete_plan.yaml" `
  -SkipProxy
```

## Phase Workflow

```
PENDING -> ARCHITECT (KI #1) -> PROXY_PLAN (KI #0)
        -> EXECUTOR (KI #2) -> PROXY_IMPL (KI #0)
        -> VALIDATOR (KI #3) -> PROXY_FINAL (KI #0)
        -> COMPLETE
```

## Task-Status Werte

| Status | Bedeutung |
|--------|-----------|
| PENDING | Task wartet auf Bearbeitung |
| IN_PROGRESS | Task wird bearbeitet |
| COMPLETE | Task erfolgreich abgeschlossen |
| BLOCKED | Task blockiert (manuell loesen) |

## Logs und Outputs

- **Main Log**: `AI_COLLABORATION/LOGS/loop_v4.log`
- **Handoffs**: `AI_COLLABORATION/HANDOFFS/`
- **Metriken**: `AI_COLLABORATION/METRICS/`
- **Artifacts**: `AI_COLLABORATION/ARTIFACTS/`

## Projekt-Kontext

### Alte Module (migrieren)

| Datei | Zweck | Prioritaet |
|-------|-------|------------|
| `00_KENO_ALL_V5.py` | Hauptanalyse KENO | P0 |
| `00_0_Keno_6-Kombi_Analyse_V9.py` | 6er-Kombis | P0 |
| `00_DataAnalyse_EJ_v5.py` | EuroJackpot Duos/Trios | P1 |
| `00_EJ_check_v12_149.py` | Archiv-Pruefung | P1 |
| `00_Iteration111_V5.py` | 111-Prinzip | P2 |

### Datenquellen

| Datei | Inhalt |
|-------|--------|
| `Keno_GPTs/KENO_ab_2018*.csv` | KENO Ziehungen |
| `Keno_GPTs/eurojackpot_archiv*.csv` | EuroJackpot |
| `Keno_GPTs/Lotto_archiv*.csv` | Lotto 6aus49 |
| `Keno_GPTs/Daten/*.csv` | Gewinnquoten |

### Physik-Konzepte (aus v_master_Criticality)

| Konzept | ADR | Anwendung |
|---------|-----|-----------|
| Model Law A | ADR-018 | Stabilitaetstest fuer Muster |
| Model Law B | ADR-018 | Least-Action Pipeline-Auswahl |
| Model Law C | ADR-018/020 | Criticality-Score |
| Avalanche | ADR-021 | Anti-Avalanche Strategie |

## Troubleshooting

### Loop startet nicht
```powershell
# Lock-Datei loeschen
Remove-Item AI_COLLABORATION/MESSAGE_QUEUE/loop_v4.lock.json -Force
```

### Task haengt
1. Pruefe `AI_COLLABORATION/HANDOFFS/` fuer letzten Handoff
2. Pruefe `AI_COLLABORATION/LOGS/loop_v4.log`
3. Manuell Status in YAML-Plan setzen

### Rate Limit
- Loop erkennt 429 automatisch
- Wartet auf Retry-Window
- Backend-Wechsel wenn konfiguriert
