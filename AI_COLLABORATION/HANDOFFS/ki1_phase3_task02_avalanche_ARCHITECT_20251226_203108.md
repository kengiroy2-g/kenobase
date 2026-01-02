---
status: COMPLETE
task: phase3_task02_avalanche
role: ARCHITECT
phase: ARCHITECT
files_changed: []
summary:
  - Avalanche module already fully implemented at kenobase/physics/avalanche.py (229 lines)
  - All 8 functions present: calculate_theta, get_avalanche_state, is_profitable, calculate_expected_value, analyze_combination, max_picks_for_theta, get_avalanche_state_with_thresholds
  - AvalancheState enum (SAFE/MODERATE/WARNING/CRITICAL) and AvalancheResult NamedTuple defined
  - Tests exist at tests/unit/test_avalanche.py with 28 tests (all passing)
  - Test coverage at 90% (62 statements, 6 missing - edge cases in threshold func and max_picks)
  - Module exported via kenobase/physics/__init__.py
  - Config integration present in config/default.yaml (enable_avalanche, anti_avalanche_mode)
---
# Rule Confirmation
- Rule 1 (SYSTEM_STATUS + ADR/Docs + git status): UNVERIFIED (no git repo, no SYSTEM_STATUS.json exists)
- Rule 2 (granularity stated): per-combination
- Rule 3 (semantics defined): theta=loss_probability, state=SAFE/MODERATE/WARNING/CRITICAL, is_safe_to_bet=boolean
- Rule 4 (target metric): risk-classification
- Rule 5 (helper-only boundaries): CONFIRMED
- Rule 6 (reproducibility): pytest tests/unit/test_avalanche.py -v -> 28 passed

## Task Setup
- Granularity: per-combination (theta calculated for each combination of n picks at precision p)
- Semantics: theta = 1 - p^n (loss probability), AvalancheState = risk tier, is_profitable = p*q > 1
- Target metric: risk-classification for bet-selection

## Repro Commands
- `pytest tests/unit/test_avalanche.py -v` -> 28 passed
- `pytest tests/unit/test_avalanche.py --cov=kenobase.physics.avalanche --cov-report=term-missing` -> 90% coverage

# Implementierungsplan

## Status: ALREADY COMPLETE

The task P3-02 (Avalanche-Theorie implementieren) is **already fully implemented**. No additional work required.

### Existing Implementation

**File:** `kenobase/physics/avalanche.py` (229 lines)

#### Functions Implemented:
1. `calculate_theta(precision, n_picks)` - Core theta formula: 1 - p^n
2. `get_avalanche_state(theta)` - Default threshold state classification
3. `get_avalanche_state_with_thresholds(theta, ...)` - Configurable thresholds
4. `is_profitable(precision, avg_odds)` - Fundamental theorem: p*q > 1
5. `calculate_expected_value(precision, avg_odds, stake)` - EV calculation
6. `analyze_combination(precision, n_picks, avg_odds)` - Full analysis returning AvalancheResult
7. `max_picks_for_theta(precision, max_theta)` - Anti-avalanche strategy

#### Types Defined:
- `AvalancheState(str, Enum)`: SAFE, MODERATE, WARNING, CRITICAL
- `AvalancheResult(NamedTuple)`: theta, state, is_safe_to_bet
- `THETA_SAFE = 0.50`, `THETA_MODERATE = 0.75`, `THETA_WARNING = 0.85`

### Test Coverage

**File:** `tests/unit/test_avalanche.py` (224 lines)

| Test Class | Tests | Status |
|------------|-------|--------|
| TestCalculateTheta | 6 | PASS |
| TestGetAvalancheState | 5 | PASS |
| TestGetAvalancheStateWithThresholds | 2 | PASS |
| TestIsProfitable | 4 | PASS |
| TestCalculateExpectedValue | 3 | PASS |
| TestAnalyzeCombination | 2 | PASS |
| TestMaxPicksForTheta | 4 | PASS |
| TestAvalancheStateEnum | 2 | PASS |
| **Total** | **28** | **ALL PASS** |

Coverage: 90% (lines 110-113, 197, 199, 210 not covered - rare edge cases)

### Config Integration

**File:** `config/default.yaml` (lines 42-44)
```yaml
physics:
  enable_avalanche: true
  anti_avalanche_mode: true
```

### Module Export

**File:** `kenobase/physics/__init__.py` exports all avalanche functions.

## Recommendation

**SKIP TO NEXT TASK** - P3-02 is complete. Proceed to P3-03 (metrics.py) or P3-04 (integration).

## Acceptance Criteria Verification

| Criterion | Status | Evidence |
|-----------|--------|----------|
| theta = 1 - p^n correct | PASS | test_theta_formula, test_six_picks_at_70_percent |
| States SAFE/MODERATE/WARNING/CRITICAL | PASS | TestGetAvalancheState (5 tests) |
| is_profitable() function | PASS | TestIsProfitable (4 tests) |
| Integration in config | PASS | config/default.yaml lines 42-44 |
| Unit tests | PASS | 28 tests, 90% coverage |
