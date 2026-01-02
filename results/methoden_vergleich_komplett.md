# Methodenvergleich: Alle drei Methoden

Vergleich aller Zahlen-Auswahlmethoden fuer KENO Typ 6 (6/6 = 500€).

---

## Methoden-Beschreibung

### 1. NumberPoolGenerator (Legacy V9)

**Algorithmus:**
1. Letzte 30 Ziehungen in 3 Perioden aufteilen (je 10 Ziehungen)
2. Top-11 haeufigste Zahlen pro Periode ermitteln
3. Top-20 haeufigste Zahlen gesamt ermitteln
4. Schnittmengen: (Top-11 Periode) ∩ (Top-20 Gesamt)
5. Paarweise Schnittmengen der 3 Perioden
6. Top-7 aus Pool (nach Haeufigkeit sortiert)

**Charakteristik:** DYNAMISCH - Aendert sich jeden Monat

### 2. HypothesisSynthesizer

**Algorithmus:**
1. Lade Ergebnisse von HYP-007, HYP-010, HYP-011, HYP-012
2. Berechne gewichteten Score pro Zahl (1-70)
3. Gewichtung:
   - HYP-007 (Patterns): 0.1 (nicht signifikant)
   - HYP-010 (Odds): 0.3
   - HYP-011 (Temporal): 0.3 (Feiertags-Effekt signifikant)
   - HYP-012 (Stake): 0.3 (Auszahlung signifikant)
4. Top-7 nach Combined Score

**Charakteristik:** STATISCH - Immer dieselben Zahlen: **[36, 64, 14, 24, 42, 60, 57]**

### 3. Hot-Zone W50 / W20

**Algorithmus:**
1. Letzte N Ziehungen nehmen (50 oder 20)
2. Top-7 haeufigste Zahlen ermitteln

**Charakteristik:** DYNAMISCH - Aendert sich jeden Monat

---

## Ergebnisse: Januar 2022 - Dezember 2024

| Methode | Typ | Unique Tage | Total JP | Erfolgsquote | JP/Tag |
|---------|-----|-------------|----------|--------------|--------|
| NumberPoolGenerator | Dynamisch | 47 | 59 | 24/32 (75%) | 1.26 |
| HypothesisSynthesizer | **Statisch** | 57 | 57 | 24/32 (75%) | 1.00 |
| Hot-Zone W50 | Dynamisch | 47 | 65 | 23/32 (71%) | 1.38 |
| Hot-Zone W20 | Dynamisch | 57 | 69 | 24/32 (75%) | 1.21 |

---

## Ranking

### Nach Unique Tagen:
1. **Hot-Zone W20**: 57 Tage
2. **Hot-Zone W50**: 47 Tage
3. **NumberPoolGenerator**: 47 Tage
4. **HypothesisSynthesizer**: 57 Tage

### Nach Total Jackpots:
1. **Hot-Zone W20**: 69 Jackpots
2. **Hot-Zone W50**: 65 Jackpots
3. **NumberPoolGenerator**: 59 Jackpots
4. **HypothesisSynthesizer**: 57 Jackpots

### Nach Erfolgsquote:
1. **Hot-Zone W20**: 75%
2. **Hot-Zone W50**: 71%
3. **NumberPoolGenerator**: 75%
4. **HypothesisSynthesizer**: 75%

---

## Erkenntnisse

### HypothesisSynthesizer Problem

Der HypothesisSynthesizer hat das **schlechteste Ergebnis** weil:

1. **Statische Zahlen**: Verwendet immer dieselben 7 Zahlen ([36, 64, 14, 24, 42, 60, 57])
2. **Keine Adaption**: Reagiert nicht auf aktuelle Trends
3. **Hypothesen-basiert**: Scores basieren auf allgemeinen Eigenschaften, nicht auf aktuelle Haeufigkeit

### Dynamische Methoden gewinnen

Die **Hot-Zone Methoden** (W20, W50) sind am besten weil:

1. **Dynamisch**: Passen sich monatlich an
2. **Frequenz-basiert**: Nutzen aktuelle Ziehungstrends
3. **Einfach**: Weniger Komplexitaet = weniger Fehlerquellen

### Least-Action Prinzip bestaetigt

Die einfachste Methode (Hot-Zone) liefert die besten Ergebnisse.
Der komplexeste Ansatz (HypothesisSynthesizer mit 4 Hypothesen) schneidet am schlechtesten ab.

---

*Erstellt: 31.12.2025*
