# Jackpot Selection Analysis - Zentrale Architektur

**Version:** 1.0
**Erstellt:** 2026-01-01
**Ziel:** Reverse-Engineering des KENO Jackpot-Auswahlalgorithmus

---

## 1. FORSCHUNGSFRAGE

**Kernfrage:** Wie wählt das KENO-System aus den 20 gezogenen Zahlen die 10 "Gewinner-Zahlen" aus?

**Hypothese:** Das System wählt NICHT zufällig, sondern nach bestimmten Kriterien die minimale Auszahlung sicherstellen.

**Evidenz (Kyritz-Fall):**
- Dieselben 10 Zahlen in 2 verschiedenen 20er-Ziehungen an aufeinanderfolgenden Tagen
- Wahrscheinlichkeit bei Zufall: ~1 : 4,6 Billionen
- Gewinner-Kombination hat 8 gerade Zahlen (Top 1.2%)

---

## 2. ANALYSE-ARCHITEKTUR

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    JACKPOT SELECTION ANALYSIS FRAMEWORK                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                        LAYER 0: DATEN-BASIS                            │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │ │
│  │  │ Ziehungs-   │  │ Gewinner-   │  │ Quoten/     │  │ Spieler-    │   │ │
│  │  │ Daten       │  │ Daten       │  │ Auszahlung  │  │ Verhalten   │   │ │
│  │  │ (20 Zahlen) │  │ (10 Zahlen) │  │ (EUR/Tag)   │  │ (Dauerschein│   │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│                                    ▼                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                     LAYER 1: FEATURE EXTRACTION                        │ │
│  │                                                                         │ │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐               │ │
│  │  │ Statistische  │  │ Strukturelle  │  │ Historische   │               │ │
│  │  │ Features      │  │ Features      │  │ Features      │               │ │
│  │  │               │  │               │  │               │               │ │
│  │  │ - Summe       │  │ - Gerade/Ung. │  │ - Prev. Hits  │               │ │
│  │  │ - Mean        │  │ - Decades     │  │ - Freq. Trend │               │ │
│  │  │ - Std         │  │ - Gaps        │  │ - Last 10/10  │               │ │
│  │  │ - Range       │  │ - Konsekutiv  │  │ - Cooldown    │               │ │
│  │  └───────────────┘  └───────────────┘  └───────────────┘               │ │
│  │                                                                         │ │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐               │ │
│  │  │ Temporal      │  │ Spieler-      │  │ System-       │               │ │
│  │  │ Features      │  │ Features      │  │ Features      │               │ │
│  │  │               │  │               │  │               │               │ │
│  │  │ - Wochentag   │  │ - Dauerschein │  │ - Post-JP     │               │ │
│  │  │ - Tag im Mon. │  │ - Popularität │  │ - Auszahl.Lvl │               │ │
│  │  │ - Jahreszeit  │  │ - Uniqueness  │  │ - Budget-Druck│               │ │
│  │  └───────────────┘  └───────────────┘  └───────────────┘               │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│                                    ▼                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                     LAYER 2: KOMBINATIONS-ANALYSE                      │ │
│  │                                                                         │ │
│  │  Für jeden Jackpot-Tag:                                                │ │
│  │  1. Generiere alle C(20,10) = 184.756 Kombinationen                    │ │
│  │  2. Berechne alle Features für jede Kombination                        │ │
│  │  3. Markiere die echte Gewinner-Kombination                            │ │
│  │  4. Berechne Percentile/Ranking für jedes Feature                      │ │
│  │  5. Identifiziere unterscheidende Merkmale                             │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│                                    ▼                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                     LAYER 3: MUSTER-ERKENNUNG                          │ │
│  │                                                                         │ │
│  │  Cross-Jackpot Analyse:                                                │ │
│  │  - Welche Features sind bei ALLEN Jackpots unterscheidend?             │ │
│  │  - Gibt es konsistente Regeln?                                         │ │
│  │  - Machine Learning: Decision Tree / Random Forest                     │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│                                    ▼                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                     LAYER 4: REGEL-EXTRAKTION                          │ │
│  │                                                                         │ │
│  │  Formuliere explizite Regeln:                                          │ │
│  │  - IF gerade >= 8 AND konsekutiv == 0 AND ... THEN Gewinner            │ │
│  │  - Validiere Regeln auf Out-of-Sample Daten                            │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│                                    ▼                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                     LAYER 5: STRATEGIE-ABLEITUNG                       │ │
│  │                                                                         │ │
│  │  Praktische Anwendung:                                                 │ │
│  │  - Welche 10 Zahlen aus den 20 gezogenen wählen?                       │ │
│  │  - Scoring-System für Live-Vorhersage                                  │ │
│  │  - Backtest der abgeleiteten Regeln                                    │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. DATENSTRUKTUREN

### 3.1 Jackpot-Ereignis

```python
@dataclass
class JackpotEvent:
    """Ein dokumentierter Jackpot-Tag."""
    date: str                    # "2025-10-25"
    drawn_20: list[int]          # Die 20 gezogenen Zahlen
    winner_10: list[int]         # Die 10 Gewinner-Zahlen
    region: str                  # "Brandenburg"
    city: str                    # "Kyritz"
    amount_eur: float            # 100000.0
    keno_type: int               # 10
    source: str                  # URL oder Quelle
```

### 3.2 Kombinations-Features

```python
@dataclass
class ComboFeatures:
    """Features einer 10er-Kombination."""
    combo: list[int]

    # Statistische Features
    sum: int
    mean: float
    std: float
    range: int

    # Strukturelle Features
    even_count: int
    odd_count: int
    prime_count: int
    consecutive_pairs: int
    decades_used: int
    max_per_decade: int
    gaps: list[int]
    avg_gap: float
    min_gap: int
    max_gap: int

    # Historische Features
    historical_10_10: int        # Wie oft war diese Kombi 10/10?
    avg_historical_hits: float   # Durchschn. Treffer historisch
    max_historical_hits: int     # Max Treffer historisch
    days_6plus_hits: int         # Tage mit 6+ Treffern
    days_8plus_hits: int         # Tage mit 8+ Treffern

    # Berechnete Rankings
    percentile_even: float       # Percentile für gerade Zahlen
    percentile_sum: float        # Percentile für Summe
    # ... weitere Percentiles
```

### 3.3 Analyse-Ergebnis

```python
@dataclass
class AnalysisResult:
    """Ergebnis der Analyse eines Jackpot-Tags."""
    event: JackpotEvent
    total_combinations: int      # 184756
    analyzed_combinations: int   # Kann Sample sein

    winner_features: ComboFeatures

    distinguishing_features: list[dict]  # Features im Top/Bottom 5%

    # Statistiken über alle Kombinationen
    feature_distributions: dict  # {feature_name: [min, max, mean, std]}
```

---

## 4. ZENTRALE DATEI-STRUKTUR

```
AI_COLLABORATION/
├── ARCHITECTURE/
│   └── JACKPOT_SELECTION_ANALYSIS.md    # DIESES DOKUMENT
│
├── JACKPOT_ANALYSIS/                     # NEUER ORDNER
│   ├── README.md                         # Übersicht & Status
│   ├── config.yaml                       # Analyse-Konfiguration
│   │
│   ├── data/
│   │   ├── jackpot_events.json           # Alle dokumentierten Jackpots
│   │   ├── kyritz_2025_10_25.json        # Detail-Daten pro Jackpot
│   │   └── ...
│   │
│   ├── results/
│   │   ├── layer1_features/              # Feature-Berechnungen
│   │   ├── layer2_combinations/          # Kombinations-Analysen
│   │   ├── layer3_patterns/              # Erkannte Muster
│   │   ├── layer4_rules/                 # Extrahierte Regeln
│   │   └── layer5_strategy/              # Abgeleitete Strategien
│   │
│   └── reports/
│       ├── ERKENNTNISSE.md               # Laufende Erkenntnisse
│       └── FINAL_REPORT.md               # Abschlussbericht
│
scripts/
├── jackpot_analysis/
│   ├── __init__.py
│   ├── data_loader.py                    # Lade Jackpot-Events
│   ├── feature_extractor.py              # Berechne Features
│   ├── combination_analyzer.py           # Analysiere alle Kombis
│   ├── pattern_finder.py                 # Finde Muster
│   ├── rule_extractor.py                 # Extrahiere Regeln
│   └── strategy_builder.py               # Baue Strategie
```

---

## 5. TASK-PLAN

### Phase 1: Daten-Sammlung (LAYER 0)

| Task | Beschreibung | Status | Verantwortlich |
|------|--------------|--------|----------------|
| T1.1 | Jackpot-Events dokumentieren (Kyritz + weitere) | OFFEN | KI |
| T1.2 | Quoten-Daten laden (Anzahl Gewinner pro Tag) | OFFEN | KI |
| T1.3 | Spieler-Verhaltensdaten sammeln (Dauerschein-Muster) | OFFEN | KI |

### Phase 2: Feature Engineering (LAYER 1)

| Task | Beschreibung | Status | Verantwortlich |
|------|--------------|--------|----------------|
| T2.1 | Statistische Features implementieren | DONE | - |
| T2.2 | Strukturelle Features implementieren | DONE | - |
| T2.3 | Historische Features implementieren | DONE | - |
| T2.4 | Temporale Features hinzufügen | OFFEN | KI |
| T2.5 | Spieler-Features hinzufügen | OFFEN | KI |
| T2.6 | System-Features hinzufügen | OFFEN | KI |

### Phase 3: Kombinations-Analyse (LAYER 2)

| Task | Beschreibung | Status | Verantwortlich |
|------|--------------|--------|----------------|
| T3.1 | Kyritz vollständig analysieren (184k Kombis) | TEIL | - |
| T3.2 | Weitere Jackpot-Tage identifizieren | OFFEN | KI |
| T3.3 | Alle Jackpot-Tage analysieren | OFFEN | KI |
| T3.4 | Cross-Jackpot Vergleich | OFFEN | KI |

### Phase 4: Muster-Erkennung (LAYER 3)

| Task | Beschreibung | Status | Verantwortlich |
|------|--------------|--------|----------------|
| T4.1 | Konsistente Features identifizieren | OFFEN | KI |
| T4.2 | Decision Tree trainieren | OFFEN | KI |
| T4.3 | Feature Importance berechnen | OFFEN | KI |

### Phase 5: Regel-Extraktion (LAYER 4)

| Task | Beschreibung | Status | Verantwortlich |
|------|--------------|--------|----------------|
| T5.1 | Explizite Regeln formulieren | OFFEN | KI |
| T5.2 | Regeln auf Out-of-Sample validieren | OFFEN | KI |

### Phase 6: Strategie (LAYER 5)

| Task | Beschreibung | Status | Verantwortlich |
|------|--------------|--------|----------------|
| T6.1 | Scoring-System entwickeln | OFFEN | KI |
| T6.2 | Backtest durchführen | OFFEN | KI |
| T6.3 | Finale Strategie dokumentieren | OFFEN | KI |

---

## 6. KI-SCHNITTSTELLE

### 6.1 Wie KIs beitragen können

Jede KI kann an spezifischen Perspektiven arbeiten:

| Perspektive | Beschreibung | Input | Output |
|-------------|--------------|-------|--------|
| **Statistisch** | Statistische Anomalien finden | Ziehungsdaten | Statistische Features |
| **Strukturell** | Zahlen-Muster analysieren | 20er/10er Kombis | Struktur-Features |
| **Temporal** | Zeitliche Muster finden | Datum, Wochentag | Temporal-Features |
| **Adversarial** | System-Verhalten modellieren | Quoten, Auszahlungen | System-Features |
| **Spieler** | Spieler-Perspektive | Dauerschein-Muster | Spieler-Features |
| **ML** | Machine Learning anwenden | Alle Features | Klassifikator |

### 6.2 Beitrags-Format

```yaml
# Jeder KI-Beitrag sollte folgendes Format haben:

perspektive: "Statistisch"
ki_id: "Claude-1"
datum: "2026-01-01"

analyse:
  beschreibung: "Analyse der Summenverteilung"
  methodik: "Berechnung der Summen aller 184k Kombinationen"

ergebnisse:
  - feature: "sum"
    gewinner_wert: 334
    gewinner_percentile: 27.5
    interpretation: "Gewinner hat unterdurchschnittliche Summe"

  - feature: "even_count"
    gewinner_wert: 8
    gewinner_percentile: 99.0
    interpretation: "Gewinner hat extrem viele gerade Zahlen"

schlussfolgerung: |
  Die Gewinner-Kombination hat:
  1. Unterdurchschnittliche Summe (27.5 Percentile)
  2. Überdurchschnittlich viele gerade Zahlen (99 Percentile)

naechste_schritte:
  - "Prüfen ob Summen-Regel konsistent über alle Jackpots ist"
  - "Gerade/Ungerade Verteilung bei anderen Jackpots analysieren"
```

### 6.3 Zentrale Ergebnis-Aggregation

Alle KI-Beiträge werden in `AI_COLLABORATION/JACKPOT_ANALYSIS/results/` gespeichert und können von anderen KIs gelesen werden.

---

## 7. BISHERIGE ERKENNTNISSE (KYRITZ)

### 7.1 Stark unterscheidende Merkmale (Top/Bottom 5%)

| Merkmal | Gewinner | Durchschnitt | Percentile | Richtung |
|---------|----------|--------------|------------|----------|
| Gerade Zahlen | 8 | 6.0 | 99.0% | HOCH |
| Max. hist. Treffer | 10 | 7.6 | 100% | HOCH |
| Historische 10/10 | 1 | 0.0 | 100% | HOCH |

### 7.2 Bemerkenswerte Merkmale (Top/Bottom 10%)

| Merkmal | Gewinner | Durchschnitt | Percentile | Richtung |
|---------|----------|--------------|------------|----------|
| Ungerade Zahlen | 2 | 4.0 | 8.6% | NIEDRIG |
| Tage mit 8+ Hits | 2 | 0.8 | 94.6% | HOCH |
| Min. Abstand | 2 | 1.3 | 91.9% | HOCH |

### 7.3 Hypothesen

1. **H1: Gerade-Regel** - Das System bevorzugt Kombinationen mit >= 8 geraden Zahlen
2. **H2: Reife-Regel** - Das System wählt Kombinationen die bereits nahe 10/10 waren
3. **H3: Keine-Konsekutive-Regel** - Das System vermeidet aufeinanderfolgende Zahlen
4. **H4: Niedrige-Summe-Regel** - Das System bevorzugt niedrigere Summen

---

## 8. NÄCHSTE SCHRITTE

1. **Ordnerstruktur anlegen** - `AI_COLLABORATION/JACKPOT_ANALYSIS/`
2. **Weitere Jackpot-Events finden** - Quoten-Daten durchsuchen
3. **Feature-Extractor modularisieren** - Als wiederverwendbares Script
4. **Cross-Jackpot Analyse** - Prüfen ob Muster konsistent sind
5. **ML-Modell trainieren** - Decision Tree für Klassifikation

---

*Dieses Dokument ist die zentrale Referenz für alle KIs die an der Jackpot Selection Analysis arbeiten.*
