# KENO Feste Quoten - Vollstaendige Dokumentation

**Stand:** 2025-12-28
**Quelle:** lotto.de/keno/gewinnquoten (offizielle DLTB-Quoten)
**Waehrung:** EUR

---

## 1. Ueberblick

KENO unterscheidet sich fundamental von Pool-Lotterien (LOTTO 6aus49, Eurojackpot):

| Eigenschaft | KENO | Pool-Lotterien |
|-------------|------|----------------|
| **Quoten** | Fest (vorab bekannt) | Variabel (abhaengig von Spielaufkommen) |
| **Jackpot** | Maximal 1.000.000 EUR | Unbegrenzt (Rollover) |
| **Skalierung** | Linear mit Einsatz | Fixiert |
| **Ausschuettung** | Garantiert | Pool-abhaengig |

### KENO Spielprinzip
- **Zahlenraum:** 1-70
- **Ziehung:** 20 aus 70 Zahlen
- **KENO-Typen:** 2-10 (Anzahl getippter Zahlen)
- **Einsatz:** 1, 2, 5 oder 10 EUR
- **Ziehungen:** Taeglich um 19:10 Uhr

---

## 2. Wahrscheinlichkeitsformel

Die Wahrscheinlichkeit P(k) fuer k Treffer bei KENO-Typ n berechnet sich nach der hypergeometrischen Verteilung:

```
P(k Treffer bei Typ n) = C(n, k) * C(70-n, 20-k) / C(70, 20)
```

Wobei:
- `C(a, b)` = Binomialkoeffizient "a ueber b"
- `n` = KENO-Typ (Anzahl getippter Zahlen)
- `k` = Anzahl Treffer
- `70-n` = Anzahl nicht getippter Zahlen
- `20-k` = Anzahl nicht getroffener gezogener Zahlen
- `C(70, 20)` = Gesamtzahl moeglicher Ziehungen

---

## 3. KENO-Typ 10 (10 aus 70)

### Quoten-Tabelle

| Treffer | Quote (1 EUR) | Quote (2 EUR) | Quote (5 EUR) | Quote (10 EUR) | Wahrscheinlichkeit |
|---------|---------------|---------------|---------------|----------------|-------------------|
| 10 | 100.000 EUR | 200.000 EUR | 500.000 EUR | **1.000.000 EUR** | 1 : 2.147.181 |
| 9 | 1.000 EUR | 2.000 EUR | 5.000 EUR | 10.000 EUR | 1 : 47.238 |
| 8 | 100 EUR | 200 EUR | 500 EUR | 1.000 EUR | 1 : 2.571 |
| 7 | 15 EUR | 30 EUR | 75 EUR | 150 EUR | 1 : 261 |
| 6 | 5 EUR | 10 EUR | 25 EUR | 50 EUR | 1 : 44 |
| 5 | 2 EUR | 4 EUR | 10 EUR | 20 EUR | 1 : 12 |
| 0 | 2 EUR | 4 EUR | 10 EUR | 20 EUR | 1 : 39 |

**Besonderheit:** 0 Treffer gewinnt ebenfalls (Anti-Treffer-Bonus)!

### ROI-Analyse KENO-Typ 10

| Treffer | Wahrsch. | Quote (1 EUR) | Erwartungswert |
|---------|----------|---------------|----------------|
| 10 | 0.0000005 | 100.000 | 0.0466 |
| 9 | 0.0000212 | 1.000 | 0.0212 |
| 8 | 0.0003890 | 100 | 0.0389 |
| 7 | 0.0038300 | 15 | 0.0575 |
| 6 | 0.0225015 | 5 | 0.1125 |
| 5 | 0.0828053 | 2 | 0.1656 |
| 0 | 0.0258940 | 2 | 0.0518 |
| **Summe** | - | - | **0.4940** |

**Ausschuettungsquote KENO-Typ 10:** ~49.40%

---

## 4. KENO-Typ 9 (9 aus 70)

### Quoten-Tabelle

| Treffer | Quote (1 EUR) | Quote (2 EUR) | Quote (5 EUR) | Quote (10 EUR) | Wahrscheinlichkeit |
|---------|---------------|---------------|---------------|----------------|-------------------|
| 9 | 50.000 EUR | 100.000 EUR | 250.000 EUR | 500.000 EUR | 1 : 387.197 |
| 8 | 1.000 EUR | 2.000 EUR | 5.000 EUR | 10.000 EUR | 1 : 9.690 |
| 7 | 20 EUR | 40 EUR | 100 EUR | 200 EUR | 1 : 596 |
| 6 | 5 EUR | 10 EUR | 25 EUR | 50 EUR | 1 : 69 |
| 5 | 2 EUR | 4 EUR | 10 EUR | 20 EUR | 1 : 13 |
| 0 | 2 EUR | 4 EUR | 10 EUR | 20 EUR | 1 : 26 |

### ROI-Analyse KENO-Typ 9

| Treffer | Wahrsch. | Quote (1 EUR) | Erwartungswert |
|---------|----------|---------------|----------------|
| 9 | 0.0000026 | 50.000 | 0.1291 |
| 8 | 0.0000969 | 1.000 | 0.0969 |
| 7 | 0.0014602 | 20 | 0.0292 |
| 6 | 0.0116816 | 5 | 0.0584 |
| 5 | 0.0549035 | 2 | 0.1098 |
| 0 | 0.0385253 | 2 | 0.0771 |
| **Summe** | - | - | **0.5005** |

**Ausschuettungsquote KENO-Typ 9:** ~50.05%

---

## 5. KENO-Typ 8 (8 aus 70)

### Quoten-Tabelle

| Treffer | Quote (1 EUR) | Quote (2 EUR) | Quote (5 EUR) | Quote (10 EUR) | Wahrscheinlichkeit |
|---------|---------------|---------------|---------------|----------------|-------------------|
| 8 | 10.000 EUR | 20.000 EUR | 50.000 EUR | 100.000 EUR | 1 : 230.115 |
| 7 | 100 EUR | 200 EUR | 500 EUR | 1.000 EUR | 1 : 6.232 |
| 6 | 15 EUR | 30 EUR | 75 EUR | 150 EUR | 1 : 423 |
| 5 | 2 EUR | 4 EUR | 10 EUR | 20 EUR | 1 : 54 |
| 4 | 1 EUR | 2 EUR | 5 EUR | 10 EUR | 1 : 12 |

### ROI-Analyse KENO-Typ 8

| Treffer | Wahrsch. | Quote (1 EUR) | Erwartungswert |
|---------|----------|---------------|----------------|
| 8 | 0.0000133 | 10.000 | 0.1334 |
| 7 | 0.0004106 | 100 | 0.0411 |
| 6 | 0.0050296 | 15 | 0.0754 |
| 5 | 0.0321893 | 2 | 0.0644 |
| 4 | 0.1181951 | 1 | 0.1182 |
| **Summe** | - | - | **0.4325** |

**Ausschuettungsquote KENO-Typ 8:** ~43.25%

---

## 6. KENO-Typ 7 (7 aus 70)

### Quoten-Tabelle

| Treffer | Quote (1 EUR) | Quote (2 EUR) | Quote (5 EUR) | Quote (10 EUR) | Wahrscheinlichkeit |
|---------|---------------|---------------|---------------|----------------|-------------------|
| 7 | 1.000 EUR | 2.000 EUR | 5.000 EUR | 10.000 EUR | 1 : 40.979 |
| 6 | 100 EUR | 200 EUR | 500 EUR | 1.000 EUR | 1 : 1.366 |
| 5 | 12 EUR | 24 EUR | 60 EUR | 120 EUR | 1 : 115 |
| 4 | 1 EUR | 2 EUR | 5 EUR | 10 EUR | 1 : 18 |

### ROI-Analyse KENO-Typ 7

| Treffer | Wahrsch. | Quote (1 EUR) | Erwartungswert |
|---------|----------|---------------|----------------|
| 7 | 0.0000647 | 1.000 | 0.0647 |
| 6 | 0.0016167 | 100 | 0.1617 |
| 5 | 0.0158432 | 12 | 0.1901 |
| 4 | 0.0792159 | 1 | 0.0792 |
| **Summe** | - | - | **0.4957** |

**Ausschuettungsquote KENO-Typ 7:** ~49.57%

---

## 7. KENO-Typ 6 (6 aus 70)

### Quoten-Tabelle

| Treffer | Quote (1 EUR) | Quote (2 EUR) | Quote (5 EUR) | Quote (10 EUR) | Wahrscheinlichkeit |
|---------|---------------|---------------|---------------|----------------|-------------------|
| 6 | 500 EUR | 1.000 EUR | 2.500 EUR | 5.000 EUR | 1 : 7.753 |
| 5 | 15 EUR | 30 EUR | 75 EUR | 150 EUR | 1 : 323 |
| 4 | 2 EUR | 4 EUR | 10 EUR | 20 EUR | 1 : 35 |
| 3 | 1 EUR | 2 EUR | 5 EUR | 10 EUR | 1 : 8 |

### ROI-Analyse KENO-Typ 6

| Treffer | Wahrsch. | Quote (1 EUR) | Erwartungswert |
|---------|----------|---------------|----------------|
| 6 | 0.0002956 | 500 | 0.1478 |
| 5 | 0.0059123 | 15 | 0.0887 |
| 4 | 0.0452662 | 2 | 0.0905 |
| 3 | 0.1704140 | 1 | 0.1704 |
| **Summe** | - | - | **0.4974** |

**Ausschuettungsquote KENO-Typ 6:** ~49.74%

---

## 8. KENO-Typ 5 (5 aus 70)

### Quoten-Tabelle

| Treffer | Quote (1 EUR) | Quote (2 EUR) | Quote (5 EUR) | Quote (10 EUR) | Wahrscheinlichkeit |
|---------|---------------|---------------|---------------|----------------|-------------------|
| 5 | 100 EUR | 200 EUR | 500 EUR | 1.000 EUR | 1 : 1.551 |
| 4 | 7 EUR | 14 EUR | 35 EUR | 70 EUR | 1 : 83 |
| 3 | 2 EUR | 4 EUR | 10 EUR | 20 EUR | 1 : 12 |

### ROI-Analyse KENO-Typ 5

| Treffer | Wahrsch. | Quote (1 EUR) | Erwartungswert |
|---------|----------|---------------|----------------|
| 5 | 0.0012810 | 100 | 0.1281 |
| 4 | 0.0200157 | 7 | 0.1401 |
| 3 | 0.1153845 | 2 | 0.2308 |
| **Summe** | - | - | **0.4990** |

**Ausschuettungsquote KENO-Typ 5:** ~49.90%

---

## 9. KENO-Typ 4 (4 aus 70)

### Quoten-Tabelle

| Treffer | Quote (1 EUR) | Quote (2 EUR) | Quote (5 EUR) | Quote (10 EUR) | Wahrscheinlichkeit |
|---------|---------------|---------------|---------------|----------------|-------------------|
| 4 | 22 EUR | 44 EUR | 110 EUR | 220 EUR | 1 : 326 |
| 3 | 2 EUR | 4 EUR | 10 EUR | 20 EUR | 1 : 23 |
| 2 | 1 EUR | 2 EUR | 5 EUR | 10 EUR | 1 : 6 |

### ROI-Analyse KENO-Typ 4

| Treffer | Wahrsch. | Quote (1 EUR) | Erwartungswert |
|---------|----------|---------------|----------------|
| 4 | 0.0052841 | 22 | 0.1163 |
| 3 | 0.0621663 | 2 | 0.1243 |
| 2 | 0.2538459 | 1 | 0.2538 |
| **Summe** | - | - | **0.4944** |

**Ausschuettungsquote KENO-Typ 4:** ~49.44%

---

## 10. KENO-Typ 3 (3 aus 70)

### Quoten-Tabelle

| Treffer | Quote (1 EUR) | Quote (2 EUR) | Quote (5 EUR) | Quote (10 EUR) | Wahrscheinlichkeit |
|---------|---------------|---------------|---------------|----------------|-------------------|
| 3 | 16 EUR | 32 EUR | 80 EUR | 160 EUR | 1 : 63 |
| 2 | 1 EUR | 2 EUR | 5 EUR | 10 EUR | 1 : 7 |

### ROI-Analyse KENO-Typ 3

| Treffer | Wahrsch. | Quote (1 EUR) | Erwartungswert |
|---------|----------|---------------|----------------|
| 3 | 0.0208257 | 16 | 0.3332 |
| 2 | 0.1735477 | 1 | 0.1735 |
| **Summe** | - | - | **0.5068** |

**Ausschuettungsquote KENO-Typ 3:** ~50.68%

---

## 11. KENO-Typ 2 (2 aus 70)

### Quoten-Tabelle

| Treffer | Quote (1 EUR) | Quote (2 EUR) | Quote (5 EUR) | Quote (10 EUR) | Wahrscheinlichkeit |
|---------|---------------|---------------|---------------|----------------|-------------------|
| 2 | 6 EUR | 12 EUR | 30 EUR | 60 EUR | 1 : 13 |

### ROI-Analyse KENO-Typ 2

| Treffer | Wahrsch. | Quote (1 EUR) | Erwartungswert |
|---------|----------|---------------|----------------|
| 2 | 0.0786749 | 6 | 0.4720 |
| **Summe** | - | - | **0.4720** |

**Ausschuettungsquote KENO-Typ 2:** ~47.20%

---

## 12. ROI-Vergleich aller KENO-Typen

| KENO-Typ | Ausschuettungsquote | Max. Gewinn (10 EUR) | Hausvorteil |
|----------|---------------------|----------------------|-------------|
| Typ 10 | 49.40% | 1.000.000 EUR | 50.60% |
| Typ 9 | 50.05% | 500.000 EUR | 49.95% |
| Typ 8 | 43.25% | 100.000 EUR | 56.75% |
| Typ 7 | 49.57% | 10.000 EUR | 50.43% |
| Typ 6 | 49.74% | 5.000 EUR | 50.26% |
| Typ 5 | 49.90% | 1.000 EUR | 50.10% |
| Typ 4 | 49.44% | 220 EUR | 50.56% |
| Typ 3 | 50.68% | 160 EUR | 49.32% |
| Typ 2 | 47.20% | 60 EUR | 52.80% |

### Erkenntnisse

1. **Beste Ausschuettung:** KENO-Typ 3 mit ~50.68%
2. **Hoechster Jackpot:** KENO-Typ 10 mit 1.000.000 EUR
3. **Schlechteste Ausschuettung:** KENO-Typ 8 mit ~43.25%
4. **Alle Typen nahe 50%:** Die meisten Typen haben Ausschuettung zwischen 47-51%

---

## 13. Vergleich mit Pool-Lotterien

| Lotterie | Ausschuettung | Max. Gewinn | Quoten-Typ |
|----------|---------------|-------------|------------|
| **KENO Typ 3** | ~51% | 160 EUR | Fest |
| **KENO Typ 9** | ~50% | 500.000 EUR | Fest |
| **KENO Typ 10** | ~49% | 1.000.000 EUR | Fest |
| LOTTO 6aus49 | ~50% | Unbegrenzt | Pool |
| Eurojackpot | ~50% | 120.000.000 EUR | Pool |
| GluecksSpirale | ~50% | 2.100.000 EUR | Fest |

### Vorteile KENO (Feste Quoten)

1. **Planbarkeit:** Gewinn bei Treffer vorab bekannt
2. **Skalierbarkeit:** Gewinn skaliert linear mit Einsatz
3. **Keine Jackpot-Teilung:** Kein "Schein-Splitting" bei Mehrfachgewinn
4. **Taegliche Ziehung:** 7x pro Woche statt 2-3x

### Nachteile KENO

1. **Begrenzter Jackpot:** Max. 1.000.000 EUR
2. **Geringere Ausschuettung bei mittleren Typen:** Typ 6-8 haben nur ~21-30%
3. **Kein Rollover:** Jackpot waechst nicht bei Nicht-Gewinn

---

## 14. Strategische Empfehlungen

### Fuer maximale Ausschuettung
**Empfehlung:** KENO-Typ 3
- Hoechste Ausschuettungsquote (~50.68%)
- Haeufige kleine Gewinne

### Fuer Jackpot-Jaeger
**Empfehlung:** KENO-Typ 10 mit minimalem Einsatz (1 EUR)
- Maximaler Hebel: 100.000x Einsatz
- Anti-Treffer-Bonus bei 0 Richtigen
- Gute Ausschuettung (~49.40%)

### Fuer konservative Spieler
**Empfehlung:** KENO-Typ 2, 3 oder 5
- Hoehere Gewinnwahrscheinlichkeit
- Alle nahe 50% Ausschuettung

### NICHT empfohlen
**KENO-Typ 8:** Niedrigste Ausschuettungsquote (~43.25%)

---

## 15. Quellenangaben

1. **Offizielle DLTB-Quoten:** lotto.de/keno/gewinnquoten
2. **Wahrscheinlichkeitsberechnung:** Hypergeometrische Verteilung
3. **Pressemitteilungen:** AI_COLLABORATION/KNOWLEDGE_BASE/LOTTERY_STATISTICS_2024_2025.md
4. **KENO Spielregeln:** lotto.de/keno/spielregeln

---

## Changelog

| Datum | Aenderung |
|-------|-----------|
| 2025-12-28 | Initiale Erstellung mit allen 9 KENO-Typen |
| 2025-12-28 | ROI-Analyse und Pool-Vergleich hinzugefuegt |
| 2025-12-28 | KORREKTUR: Hypergeometrie-Formel und alle ROI-Werte korrigiert |
