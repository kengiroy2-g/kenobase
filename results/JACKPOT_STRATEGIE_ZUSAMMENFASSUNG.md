# JACKPOT-STRATEGIE: 30-Tage Konvergenz-Analyse

**Erstellt:** 2026-01-02
**Basierend auf:** 1460 Ziehungen (2022-2026)

---

## Executive Summary

### Kern-Erkenntnis

Die Hypothese wurde **TEILWEISE BESTAETIGT**:

| Metrik | Wert |
|--------|------|
| Pool eliminiert selektiv Nicht-JP-Zahlen | **+3.9% Selektivitaet** |
| Top-Beispiele zeigen | **+85% Selektivitaet** |
| Neue Jackpot-Zahlen kommen hinzu | **3.06 pro Ereignis** |
| Tage mit >= 6 Treffer im Pool | **507 von 1460 (34.7%)** |

### Die Wahrheit

```
MIT 1 TICKET (Top-6 Zahlen):
  - 0 mal 6/6 in 864 Spieltagen
  - ROI: -62.7%

MIT ALLEN KOMBINATIONEN aus Top-12:
  - 6.7% Treffer-Rate pro Tag
  - Aber: 924 Tickets noetig = 924€ pro Spieltag
  - ROI: immer noch negativ
```

---

## Detaillierte Analyse

### 1. Pool-Evolution Hypothese

**BESTAETIGT:** Der dynamische Pool "konvergiert" zum Jackpot:

| Metrik | Wert |
|--------|------|
| Treffer-Retention | 42.4% (Jackpot-Zahlen bleiben) |
| Nicht-JP-Elimination | 61.5% (falsche Zahlen verschwinden) |
| Selektivitaet | +3.9% (eliminiert mehr falsche als richtige) |

**Aber:** Die Konvergenz ist zu schwach fuer konsistente Gewinne.

### 2. Treffer-Verteilung nach Top-N

Bei Konvergenz >= 80 und Timing >= 50:

| Top-N | 6/6 Rate | 5/6 Rate | Tickets noetig |
|-------|----------|----------|----------------|
| Top-6 | 0.00% | 0.69% | 1 |
| Top-7 | 0.23% | 1.74% | 7 |
| Top-8 | 0.46% | 3.94% | 28 |
| Top-9 | 1.16% | 6.94% | 84 |
| Top-10 | 2.20% | 11.00% | 210 |
| Top-12 | **6.71%** | 20.25% | 924 |

### 3. Kosten-Analyse

**Fuer 6.71% Treffer-Rate (Top-12):**

```
Kosten pro Spieltag:        924€ (alle C(12,6) Kombinationen)
Erwarteter Gewinn bei 6/6:  500€
Break-Even Rate noetig:     924€ / 500€ = 184.8%

ERGEBNIS: Mathematisch unmoeglich profitabel!
```

**Fuer 1 Ticket Strategie (Top-6):**

```
864 Spieltage im Backtest
Kosten: 864€
Gewinne: 322€ (nur 5/6, 4/6, 3/6 Treffer)
Netto: -542€
ROI: -62.7%
```

---

## Optimale Strategie (relativ beste Option)

### NICHT JEDEN TAG SPIELEN!

Nur spielen wenn ALLE Bedingungen erfuellt:

| Bedingung | Wert | Grund |
|-----------|------|-------|
| Konvergenz-Score | >= 85 | Pool-Qualitaet |
| Timing-Score | >= 55 | FRUEH-Phase oder Tag 24-28 |
| Stabilitaet | >= 0.5 | Pool hat sich stabilisiert |

### Empfohlene Spieltage

Basierend auf Backtest:

```
FRUEH-Phase (Tag 1-14 des Monats):
  + 20 Punkte Timing-Bonus
  + 364% ROI-Differenz vs SPAET

Tag 24-28 des Monats:
  + 15 Punkte Timing-Bonus
  + Anti-Momentum Fenster

Mittwoch:
  + 10 Punkte Timing-Bonus

NICHT SPIELEN:
  - Tag 15-23 ohne anderen Bonus
  - 0-7 Tage nach Jackpot (Cooldown-Beginn)
```

### Wenn man spielen moechte:

**Budget-Variante (84€):**
```
- Top-9 Zahlen aus Pool nehmen
- Alle C(9,6) = 84 Kombinationen spielen
- 1.16% Chance auf 6/6 pro Spieltag
```

**Standard-Variante (210€):**
```
- Top-10 Zahlen aus Pool nehmen
- Alle C(10,6) = 210 Kombinationen spielen
- 2.20% Chance auf 6/6 pro Spieltag
```

---

## Schlussfolgerung

### Was die Analyse zeigt:

1. **Die Pool-Evolution funktioniert** - Das System eliminiert tatsaechlich mehr "falsche" als "richtige" Zahlen

2. **Aber nicht stark genug** - Die Selektivitaet von +3.9% reicht nicht fuer konsistente Gewinne

3. **Top-6 allein ist zu wenig** - Null 6/6 Treffer bei 864 Versuchen

4. **Top-12 ist zu teuer** - 924€ pro Spieltag fuer 6.7% Treffer-Rate

### Die ehrliche Antwort:

```
FRAGE: Kann man mit diesem Algorithmus in 30 Tagen einen Jackpot knacken?

ANTWORT:
- Mit 1 Ticket: Praktisch unmoeglich (0% in 864 Versuchen)
- Mit Top-12 Tickets: ~6.7% pro Tag, aber ~28.000€ Kosten fuer 30 Tage
- Erwarteter Break-Even: Nie (House Edge dominiert)
```

### Alternative Nutzung:

Der Algorithmus kann dennoch nuetzlich sein fuer:

1. **Timing-Optimierung** - WANN man spielt ist wichtiger als WAS
2. **Pool-Reduktion** - 70 → 17 Zahlen ist wertvoll
3. **Pattern-Filterung** - BAD_PATTERNS vermeiden
4. **Wartezeit-Optimierung** - Nicht jeden Tag spielen

---

## Technische Details

### Konvergenz-Score Berechnung:

```python
convergence = (
    avg_score * 0.3 +
    (1 - bad_patterns / 17) * 30 +
    good_patterns * 5 +
    stability * 20 +
    timing * 0.5
)
```

### Timing-Score Berechnung:

```python
timing = 50  # Basis
if day_of_month <= 14:
    timing += 20  # FRUEH-Phase
else:
    timing -= 15  # SPAET-Phase
if weekday == 2:  # Mittwoch
    timing += 10
if 24 <= day_of_month <= 28:
    timing += 15
```

### Dateien:

- `scripts/analyze_30day_jackpot_window.py`
- `scripts/backtest_convergence_algorithm.py`
- `scripts/analyze_top_number_precision.py`
- `scripts/test_pool_evolution_hypothesis.py`

---

*Analyse abgeschlossen: 2026-01-02*
