# Regionale Affinitaet (Bundesland)

Kurzuebersicht der neuen Analyse zur Ermittlung regionaler Bias je Zahl (per-market, Bundesland) gegenueber einer globalen Baseline.

## Methode
- Input: Ziehungen mit Region in der CSV (Spalten `Bundesland`/`Region`/`State`), normalisiert auf ASCII (`nordrhein-westfalen`, `bayern`, etc.).
- Baseline: Globale relative Frequenz pro Zahl ueber alle Ziehungen.
- Regional: Relative Frequenz + Lift vs. Baseline mit Laplace-Smoothing (`smoothing_alpha`).
- Signifikanz: Z-Score (Binomial-Naeherung) und zweiseitiger p-Wert; Flag `is_significant` bei |z| >= `z_threshold`.
- Skip: Regionen mit weniger als `min_draws_per_region` werden ausgelassen und als Warning ausgegeben.

## Konfiguration (`config/default.yaml`)
```yaml
analysis:
  regional_affinity:
    enabled: true
    min_draws_per_region: 30
    smoothing_alpha: 1.0
    z_threshold: 2.0
    numbers_per_draw_override: null  # sonst aus Spielkonfiguration
```

## Pipeline/CLI
- Pipeline Runner berechnet die Analyse automatisch wenn `enabled`.
- CLI-Export:
```bash
python scripts/analyze.py analyze \
  --config config/default.yaml \
  --data data/raw/keno/KENO_ab_2018.csv \
  --regional-affinity-output results/regional_affinity.json
```
- Ergebnisstruktur: `analysis`-Block `regional_affinity` mit Metadaten, globaler Baseline, Regionen-Lifts, Signifikanzflags und Warnings (z.B. fehlende Region-Metadaten).

## Akzeptanz / Artefakte
- Artefakt: `results/regional_affinity.json` (siehe obige Repro).
- Tests: `pytest tests/unit/test_regional_affinity.py`
- Warnings dokumentieren fehlende Region-Metadaten oder zu wenige Ziehungen.
