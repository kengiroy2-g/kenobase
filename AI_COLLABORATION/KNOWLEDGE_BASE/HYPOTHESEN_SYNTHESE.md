# Kenobase V2.2 - Hypothesen-Synthese

**Erstellt:** 2025-12-30
**Quelle:** HYPOTHESES_CATALOG.md (Single Source of Truth)
**Zweck:** Entscheidungshilfe fuer taegliche Empfehlungen

---

## Executive Summary

### Statistik

| Status | Anzahl | Prozent |
|--------|--------|---------|
| BESTAETIGT | 13 | 54% |
| FALSIFIZIERT | 5 | 21% |
| NICHT_SIGNIFIKANT | 4 | 17% |
| OFFEN | 2 | 8% |
| **GESAMT** | **24** | 100% |

### Kern-Erkenntnisse (BESTAETIGT)

1. **WL-003: Jackpot-Cooldown** (-66% ROI)
   - Nach GK10_10 Jackpot: 30 Tage NICHT spielen
   - Grund: System "spart" nach grosser Auszahlung

2. **HYP_CYC_001: 28-Tage-Zyklus** (+422% Differenz)
   - FRUEH-Phase (Tag 1-14): +364% ROI (Typ 9)
   - SPAET-Phase (Tag 15-28): -58% ROI (Typ 9)
   - Empfehlung: Nur in FRUEH-Phase spielen

3. **WL-001: Paar-Garantie** (100%)
   - 30/30 starke Paare gewinnen >90% der Monate
   - Top-Paar: (21,42) mit 93.2% Garantie

4. **WL-006: Jackpot-Einzigartigkeit** (90.9%)
   - Jackpots haben systematisch hohe Uniqueness-Scores
   - Anti-Birthday-Zahlen (>31) sind bevorzugt

---

## Handlungsmatrix

### SPIELEN (Gruene Zone)

| Bedingung | Begründung | Hypothese |
|-----------|------------|-----------|
| FRUEH-Phase (Tag 1-14 im Monat) | +422% besser als SPAET | HYP_CYC_001 |
| >30 Tage nach Jackpot | -66% ROI in Cooldown | WL-003 |
| Typ 9 bevorzugen | Beste ROI ueber alle Tests | Multiple |
| Starke Paare verwenden | 100% Garantie auf Gewinne | WL-001, WL-005 |

### NICHT SPIELEN (Rote Zone)

| Bedingung | Begründung | Hypothese |
|-----------|------------|-----------|
| 0-30 Tage nach Jackpot | System spart, -66% ROI | WL-003 |
| SPAET-Phase (Tag 15-28) | Negative ROI | HYP_CYC_001 |
| Beliebte Kombinationen | House-Edge maximiert | WL-006 |

### IGNORIEREN (Falsifiziert)

| Hypothese | Grund |
|-----------|-------|
| HYP-002: Jackpot-Zyklen | CV=0.95, keine Periodizitaet |
| HYP-005: Dekaden-Affinitaet | 0 signifikante Paare |
| HYP-008: 111-Prinzip | Keine Korrelation nachweisbar |
| DIST-003: Sum-Manipulation | Erklaerbar durch Zentralen Grenzwertsatz |
| PRED-001/002/003: Pre-GK1 | p>0.05, nicht vorhersagbar |

---

## Optimale Tickets (aus Backtests)

### Empfohlene Typ-9 Tickets

| Ticket | ROI (Backtest) | Quelle |
|--------|----------------|--------|
| [3,9,10,20,24,36,49,51,64] | +351% | Position-Rules |
| [3,7,36,43,48,51,58,61,64] | V2-Birthday-Avoidance | Super Model |

### Kern-Zahlen (ueber alle Analysen)

```
ABSOLUT:    3, 24, 49
ERWEITERT:  2, 9, 36, 51, 64
ANTI-BIRTHDAY: 37, 41, 49, 51 (>31)
```

### Top-Paare (Co-Occurrence >210x)

```
(9,50):218   (20,36):218   (33,49):213
(2,3):211    (33,50):211   (24,40):211
```

---

## Axiome (Unverhandelbar)

| ID | Axiom | Wirtschaftliche Begruendung |
|----|-------|----------------------------|
| A1 | House-Edge | 50% Redistribution gesetzlich garantiert |
| A2 | Dauerscheine | Spieler nutzen feste Kombinationen |
| A3 | Attraktivitaet | Kleine Gewinne MUESSEN regelmaessig sein |
| A4 | Paar-Garantie | Zahlenpaare sichern Spielerbindung |
| A5 | Pseudo-Zufall | Jede Zahl muss in Periode erscheinen |
| A6 | Regionale Verteilung | Gewinne pro Bundesland |
| A7 | Reset-Zyklen | System "spart" nach Jackpots |

---

## Offene Fragen (2)

| ID | Hypothese | Prioritaet | Naechster Schritt |
|----|-----------|------------|-------------------|
| WL-002 | Bundesland-Verteilung | HOCH | Korrelation mit Bevoelkerung testen |
| WL-004 | Dauerschein-Muster | MITTEL | Beliebte Kombinationen identifizieren |

---

## Taegliche Empfehlungs-Logik

```python
# Pseudo-Code fuer daily_recommendation.py

def sollte_spielen(datum, letzter_jackpot):
    """Entscheidet ob heute gespielt werden sollte."""

    # 1. Jackpot-Cooldown pruefen (WL-003)
    tage_seit_jackpot = (datum - letzter_jackpot).days
    if tage_seit_jackpot <= 30:
        return False, "Cooldown-Phase nach Jackpot"

    # 2. Monats-Phase pruefen (HYP_CYC_001)
    tag_im_monat = datum.day
    if tag_im_monat > 14:
        return False, "SPAET-Phase (Tag 15-28)"

    return True, "FRUEH-Phase, kein Cooldown"

def empfohlenes_ticket():
    """Generiert empfohlenes Ticket."""
    return {
        "typ": 9,
        "zahlen": [3, 7, 36, 43, 48, 51, 58, 61, 64],
        "grund": "V2-Birthday-Avoidance + Kern-Zahlen"
    }
```

---

## Wichtige Warnungen

1. **ROI-Erwartung:** Trotz bestaetiger Hypothesen ist House-Edge ~50%.
   Backtests mit korrigierten Quoten zeigen negative ROI (-43% bis -67%).

2. **Sample Size:** Einige Hypothesen (HYP_002, HYP_CYC_006) sind wegen
   zu geringer Datenmenge nicht signifikant, nicht weil sie falsch sind.

3. **Overfitting-Risiko:** Position-Rules mit +351% ROI muessen
   Walk-Forward validiert werden (Out-of-Sample).

4. **Quoten-Quelle:** Single Source of Truth ist `kenobase/core/keno_quotes.py`.
   Fruehere Analysen nutzten falsche Quoten.

---

## Referenzen

- **Hypothesen-Katalog:** `AI_COLLABORATION/KNOWLEDGE_BASE/HYPOTHESES_CATALOG.md`
- **Quoten:** `kenobase/core/keno_quotes.py`
- **Daily Script:** `scripts/daily_recommendation.py`
- **Backtest-Ergebnisse:** `results/cycles_comprehensive_analysis.json`

---

*Synthese-Dokument V1.0 - Generiert aus HYPOTHESES_CATALOG.md*
