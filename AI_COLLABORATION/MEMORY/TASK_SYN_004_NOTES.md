## [2026-01-01 07:28:01] SYN_004 - ARCHITECT (ki5)

### Summary
- Task: Test Payout-Correlation Rule (7d after high payout >= 400 EUR)
- Axiom: A7 Reset-Cycles - system may "save" after large payouts
- Existing artifacts: high_payout_backtest_2018_2024.json contains 15 high-payout events with dates
- Hypothesis: ROI in 7 days after high payout differs from baseline
- Approach: Tag draws by "days_since_last_high_payout" and compare ROI windows
- Train/Test split required: 2018-2024 Train, 2025 OOS Test
- Null model: Permutation of high-payout dates (block-preserving)

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki5_SYN_004_ARCHITECT_20260101_072501.md

## [2026-01-01 07:59:02] SYN_004 - PROXY_PLAN (ki0)

### Summary
- Plan tests Axiom A7 (Reset-Cycles): ROI in 7d window after high payout >= 400 EUR
- Artifact exists: results/high_payout_backtest_2018_2024.json (2237 draws, 48 tickets, 15 high-payout events)
- High-payout events from artifact: 2018-05-12 through 2023-10-10 (sparse, ~2-3/year)
- Train/Test split correctly specified: 2018-2024 Train, 2025 OOS
- Null model: block-preserving permutation of high-payout dates (correct approach)
- CLARIFICATION: high-payout events are ticket-level in artifact; plan must aggregate to get global event dates
- Repro commands well-defined; output paths specified
- Acceptance criteria implicit: effect size + p-value needed

### Handoff
- File: C:\Users\kenfu\Documents\keno_base\AI_COLLABORATION\HANDOFFS\ki0_SYN_004_PROXY_PLAN_20260101_072801.md

