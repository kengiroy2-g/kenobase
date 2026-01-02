# KENO ROI Validation Report
**Generated:** 2025-12-28 18:28
**Task:** QUOTE-001
**Validator:** ki3

## Executive Summary

**STATUS: REJECTED**

The document `docs/keno_quotes.md` contains **CRITICAL calculation errors** in ROI/probability values for 8 of 9 KENO types. Only Type 10 values are correct.

## Validation Method

Formula verified (Line 34):
```
P(k Treffer bei Typ n) = C(n, k) * C(70-n, 20-k) / C(70, 20)
```
**Formula is CORRECT** - the issue is that probability and ROI values in tables were miscalculated.

## Correct ROI Values

| Type | Doc ROI | Correct ROI | Error | Status |
|------|---------|-------------|-------|--------|
| 10 | 49.66% | 49.40% | -0.26pp | **PASS** |
| 9 | 56.41% | 50.05% | -6.36pp | **FAIL** |
| 8 | 21.31% | 43.25% | +21.94pp | **FAIL** |
| 7 | 25.66% | 49.57% | +23.91pp | **FAIL** |
| 6 | 29.80% | 49.74% | +19.94pp | **FAIL** |
| 5 | 31.70% | 49.90% | +18.20pp | **FAIL** |
| 4 | 36.67% | 49.44% | +12.77pp | **FAIL** |
| 3 | 39.29% | 50.68% | +11.39pp | **FAIL** |
| 2 | 46.15% | 47.20% | +1.05pp | **FAIL** |

**Tolerance:** 1 percentage point (as per AC4)

## Root Cause Analysis

The probability values in the document tables are systematically wrong:

### Type 8 Example (Lines 123-129)
| k | Doc Prob | Correct Prob | Doc Odds | Correct Odds |
|---|----------|--------------|----------|--------------|
| 8 | 0.0000043 | 0.0000133 | 1:230,115 | 1:74,941 |
| 7 | 0.0001605 | 0.0004106 | 1:6,232 | 1:2,436 |
| 6 | 0.0023645 | 0.0050296 | 1:423 | 1:199 |
| 5 | 0.0183019 | 0.0321893 | 1:54 | 1:31 |
| 4 | 0.0815032 | 0.1181951 | 1:12 | 1:8 |

**Error pattern:** Document probabilities are 1.45x to 3.1x too low.

## German Lottery Standard

All KENO types should have approximately 50% payout (German lottery standard). The document claim of 21-56% range is implausible and indicates calculation errors.

Correct ROI range: **43.25% - 50.68%** (all near 50%)

## Acceptance Criteria Assessment

| AC | Description | Result |
|----|-------------|--------|
| AC1 | All 9 KENO types documented | PASS |
| AC2 | Probabilities correct (hypergeometric) | **FAIL** (8/9 wrong) |
| AC3 | Quotes match lotto.de | PASS (quotes are from official source) |
| AC4 | ROI within 1pp of correct | **FAIL** (8/9 exceed tolerance) |

## Required Corrections

1. **Recalculate all probability tables** for Types 2-9
2. **Recalculate all ROI tables** using correct probabilities
3. **Update summary table** (Section 12) with correct values
4. **Correct strategic recommendations** (Section 14) - Typ 8 is NOT worst

### Correct Summary Table (Section 12)
| KENO-Typ | Correct ROI | Max. Gewinn (10 EUR) | Hausvorteil |
|----------|-------------|----------------------|-------------|
| Typ 10 | 49.40% | 1.000.000 EUR | 50.60% |
| Typ 9 | 50.05% | 500.000 EUR | 49.95% |
| Typ 8 | 43.25% | 100.000 EUR | 56.75% |
| Typ 7 | 49.57% | 10.000 EUR | 50.43% |
| Typ 6 | 49.74% | 5.000 EUR | 50.26% |
| Typ 5 | 49.90% | 1.000 EUR | 50.10% |
| Typ 4 | 49.44% | 220 EUR | 50.56% |
| Typ 3 | 50.68% | 160 EUR | 49.32% |
| Typ 2 | 47.20% | 60 EUR | 52.80% |

## Repro Command

```python
from math import comb

def hyper_prob(n, k):
    if k > min(n, 20) or k < max(0, n - 50):
        return 0.0
    return comb(n, k) * comb(70 - n, 20 - k) / comb(70, 20)

# Example: Type 8
quotes = {8: 10000, 7: 100, 6: 15, 5: 2, 4: 1}
ev = sum(hyper_prob(8, k) * q for k, q in quotes.items())
print(f"Type 8 ROI: {ev*100:.2f}%")  # Output: 43.25%
```

## Recommendation

**RETURN TO EXECUTOR** for complete probability and ROI recalculation.
