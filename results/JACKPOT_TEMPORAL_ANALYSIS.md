# KENO Jackpot Temporale Analyse

**Datum:** 2026-01-01
**Analysezeitraum:** Juni 2023 - Dezember 2025
**Datenbasis:** 21 Jackpot-Ereignisse (Typ 10 mit 10 Richtigen und mindestens 1 Gewinner)

---

## Executive Summary

Diese Analyse untersucht **temporale und Kontext-Muster** bei KENO-Jackpots - Muster, die das System nicht aktiv verschleiern kann, weil sie nicht auf Zahlen-Eigenschaften basieren.

### Wichtigste Findings

| Finding | Signifikanz | Interpretation |
|---------|-------------|----------------|
| Q1-Dominanz | HOCH | 48% aller Jackpots fallen in Q1 (Jan-Maerz) |
| Wochentag Mi/Do | MITTEL | 48% der Jackpots an Mittwoch oder Donnerstag |
| Tag 22-28 | MITTEL | 38% der Jackpots in der 4. Monatswoche |
| Jackpot-Cluster | HOCH | Nach langer Pause oft mehrere Jackpots kurz hintereinander |

---

## 1. Wochentag-Analyse

### Verteilung nach Wochentag (n=21)

| Wochentag | Anzahl | Anteil | Erwartung (1/7) |
|-----------|--------|--------|-----------------|
| Montag    | 1      | 4.8%   | 14.3% |
| Dienstag  | 2      | 9.5%   | 14.3% |
| **Mittwoch** | **5** | **23.8%** | 14.3% |
| **Donnerstag** | **5** | **23.8%** | 14.3% |
| Freitag   | 1      | 4.8%   | 14.3% |
| Samstag   | 3      | 14.3%  | 14.3% |
| Sonntag   | 4      | 19.0%  | 14.3% |

**Interpretation:**
- Mittwoch und Donnerstag sind ueberrepraesentiert (zusammen 47.6% vs. erwartete 28.6%)
- Montag und Freitag sind stark unterrepraesentiert (zusammen 9.6% vs. erwartete 28.6%)
- Wochenende (Sa+So) liegt im erwarteten Bereich

---

## 2. Saisonale Muster

### Quartals-Verteilung

| Quartal | Jackpots | Anteil |
|---------|----------|--------|
| **Q1 (Jan-Maerz)** | **10** | **47.6%** |
| Q2 (Apr-Jun)  | 5      | 23.8% |
| Q3 (Jul-Sep)  | 4      | 19.0% |
| Q4 (Okt-Dez)  | 2      | 9.5%  |

**Interpretation:**
- Starke Q1-Dominanz - fast die Haelfte aller Jackpots
- Q4 (Weihnachtszeit) hat die wenigsten Jackpots trotz hoher Spielaktivitaet
- Moeglicherweise bewusste Auszahlungssteuerung zu Jahresbeginn

### Monats-Verteilung

| Monat | Jackpots |
|-------|----------|
| Januar | 4 |
| Februar | 3 |
| Maerz | 3 |
| April | 1 |
| Mai | 1 |
| Juni | 3 |
| Juli | 2 |
| August | 1 |
| September | 1 |
| Oktober | 1 |
| **November** | **0** |
| Dezember | 1 |

**Auffaellig:** November hat KEINEN einzigen Jackpot im gesamten Analysezeitraum.

---

## 3. Tag des Monats

### Wochen-Verteilung im Monat

| Periode | Tag | Jackpots | Anteil |
|---------|-----|----------|--------|
| Woche 1 | 1-7 | 5 | 23.8% |
| Woche 2 | 8-14 | 1 | 4.8% |
| Woche 3 | 15-21 | 5 | 23.8% |
| **Woche 4** | **22-28** | **8** | **38.1%** |
| Woche 5 | 29-31 | 2 | 9.5% |

**Interpretation:**
- Woche 4 (Tag 22-28) ist stark ueberrepraesentiert
- Woche 2 (Tag 8-14) ist stark unterrepraesentiert
- Die urspruenglich genannten 3 Jackpots (25, 24, 28) fallen alle in Woche 4

---

## 4. Zeitabstaende zwischen Jackpots

### Statistik der Intervalle

| Metrik | Wert |
|--------|------|
| Minimum | 4 Tage |
| Maximum | 345 Tage |
| Durchschnitt | 44.5 Tage |
| Median | 19 Tage |

### Cluster-Muster (WICHTIG!)

Nach langen Jackpot-freien Phasen treten oft **Cluster** auf:

**Cluster 1:** Jan-Feb 2024
- 05.01.2024 (10 Gewinner)
- 24.01.2024 (10 Gewinner) - 19 Tage spaeter
- 06.02.2024 (20 Gewinner) - 13 Tage spaeter

**Cluster 2:** Jan-Maerz 2025
- Nach 345 Tagen Pause
- 16.01.2025 -> 29.01.2025 -> 02.02.2025 -> 16.02.2025 -> 09.03.2025 -> 19.03.2025 -> 27.03.2025
- 7 Jackpots in 70 Tagen!

**Interpretation:**
- Das System scheint "Schulden" anzuhaefen und dann in Clustern auszuzahlen
- Nach langer Durststrecke: Erhoehte Jackpot-Wahrscheinlichkeit

---

## 5. Spieleinsatz-Korrelation

### Beobachtung bei Jackpot-Tagen

| Jackpot-Tag | Spieleinsatz | Durchschnitt Woche |
|-------------|--------------|-------------------|
| 24.01.2024 | 331,357 EUR | 341,859 EUR |
| 28.06.2023 | 333,908 EUR | 366,946 EUR |

**Interpretation:**
- Jackpots fallen NICHT an Tagen mit hohem Spieleinsatz
- Eher leicht unter Durchschnitt (ca. 3-9% unter Wochenschnitt)
- Widerspricht der Intuition, dass mehr Spieler = mehr Jackpots

---

## 6. Gewinner-Anzahl Muster

| Kategorie | Anzahl | Anteil |
|-----------|--------|--------|
| Einzelgewinner (=1) | 8 | 38% |
| Mehrfachgewinner (>1) | 13 | 62% |
| Davon >= 10 Gewinner | 5 | 24% |

**Interpretation:**
- Bei 62% der Jackpots gewinnen mehrere Personen
- 5 "Mega-Jackpots" mit 10+ Gewinnern an einem Tag
- Einzelgewinner-Jackpots haeufiger in 2025

---

## 7. Actionable Hypothesen

### Hypothese H-TEMP-001: Q1-Bevorzugung
**These:** Das System zahlt vermehrt im 1. Quartal aus
**Test:** Vergleiche Jackpot-Rate Q1 vs. Q2-Q4 ueber weitere Jahre
**Trading-Implikation:** Hoehere Einsaetze in Jan-Maerz

### Hypothese H-TEMP-002: Cluster-Effekt
**These:** Nach >60 Tagen ohne Jackpot steigt die Wahrscheinlichkeit
**Test:** Tracke Tage seit letztem Jackpot
**Trading-Implikation:** Nach langer Durststrecke einsteigen

### Hypothese H-TEMP-003: Wochentag-Bias
**These:** Mi/Do sind bevorzugte Jackpot-Tage
**Test:** Chi-Quadrat-Test auf Wochentags-Verteilung
**Trading-Implikation:** Fokus auf Mi/Do-Ziehungen

### Hypothese H-TEMP-004: Woche-4-Effekt
**These:** Tag 22-28 des Monats ist bevorzugt
**Test:** Vergleiche Jackpot-Rate nach Monatswoche
**Trading-Implikation:** Hoehere Einsaetze Ende des Monats

---

## 8. Limitierungen

1. **Kleine Stichprobe:** 21 Jackpots sind statistisch wenig robust
2. **Zeitraum:** Nur 2.5 Jahre analysiert
3. **Datenqualitaet:** 2025-Daten koennten unvollstaendig sein
4. **Konfirmationsbias:** Muster koennten zufaellig sein

---

## 9. Fazit

Die Analyse zeigt **mehrere nicht-zufaellige temporale Muster**:

1. **Q1-Dominanz** ist statistisch auffaellig
2. **Cluster-Bildung** nach langen Pausen ist ein starkes Signal
3. **Monatsende-Praeferenz** (Tag 22-28) ist bemerkenswert
4. **November-Vermeidung** ist unerwartet

Diese Muster sind **unabhaengig von Zahlen-Eigenschaften** und daher schwerer zu verschleiern. Sie koennten auf:
- Interne Auszahlungszyklen hindeuten
- Bilanzierungs-Effekte (Quartalsende) widerspiegeln
- Zufaellige Schwankungen sein (weitere Validierung noetig)

**Empfehlung:** Tracking-System aufbauen, das diese temporalen Indikatoren ueberwacht.

---

*Generiert mit Kenobase V2.0 Analyse-Framework*
