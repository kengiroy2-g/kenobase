# Kenobase V2.0

Wissenschaftlich fundiertes Lottozahlen-Analysesystem mit Physics-Integration basierend auf Self-Organized Criticality und Model Laws.

## Features

- **Physics Layer**: Integration von Model Laws A/B/C (Stabilitaet, Least-Action, Criticality)
- **Avalanche-Theorie**: Anti-Avalanche-Strategie zur Risikobewertung
- **Multi-Game Support**: KENO, EuroJackpot, Lotto 6aus49
- **Pattern-Analyse**: Haeufigkeiten, Duo/Trio-Erkennung
- **Backtest-Framework**: Historische Validierung von Strategien
- **Multiple Output-Formate**: JSON, CSV, HTML, Markdown, YAML

## Installation

### Voraussetzungen

- Python 3.10+
- pip

### Setup

```bash
# Repository klonen
git clone <repo-url> keno_base
cd keno_base

# Virtual Environment erstellen
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

## Schnellstart

### Analyse durchfuehren

```bash
python scripts/analyze.py analyze \
  --data data/raw/keno/KENO.csv \
  --config config/default.yaml \
  --format json \
  --output output/results.json
```

### Kombination validieren

```bash
python scripts/analyze.py validate \
  --combination 1,2,3,4,5,6 \
  --precision 0.7
```

### Backtest ausfuehren

```bash
python scripts/analyze.py backtest \
  --data data/raw/keno/KENO.csv \
  --periods 12 \
  --output output/backtest.json
```

### Konfiguration anzeigen

```bash
python scripts/analyze.py info --config config/default.yaml
```

## CLI-Referenz

```
kenobase [OPTIONS] COMMAND [ARGS]

Commands:
  analyze   Fuehrt vollstaendige Analyse-Pipeline aus
  backtest  Fuehrt historischen Backtest durch
  validate  Validiert Kombination gegen Physics-Constraints
  info      Zeigt Konfigurationsinformationen an

Options:
  --version  Show version
  --help     Show help
```

### analyze

```
Options:
  -c, --config PATH      Pfad zur Konfigurationsdatei [default: config/default.yaml]
  -d, --data PATH        Pfad zur Eingabe-CSV-Datei (required)
  -o, --output PATH      Pfad zur Ausgabedatei
  -f, --format FORMAT    Ausgabeformat: json|csv|html|markdown|yaml [default: json]
  -s, --start-date DATE  Startdatum (YYYY-MM-DD)
  -e, --end-date DATE    Enddatum (YYYY-MM-DD)
  --combination TEXT     Spielkombination fuer Pattern-Analyse
  -v, --verbose          Verbosity (-v INFO, -vv DEBUG)
```

### backtest

```
Options:
  -c, --config PATH   Pfad zur Konfigurationsdatei
  -d, --data PATH     Pfad zur Eingabe-CSV-Datei (required)
  -p, --periods INT   Anzahl der Backtest-Perioden [default: 10]
  -o, --output PATH   Pfad zur Ausgabedatei
  -v, --verbose       Verbosity
```

### validate

```
Options:
  -c, --config PATH      Pfad zur Konfigurationsdatei
  --combination TEXT     Spielkombination, z.B. "1,2,3,4,5,6" (required)
  -p, --precision FLOAT  Geschaetzte Precision pro Zahl [default: 0.7]
  -v, --verbose          Verbosity
```

## Projektstruktur

```
keno_base/
├── kenobase/                    # Hauptpaket (18 Python-Module)
│   ├── __init__.py
│   ├── core/                    # Kern-Module
│   │   ├── __init__.py
│   │   ├── config.py            # YAML-Config-Loader
│   │   ├── data_loader.py       # CSV/JSON-Import
│   │   ├── number_pool.py       # Zahlenpool-Generierung
│   │   └── combination_engine.py # Kombinationslogik
│   │
│   ├── analysis/                # Analyse-Module
│   │   ├── __init__.py
│   │   ├── frequency.py         # Haeufigkeitsanalyse
│   │   └── pattern.py           # Duo/Trio-Erkennung
│   │
│   ├── physics/                 # Physics Layer (Model Laws)
│   │   ├── __init__.py
│   │   ├── model_laws.py        # Laws A/B/C Implementation
│   │   ├── avalanche.py         # SOC und Anti-Avalanche
│   │   └── metrics.py           # Hurst, Autocorrelation
│   │
│   └── pipeline/                # Pipeline-Orchestrierung
│       ├── __init__.py
│       ├── runner.py            # Haupt-Pipeline
│       ├── least_action.py      # Pipeline-Auswahl (Gesetz B)
│       ├── output_formats.py    # JSON/CSV/HTML/MD/YAML Export
│       └── validation_metrics.py # Metriken-Berechnung
│
├── tests/                       # Test-Suite (18 Test-Dateien)
│   ├── conftest.py
│   ├── test_config.py
│   └── unit/
│       ├── test_data_loader.py
│       ├── test_number_pool.py
│       ├── test_combination_engine.py
│       ├── test_frequency.py
│       ├── test_pattern.py
│       ├── test_model_laws.py
│       ├── test_avalanche.py
│       ├── test_metrics.py
│       ├── test_runner.py
│       ├── test_least_action.py
│       ├── test_output_formats.py
│       ├── test_backtest.py
│       └── test_validation_metrics.py
│
├── config/                      # Konfigurationen
│   └── default.yaml             # Standard-Konfiguration
│
├── scripts/                     # CLI-Scripts
│   └── analyze.py               # Haupt-CLI
│
├── data/                        # Daten (nicht im Git)
│   ├── raw/                     # Original-Ziehungsdaten
│   └── processed/               # Verarbeitete Daten
│
├── requirements.txt             # Python Dependencies
└── README.md                    # Diese Datei
```

## Physics Layer

### Model Law A: Stabilitaet

Testet ob ein Muster ueber Variationen (Zeit, Datenquellen, Parameter) stabil bleibt.

```python
# Ein Pattern gilt als "Gesetz" wenn stability >= 0.9
stability = 1 - (std(results) / mean(results))
is_law = stability >= 0.9
```

**Anwendung**: Filtert Noise von echten Regularitaeten. Nur Muster mit hoher Stabilitaet werden fuer Vorhersagen verwendet.

### Model Law B: Least-Action

Waehlt die einfachste Pipeline bei gleicher Performance.

```python
action = complexity + instability - performance
# Bevorzuge Pipeline mit minimaler Action
```

**Anwendung**: Vermeidet Overfitting durch Komplexitaets-Penalty.

### Model Law C: Criticality

Identifiziert "kritische" Ziehungen mit hohem Risiko.

```python
sensitivity = 1 - |prob - 0.5| * 2
criticality = sensitivity * regime_complexity

# Levels: LOW < 0.3, MEDIUM < 0.5, HIGH < 0.7, CRITICAL >= 0.7
```

**Anwendung**: CRITICAL-Ziehungen werden als "No-Bet" Zone markiert.

### Avalanche-Theorie

Berechnet Verlustwahrscheinlichkeit fuer Kombinationen.

```python
theta = 1 - precision^n  # n = Anzahl Picks

# States:
# SAFE:     theta < 0.50
# MODERATE: 0.50 <= theta < 0.75
# WARNING:  0.75 <= theta < 0.85
# CRITICAL: theta >= 0.85 (No-Bet Zone)
```

**Beispiel**: 6er-Kombination mit 70% Precision: theta = 1 - 0.7^6 = 0.88 (CRITICAL)

## Konfiguration

Die Konfiguration erfolgt ueber YAML-Dateien. Standard: `config/default.yaml`

### Wichtige Einstellungen

```yaml
# Aktiviertes Spiel
active_game: keno  # keno|eurojackpot|lotto

# Physics Layer
physics:
  enable_model_laws: true
  stability_threshold: 0.90      # Schwelle fuer Gesetz A
  criticality_warning: 0.70      # Warning-Level
  criticality_critical: 0.85     # Critical-Level (No-Bet)
  enable_avalanche: true
  anti_avalanche_mode: true

# Analyse-Parameter
analysis:
  duo_min_occurrences: 3         # Min. Vorkommen fuer Duo-Erkennung
  trio_min_occurrences: 2        # Min. Vorkommen fuer Trio-Erkennung
  zehnergruppen_max_per_group: 3 # Max. Zahlen pro Zehnergruppe
  windows: [5, 10, 20, 50]       # Rolling Windows

# Spielkonfiguration
games:
  keno:
    numbers_range: [1, 70]
    numbers_to_draw: 20
  eurojackpot:
    numbers_range: [1, 50]
    numbers_to_draw: 5
    bonus_range: [1, 12]
  lotto:
    numbers_range: [1, 49]
    numbers_to_draw: 6
```

## Tests

```bash
# Alle Tests ausfuehren
pytest tests/ -v

# Mit Coverage
pytest tests/ --cov=kenobase --cov-report=html

# Nur Unit-Tests
pytest tests/unit/ -v

# Spezifischer Test
pytest tests/unit/test_model_laws.py -v
```

## Dependencies

- pandas>=2.0.0
- numpy>=1.24.0
- pyyaml>=6.0.0
- pydantic>=2.0.0
- scipy>=1.11.0
- click>=8.1.0
- pytest>=7.4.0

Vollstaendige Liste: siehe `requirements.txt`

## Referenzen

### Physik-Konzepte

- Bak, P. (1987). "Self-organized criticality: 1/f noise"
- Sornette, D. (2003). "Why Stock Markets Crash"
- Prigogine, I. (1977). "Self-Organization in Nonequilibrium Systems"

### Architektur-Dokumente

- ADR-018: Model Laws Alpha/Gamma
- ADR-020: Criticality-Based FP Detection
- ADR-021: Avalanche Critique/Combi Theory

## Lizenz

Proprietaer - Alle Rechte vorbehalten.

## Version

2.0.0
