# Validierung: Differenz-Summe mod 7 = 3 Hypothese

**Datum:** 2025-12-31
**Status:** TEILWEISE VALIDIERT - Weitere Daten benoetigt

---

## 1. Hypothese

> Bei KENO Jackpot-Gewinnern (Typ 10, 10 Richtige) ist die "Differenz-Summe mod 7" der gewaehlten 10 Zahlen **immer = 3**.

### Definition

- **Differenz-Summe** = Summe aller paarweisen Differenzen zwischen den 10 Zahlen
- Bei 10 Zahlen gibt es C(10,2) = 45 Paare
- `diff_sum = sum(|z_i - z_j|)` fuer alle i < j
- Hypothese: `diff_sum mod 7 = 3`

---

## 2. Bekannte Jackpot-Gewinner

| Gewinner | Zahlen | Diff-Summe | mod 7 | Status |
|----------|--------|------------|-------|--------|
| Kyritz | [5,12,20,26,34,36,42,45,48,66] | 976 | **3** | BESTAETIGT |
| Oberbayern | [3,15,18,27,47,53,54,55,66,68] | 1214 | **3** | BESTAETIGT |
| Nordsachsen | [9,19,37,38,43,45,48,57,59,67] | 934 | **3** | BESTAETIGT |

**Ergebnis:** Alle 3 bekannten Gewinner haben mod 7 = 3

---

## 3. Analyse der Jackpot-Tage

### 3.1 Methodik

Fuer jeden Jackpot-Tag (Typ 10, 10 Richtige, Gewinner > 0):
1. Lade die 20 gezogenen Zahlen
2. Generiere alle C(20,10) = 184.756 moegliche 10er-Kombinationen
3. Berechne fuer jede Kombination: diff_sum mod 7
4. Zaehle die Verteilung

### 3.2 Ergebnisse (31 Jackpot-Tage analysiert)

| Statistik | Wert |
|-----------|------|
| **Analysierte Jackpot-Tage** | 31 |
| **Total Kombinationen pro Tag** | 184.756 |
| **Kombinationen mit mod 7 = 3** | |
| - Minimum | 25.582 (13.85%) |
| - Maximum | 26.653 (14.43%) |
| - **Mittelwert** | **26.319 (14.25%)** |
| - Standardabweichung | 201 (0.11%) |
| **Erwartung bei Zufall** | 26.394 (14.29%) |

### 3.3 Detaillierte Ergebnisse

```
Datum            mod7=3    Prozent
-----------------------------------
31.01.2022       26,356     14.27%
26.03.2022       26,420     14.30%
25.05.2022       26,441     14.31%
28.05.2022       26,653     14.43%
29.05.2022       26,255     14.21%
08.06.2022       26,432     14.31%
29.06.2022       26,105     14.13%
24.07.2022       26,286     14.23%
25.07.2022       26,317     14.24%
24.09.2022       26,274     14.22%
30.09.2022       26,487     14.34%
16.10.2022       26,196     14.18%
10.12.2022       26,449     14.32%
23.12.2022       26,548     14.37%
01.02.2023       26,243     14.20%
10.03.2023       26,498     14.34%
31.03.2023       26,362     14.27%
04.04.2023       25,582     13.85%
17.04.2023       26,447     14.31%
08.06.2023       26,367     14.27%
13.06.2023       26,407     14.29%
23.06.2023       26,368     14.27%
26.06.2023       26,296     14.23%
28.06.2023       26,277     14.22%
25.07.2023       26,604     14.40%
10.10.2023       26,070     14.11%
13.11.2023       26,092     14.12%
30.12.2023       26,336     14.25%
05.01.2024       26,342     14.26%
24.01.2024       26,419     14.30%
06.02.2024       25,972     14.06%
```

---

## 4. Statistische Bewertung

### 4.1 Zufaelligkeit der mod 7 Verteilung

Die Verteilung ueber die 7 moeglichen mod-Werte ist bei allen Jackpot-Tagen nahezu gleichverteilt:

```
  mod 7 = 0: ~14.2%
  mod 7 = 1: ~14.3%
  mod 7 = 2: ~14.3%
  mod 7 = 3: ~14.3%  <-- Zielwert
  mod 7 = 4: ~14.3%
  mod 7 = 5: ~14.3%
  mod 7 = 6: ~14.3%
```

**Schlussfolgerung:** Die mod 7 Verteilung ist statistisch gleichverteilt (erwartungsgemaess).

### 4.2 Signifikanz der 3 bekannten Gewinner

- Alle 3 bekannten Gewinner haben mod 7 = 3
- Wahrscheinlichkeit bei Zufall: (1/7)^3 = 0.29%
- **p-Wert: 0.0029** (statistisch signifikant bei alpha=0.05)

### 4.3 Konfidenzintervall

Mit nur 3 Datenpunkten:
- Beobachtete Rate: 3/3 = 100%
- 95% Konfidenzintervall (Wilson): [29.2%, 100%]
- Mindestens erforderlich fuer Signifikanz: 5+ Gewinner mit mod 7 = 3

---

## 5. Praktische Auswirkungen

### 5.1 Filtereffekt

Wenn die Hypothese stimmt, reduziert der Filter "mod 7 = 3" die Kombinationen:

| Schritt | Kombinationen | Reduktion |
|---------|---------------|-----------|
| Alle 10er aus 20 | 184.756 | - |
| Filter: mod 7 = 3 | ~26.300 | **7x** |

### 5.2 Kombinierter Ansatz

Mit zusaetzlichen Filtern (z.B. Zehnergruppen-Regel):

| Filter | Verbleibende Kombinationen |
|--------|---------------------------|
| mod 7 = 3 allein | ~26.300 |
| + max 2 pro Dekade | geschaetzt ~5.000 |
| + Summenfilter | geschaetzt ~2.000 |

---

## 6. Empfehlungen

### 6.1 Sofort umsetzbar

1. **Datensammlung:** Sammle alle verfuegbaren Gewinner-Tipps mit deren konkreten 10 Zahlen
2. **Erweiterung:** Pruefe die Hypothese fuer EuroJackpot (5+2) und Lotto 6aus49

### 6.2 Weiterfuehrende Analyse

1. **Monte-Carlo-Simulation:** Generiere 10.000 zufaellige Gewinner und pruefe mod 7 Verteilung
2. **Alternative Moduli:** Teste mod 5, mod 9, mod 11 etc.
3. **Differenz-Muster:** Analysiere nicht nur Summe, sondern auch Verteilung der Differenzen

### 6.3 Entscheidungsmatrix

| Szenario | Naechster Schritt |
|----------|-------------------|
| Weitere Gewinner haben mod 7 != 3 | Hypothese falsifiziert |
| 5+ Gewinner alle mod 7 = 3 | Starke Evidenz, in Produktion verwenden |
| 10+ Gewinner alle mod 7 = 3 | Extrem signifikant (p < 10^-6) |

---

## 7. Fazit

| Aspekt | Bewertung |
|--------|-----------|
| **Hypothese** | Teilweise gestuetzt |
| **Evidenz** | 3 von 3 Gewinnern bestaetigen (100%) |
| **p-Wert** | 0.0029 (signifikant) |
| **Stichprobe** | Zu klein (n=3) |
| **Filter-Effekt** | Reduziert auf 14.3% (~7x) |
| **Naechster Schritt** | Mehr Gewinner-Daten sammeln |

**Status: MONITORING - Warte auf mehr Daten zur Bestaetigung oder Widerlegung**

---

## 8. Script

Das Validierungs-Script befindet sich unter:
```
scripts/validate_diff_sum_mod7.py
```

Aufruf:
```bash
python scripts/validate_diff_sum_mod7.py
```

---

*Generiert von Claude Code am 2025-12-31*
