# KENOBASE System Status

**Stand:** 2025-12-29
**Version:** 2.2.0 (Unified Model + Wirtschaftslogik)

---

## Aktueller Status: PARADIGMENWECHSEL KOMPLETT

### Neue Grundwahrheiten (AXIOME)

| # | Axiom | Begruendung |
|---|-------|-------------|
| A1 | System hat House-Edge | Haelfte der Einnahmen wird neu verteilt |
| A2 | Spieler nutzen Dauerscheine | Bundesland-basierte Spielermuster |
| A3 | Spiel muss attraktiv bleiben | Kleine Gewinne muessen regelmaessig kommen |
| A4 | Zahlenpaare sichern kleine Gewinne | Niedrigste Gewinnklasse wird priorisiert |
| A5 | 20 Zahlen verhalten sich pseudo-zufaellig | Jede Zahl muss in Zeitraum erscheinen |
| A6 | Gewinne werden bundeslandweit verteilt | Pro Ziehung, pro Bundesland |
| A7 | Reset-Zyklen existieren | Bis Jackpot oder Monatsende |

---

## Zwei Gruppen-Modelle

### V1: Strategy-Based Model (generate_groups.py)

| Strategie | Typ-10 Zahlen | Score |
|-----------|---------------|-------|
| Jackpot | 3,4,13,24,29,31,40,51,64,66 | 313.79 |
| Near-Miss | 3,4,11,17,18,25,31,37,45,52 | 169.23 |
| Balanced | 3,13,24,31,36,45,49,51,52,66 | 234.92 |

### V2: Pair-Focused Model (all_class_groups.json)

| Strategie | Typ-10 Zahlen | Score | Paare |
|-----------|---------------|-------|-------|
| pair_focused | 2,3,9,20,24,36,39,49,53,64 | 52.2 | 7 |
| jackpot | 2,3,4,9,20,24,25,36,49,51 | 41.2 | 5 |
| balanced | 2,3,4,9,24,25,42,49,51,61 | 36.5 | 4 |

### Unified Kern-Zahlen (beide Modelle)

```
ABSOLUTE KERN:  3, 24, 49
ERWEITERT:      2, 9, 36, 51, 64
ANTI-BIRTHDAY:  37, 41, 49, 51 (>31)
```

### Top-Paare (Co-Occurrence >210x)

```
(9,50):218   (20,36):218   (33,49):213   (2,3):211
(33,50):211  (24,40):211   (3,20):208    (53,64):208
(9,49):207   (39,64):207   (36,49):206
```

---

## Abgeschlossene Analysen

| Phase | Status | Ergebnis |
|-------|--------|----------|
| HOUSE-004 Near-Miss | DONE | 70x Switch Normal/Jackpot |
| Jahrliche Segmentierung | DONE | Nur 2023 anomal |
| Zahlen-Frequenz Kontext | DONE | Hot/Cold, Temporal, Jackpot-fav |
| Paar/Trio Global | DONE | 30 Paare, 20 Trios |
| Near-Miss Indikatoren | DONE | 20 NM + 20 JP Indikatoren |
| Gruppen-Modelle | DONE | V1 + V2 erstellt |

---

## NAECHSTE PHASE: Wirtschaftslogik-Modell

### Neue Hypothesen (zu testen)

| ID | Hypothese | Testmethode |
|----|-----------|-------------|
| WL-001 | Paare garantieren kleine Gewinne pro Gewinnklasse | Paar-Analyse pro GK separat |
| WL-002 | Bundesland-Verteilung beeinflusst Ziehungen | Regionale Daten + Bevoelkerung |
| WL-003 | Reset-Zyklen vor Jackpot erkennbar | Zeitreihen-Analyse vor GK1 |
| WL-004 | Dauerschein-Muster beeinflussen Zahlenauswahl | Beliebte Kombinationen identifizieren |
| WL-005 | Starke Paare gewinnen 1x/Monat | Backtest mit Paar-Tickets |
| WL-006 | Jackpot-Kandidaten erfuellen Einzigartigkeit | Anti-Cluster Analyse |

### Daten-Anforderungen

| Datenquelle | Zweck | Status |
|-------------|-------|--------|
| Keno_GQ_*.csv | Gewinnquoten pro Klasse | VORHANDEN |
| keno_ab_*.csv | Historische Ziehungen | VORHANDEN |
| lotto_ab_*.csv | Cross-Game Muster | VORHANDEN |
| Bundesland-Bevoelkerung | Gewinn-Verteilung | ZU LADEN |
| Dauerschein-Statistik | Spielermuster | RECHERCHE |

---

## Ziel-Metriken

| Ziel | Beschreibung | Messung |
|------|--------------|---------|
| Garantie 100EUR | Gruppe die 100EUR+ gewinnt | Backtest-Trefferquote |
| Garantie 500EUR | Gruppe die 500EUR+ gewinnt | Backtest-Trefferquote |
| Jackpot-Kandidat | Einzigartige Kombination | Uniqueness-Score |

---

## Offene Tasks fuer naechsten Loop

1. **Paar-Analyse pro Gewinnklasse** (nicht global!)
2. **Bundesland-Daten laden** (Bevoelkerung, Lotto-Verkauf)
3. **Reset-Zyklus Erkennung** (Wann kommt naechster Jackpot?)
4. **Dauerschein-Muster** (Welche Kombinationen sind beliebt?)
5. **Garantie-Modell** (Welche Gruppe gewinnt sicher X EUR?)
6. **Uniqueness-Score** (Welche Kombination ist Jackpot-wuerdig?)

---

*Generiert durch Kenobase V2.2.0 - Wirtschaftslogik-Paradigma*
