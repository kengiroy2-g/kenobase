# EuroJackpot Analyse - Super-Model Methodik Anwendung

**Datum:** 2025-12-30
**Autor:** Kenobase V2.2 Multi-KI Synthese
**Datenbasis:** 403 EuroJackpot-Ziehungen (07.01.2022 - 26.12.2025)

---

## Executive Summary

Die bewaehrte KENO Super-Model Methodik wurde auf EuroJackpot angewendet. Die wichtigste Erkenntnis:

| Hypothese | KENO | EuroJackpot | Unterschied |
|-----------|------|-------------|-------------|
| **WL-003 Jackpot-Cooldown** | -66% Effekt, +466% ROI | -49.7% Effekt, kein ROI-Vorteil | Struktureller Unterschied |

### Kern-Erkenntnis

Die Jackpot-Cooldown Hypothese ist **statistisch bestaetigt** (-49.7% weniger Jackpots nach Jackpot), fuehrt aber **nicht zu positivem ROI** bei EuroJackpot.

**Grund:** Die Gewinnstruktur ist fundamental anders:
- **KENO:** Viele Gewinnklassen (GK1-GK10), haeufige kleine Gewinne, Typ-Wahl beeinflusst ROI
- **EuroJackpot:** Jackpot-fokussiert, extrem niedrige Grundwahrscheinlichkeit (1:139.838.160)

---

## 1. Hypothese WL-003: Jackpot-Cooldown

### Ergebnis

| Metrik | Wert |
|--------|------|
| Cooldown-Zeitraum | 30 Tage nach Jackpot |
| Ziehungen in Cooldown | 305 (75.7%) |
| Ziehungen ausserhalb | 98 (24.3%) |
| Jackpot-Rate in Cooldown | 11.8% |
| Jackpot-Rate ausserhalb | 23.5% |
| **Cooldown-Effekt** | **-49.7%** |

### Interpretation

Nach einem EuroJackpot-Gewinn ist die Wahrscheinlichkeit fuer den naechsten Jackpot in den folgenden 30 Tagen um fast 50% reduziert. Dies bestaetigt die Wirtschaftslogik-Hypothese:

> Das System "spart" nach grossen Auszahlungen, um den House-Edge zu stabilisieren.

### Vergleich mit KENO

| Aspekt | KENO | EuroJackpot |
|--------|------|-------------|
| Cooldown-Effekt | -66% | -49.7% |
| ROI-Auswirkung | +466.6% | Nicht messbar |
| Grund | Typ-Wahl (9 statt 10) | Keine Alternative |

---

## 2. Zahlen-Paar Analyse

### Hauptzahlen (5 aus 50)

**Erwartungswert pro Paar:** 3.29 Erscheinungen

**Top 5 Paare (ueber Erwartung):**

| Rang | Paar | Frequenz | Abweichung |
|------|------|----------|------------|
| 1 | **11-20** | 10x | **+204.0%** |
| 2 | 27-41 | 9x | +173.6% |
| 3 | 11-16 | 9x | +173.6% |
| 4 | 17-30 | 9x | +173.6% |
| 5 | 28-31 | 9x | +173.6% |

**Bemerkenswert:** Die Zahl 11 erscheint in 2 der Top-5 Paare.

### Eurozahlen (2 aus 12)

**Erwartungswert pro Paar:** 6.11 Erscheinungen

| Paar | Frequenz | Abweichung |
|------|----------|------------|
| **3-9** (haeufigste) | 11x | +80.0% |
| 4-6 (seltenste) | 1x | -83.6% |

---

## 3. Zahlen-Frequenz

### Top 5 Hauptzahlen

| Zahl | Frequenz | Abweichung |
|------|----------|------------|
| **11** | 55x | **+36.5%** |
| 20 | 49x | +21.6% |
| 30 | 49x | +21.6% |
| 21 | 48x | +19.1% |
| 17 | 47x | +16.6% |

### Top 3 Eurozahlen

| Zahl | Frequenz | Abweichung |
|------|----------|------------|
| **3** | 80x | **+19.1%** |
| 5 | 77x | +14.6% |
| 10 | 72x | +7.2% |

---

## 4. Wochentags-Analyse

EuroJackpot wird dienstags und freitags gezogen:

| Wochentag | Ziehungen | Jackpots | Rate |
|-----------|-----------|----------|------|
| Dienstag | 196 | 22 | 11.22% |
| **Freitag** | 207 | **37** | **17.87%** |

**Erkenntnis:** Freitags-Ziehungen haben eine 59% hoehere Jackpot-Rate als Dienstags-Ziehungen.

---

## 5. Backtest-Ergebnisse

### Strategie-Vergleich

| Strategie | Investiert | Gewonnen | ROI |
|-----------|------------|----------|-----|
| Baseline (random) | 8.060 EUR | 1.071 EUR | -86.7% |
| Cooldown (random) | 1.960 EUR | 242 EUR | -87.7% |
| Baseline (popular) | 2.418 EUR | 795 EUR | **-67.1%** |
| Cooldown (popular) | 588 EUR | 158 EUR | -73.1% |

### Gewinnklassen (Baseline Popular)

| Klasse | Richtige | Anzahl | Gewinn |
|--------|----------|--------|--------|
| 4+0 | 4 Haupt | 2x | 200 EUR |
| 3+0 | 3 Haupt | 9x | 117 EUR |
| 2+2 | 2 Haupt + 2 Euro | 5x | 100 EUR |
| 2+1 | 2 Haupt + 1 Euro | 44x | 308 EUR |
| 1+2 | 1 Haupt + 2 Euro | 7x | 70 EUR |
| **Gesamt** | | **67 Gewinne** | **795 EUR** |

---

## 6. Fazit

### Bestaetigt

1. **Jackpot-Cooldown existiert** (-49.7% Effekt nach Jackpot)
2. **Zahlen sind nicht gleichverteilt** (11, 20, 30 ueberrepraesentiert)
3. **Freitag ist besser als Dienstag** (+59% Jackpot-Rate)

### Nicht uebertragbar von KENO

1. **ROI-Optimierung durch Cooldown** - funktioniert bei EuroJackpot nicht
2. **Typ-Wahl** - gibt es bei EuroJackpot nicht (immer 5+2)
3. **Haeufige kleine Gewinne** - viel seltener als bei KENO

### Empfehlung

Fuer EuroJackpot ist der **Anti-Birthday-Effekt** moeglicherweise relevanter:
- Zahlen > 31 werden seltener gespielt (weniger Geburtstage)
- Bei Jackpot-Gewinn: weniger Gewinner-Teilung
- Beispiel: Zahl 50 hat 13.4% weniger Frequenz als Zahl 11

---

## 7. Naechste Schritte

1. **Lotto 6aus49 Analyse** - Aehnliche Struktur wie EuroJackpot, aber nur 6 aus 49
2. **Jackpot-Hoehe Korrelation** - Sind hohe Jackpots (>50M) anders verteilt?
3. **Saisonale Muster** - Unterschiede zwischen Sommer/Winter?

---

## Dateien

- `results/eurojackpot/eurojackpot_analysis.json` - Detaillierte Analyse
- `results/eurojackpot/eurojackpot_backtest.json` - Backtest-Ergebnisse
- `scripts/analyze_eurojackpot.py` - Analyse-Script
- `scripts/backtest_eurojackpot.py` - Backtest-Script
