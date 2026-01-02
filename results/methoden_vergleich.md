# Methodenvergleich: NumberPoolGenerator vs Hot-Zone

Vergleich der verschiedenen Zahlen-Auswahlmethoden fuer KENO Typ 6 (6/6 = 500€).

---

## Methoden-Beschreibung

### 1. NumberPoolGenerator (Legacy V9)

**Algorithmus:**
1. Letzte 30 Ziehungen in 3 Perioden aufteilen (je 10 Ziehungen)
2. Top-11 haeufigste Zahlen pro Periode ermitteln
3. Top-20 haeufigste Zahlen gesamt ermitteln
4. Schnittmengen: (Top-11 Periode) ∩ (Top-20 Gesamt)
5. Paarweise Schnittmengen der 3 Perioden
6. Union aller Schnittmengen = Zahlenpool

**Charakteristik:**
- Komplexer Algorithmus mit Schnittmengen-Logik
- Pool-Groesse variabel (typisch 10-20 Zahlen)
- Beruecksichtigt zeitliche Persistenz (3 Perioden)

### 2. Hot-Zone W50

**Algorithmus:**
1. Letzte 50 Ziehungen nehmen
2. Top-7 haeufigste Zahlen ermitteln

**Charakteristik:**
- Einfacher Frequenz-Ansatz
- Immer exakt 7 Zahlen
- Mittelfristiges Gedaechtnis (ca. 50 Tage)

### 3. Hot-Zone W20

**Algorithmus:**
1. Letzte 20 Ziehungen nehmen
2. Top-7 haeufigste Zahlen ermitteln

**Charakteristik:**
- Kurzfristiges Gedaechtnis (ca. 20 Tage)
- Reagiert schneller auf Trends

---

## Ergebnisse: Januar 2022 - Dezember 2024

| Methode | Unique Tage | Total JP | Erfolgsquote | JP/Tag |
|---------|-------------|----------|--------------|--------|
| NumberPoolGenerator | 41 | 47 | 21/32 (65%) | 1.15 |
| Hot-Zone W50 | 47 | 65 | 23/32 (71%) | 1.38 |
| Hot-Zone W20 | 57 | 69 | 24/32 (75%) | 1.21 |

---

## Monatliche Details

| Monat | NPG Pool | NPG Days | HZ50 Days | HZ20 Days |
|-------|----------|----------|-----------|-----------|
| 2022-05 | 14 | 1 | 2 | 1 |
| 2022-06 | 15 | 0 | 2 | 1 |
| 2022-07 | 17 | 4 | 1 | 5 |
| 2022-08 | 14 | 0 | 3 | 5 |
| 2022-09 | 15 | 3 | 0 | 1 |
| 2022-10 | 17 | 3 | 3 | 4 |
| 2022-11 | 15 | 2 | 2 | 2 |
| 2022-12 | 14 | 2 | 2 | 2 |
| 2023-01 | 14 | 2 | 0 | 1 |
| 2023-02 | 18 | 1 | 0 | 6 |
| 2023-03 | 15 | 4 | 1 | 1 |
| 2023-04 | 15 | 2 | 2 | 5 |
| 2023-05 | 16 | 3 | 3 | 1 |
| 2023-06 | 14 | 1 | 2 | 5 |
| 2023-07 | 20 | 0 | 0 | 0 |
| 2023-08 | 17 | 1 | 3 | 0 |
| 2023-09 | 17 | 2 | 3 | 0 |
| 2023-10 | 16 | 1 | 0 | 0 |
| 2023-11 | 16 | 0 | 2 | 1 |
| 2023-12 | 17 | 0 | 0 | 1 |
| 2024-01 | 17 | 0 | 4 | 1 |
| 2024-02 | 19 | 3 | 2 | 3 |
| 2024-03 | 13 | 1 | 2 | 2 |
| 2024-04 | 19 | 2 | 1 | 1 |
| 2024-05 | 15 | 0 | 0 | 1 |
| 2024-06 | 17 | 1 | 1 | 5 |
| 2024-07 | 18 | 0 | 2 | 0 |
| 2024-08 | 16 | 0 | 1 | 0 |
| 2024-09 | 16 | 0 | 1 | 0 |
| 2024-10 | 17 | 1 | 0 | 1 |
| 2024-11 | 15 | 1 | 2 | 0 |
| 2024-12 | 18 | 0 | 0 | 1 |
| **TOTAL** | - | **41** | **47** | **57** |

---

## Fazit

### Ranking nach Unique Tagen:
1. **Hot-Zone W20**: 57 Tage
2. **Hot-Zone W50**: 47 Tage
3. **NumberPoolGenerator**: 41 Tage

### Ranking nach Total Jackpots:
1. **Hot-Zone W20**: 69 Jackpots
2. **Hot-Zone W50**: 65 Jackpots
3. **NumberPoolGenerator**: 47 Jackpots

### Ranking nach Erfolgsquote:
1. **Hot-Zone W20**: 75%
2. **Hot-Zone W50**: 71%
3. **NumberPoolGenerator**: 65%

### Erkenntnis

Die **Hot-Zone Methode** (einfache Frequenz-Analyse) uebertrifft den komplexeren
**NumberPoolGenerator** (Schnittmengen-Ansatz) in allen Metriken.

Dies entspricht dem **Least-Action Prinzip** (Model Law B):
Die einfachere Methode liefert bessere Ergebnisse.

---

*Erstellt: 31.12.2025*
