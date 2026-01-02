# Super-Model Vergleich: Original vs V1/V2 (korrigierte Quotes)

**Datum:** 2025-12-30  
**Ziel:** Birthday-Avoidance Erkenntnis in Strategie umsetzen

---

## Hinweis (wichtig)

Fruehere ROI-Werte in diesem Repo waren durch eine falsche (ca. 10x zu hohe) KENO-Quote-Tabelle verfälscht.
Seit 2025-12-30 nutzen die Super-Modelle fuer Auszahlungen die Fixed Quotes pro 1 EUR Einsatz aus:

- `kenobase/core/keno_quotes.py`

Die Vergleichs-JSONs wurden neu generiert:

- `results/super_model_v1_comparison.json`
- `results/super_model_v1_1_comparison.json`
- `results/super_model_v2_comparison.json`

---

## Ausgangslage

Die High-Wins Analyse zeigte:
- KENO Typ10/10 Jackpots vermeiden Birthday-Zahlen (1-31) relativ deutlich
- Unter-repraesentiert bei Jackpots: 6, 5, 16, 1, 25, 20, 8, 27
- Ueber-repraesentiert bei Jackpots: 51, 58, 61, 7, 36, 13, 43, 15

---

## Ergebnisse (ROI)

**High-Wins** = Auszahlungen >= 100 EUR (nicht >=400 EUR).

### Typ 8 (Einsatz 1 EUR)

| Modell | ROI | High-Wins |
|--------|-----|-----------|
| **Original** | **-55.6%** | **1** |
| V1 (Jackpot) | -61.5% | 1 |
| V1 (Balanced) | -67.1% | 0 |
| V1.1 | -55.6% | 1 |
| V2 | -57.1% | 1 |

### Typ 9 (Einsatz 1 EUR)

| Modell | ROI | High-Wins |
|--------|-----|-----------|
| **Original** | **-50.6%** | **0** |
| V1 (Jackpot) | -53.6% | 0 |
| V1 (Balanced) | -52.7% | 0 |
| V1.1 | -50.6% | 0 |
| V2 | -51.0% | 0 |

### Typ 10 (Einsatz 1 EUR)

| Modell | ROI | High-Wins |
|--------|-----|-----------|
| **Original** | **-38.5%** | **3** |
| V1 (Jackpot) | -53.4% | 1 |
| V1 (Balanced) | -51.7% | 1 |
| V1.1 | -38.5% | 3 |
| V2 | -47.9% | 2 |

---

## Schlussfolgerungen

- Birthday-Avoidance ist als Erklaerung fuer vergangene Jackpots interessant, verbessert aber das Ergebnis nicht stabil.
- Das Original-Modell bleibt im Vergleich am besten.
- Positive Phasen koennen auftreten (seltene High-Wins), aber das aendert nicht den negativen Erwartungswert.

---

## Dateien

- `scripts/super_model_synthesis.py` - Original (Baseline)
- `scripts/super_model_v1_birthday.py` - V1 Aggressive
- `scripts/super_model_v1_1_adaptive.py` - V1.1 Adaptive
- `scripts/super_model_v2_birthday_signal.py` - V2 Signal
- `results/super_model_v1_comparison.json` - V1 Ergebnisse
- `results/super_model_v1_1_comparison.json` - V1.1 Ergebnisse
- `results/super_model_v2_comparison.json` - V2 Ergebnisse

