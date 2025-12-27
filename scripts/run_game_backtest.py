#!/usr/bin/env python3
"""Run backtest for specific game with game-specific thresholds."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from kenobase.core.config import load_config
from kenobase.core.data_loader import DataLoader
from backtest import BacktestEngine

def run_backtest(game_name: str, data_file: str):
    # Load config and set game
    cfg = load_config("config/default.yaml")
    cfg.active_game = game_name

    game = cfg.get_active_game()
    print(f"=== {game.name} Backtest (Game-Specific Thresholds) ===")
    print(f"Hot threshold: {game.get_hot_threshold():.4f}")
    print(f"Cold threshold: {game.get_cold_threshold():.4f}")
    print()

    # Load data
    loader = DataLoader()
    draws = loader.load(data_file)
    print(f"Loaded {len(draws)} draws")

    # Run backtest
    engine = BacktestEngine(cfg)
    result = engine.run(draws, n_periods=12, train_ratio=0.8)

    # Print results
    print(f"\n=== Summary ===")
    print(f"Avg F1-Score:     {result.summary['avg_f1']:.4f}")
    print(f"Avg Precision:    {result.summary['avg_precision']:.4f}")
    print(f"Avg Recall:       {result.summary['avg_recall']:.4f}")
    print(f"Avg Stability:    {result.summary['avg_stability']*100:.1f}%")
    print(f"Critical Periods: {result.summary['critical_periods']}/{result.n_periods}")
    print(f"Best Period:      #{result.summary['best_period']} (F1={result.summary['best_f1']:.4f})")

    print(f"\nPeriod Details:")
    for r in result.period_results:
        status = "CRITICAL" if r.criticality_level == "CRITICAL" else "OK"
        print(f"  P{r.period_id:2d}: {len(r.predicted_hot):2d} hot, {r.total_hits:3d} hits, F1={r.f1_score:.4f} [{status}]")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python run_game_backtest.py <game_name> <data_file>")
        sys.exit(1)

    run_backtest(sys.argv[1], sys.argv[2])
