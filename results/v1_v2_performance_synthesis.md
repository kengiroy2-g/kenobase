# V1 vs V2 Performance Synthese

**Stand:** 2025-12-31
**Datenquelle:** `results/backtest_v1_v2_comparison.json`
**Zeitraum:** 2018-01-01 bis 2024-02-15
**Ziehungen (N):** 2237

---

## Executive Summary

V2 zeigt signifikant bessere ROI-Werte als V1, aber die positiven ROI-Ergebnisse
sind mit hoher Wahrscheinlichkeit Overfitting-Artefakte, da kein Train/Test-Split
durchgefuehrt wurde.

**WARNUNG:** Die berichteten positiven ROI-Werte (+53.24%, +28.79%, +20.65%)
basieren auf In-Sample-Backtesting ohne Out-of-Sample-Validierung.

---

## Kernergebnisse

| Metrik | V1 (18 Tickets) | V2 (30 Tickets) | Delta |
|--------|-----------------|-----------------|-------|
| Beste ROI | -0.18% | +53.24% | +53.42pp |
| Tickets mit ROI > 0 | 0 | 3 | +3 |
| Durchschnitt ROI | -43.5% | -32.4% | +11.1pp |
| Schlechteste ROI | -68.44% | -66.38% | +2.06pp |

---

## Top 5 Tickets nach ROI

| Rang | Modell | Typ | Strategie | Zahlen | ROI |
|------|--------|-----|-----------|--------|-----|
| 1 | V2 | 6 | pair_focused | [2,3,9,33,49,50] | +53.24% |
| 2 | V2 | 7 | pair_focused | [2,3,9,24,33,49,50] | +28.79% |
| 3 | V2 | 7 | balanced | [2,3,4,9,42,49,61] | +20.65% |
| 4 | V1 | 7 | near_miss | [17,18,25,31,37,49,51] | -0.18% |
| 5 | V2 | 7 | jackpot | [2,3,4,9,20,36,49] | -4.92% |

---

## Strategie-Analyse

### V2 pair_focused (einzige positive ROI)

Die `pair_focused` Strategie in V2 nutzt Kern-Paare aus der Analyse:
- Paar [9,50]: Globale Cooccurrence >210
- Paar [33,49]: Globale Cooccurrence >210
- Zahlen 2,3: Haeufig in High-Performance-Tickets

**Gewinnklassen-Verteilung (V2 Typ6 pair_focused):**
- GK1: 5 (Jackpots)
- GK2: 19
- GK3: 122
- GK4: 399
- Gesamtgewinne: 3428 EUR bei 2237 EUR Einsatz

### V1 Baseline

V1 verwendet traditionelle Strategien (near_miss, jackpot, balanced) ohne
Paar-basierte Optimierung. Kein V1-Ticket erreicht positive ROI.

---

## Overfitting-Warnung

### Risikofaktoren

1. **Kein Train/Test-Split:** Alle 2237 Ziehungen wurden fuer Optimierung UND
   Evaluation verwendet.

2. **Multiple Testing:** 48 Ticket-Kombinationen getestet (18 V1 + 30 V2).
   Bei alpha=0.05: Erwartete False Positives = 48 * 0.05 = 2.4

3. **SYSTEM_STATUS.json Konsistenz:** Offizielle Dokumentation zeigt
   **keine stabile positive ROI** nach Quoten-Korrektur.

4. **2025 OOS-Daten:** Laut SYSTEM_STATUS.json zeigen pair-basierte Tickets
   **negative ROI** trotz 100% Gewinnmonate.

### Empfehlung

Die positiven ROI-Werte (+53.24%, +28.79%, +20.65%) sollten **nicht** als
Beweis fuer eine profitable Strategie interpretiert werden. Eine
Walk-Forward-Validierung oder echte Out-of-Sample-Tests sind erforderlich.

---

## Quellen und Reproduzierbarkeit

**Repro Command:**
```bash
# Artefakt bereits vorhanden:
cat results/backtest_v1_v2_comparison.json | python -c "import json,sys; d=json.load(sys.stdin); print(f'N={d[\"draws_count\"]}')"
# Output: N=2237
```

**Referenz-Artefakte:**
- `results/backtest_v1_v2_comparison.json` (Roh-Daten)
- `AI_COLLABORATION/SYSTEM_STATUS.json` (Quoten-korrigierte Baseline)

---

## Fazit

| Aspekt | Bewertung |
|--------|-----------|
| V2 > V1 | **Ja** (statistisch, aber nicht praktisch bewiesen) |
| Positive ROI real? | **Unklar** (wahrscheinlich Overfitting) |
| Empfehlung | Walk-Forward-Validation vor Produktion |
| Naechster Schritt | OOS-Test auf 2025-Daten |

**Gesamturteil:** V2 pair_focused ist vielversprechend, aber nicht produktionsreif
ohne weitere Validierung.
