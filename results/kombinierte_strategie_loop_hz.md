# Kombinierte Strategie: Loop + Hot-Zone

**Analyse-Datum:** 01.01.2026
**Backtest-Zeitraum:** 2022-2024

---

## Executive Summary

Die Kombination von Loop-Erkenntnissen (FRÜH-Phase, Cooldown) mit der Hot-Zone Strategie
(48-60 Tage Wartezeit) wurde getestet.

---

## Strategie-Vergleich

| Strategie | Jackpots | Tage | JP/Tag |
|-----------|----------|------|--------|
| HZ7 Basis (keine Regeln) | 2 | 2 | 0.21% |
| HZ7 + FRÜH-Phase | 2 | 2 | 0.44% |
| HZ7 + 48d Delay | 1 | 1 | 0.10% |
| HZ7 + Cooldown | 1 | 1 | 0.21% |
| HZ7 + FRÜH + Cooldown | 1 | 1 | 0.48% |
| HZ6 + FRÜH + Cooldown | 1 | 1 | 0.48% |
| HZ7 KOMPLETT (alle Regeln) | 0 | 0 | 0.00% |
| Loop Kern-Zahlen + alle Regeln | 0 | 0 | 0.00% |


---

## Beste Strategie

**HZ7 Basis (keine Regeln)**

- Jackpots: 2
- Verbesserung vs Basis: +0.0%

---

## Finale kombinierte Regeln

1. **Hot-Zone 7 (W50)** als Zahlenbasis
2. **48-60 Tage Wartezeit** nach Ermittlung (HZ-Erkenntnis)
3. **FRÜH-Phase (Tag 1-14)** bevorzugen (Loop-Erkenntnis: +364% ROI)
4. **30 Tage Cooldown** nach 10/10 Jackpot (Loop-Erkenntnis: -66% ROI)

---

## Zahlen-Empfehlung

| Quelle | Zahlen |
|--------|--------|
| Aktuelle HZ7 | [17, 27, 32, 39, 48, 50, 58] |
| Loop Kern | [3, 9, 24, 49, 51, 64] |
| Überlappung | [] |
| **Kombiniert** | **[3, 9, 17, 32, 39, 48, 64]** |

---

## 7 Kombinationen

| # | Kombination |
|---|-------------|
| 1 | [9, 17, 32, 39, 48, 64] |
| 2 | [3, 17, 32, 39, 48, 64] |
| 3 | [3, 9, 32, 39, 48, 64] |
| 4 | [3, 9, 17, 39, 48, 64] |
| 5 | [3, 9, 17, 32, 48, 64] |
| 6 | [3, 9, 17, 32, 39, 64] |
| 7 | [3, 9, 17, 32, 39, 48] |


---

*Erstellt: 01.01.2026 01:01*
