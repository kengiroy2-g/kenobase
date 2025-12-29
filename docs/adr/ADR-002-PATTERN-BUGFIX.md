# ADR-002: Pattern Bug-Fix (elif -> if)

**Status:** ACCEPTED
**Date:** 2025-12-27
**Author:** Executor KI (ISSUE-004)
**Relates to:** ISSUE-004 (Korrelations-Analysen)

## Context

Das urspruengliche KENO-Analyseskript (V9, Zeilen 130-135) verwendete eine exklusive
`elif`-Kette fuer die Pattern-Extraktion (Duo/Trio/Quatro). Dies fuehrte dazu, dass
bei 4 Treffern NUR ein Quatro extrahiert wurde, waehrend die 4 enthaltenen Trios
und 6 Duos verloren gingen.

### Alter Code (V9:130-135)
```python
if match_count == 4:
    quatros.append(matched)
elif match_count == 3:  # EXKLUSIV - Trios bei 4 Treffern ignoriert!
    trios.append(matched)
elif match_count == 2:  # EXKLUSIV - Duos bei 3+ Treffern ignoriert!
    duos.append(matched)
```

### Mathematisches Problem
Bei N Treffern enthaelt die Menge:
- C(N,4) Quatros
- C(N,3) Trios
- C(N,2) Duos

Beispiel 4 Treffer: 1 + 4 + 6 = 11 Patterns (nicht nur 1!)

## Decision

Ersetze die exklusive `elif`-Kette durch parallele `if`-Statements mit
`itertools.combinations` fuer korrekte Sub-Pattern-Extraktion.

### Neuer Code (pattern.py:118-131)
```python
if match_count >= 4:
    quatros = [tuple(sorted(q)) for q in combinations(matched, 4)]

if match_count >= 3:
    trios = [tuple(sorted(t)) for t in combinations(matched, 3)]

if match_count >= 2:
    duos = [tuple(sorted(d)) for d in combinations(matched, 2)]
```

## Consequences

### Positive
1. **Korrekte Kombinatorik:** Alle C(n,k) Sub-Patterns werden extrahiert
2. **Testbar:** 16 Unit-Tests verifizieren mathematische Korrektheit
3. **Konsistent:** Sortierte Tupel ermoeglichen deterministische Aggregation

### Negative
1. **Mehr Output:** Bei 6 Treffern entstehen 50 Patterns statt 1
2. **Performance:** O(C(n,k)) statt O(1) pro Pattern-Typ

### Neutral
1. Rueckwaertskompatibilit: Keine - alte Ergebnisse sind falsch

## Validation

### Unit-Tests (tests/unit/test_pattern.py)
```
pytest tests/unit/test_pattern.py -v
```

| Test Case | Expected | Verified |
|-----------|----------|----------|
| 4 Treffer | 11 Patterns (1+4+6) | PASS |
| 3 Treffer | 4 Patterns (1+3) | PASS |
| 2 Treffer | 1 Pattern (1) | PASS |
| 5 Treffer | 25 Patterns (5+10+10) | PASS |
| 6 Treffer | 50 Patterns (15+20+15) | PASS |

### Backtest (scripts/backtest_patterns.py)
```
python scripts/backtest_patterns.py --data data/raw/keno/KENO_ab_2018.csv
```

Metriken:
- Precision: Anteil korrekter Pattern-Vorhersagen
- Recall: Anteil gefundener Patterns
- Lift: Verbesserung gegenueber Zufalls-Baseline

### Feature-Importance (pattern.py)
Neue Funktionen zur Signifikanz-Bewertung:
- `calculate_pattern_lift()`: Lift-Berechnung
- `calculate_feature_importance()`: Sortierung nach Lift
- `get_significant_patterns()`: Filterung signifikanter Patterns

## Related Decisions

- ADR-001: Model Laws Integration (geplant)
- ISSUE-004: Korrelations-Analysen (dieses Issue)

## References

- Kombinatorik: C(n,k) = n! / (k!(n-k)!)
- Hypergeometrische Verteilung fuer Baseline-Berechnung
- Walk-Forward Validation fuer Backtest
