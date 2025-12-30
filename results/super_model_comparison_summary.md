# Super-Model Vergleich: Original vs V1/V2

**Datum:** 2025-12-30
**Ziel:** Birthday-Avoidance Erkenntnis in Strategie umsetzen

---

## Ausgangslage

Die High-Wins Analyse zeigte:
- **KENO Typ10/10 Jackpots** vermeiden Birthday-Zahlen (1-31) um **-10.5%**
- Bei Jackpots unter-repraesentiert: 6, 5, 16, 1, 25, 20, 8, 27
- Bei Jackpots ueber-repraesentiert: 51, 58, 61, 7, 36, 13, 43, 15

---

## Getestete Strategien

### Original (Baseline)
- Standard OPTIMAL_TICKETS + Anti-Birthday (>31 bevorzugen)
- Bewaehrte Komponenten aus 3-KI Synthese

### V1: Aggressive Birthday-Avoidance
- Jackpot-unterrepraesentierte Zahlen hart excludieren
- Jackpot-Favoriten stark boosten
- Mindestens 60% hohe Zahlen (>31)

### V1.1: Adaptive Birthday-Avoidance
- Birthday-Vermeidung nur wenn Jackpot "faellig" (>15 Tage)
- Dynamische Gewichtung

### V2: Birthday-Signal Strategy
- Birthday-Ratio der letzten Ziehung als Mode-Indikator
- <40%: Jackpot-optimiertes Ticket
- 40-50%: Standard-Ticket
- >50%: Conservative Ticket

---

## Ergebnisse

### Typ 8 (Einsatz 1 EUR)

| Modell | ROI | High-Wins |
|--------|-----|-----------|
| **Original** | **+115.8%** | **15** |
| V1 (Jackpot) | +76.1% | 10 |
| V1 (Balanced) | +6.8% | 6 |
| V1.1 | +115.8% | 15 |
| V2 | +98.9% | 13 |

### Typ 9 (Einsatz 1 EUR)

| Modell | ROI | High-Wins |
|--------|-----|-----------|
| **Original** | **+228.4%** | **5** |
| V1 (Jackpot) | +176.0% | 4 |
| V1 (Balanced) | +174.6% | 4 |
| V1.1 | +228.4% | 5 |
| V2 | +156.3% | 3 |

### Typ 10 (Einsatz 1 EUR)

| Modell | ROI | High-Wins |
|--------|-----|-----------|
| **Original** | **+224.7%** | **10** |
| V1 (Jackpot) | +83.4% | 6 |
| V1 (Balanced) | +85.1% | 6 |
| V1.1 | +224.7% | 10 |
| V2 | +135.6% | 5 |

---

## V2 Mode-Analyse (Detailliert)

V2 wechselt das Ticket basierend auf der Birthday-Ratio der letzten Ziehung:

### Typ 8
| Mode | Spiele | ROI |
|------|--------|-----|
| normal | 904 | **+173.0%** |
| conservative | 298 | +14.1% |
| jackpot | 379 | **-11.3%** |

### Typ 9
| Mode | Spiele | ROI |
|------|--------|-----|
| normal | 904 | +184.7% |
| conservative | 298 | **+196.0%** |
| jackpot | 379 | +57.3% |

### Typ 10
| Mode | Spiele | ROI |
|------|--------|-----|
| normal | 904 | **+237.1%** |
| conservative | 298 | +10.7% |
| jackpot | 379 | **-8.2%** |

---

## Schlussfolgerungen

### 1. Birthday-Avoidance ist KEINE profitable Strategie
- Der Effekt ist bei Jackpots real (-10.5%)
- ABER: Jackpots sind zu selten (31 in 5+ Jahren)
- Zu aggressive Vermeidung schadet dem ROI

### 2. Das Original-Modell bleibt das Beste
- Konsistente Tickets performen besser als Mode-Wechsel
- Die bewaehrten OPTIMAL_TICKETS sind robust optimiert
- Einfachheit schlaegt Komplexitaet

### 3. "Jackpot-Chasing" funktioniert nicht
- V2's "jackpot" Mode hat NEGATIVEN ROI bei Typ 8 und 10
- Das System ist nicht so einfach zu "ueberlisten"
- Birthday-Avoidance erklaert vergangene Jackpots, hilft aber nicht bei zukuenftigen

### 4. Wertvolle Negative Erkenntnis
- Die Axiom-First Analyse war korrekt: Das System ist sophistiziert
- Einfache Pattern-Exploitation funktioniert nicht
- Der Befund bestaetigt die House-Edge Absicherung

---

## Empfehlung

**Behalte das Original-Modell bei.**

Die Birthday-Avoidance Erkenntnis ist wertvoll fuer das **Verstaendnis** des Systems,
aber nicht fuer eine **Strategie-Aenderung**.

Das Original-Modell mit seinen Komponenten:
- jackpot_warning (30-Tage Cooldown)
- exclusion_rules (Position-basiert)
- temporal (Monats-Start/Ende)
- weekday (Wochentags-Favoriten)
- sum_context (Summen-basiert)
- pair_synergy (Starke Paare)
- correlated_absence (Korrelierte Abwesenheiten)
- anti_birthday (>31 bevorzugen)

...bleibt die beste verfuegbare Strategie.

---

## Dateien

- `scripts/super_model_synthesis.py` - Original (BEHALTEN)
- `scripts/super_model_v1_birthday.py` - V1 Aggressive (ARCHIV)
- `scripts/super_model_v1_1_adaptive.py` - V1.1 Adaptive (ARCHIV)
- `scripts/super_model_v2_birthday_signal.py` - V2 Signal (ARCHIV)
- `results/super_model_v1_comparison.json` - V1 Ergebnisse
- `results/super_model_v1_1_comparison.json` - V1.1 Ergebnisse
- `results/super_model_v2_comparison.json` - V2 Ergebnisse
