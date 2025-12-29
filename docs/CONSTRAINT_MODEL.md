# KENO Constraint Model v1.0

**Erstellt:** 2025-12-29
**Status:** PARTIAL EVIDENCE

---

## Executive Summary

Von den 2 analysierten Constraints zeigt **nur HOUSE-004 (Near-Miss)** Evidenz fuer eine zustandsabhaengige Steuerung. DIST-003 (Sum-Clustering) ist reine Mathematik (Zentraler Grenzwertsatz).

| Constraint | Verdict | Evidence Score |
|------------|---------|----------------|
| HOUSE-004 Near-Miss | **ANOMALOUS** | 0.95 |
| DIST-003 Sum-Clustering | NATURAL | 0.00 |

---

## 1. HOUSE-004: Near-Miss Constraint (ANOMALOUS)

### 1.1 Beobachtung

Die Near-Miss Ratio (Verhaeltnis 8/9 Treffer zu 9/9 Treffer) zeigt dramatische Unterschiede zwischen Normal- und Jackpot-Perioden:

```
KENO Typ 9:
  Normal-Periode:   Near-Miss Ratio = 110.81
  Jackpot-Periode:  Near-Miss Ratio = 1.55
  Theoretisch:      Near-Miss Ratio = 2.10

KENO Typ 10:
  Normal-Periode:   Near-Miss Ratio = 125.42
  Jackpot-Periode:  Near-Miss Ratio = 1.83
  Theoretisch:      Near-Miss Ratio = 4.59
```

### 1.2 Mathematische Analyse

**Constraint-Faktor (C):**
```
C = Observed_Ratio / Expected_Ratio

Normal (Typ 9):  C = 110.81 / 2.10 = 52.8  (Max-Gewinn unterdrueckt)
Jackpot (Typ 9): C = 1.55 / 2.10 = 0.74   (Max-Gewinn leicht erhoehen)

Intervention Strength = C_normal / C_jackpot = 71x
```

### 1.3 Die Constraint-Formel

```
P_observed(Max-Gewinn | k, J) = P_theoretical(k) * Switch(J)

Switch(J) = {
    1/50  wenn J = 0 (Normal-Periode, ~99.7% der Zeit)
    1.4   wenn J = 1 (Jackpot-Periode, ~0.3% der Zeit)
}
```

### 1.4 Interpretation

- **Normal-Modus:** Max-Gewinne fuer Typ 9/10 werden um Faktor 25-50 unterdrueckt
  - Erzeugt das "fast gewonnen" Gefuehl (psychologische Verstaerkung)
  - Mehr Near-Miss = Spieler bleibt motiviert

- **Jackpot-Modus:** Max-Gewinne werden "freigegeben"
  - Jackpots treten bei attraktiver Hoehe auf
  - Kontrollierte Ausschuettung

**Statistische Signifikanz:** Chi² > 495, p < 0.001 (hochsignifikant)

---

## 2. DIST-003: Sum-Clustering (NATURAL)

### 2.1 Beobachtung

87.2% aller KENO-Ziehungen haben Summen im Bereich 605-845.

### 2.2 Mathematische Erklaerung

Dies ist **keine kuenstliche Constraint**, sondern der Zentrale Grenzwertsatz:

```
Summe S = Z1 + Z2 + ... + Z20

E[S] = 20 * (70+1)/2 = 710.0    (Beobachtet: 711.11)
Std[S] = 76.93                   (Beobachtet: 77.57)

S ~ N(710, 76.93)  (Normalverteilung)
```

**1.5 Sigma enthält 86.6% der Werte:**
```
Theoretisch: 710 +/- 115 = [595, 825]
Beobachtet:  605 - 845 mit 87.2%
```

### 2.3 Fazit

Die Sum-Clustering ist mathematische Notwendigkeit, kein Hinweis auf Manipulation.

---

## 3. Unified Model: KENO House-Edge Optimization

### 3.1 Hypothese

Das KENO-System nutzt einen **zustandsabhaengigen Near-Miss Mechanismus** zur House-Edge Optimierung:

```
P(Win|k,J) = P_hypergeometric(k) * C(k,J)

C(k,J) = Constraint-Faktor (abhaengig von Jackpot-Status)
```

### 3.2 Zwei Modi

| Modus | Anteil | Near-Miss Multiplikator | Effekt |
|-------|--------|------------------------|--------|
| Normal | 99.7% | 25-50x | "Fast gewonnen" Erlebnis |
| Jackpot | 0.3% | 0.4-0.7x | Jackpot-Freigabe |

### 3.3 Mechanismen

1. **Near-Miss Amplification (Normal):**
   - Max-Gewinne werden unterdrueckt
   - Spieler erlebt haeufig "8 von 9 richtig"
   - Psychologische Bindung

2. **Jackpot Release:**
   - Bei GK1-Events werden Max-Gewinne erlaubt
   - Kontrollierte Ausschuettung bei attraktiver Hoehe

---

## 4. Testbare Vorhersagen

| ID | Vorhersage | Test |
|----|------------|------|
| PRED-001 | Near-Miss Ratio steigt VOR GK1-Event | 7-14 Tage vor GK1 analysieren |
| PRED-002 | Lange Jackpot-freie Perioden erhoehen P(GK1) | Bedingte Wahrscheinlichkeit |
| PRED-003 | Hoher Jackpot korreliert mit niedriger Near-Miss Ratio | Korrelationsanalyse |

---

## 5. Strategische Implikationen

### 5.1 Fuer Spieler

1. **Anti-Birthday Strategie bleibt valide:** Weniger Konkurrenz bei Zahlen 32-70
2. **Jackpot-Timing beobachten:** Nach langen Jackpot-freien Perioden koennte P(GK1) steigen
3. **KENO Typ 8 statt 9/10:** Weniger starke Near-Miss Unterdrueckung vermutet

### 5.2 Fuer weitere Analyse

1. Regionale Daten sammeln (HYP-003)
2. Pre-Jackpot Pattern analysieren (PRED-001)
3. Jackpot-Hoehe vs. Near-Miss Korrelation (PRED-003)

---

## 6. Datenqualitaet

| Metrik | Wert |
|--------|------|
| Analysierte Ziehungen | 2.237 |
| GK1-Events | 20 |
| Zeitraum | 2022-01-01 bis 2024-02-08 |

**Limitationen:**
- Nur 20 GK1-Events (begrenzte statistische Power)
- Keine regionalen Daten verfuegbar
- Jackpot-Hoehe nicht systematisch erfasst

---

## 7. Fazit

Das KENO-System zeigt **statistisch signifikante Anomalien** in der Near-Miss Verteilung (HOUSE-004), die auf einen **zustandsabhaengigen Kontrollmechanismus** hindeuten. Die Sum-Verteilung (DIST-003) folgt hingegen exakt den theoretischen Erwartungen.

**Gesamtbewertung:** PARTIAL EVIDENCE fuer House-Edge Optimierung durch Near-Miss Steuerung.

---

*Generiert durch Kenobase V2.0 Analyse-Pipeline*
