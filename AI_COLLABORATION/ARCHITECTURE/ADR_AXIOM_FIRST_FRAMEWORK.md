# ADR: Axiom-First Framework

**Status:** ACCEPTED
**Date:** 2025-12-30
**Author:** EXECUTOR (TASK AXIOM-001)

## Context

Kenobase V2.0 benoetigt ein Analyse-Framework das NICHT auf naiver Pattern-Suche basiert.
Das deutsche Lotterie-System wurde von Top-Ingenieuren konzipiert und ist ein Milliarden-Geschaeft.
Einfache statistische Muster wurden ABSICHTLICH eliminiert.

**Kern-Erkenntnis:** Lotterien sind WIRTSCHAFTLICHE Systeme, keine rein mathematischen Zufallssysteme.

## Decision

### Paradigma: Axiom-First statt Pattern-First

**VERBOTEN (Pattern-First):**
```
Daten -> Statistische Muster suchen -> Interpretation
```

**PFLICHT (Axiom-First):**
```
Wirtschaftslogik (Axiome) -> Vorhersagen ableiten -> Daten testen
```

### Die 7 Axiome

| ID | Name | Wirtschaftliche Begruendung |
|----|------|----------------------------|
| A1 | House-Edge | 50% Redistribution gesetzlich garantiert |
| A2 | Dauerscheine | Spieler nutzen feste Kombinationen |
| A3 | Attraktivitaet | Kleine Gewinne MUESSEN regelmaessig sein |
| A4 | Paar-Garantie | Zahlenpaare sichern Spielerbindung |
| A5 | Pseudo-Zufall | Jede Zahl muss in Periode erscheinen |
| A6 | Regionale Verteilung | Gewinne pro Bundesland (DATAREQ-001) |
| A7 | Reset-Zyklen | System "spart" nach Jackpots |

### Falsifizierbare Predictions (3 pro Axiom = 21 total)

#### A1: House-Edge Stability
- **P1.1:** ROI ueber 12 Monate: -45% bis -55% (Median ~-50%)
- **P1.2:** Kein Spieler-Typ erzielt dauerhaft > 0% ROI
- **P1.3:** House-Edge Varianz < 5% (Std) zwischen Quartalen

#### A2: Dauerscheine
- **P2.1:** Bestimmte Kombinationen erscheinen haeufiger in Tippscheinen
- **P2.2:** "Birthday-Zahlen" (1-31) sind ueberrepraesentiert in Tipps
- **P2.3:** Gewinnquoten fuer populaere Kombinationen sind niedriger

#### A3: Attraktivitaet
- **P3.1:** Kleine Gewinne (Typ 6-8) treten regelmaessig auf
- **P3.2:** "Beinahe-Treffer" (5 von 6) sind haeufiger als IID erwarten laesst
- **P3.3:** Mindestens 1 Gewinner pro Woche in jeder Gewinnklasse

#### A4: Paar-Garantie
- **P4.1:** Bestimmte Zahlenpaare erscheinen signifikant oefter zusammen
- **P4.2:** "Beliebte" Paare (wie 7-11, 3-7) haben erhoehte Kopplung
- **P4.3:** Paar-Frequenz korreliert mit Dauerschein-Popularitaet

#### A5: Pseudo-Zufall
- **P5.1:** Jede Zahl erscheint mindestens 1x in Periode N (z.B. 20 Ziehungen)
- **P5.2:** Maximale "Luecke" einer Zahl ist begrenzt (z.B. < 50 Ziehungen)
- **P5.3:** Frequenz-Verteilung ist enger als IID Poisson

#### A6: Regionale Verteilung (DATAREQ-001)
- **P6.1:** Gewinne pro Bundesland korrelieren mit Bevoelkerung
- **P6.2:** Keine Region hat signifikant mehr Jackpots pro Kopf
- **P6.3:** Grosse Gewinne verteilen sich gleichmaessig ueber Zeit

#### A7: Reset-Zyklen
- **P7.1:** ROI sinkt 30 Tage nach Jackpot um > 20%
- **P7.2:** "Heisse" Zahlen vor Jackpot werden "kalt" danach
- **P7.3:** System-weite Gewinnquote sinkt post-Jackpot

### Train/Test Split

- **Train:** Alle Daten vor 2024-01-01
- **Test:** 2024-01-01 bis heute
- **Regel:** Rules werden im Train "gemined" und im Test FROZEN evaluiert

### Nullmodell-Strategien

| Prediction-Typ | Nullmodell |
|---------------|------------|
| Frequenz-Tests | IID Poisson/Binomial |
| Zeitreihen | Permutation (Block-preserving) |
| Korrelationen | Schedule-preserving Shuffle |
| Post-Event | Fake-Lag Kontrolle |

### Multiple Testing Guardrails

- Max 21 primaere Tests (7 Axiome x 3 Predictions)
- Benjamini-Hochberg (BH) FDR-Korrektur bei alpha=0.05
- Keine sekundaere "p-hacking" Iterationen

### EuroJackpot als Negativ-Kontrolle

EuroJackpot ist NICHT Teil des deutschen Oekosystems:
- Internationale Kontrolle
- Andere Spielerschaft
- Eigene Wirtschaftslogik

EuroJackpot dient als **externer Kontrollkanal** (negative control).
Deutsche Axiome (A2, A4, A6) sollten bei EuroJackpot NICHT gelten.

## Implementation

### Core-Modul: `kenobase/core/axioms.py`

```python
@dataclass
class Axiom:
    id: str           # "A1", "A2", ...
    name: str         # "House-Edge", ...
    description: str
    predictions: list[Prediction]

@dataclass
class Prediction:
    id: str           # "P1.1", "P1.2", ...
    description: str
    metric: str       # "ROI", "Frequency", ...
    threshold: float
    direction: str    # "less", "greater", "between"
    null_model: str   # "IID", "Permutation", ...
```

### CLI: `scripts/validate_axiom_predictions.py`

```bash
python scripts/validate_axiom_predictions.py \
  --axiom A1 \
  --output results/axiom_validation.json
```

## Acceptance Criteria

- [ ] 7 Axiome formal definiert in `axioms.py`
- [ ] 21 Predictions mit Metriken/Thresholds
- [ ] Train/Test Split implementiert
- [ ] Nullmodell-Funktionen vorhanden
- [ ] Unit-Tests mit >= 80% Coverage
- [ ] CLI-Script lauffaehig

## Consequences

### Positive
- Falsifizierbare Hypothesen statt Spekulation
- Wirtschaftslogik als Fundament
- Robuste Validierung durch Nullmodelle
- Train/Test verhindert Overfitting

### Negative
- A6 (Regionale Verteilung) erfordert externe Daten
- Komplexer als naive Pattern-Suche
- Ergebnisse koennten "langweilig" sein (House-Edge dominiert)

## Related ADRs
- ADR_PREDICTION_MODEL.md
- ADR-018: Model Laws A/B/C
- ADR-021: Avalanche Critique Combi Theory

## Files
- `kenobase/core/axioms.py` - Axiom/Prediction Definitionen
- `scripts/validate_axiom_predictions.py` - CLI Validierung
- `tests/unit/test_axioms.py` - Unit Tests
