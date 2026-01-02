# Reproducibility Commands for Kenobase Results

**Generated:** 2025-12-30
**Total Artifacts:** 92 JSON files in `results/`

This document maps each artifact to its generating script and CLI parameters.

---

## Key Artifacts (High Priority)

### super_model_synthesis.json
```bash
python scripts/super_model_synthesis.py
# Output: results/super_model_synthesis.json
# Description: Combines findings from 3 AI sessions (Jackpot-Warning, Position-Rules, Number-Group-Model)
```

### axiom_validation.json
```bash
python scripts/validate_axiom_predictions.py --all --output results/axiom_validation.json
# Output: results/axiom_validation.json
# Description: Validates Axiom-First predictions (A1-A7) with train/test split
```

### cross_lottery_coupling.json
```bash
python scripts/analyze_cross_lottery_coupling.py --output results/cross_lottery_coupling.json
# Output: results/cross_lottery_coupling.json
# Description: Analyzes coupling between German lottery games (KENO, Lotto, Gluecksspirale)
```

### ecosystem_graph.json
```bash
python scripts/build_ecosystem_graph.py
# Output: results/ecosystem_graph.json
# Description: Builds graph structure of lottery ecosystem relationships
```

### ej_negative_control.json
```bash
python scripts/validate_ej_negative_control.py
# Output: results/ej_negative_control.json
# Description: EuroJackpot negative control (verifies German axioms don't apply)
```

---

## Backtest Artifacts

### cross_game_rule_layer_train_test_backtest.json
```bash
python scripts/backtest_cross_game_rule_layer_train_test.py --train-end 2023-12-31 --output results/cross_game_rule_layer_train_test_backtest.json
# Description: Train/test backtest of cross-game rule layer
```

### cross_game_rule_layer_backtest.json
```bash
python scripts/backtest_cross_game_rule_layer.py
# Output: results/cross_game_rule_layer_backtest.json
```

### position_rule_layer_backtest.json
```bash
python scripts/backtest_position_rule_layer.py
# Output: results/position_rule_layer_backtest.json
```

### position_rule_layer_backtest_*.json (variants)
```bash
# Default
python scripts/backtest_position_rule_layer.py
# With parameters (example for exlb075_ms5):
python scripts/backtest_position_rule_layer.py --excl-lb 0.75 --min-support 5
```

### backtest_3months_2024.json
```bash
python scripts/backtest_3months_2024.py
# Output: results/backtest_3months_2024.json
```

### anti_birthday_backtest.json
```bash
python scripts/backtest_anti_birthday.py
# Output: results/anti_birthday_backtest.json
```

### pair_guarantee_backtest.json
```bash
python scripts/backtest_pair_guarantee.py
# Output: results/pair_guarantee_backtest.json
```

### post_jackpot_backtest.json
```bash
python scripts/backtest_post_jackpot.py
# Output: results/post_jackpot_backtest.json
```

### number_arbitrage_backtest.json
```bash
python scripts/backtest_number_arbitrage.py
# Output: results/number_arbitrage_backtest.json
```

### eurojackpot_backtest.json
```bash
python scripts/backtest_eurojackpot.py
# Output: results/eurojackpot_backtest.json
```

### lotto_backtest.json / lotto_backtest_2018.json
```bash
python scripts/backtest.py --game lotto
# or for specific period:
python scripts/backtest.py --game lotto --start 2018-01-01
```

### dynamic_backtest_2024.json
```bash
python scripts/backtest_dynamic_2024.py
# Output: results/dynamic_backtest_2024.json
```

---

## Hypothesis Analysis Artifacts

### hyp001_distribution_complete.json
```bash
python scripts/analyze_hyp001_complete.py
# Output: results/hyp001_distribution_complete.json
```

### hyp002_gk1_waiting.json / hyp002_validation_test.json
```bash
python scripts/analyze_hyp002.py
# Output: results/hyp002_gk1_waiting.json
```

### hyp003_cluster_reset.json / hyp003_regional_distribution.json
```bash
python scripts/analyze_hyp003.py
python scripts/analyze_hyp003_regional.py
```

### hyp005_decade_affinity.json / hyp005_index_reset.json
```bash
python scripts/analyze_hyp005.py
python scripts/analyze_index_reset.py
```

### hyp007_pattern_validation.json
```bash
python scripts/analyze_hyp007.py
# Output: results/hyp007_pattern_validation.json
```

### hyp008_111_falsification.json / hyp008_111_validation_test.json
```bash
python scripts/falsify_hyp008_111.py
# Output: results/hyp008_111_falsification.json
```

### hyp010_odds_correlation.json
```bash
python scripts/analyze_hyp010.py
# Output: results/hyp010_odds_correlation.json
```

### hyp011_temporal_cycles.json / hyp011_validation_test.json
```bash
python scripts/analyze_hyp011.py
# Output: results/hyp011_temporal_cycles.json
```

### hyp012_stake_correlation.json
```bash
python scripts/analyze_hyp012.py
# Output: results/hyp012_stake_correlation.json
```

### hyp013_overlap_birthday_phase.json
```bash
python scripts/test_hyp013_overlap_birthday_phase.py --draws data/raw/keno/KENO_ab_2022_bereinigt.csv --jackpots data/processed/ecosystem/timeline_2025.csv --output results/hyp013_overlap_birthday_phase.json
# Output: results/hyp013_overlap_birthday_phase.json
# Description: Overlap count and birthday share per phase (PRE/POST/COOLDOWN/NORMAL) with z-tests, KW/MW, Bonferroni+BH
```

### hyp015_jackpot_correlation.json
```bash
python scripts/analyze_hyp015_jackpot.py
# Output: results/hyp015_jackpot_correlation.json
```

---

## Distribution Analysis Artifacts

### distribution_analysis.json
```bash
python scripts/analyze_distribution.py
# Output: results/distribution_analysis.json
```

### dist002_payout_ratio.json
```bash
# Part of house analysis series
python scripts/analyze_house002.py
```

### dist005_synthesis.json
```bash
python scripts/analyze_dist005.py
# Output: results/dist005_synthesis.json
```

---

## House Edge Analysis

### house002_stake_popularity.json
```bash
python scripts/analyze_house002.py
# Output: results/house002_stake_popularity.json
```

### house003_rolling_stability.json
```bash
python scripts/analyze_house003.py
# Output: results/house003_rolling_stability.json
```

### house004_near_miss_jackpot.json
```bash
python scripts/analyze_house004.py
# Output: results/house004_near_miss_jackpot.json
```

### house005_synthesis_report.json
```bash
python scripts/analyze_house005.py
# Output: results/house005_synthesis_report.json
```

---

## Cross-Game Analysis

### cross_game_timing.json
```bash
python scripts/analyze_cross_game_timing.py
# Output: results/cross_game_timing.json
```

### granger_causality_results.json
```bash
# Generated by cross_lottery_coupling analysis
python scripts/analyze_cross_lottery_coupling.py
```

### strategy_from_ecosystem.json
```bash
python scripts/strategy_from_ecosystem.py
# Output: results/strategy_from_ecosystem.json
```

### timeline_grid_summary.json
```bash
python scripts/build_timeline_grid.py
# Output: results/timeline_grid_summary.json
```

---

## Prediction & Model Artifacts

### pred001_pre_gk1_analysis.json
```bash
python scripts/analyze_pred001.py
# Output: results/pred001_pre_gk1_analysis.json
```

### pred002_waiting_time_analysis.json
```bash
python scripts/analyze_pred002.py
# Output: results/pred002_waiting_time_analysis.json
```

### pred003_jackpot_correlation.json
```bash
python scripts/analyze_pred003.py
# Output: results/pred003_jackpot_correlation.json
```

### prediction_synthesis.json
```bash
# Generated by final integrated model
python scripts/final_integrated_model.py
```

### integrated_model_prediction.json
```bash
python scripts/final_integrated_model.py
# Output: results/integrated_model_prediction.json
```

### constraint_model.json
```bash
# Part of analysis pipeline
python scripts/analyze.py --model constraint
```

### creative_patterns.json
```bash
python scripts/creative_pattern_model.py
# Output: results/creative_patterns.json
```

---

## Validation Artifacts

### a6_validation.json
```bash
python scripts/validate_a6_regional.py
# Output: results/a6_validation.json
```

### zehnergruppen_validation.json
```bash
python scripts/validate_zehnergruppen.py
# Output: results/zehnergruppen_validation.json
```

### validation_test.json
```bash
python scripts/validate_hypotheses.py
# Output: results/validation_test.json
```

### test_sum_validation.json
```bash
# Part of sum analysis
python scripts/analyze_dist003_sum.py
```

---

## Pattern & Position Analysis

### position_patterns.json / position_patterns_v2.json
```bash
python scripts/analyze_position_patterns.py
python scripts/analyze_position_patterns_v2.py
```

### position_predictive.json
```bash
python scripts/analyze_position_predictive.py
# Output: results/position_predictive.json
```

### number_pairs_analysis.json
```bash
python scripts/analyze_number_pairs.py
# Output: results/number_pairs_analysis.json
```

### pairs_per_gk_analysis.json
```bash
python scripts/analyze_pairs_per_gk.py
# Output: results/pairs_per_gk_analysis.json
```

### sequence_context_analysis.json
```bash
python scripts/analyze_sequence_context.py
# Output: results/sequence_context_analysis.json
```

### near_miss_numbers.json
```bash
python scripts/analyze_near_miss_numbers.py
# Output: results/near_miss_numbers.json
```

---

## Miscellaneous Artifacts

### summen_signatur_latest.json
```bash
python scripts/compute_summen_signatur.py
# Output: results/summen_signatur_latest.json
```

### alternative_coupling_synthetic.json
```bash
python scripts/analyze_alternative_methods.py
# Output: results/alternative_coupling_synthetic.json
```

### popularity_proxy.json / popularity_reverse_engineering.json
```bash
python scripts/analyze_popularity_proxy.py
python scripts/analyze_popularity.py
```

### payout_inference.json
```bash
python scripts/analyze_payout_inference.py
# Output: results/payout_inference.json
```

### longterm_balance.json
```bash
python scripts/analyze_longterm_balance.py
# Output: results/longterm_balance.json
```

### yearly_segmentation.json
```bash
python scripts/analyze_yearly_segmentation.py
# Output: results/yearly_segmentation.json
```

### regional_affinity.json
```bash
# Generated by regional analysis
python scripts/analyze_hyp003_regional.py
```

### event_correlation.json
```bash
python scripts/analyze_event_correlation.py
# Output: results/event_correlation.json
```

### number_frequency_context.json
```bash
python scripts/analyze_number_frequency.py
# Output: results/number_frequency_context.json
```

### uniqueness_analysis.json
```bash
python scripts/analyze_uniqueness.py
# Output: results/uniqueness_analysis.json
```

### sum_windows_analysis.json
```bash
python scripts/analyze_sum_windows.py
# Output: results/sum_windows_analysis.json
```

---

## Recommendation & Ticket Artifacts

### dynamic_recommendations.json
```bash
python scripts/dynamic_recommendation.py
# Output: results/dynamic_recommendations.json
```

### group_recommendations.json
```bash
python scripts/generate_groups.py
# Output: results/group_recommendations.json
```

### guarantee_recommendations.json
```bash
python scripts/generate_guarantee.py
# Output: results/guarantee_recommendations.json
```

### optimal_tickets_all_types.json
```bash
python scripts/optimize_all_types.py
# Output: results/optimal_tickets_all_types.json
```

### nextday_suggestions_position_rules.json
```bash
python scripts/suggest_tickets_nextday_position_rules.py
# Output: results/nextday_suggestions_position_rules.json
```

### pool_optimization.json
```bash
python scripts/optimize_pool_size.py
# Output: results/pool_optimization.json
```

---

## EuroJackpot Subfolder

### eurojackpot/eurojackpot_analysis.json
```bash
python scripts/analyze_eurojackpot.py
# Output: results/eurojackpot/eurojackpot_analysis.json
```

### eurojackpot/eurojackpot_backtest.json
```bash
python scripts/backtest_eurojackpot.py
# Output: results/eurojackpot/eurojackpot_backtest.json
```

---

## Validation Commands

To validate all JSON artifacts are valid:
```bash
for f in results/*.json; do python -c "import json; json.load(open('$f'))" && echo "OK: $f"; done
```

PowerShell variant:
```powershell
Get-ChildItem results/*.json | ForEach-Object {
    try {
        $null = Get-Content $_.FullName | ConvertFrom-Json
        Write-Host "OK: $($_.Name)"
    } catch {
        Write-Host "INVALID: $($_.Name)" -ForegroundColor Red
    }
}
```

---

## Notes

1. All scripts assume execution from repository root (`C:\Users\kenfu\Documents\keno_base`)
2. Some artifacts may have been generated with older script versions
3. Default config is loaded from `config/default.yaml`
4. Data files are expected in `data/` directory
