# Agent Guide — `keno_base` (Kenobase V2)

Kurzleitfaden, um in diesem Ordner schnell produktiv zu werden (Navigation, Entry-Points, Runs/Tests, Stolperfallen).

## 1) Erste Orientierung

- `CLAUDE.md`: Arbeits-/Umsetzungsleitfaden (LOOP v4 Quick Start, Backlog-Workflow).
- `README.md`: Quickstart + CLI-Referenz.
- `AI_COLLABORATION/ARCHITECTURE/MODULE_MAP.md`: Architektur-/Modulkarte.
- `AI_COLLABORATION/BACKLOG/KENOBASE_ISSUES.md`: priorisierte Issues + Acceptance Criteria.
- `AI_COLLABORATION/SYSTEM_STATUS.md`: aktueller Stand (inkl. Phase-4 Korrekturen).

## 2) Quickstart (Windows / PowerShell)

```powershell
cd C:\Users\kenfu\Documents\keno_base

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

pytest -q
```

## 3) Wichtige Datenquellen

- Ziehungen: `data/raw/keno/KENO_ab_2018.csv` (2018-2024, 2237 Ziehungen)
- Gewinnquoten (feste Quoten pro 1 EUR): `Keno_GPTs/Keno_GQ_2022_2023-2024.csv` (2022-2024)
- GK1 Events: `Keno_GPTs/10-9_KGDaten_gefiltert.csv`

## 4) Kritische Stolperfallen (sehr wichtig)

- **Quoten/Paytable:** Single source of truth ist `kenobase/core/keno_quotes.py`.
  - Wenn irgendwo ROI positiv wird: zuerst prüfen ob eine falsche Quoten-Tabelle hardcoded wurde.
- **Parsing:** GQ-Daten haben Mixed-Formats (z.B. `275.0`, `3.462`, `2.91`).
  - Nutze `kenobase/core/parsing.py` (`parse_int_mixed_german`, `parse_float_mixed_german`), nicht "Punkte entfernen" als pauschale Regel.

## 5) Phase-4 Entry Points (WL-00x)

- WL-001 / WL-007 (Paar-Garantie + GK-spezifische Paare):
  - `python scripts/analyze_pairs_per_gk.py`
- WL-005 (Paar-Gewinn-Frequenz; ROI ist bei korrekten Quoten negativ):
  - `python scripts/backtest_pair_guarantee.py`
- WL-006 (Jackpot-Uniqueness):
  - `python scripts/analyze_uniqueness.py`
- Empfehlungen/Export (zieht Backtest + Quoten zusammen):
  - `python scripts/generate_guarantee.py`

## 6) Near-Miss / Distribution Checks

- HOUSE-004 (Near-Miss Ratio):
  - `python scripts/analyze_house004.py --gq-file "Keno_GPTs/Keno_GQ_2022_2023-2024.csv"`
- DIST-003 (Summen-Verteilung):
  - `python scripts/analyze_dist003_sum.py --data "data/raw/keno/KENO_ab_2018.csv" --bin-width 20`

## 7) Ticket-Suggester / Walk-Forward Backtests

- Ticket-Vorschlaege (Typ 6-9):
  - `python scripts/suggest_tickets.py --types 6 7 8 9`
- Walk-Forward Backtest (ohne Lookahead):
  - `python scripts/backtest_tickets.py --types 6 7 8 9 --start-index 365`

## 8) Dev-Standards (kurz)

- Lint/Format: `ruff check .`, `black .` (line length 100)
- Tests: `pytest` (schnell: `pytest tests/unit -q`)
- Artefakte: Output nach `results/` oder `output/` (keine grossen Dumps versehentlich commiten)

## 9) LOOP v4 (optional)

```powershell
.\scripts\autonomous_loop_v4.ps1 -Team alpha -PlanFile "AI_COLLABORATION/PLANS/kenobase_v2_complete_plan.yaml"
```

