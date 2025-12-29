# Phase 4: Wirtschaftslogik-Modell

**Erstellt:** 2025-12-29
**Status:** PLANUNG
**Prioritaet:** HOCH

---

## Uebergeordnetes Ziel

Ein dynamisches Modell entwickeln das:
1. **Garantierte kleine Gewinne** (100-500 EUR) pro Ziehung ermoeglicht
2. **Jackpot-Kandidaten** identifiziert (einzigartige Kombinationen)
3. **Reset-Zyklen** erkennt (optimales Timing)

---

## Grundaxiome (als WAHRHEIT gesetzt)

```
A1: System hat House-Edge (50% Redistribution)
A2: Spieler nutzen Dauerscheine (Bundesland-Pattern)
A3: Spiel muss attraktiv bleiben (kleine Gewinne regelmaessig)
A4: Zahlenpaare sichern kleine Gewinne (niedrigste GK priorisiert)
A5: 20 Zahlen pseudo-zufaellig (jede muss in Periode erscheinen)
A6: Gewinne bundeslandweit verteilt (pro Ziehung)
A7: Reset-Zyklen existieren (bis Jackpot/Monatsende)
```

---

## Neue Hypothesen

### WL-001: Paar-Garantie pro Gewinnklasse

**These:** Starke Zahlenpaare garantieren mindestens 1x/Monat einen Gewinn in der niedrigsten Klasse.

**Test:**
```python
# Fuer jedes starke Paar (Co-Occ > 200):
# - Zaehle wie oft beide Zahlen in einer Ziehung erscheinen
# - Berechne: Wie oft gewinnt ein Typ-2 Ticket mit diesem Paar?
# - Pruefe: Gewinnt jedes Paar mind. 1x/Monat?
```

**Daten:** Keno_GQ_*.csv (Gewinnklassen), KENO_ab_*.csv (Ziehungen)

**Erwartung:** >90% der starken Paare gewinnen 1x/Monat

---

### WL-002: Bundesland-Verteilung

**These:** Gewinnverteilung korreliert mit Bundesland-Bevoelkerung und Lotto-Verkaufszahlen.

**Test:**
```python
# Lade Bundesland-Daten:
# - Bevoelkerung pro BL
# - Lotto-Umsatz pro BL (falls verfuegbar)
# - Anzahl Gewinner pro BL (aus Keno_GQ)
#
# Korrelation: Gewinner_BL ~ Bevoelkerung_BL
```

**Daten:** Bundesland-Statistik, Keno_GQ_*.csv

**Erwartung:** r > 0.8 Korrelation

---

### WL-003: Reset-Zyklus Erkennung

**These:** Vor einem Jackpot (GK1-Event) gibt es erkennbare Muster in der Zahlenverteilung.

**Test:**
```python
# Analysiere 7-14 Tage vor jedem der 20 GK1-Events:
# - Entropy der Zahlenverteilung
# - Varianz der Paar-Haeufigkeiten
# - Near-Miss Ratio Trend
#
# Finde: Gibt es einen "Aufbau" vor dem Jackpot?
```

**Daten:** 10-9_KGDaten_gefiltert.csv (GK1-Events), KENO_ab_*.csv

**Erwartung:** Signifikante Veraenderung 3-7 Tage vor GK1

---

### WL-004: Dauerschein-Muster

**These:** Bestimmte Zahlenkombinationen werden haeufiger gespielt (Dauerschein-Muster) und das System muss diese bedienen.

**Test:**
```python
# Identifiziere "beliebte" Kombinationen:
# - Geburtstagszahlen (1-31)
# - Konsekutive (1,2,3,4,5,6)
# - Diagonalen, Muster
#
# Pruefe: Erscheinen diese haeufiger als erwartet?
```

**Daten:** KENO_ab_*.csv, Lotto_ab_*.csv

**Erwartung:** Beliebte Muster erscheinen 5-10% haeufiger

---

### WL-005: Paar-Gewinn-Frequenz

**These:** Tickets mit starken Paaren gewinnen mindestens 1x pro Monat einen kleinen Betrag.

**Test:**
```python
# Backtest mit 12 Monaten:
# - Erstelle virtuelles Ticket mit Top-Paar
# - Simuliere taegliches Spielen
# - Zaehle: Wie oft Gewinn pro Monat?
#
# Fuer alle Top-20 Paare
```

**Daten:** KENO_ab_2018.csv (2237 Ziehungen)

**Erwartung:** Jedes Top-Paar gewinnt 2-4x/Monat

---

### WL-006: Jackpot-Einzigartigkeit

**These:** Jackpot-Kombinationen erfuellen bestimmte "Einzigartigkeit"-Kriterien.

**Test:**
```python
# Analysiere alle 20 GK1-Events:
# - Keine beliebten Muster (Anti-Birthday)
# - Decade-Verteilung (gut verteilt)
# - Keine konsekutiven Paare
# - Sum in extremem Bereich?
#
# Berechne: Uniqueness-Score
```

**Daten:** 10-9_KGDaten_gefiltert.csv

**Erwartung:** Jackpot-Kombis haben Uniqueness > 0.7

---

## Paar-Analyse pro Gewinnklasse (WL-007)

**These:** Paare haben unterschiedliche Staerke je nach Gewinnklasse.

**Analyse-Matrix:**

| Gewinnklasse | Zahlen getippt | Treffer noetig | Paar-Relevanz |
|--------------|----------------|----------------|---------------|
| GK10 (Typ 10) | 10 | 10/10 | Sehr niedrig |
| GK9 (Typ 10) | 10 | 9/10 | Niedrig |
| GK8 (Typ 10) | 10 | 8/10 | Mittel |
| ... | ... | ... | ... |
| GK2 (Typ 2) | 2 | 2/2 | SEHR HOCH |

**Test:**
```python
# Fuer jede Gewinnklasse separat:
# - Berechne Paar-Co-Occurrence
# - Identifiziere GK-spezifische starke Paare
# - Vergleiche mit globalen Paaren
```

---

## Dynamisches Garantie-Modell (ZIEL)

### Modell-Architektur

```
┌─────────────────────────────────────────────────────────┐
│                GARANTIE-MODELL V1.0                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  INPUT:                                                  │
│  ├── Aktuelles Datum                                    │
│  ├── Tage seit letztem Jackpot                         │
│  ├── Aktuelle Jackpot-Hoehe                            │
│  └── Letzte 30 Ziehungen                                │
│                                                          │
│  BERECHNUNG:                                             │
│  ├── Reset-Zyklus-Phase bestimmen                       │
│  ├── Paar-Scoring basierend auf GK                      │
│  ├── Bundesland-Gewichtung                              │
│  └── Uniqueness-Score fuer Jackpot                      │
│                                                          │
│  OUTPUT:                                                 │
│  ├── Gruppe fuer 100EUR Garantie (Typ 6-8)             │
│  ├── Gruppe fuer 500EUR Garantie (Typ 8-10)            │
│  └── Jackpot-Kandidat (Typ 10, unique)                 │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Gewinn-Schwellen

| Ziel | KENO Typ | Treffer | Quote (ca.) |
|------|----------|---------|-------------|
| 100 EUR | Typ 6 | 5/6 | 100 EUR |
| 100 EUR | Typ 7 | 5/7 | 12 EUR (8x) |
| 500 EUR | Typ 8 | 6/8 | 100 EUR |
| 500 EUR | Typ 9 | 7/9 | 500 EUR |
| Jackpot | Typ 10 | 10/10 | 1.000.000 EUR |

---

## Task-Reihenfolge

### Phase 4.1: Daten-Vorbereitung (2h)
- [ ] Bundesland-Bevoelkerungsdaten laden
- [ ] Keno_GQ Gewinnklassen-Struktur verstehen
- [ ] Cross-Game Daten (Lotto, EuroJackpot) laden

### Phase 4.2: Paar-Analyse pro GK (4h)
- [ ] WL-001: Paar-Garantie Test implementieren
- [ ] WL-007: GK-spezifische Paar-Staerken berechnen
- [ ] Vergleich global vs. GK-spezifisch

### Phase 4.3: Bundesland-Analyse (3h)
- [ ] WL-002: Verteilung nach Bevoelkerung testen
- [ ] Regionale Muster in Gewinnzahlen identifizieren
- [ ] Dauerschein-Hypothese pruefen

### Phase 4.4: Reset-Zyklus Analyse (3h)
- [ ] WL-003: Pre-Jackpot Muster finden
- [ ] WL-006: Uniqueness-Score entwickeln
- [ ] Timing-Modell erstellen

### Phase 4.5: Garantie-Modell (4h)
- [ ] WL-005: Backtest Paar-Gewinn-Frequenz
- [ ] 100 EUR Garantie-Gruppe optimieren
- [ ] 500 EUR Garantie-Gruppe optimieren
- [ ] Jackpot-Kandidat-Generator

### Phase 4.6: Validation (2h)
- [ ] Walk-Forward Backtest
- [ ] Cross-Validation mit anderen Spielen
- [ ] Dokumentation

---

## Erfolgskriterien

| Kriterium | Schwelle | Messung |
|-----------|----------|---------|
| 100EUR Garantie | >80% Monate | Backtest |
| 500EUR Garantie | >50% Monate | Backtest |
| Jackpot-Timing | >60% korrekt | Pre-GK1 Erkennung |
| Paar-Prediction | >75% Treffer | GK2/GK3 Gewinne |

---

## Dateien

| Datei | Zweck |
|-------|-------|
| scripts/analyze_pairs_per_gk.py | WL-001, WL-007 |
| scripts/analyze_bundesland.py | WL-002 |
| scripts/analyze_reset_cycles.py | WL-003 |
| scripts/analyze_dauerschein.py | WL-004 |
| scripts/backtest_pairs.py | WL-005 |
| scripts/calculate_uniqueness.py | WL-006 |
| scripts/generate_guarantee.py | Garantie-Modell |

---

*Phase 4 Plan - Kenobase V2.2.0*
