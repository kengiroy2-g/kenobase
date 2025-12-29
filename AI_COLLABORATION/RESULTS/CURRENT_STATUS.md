# CURRENT_STATUS (Kenobase)

## 2025-12-28

### Repo-Review + Agent-Guide

- Ergebnis: `Agent.md` erstellt (Navigation + Run/Tests + Stolperfallen).
- Beobachtung: Sehr viele Dateien im Workspace (u.a. `AI_COLLABORATION/`, `.git/`, `.mypy_cache/`, große Legacy-Daten unter `Keno_GPTs/`). Aktiver Codepfad ist primär `kenobase/` + `scripts/` + `config/` + `tests/`.

**Wichtige Kommandos (Repro / Navigation):**

- Inventar: `Get-ChildItem -Recurse -File | Measure-Object` (Filecount) + Grouping nach Extensions/Top-Dirs
- Doku: `Get-Content CLAUDE.md`, `Get-Content README.md`
- Code-Index (Module/Docstrings): Python AST-Summarizer über `kenobase/**/*.py` und `scripts/**/*.py`

## 2025-12-29

### DIST-003 Null-Model Fix + Run

- Fix: `kenobase/analysis/dist003_sum_null_model.py` nutzt jetzt den vollen theoretischen Summen-Support (statt nur observed min/max), merged Low-Expected-Bins (>=5) und normalisiert Expected-Counts so, dass `scipy.stats.chisquare` nicht mehr wegen Sum-Mismatch abbricht.
- Run: `python scripts/analyze_dist003_sum.py`
  - Ergebnis: `draws=2237`, `expected mean/std=710.00/76.92`, `chi2=15.06`, `dof=21`, `p=0.819705` (kein Hinweis auf Abweichung vom korrekten Nullmodell).
- Tests: `pytest -q` -> `1072 passed` (Warnings: LightGBM/SHAP/Scipy precision, unverändert).

### Ticket-Suggester (Typ 6-9)

- Neu: `kenobase/prediction/ticket_suggester.py` + CLI `scripts/suggest_tickets.py` (gewichtete Frequenz, liefert Vorschlaege fuer KENO-Typ 6-9).
- Run: `python scripts/suggest_tickets.py` (Standard: recent=365, weight=0.6).
- Tests: `pytest -q` -> `1074 passed`.

### Ticket-Backtest (Walk-Forward)

- Neu: `kenobase/prediction/ticket_backtester.py` + CLI `scripts/backtest_tickets.py`.
- Run: `python scripts/backtest_tickets.py` auf `data/raw/keno/KENO_ab_2018.csv` (start_index=365, recent=365, weight=0.6):
  - Typ 6: mean hits 1.7131 (exp 1.7143), Near-Miss 9/1872 (exp 11.07), Jackpot 0/1872 (exp 0.55)
  - Typ 7: mean hits 2.0005 (exp 2.0000), Near-Miss 2/1872 (exp 3.03), Jackpot 0/1872 (exp 0.12)
  - Typ 8: mean hits 2.2981 (exp 2.2857), Near-Miss 1/1872 (exp 0.77), Jackpot 0/1872 (exp 0.02)
  - Typ 9: mean hits 2.5833 (exp 2.5714), Near-Miss 0/1872 (exp 0.18), Jackpot 0/1872 (exp ~0.00)

### Phase 4: Quoten-Fix (ROI-Korrektur) + Re-Backtest

- Problem: Einige Phase-4 Skripte hatten eine falsche hardcoded Quoten-Tabelle (`KENO_QUOTES`) und lieferten dadurch scheinbar positive ROI (z.B. Typ-8/10).
- Fix:
  - Single source of truth: `kenobase/core/keno_quotes.py` (aus `Keno_GPTs/Keno_GQ_2022_2023-2024.csv` abgeleitet).
  - `kenobase/analysis/payout_inference.py` nutzt jetzt diese Quoten via Import (API `EXPECTED_ODDS` bleibt stabil).
  - Phase-4 Skripte nutzen `get_fixed_quote()` statt eigener Tabellen:
    - `scripts/backtest_pair_guarantee.py`
    - `scripts/optimize_all_types.py`
    - `scripts/generate_guarantee.py`
- Runs:
  - `python scripts/backtest_pair_guarantee.py`
    - Typ-10 (bestes Ticket): ROI -47.97% (Return 0.52 EUR / 1 EUR)
    - Typ-8 (bestes Ticket): ROI -61.20% (Return 0.39 EUR / 1 EUR)
    - Ergebnis: `results/pair_guarantee_backtest.json`
  - `python scripts/generate_guarantee.py`
    - Theoretischer EV (fixed quotes): Typ-10 E[Return] ~0.494 EUR (E[ROI] ~ -50.6%)
    - Ergebnis: `results/guarantee_recommendations.json`
- Docs aktualisiert:
  - `AI_COLLABORATION/SYSTEM_STATUS.md` (Profit-Claims entfernt, Zahlen korrigiert)
  - `AI_COLLABORATION/KNOWLEDGE_BASE/HYPOTHESES_CATALOG.md` (WL-005: Gewinnfrequenz ja, ROI negativ)
  - `Agent.md` (Runbook + Stolperfallen aktualisiert)
- Tests: `pytest -q` -> `1074 passed`

### Position-Rule-Layer (Next-Day Exclusion/Inclusion) + Walk-Forward Backtest

- Ziel: Trigger `Zahl@Position (heute)` -> `Exclude/Include Zahlen (morgen)` als Layer auf dem Ranking-Modell (ohne Lookahead).
- Fix/Erweiterung:
  - `kenobase/core/data_loader.py`: speichert Original-Ziehungsreihenfolge in `metadata["numbers_ordered"]` (DrawResult.numbers bleibt sortiert).
  - `kenobase/prediction/position_rule_layer.py`: Rolling Miner + Wilson-LB Scoring + Score-Adjustment Layer.
  - `kenobase/prediction/position_rule_backtester.py`: Walk-forward Next-Day Backtest (Baseline vs +Rules).
  - CLI:
    - `python scripts/backtest_position_rule_layer.py`
    - `python scripts/suggest_tickets_nextday_position_rules.py`
- Runs:
  - `pytest -q` -> `1078 passed`
  - Default Backtest (konservativ, wenige Rules):
    - `python scripts/backtest_position_rule_layer.py --output results/position_rule_layer_backtest_default.json`
    - Ergebnis: Exclusion = keine Rules gefeuert (Thresholds zu streng), Inclusion ~24.05% (baseline 28.57%).
  - Beispiel-Konfig mit langen Fenstern (mehr Support):
    - `python scripts/backtest_position_rule_layer.py --rule-window 2000 --rule-min-support 5 --exclude-lb 0.85 --include-lb 0.35 --output results/position_rule_layer_backtest_w2000_exlb085.json`
    - Ergebnis (indicative): Exclusion ~72.60% (baseline 71.43%), Inclusion ~28.76% (baseline 28.57%), kleine mean-hits Deltas (nicht klar signifikant).
  - Next-Day Suggestion (praktischer Daily-Use):
    - `python scripts/suggest_tickets_nextday_position_rules.py --rule-window 2000 --rule-min-support 5 --exclude-lb 0.85 --include-lb 0.35 --output results/nextday_suggestions_position_rules.json`
    - Ergebnis: gibt fired rules + empfohlene Tickets (Typ 6-10) aus.
