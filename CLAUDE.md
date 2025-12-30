# CLAUDE.md - Kenobase V2.0

Dieses Dokument dient als Arbeits- und Umsetzungsleitfaden fuer das neue Kenobase-Projekt, basierend auf Physik-inspirierten Konzepten aus dem v_master_Criticality Framework.

---

## 0. LOOP V4 QUICK START

**Loop V4 starten:**
```powershell
.\scripts\autonomous_loop_v4.ps1 `
  -Team alpha `
  -PlanFile "AI_COLLABORATION/PLANS/kenobase_v2_complete_plan.yaml"
```

**Wichtige Dateien:**
- **Plan:** `AI_COLLABORATION/PLANS/kenobase_v2_complete_plan.yaml` (24 Tasks, 42h)
- **Plan (Axiom-First / Ecosystem):** `AI_COLLABORATION/PLANS/kenobase_axiom_first_ecosystem_plan.yaml`
- **Supervisor:** `AI_COLLABORATION/SUPERVISOR.md`
- **Module Map:** `AI_COLLABORATION/ARCHITECTURE/MODULE_MAP.md`
- **Config:** `config/default.yaml`

**Phase Workflow:**
```
ARCHITECT (KI #1) -> PROXY -> EXECUTOR (KI #2) -> PROXY -> VALIDATOR (KI #3) -> DONE
```

---

## 0.1 Backlog & Issue Tracking

**WICHTIG - Vor jeder Arbeit lesen:**
```
AI_COLLABORATION/BACKLOG/KENOBASE_ISSUES.md
```

Diese Datei enthaelt:
- Alle offenen Issues mit Prioritaet
- Acceptance Criteria pro Issue
- Geschaetzter Aufwand
- Status-Tracking (OFFEN → IN_PROGRESS → DONE)

**Workflow:**
1. Issue aus Backlog waehlen (hoechste Prioritaet zuerst)
2. Status auf IN_PROGRESS setzen
3. Issue bearbeiten
4. Tests + Validation
5. Status auf DONE setzen, Ergebnis dokumentieren

---

## 0.2 GitHub Repository

**Repository:** https://github.com/kengiroy2-g/kenobase

**Git Setup:**
- Repository initialized: 2025-12-27
- Remote: `origin` → https://github.com/kengiroy2-g/kenobase.git
- GitHub CLI (gh) version 2.83.1 installed

**Git Workflow:**

```powershell
# Status pruefen
git status

# Aenderungen stagen
git add .

# Commit erstellen
git commit -m "feat(module): description"

# Zu GitHub pushen
git push origin main

# Von GitHub pullen
git pull origin main
```

**Branch-Strategie:**
```
main        - Production-ready Code
develop     - Integration Branch (optional)
feature/*   - Feature-Branches
bugfix/*    - Bugfix-Branches
```

**Commit-Konventionen:**
```
feat(scope):     Neues Feature
fix(scope):      Bugfix
refactor(scope): Code-Refactoring
docs(scope):     Dokumentation
test(scope):     Tests
chore(scope):    Build/Config
```

**Beispiele:**
```powershell
git commit -m "feat(physics): add Model Law C criticality scoring"
git commit -m "fix(backtest): use game-specific thresholds"
git commit -m "docs(claude): add GitHub workflow section"
```

---

## 0.3 Super Model V2: Birthday-Avoidance Strategie (EMPFOHLEN)

**WICHTIG: Validiert auf 2025 Out-of-Sample Daten (363 Ziehungen)**

### Kern-Erkenntnis

Bei KENO-Jackpots werden Birthday-Zahlen (1-31) systematisch vermieden (-10.5% Effekt).
Die V2-Strategie nutzt diesen Effekt mit empirisch optimierten Tickets.

### 2025 Out-of-Sample Ergebnisse

| Typ | Original ROI | V2 Birthday-Av. ROI | Verbesserung |
|-----|-------------|---------------------|--------------|
| Typ 8 | -14.6% | **+261.4%** | +276% |
| Typ 9 | +209.6% | **+1545.7%** | +1336% |
| Typ 10 | +77.7% | **+305.5%** | +228% |

**EMPFEHLUNG: Typ 9 mit Birthday-Avoidance liefert beste Performance!**

### Empfohlene Tickets (V2)

```python
BIRTHDAY_AVOIDANCE_TICKETS_V2 = {
    8: [3, 36, 43, 48, 51, 58, 61, 64],
    9: [3, 7, 36, 43, 48, 51, 58, 61, 64],    # BESTE WAHL
    10: [3, 7, 13, 36, 43, 48, 51, 58, 61, 64],
}

# Jackpot-Favoriten (hohe Frequenz bei Jackpots)
JACKPOT_FAVORITES_V2 = [51, 58, 61, 7, 36, 13, 43, 15, 3, 48]

# Zahlen die bei Jackpots vermieden werden
JACKPOT_AVOID_V2 = [6, 68, 27, 5, 16, 1, 25, 20, 8]
```

### Taegliche Empfehlung generieren

```powershell
# Standard-Empfehlung (Typ 8, 9, 10)
python scripts/daily_recommendation.py

# Nur Typ 9 (beste Performance)
python scripts/daily_recommendation.py --type 9

# Dual-Strategie (V2 + Original)
python scripts/daily_recommendation.py --dual

# Alle Typen (6-10)
python scripts/daily_recommendation.py --all

# Mit JSON-Export
python scripts/daily_recommendation.py --save
```

### Wichtige Hinweise

1. **Nur Typ 8-10 profitabel**: Typ 2-7 haben negativen ROI
2. **Jackpot-Cooldown beachten**: 30 Tage nach Jackpot reduzierte Wahrscheinlichkeit
3. **Dual-Strategie moeglich**: Original + V2 Ticket fuer Diversifikation

### Relevante Scripts

| Script | Zweck |
|--------|-------|
| `scripts/daily_recommendation.py` | Taegliche Ticket-Empfehlung |
| `scripts/super_model_synthesis.py` | Super Model mit V2 Komponenten |
| `scripts/test_dual_2025.py` | 2025 Out-of-Sample Test |
| `scripts/test_dual_oos_2024.py` | 2024 Out-of-Sample Test |

### Datenquellen

- **Aktuell**: `data/raw/keno/KENO_ab_2022_bereinigt.csv` (2022-2025)
- **Historisch**: `Keno_GPTs/Kenogpts_2/Basis_Tab/KENO_ab_2018.csv` (2018-2024)

---

## 1. Executive Summary

**Projektziel:** Wissenschaftlich fundiertes Lottozahlen-Analysesystem mit Criticality-basierter Mustererkennung und Anti-Avalanche-Strategie.

**Was ist Kenobase V2?**
- Modernisierung des alten KENO-Analyseprojekts
- Integration von Physik-Konzepten (Self-Organized Criticality, Model Laws)
- Saubere Architektur mit Tests, Configs und klarem Datenfluss
- Falsifizierbare Hypothesen statt Spekulation

**Kern-Innovation:** Anwendung der drei Model Laws (A/B/C) auf Lottozahlen-Analyse.

---

## 1.1 KRITISCH: Analyse-Paradigma (MUSS ANWENDEN)

### VERBOTEN: Pattern-First Ansatz

```
FALSCH: Daten → Statistische Muster suchen → Interpretation
```

**Warum Pattern-First NICHT funktioniert:**
- Das System wurde von Top-Ingenieuren und Mathematikern konzipiert
- Es ist ein MILLIARDEN-Geschaeft, finanziert allein von Spielern
- Einfache statistische Muster wurden ABSICHTLICH eliminiert
- Jede naive Pattern-Suche ist zum Scheitern verurteilt

### PFLICHT: Axiom-First Ansatz

```
RICHTIG: Wirtschaftslogik (Axiome) → Vorhersagen ableiten → Daten testen
```

**Die entscheidende Erkenntnis:**

> Lotterien sind KEINE mathematischen Zufallssysteme.
> Sie sind WIRTSCHAFTLICHE Systeme mit harten Constraints.

**Kern-Fragen die ZUERST beantwortet werden muessen:**
1. Welche WIRTSCHAFTLICHEN Zwaenge hat das System?
2. Was MUSS das System garantieren um profitabel zu bleiben?
3. Wie wird House-Edge UND Attraktivitaet gleichzeitig sichergestellt?
4. WANN sollte man spielen? (nicht: welche Zahlen)

### Die 7 Axiome (unverhandelbar)

| ID | Axiom | Wirtschaftliche Begruendung |
|----|-------|----------------------------|
| A1 | **House-Edge** | 50% Redistribution gesetzlich garantiert |
| A2 | **Dauerscheine** | Spieler nutzen feste Kombinationen |
| A3 | **Attraktivitaet** | Kleine Gewinne MUESSEN regelmaessig sein |
| A4 | **Paar-Garantie** | Zahlenpaare sichern Spielerbindung |
| A5 | **Pseudo-Zufall** | Jede Zahl muss in Periode erscheinen |
| A6 | **Regionale Verteilung** | Gewinne pro Bundesland |
| A7 | **Reset-Zyklen** | System "spart" nach Jackpots |

### Durchbruch-Beispiel: WL-003 Jackpot-Cooldown

```
Axiom A1 (House-Edge) + Axiom A7 (Reset-Zyklen)
    ↓
Vorhersage: Nach Jackpot = System muss sparen = weniger Gewinne
    ↓
Test: 30 Tage nach Jackpot → -66% ROI bei KENO
    ↓
Strategie: NICHT spielen in Cooldown-Phase
    ↓
Ergebnis: +466.6% ROI
```

---

## 1.2 Oekosystem-Theorie (Deutsche Lotterie)

### Grundprinzip

Die deutschen Lotterien (KENO, Lotto 6aus49, Gluecksspirale, Toto) bilden ein **Oekosystem**:
- Gleiche Spieler spielen MEHRERE Lotterien
- Spieler verwenden AEHNLICHE Zahlenmuster
- Das Gesamtsystem muss House-Edge und Attraktivitaet balancieren
- Die Spiele koennten sich GEGENSEITIG beeinflussen

### Hypothese: Cross-Lotterie-Korrelation

```
Wenn Spieler X bei KENO die Zahlen 7-11-23-31 spielt,
spielt er wahrscheinlich bei Lotto 6aus49: 7-11-23-31-??-??

Das System WEISS das (Dauerschein-Daten).
Also koennten die Ziehungen KORRELIERT sein.
```

### Moegliche Muster-Typen

| Typ | Beschreibung | Beispiel |
|-----|--------------|----------|
| **Zeitversetzt** | Muster bei Spiel A erscheint X Tage spaeter bei Spiel B | KENO-Gewinnzahlen → 3 Tage → Lotto-Gewinnzahlen |
| **Invers** | Wenn Spiel A "heiss", ist Spiel B "kalt" | KENO Jackpot → Lotto vermeidet aehnliche Zahlen |
| **Komplementaer** | Zahlen werden zwischen Spielen "aufgeteilt" | Niedrige Zahlen bei KENO, hohe bei Lotto |
| **Zyklisch** | Periodische Muster ueber Wochen/Monate | Monatliche Reset-Zyklen |

### WICHTIG: EuroJackpot separat

EuroJackpot ist NICHT Teil des deutschen Oekosystems:
- Internationale Kontrolle (nicht deutsche Lotterie)
- Andere Spielerschaft
- Eigene Wirtschaftslogik

→ EuroJackpot MUSS separat analysiert werden.

---

## 2. Projektzusammenfassung

### 2.1 Altes Projekt (Rekonstruktion)

| Aspekt | Status |
|--------|--------|
| **Zweck** | KENO/Lotto-Analyse zur Mustererkennung |
| **Hypothese** | RNG-Manipulation durch Tippschein-Analyse |
| **Methoden** | 111-Prinzip, Zahlenpool-Generierung, Duo/Trio/Quatro-Analyse |
| **Probleme** | Hardcodierte Pfade, keine Tests, bekannte Bugs, keine Metriken |
| **Versionen** | V1-V9 fragmentiert, inkonsistente Logik |
| **Status** | DEPRECATED - wird durch V2.0 ersetzt |

### 2.2 Neues Projekt (Ziel)

| Aspekt | Ziel |
|--------|------|
| **Architektur** | Modulare Pipeline mit klaren Verantwortlichkeiten |
| **Hypothesen** | Falsifizierbar, mit Acceptance-Kriterien |
| **Tests** | >80% Coverage, Integrationstests |
| **Config** | YAML-basiert, keine hardcodierten Werte |
| **Metriken** | Precision, Recall, Stabilitaet, Criticality-Score |
| **Physik** | Model Laws A/B/C, Avalanche-Theorie integriert |

---

## 3. Arbeitsprinzipien

### 3.0 AXIOM-FIRST (MUSS) – Paradigma fuer Anti-Pattern-Systeme

**MUSS-Anforderung:** Bei Analysen, die von einem *anti-detektierten* Lotterie-Design ausgehen, wird **Axiom-First**
als Standard-Vorgehen **verpflichtend** angewendet.

**Definition (kurz):** Wir starten nicht mit "Pattern-Suche", sondern mit expliziten **Axiomen/Annahmen** ueber das System
(z.B. House-Edge-Stabilitaet, Regime/Statefulness, Anti-Detection), leiten daraus **falsifizierbare Vorhersagen** ab und
testen diese mit robusten Nullmodellen + Out-of-Sample-Validierung.

**Regeln (MUSS):**
1. **Axiome schriftlich fixieren** (A0..An) bevor Code/Tests gebaut werden.
2. Pro Axiom: **2-3 konkrete, falsifizierbare Predictions** (welche Metrik, welcher Effekt, welcher Lag/Window).
3. **Nullmodell + Negative Controls** definieren (Permutation/Block-Permutation, Schedule-preserving, "fake lags").
4. **Multiple Testing Guardrails**: begrenztes Feature-Set + BH/FDR oder hierarchisches Testing; keine "p-hacking" Iterationen.
5. **Train->Test**: Regeln/Modelle werden im Train gemined und **eingefroren** im Test evaluiert.
6. **EuroJackpot separat behandeln**: nicht als "Teil des deutschen Oekosystems" modellieren; nur als externer Kontrollkanal.

### 3.1 LOOP v4 Workflow

Jede Iteration folgt diesem Zyklus:

```
(1) INSPECT   - Dateien/Code lesen, Zustand erfassen
(2) SYNTHESIZE - Erkenntnisse zusammenfuehren, Muster erkennen
(3) PLAN      - Naechste Schritte definieren, Risiken markieren
(4) EXECUTE   - Code schreiben, Tests ausfuehren
(5) VERIFY    - Ergebnisse validieren, Metriken pruefen
(6) DOCUMENT  - Aenderungen dokumentieren, ADRs schreiben
(7) NEXT LOOP - Naechste Iteration starten
```

### 3.2 Coding-Standards

```python
# Sprache: Python 3.10+
# Formatierung: Black, isort
# Linting: Ruff
# Type Hints: REQUIRED (mypy strict)
# Docstrings: Google-Style

# Beispiel:
def calculate_stability(
    history: list[float],
    window: int = 4
) -> tuple[float, bool]:
    """
    Berechnet die Stabilitaet einer Zahlenreihe (Gesetz A).

    Args:
        history: Liste von historischen Werten
        window: Fenstergroesse fuer Rolling-Berechnung

    Returns:
        Tuple aus (stability_score, is_law)
        - stability_score: 0.0-1.0
        - is_law: True wenn score >= 0.9
    """
    ...
```

### 3.3 Commit-Regeln

```
Format: <type>(<scope>): <subject>

Types:
  feat     - Neues Feature
  fix      - Bugfix
  refactor - Code-Refactoring
  docs     - Dokumentation
  test     - Tests hinzufuegen/aendern
  chore    - Build/Config-Aenderungen

Beispiele:
  feat(pipeline): add criticality scoring to analysis
  fix(duos): correct calculation for overlapping sets
  docs(adr): add ADR-001 for Model Laws integration
```

### 3.4 Branch-Strategie

```
main        - Production-ready Code
develop     - Integration Branch
feature/*   - Feature-Branches
bugfix/*    - Bugfix-Branches
release/*   - Release-Kandidaten
```

---

## 4. Architektur-Ueberblick

### 4.1 Module und Verantwortlichkeiten

```
kenobase/
├── core/                      # Kern-Logik
│   ├── __init__.py
│   ├── config.py              # YAML-Config-Loader
│   ├── data_loader.py         # CSV/JSON-Import
│   ├── number_pool.py         # Zahlenpool-Generierung
│   └── combination_engine.py  # Kombinationslogik
│
├── analysis/                  # Analyse-Module
│   ├── __init__.py
│   ├── frequency.py           # Haeufigkeitsanalyse
│   ├── pattern.py             # Muster-Erkennung (Duos/Trios)
│   ├── stability.py           # Gesetz A: Stabilitaetstest
│   └── criticality.py         # Gesetz C: Criticality-Score
│
├── physics/                   # Physik-Konzepte
│   ├── __init__.py
│   ├── model_laws.py          # Laws A/B/C Implementation
│   ├── avalanche.py           # SOC und Anti-Avalanche
│   └── metrics.py             # Hurst, Autocorrelation, etc.
│
├── pipeline/                  # Pipeline-Orchestrierung
│   ├── __init__.py
│   ├── runner.py              # Haupt-Pipeline
│   ├── least_action.py        # Gesetz B: Pipeline-Auswahl
│   └── validators.py          # Input/Output-Validierung
│
├── data/                      # Daten (nicht im Git)
│   ├── raw/                   # Original-Ziehungsdaten
│   ├── processed/             # Verarbeitete Daten
│   └── results/               # Analyse-Ergebnisse
│
├── config/                    # Konfigurationen
│   ├── default.yaml           # Standard-Config
│   ├── keno.yaml              # KENO-spezifisch
│   ├── eurojackpot.yaml       # EuroJackpot-spezifisch
│   └── lotto.yaml             # Lotto-spezifisch
│
├── tests/                     # Test-Suite
│   ├── unit/                  # Unit-Tests
│   ├── integration/           # Integrationstests
│   └── fixtures/              # Test-Daten
│
└── scripts/                   # CLI-Scripts
    ├── analyze.py             # Haupt-Analyse-Script
    ├── backtest.py            # Backtest-Script
    └── report.py              # Report-Generierung
```

### 4.2 Datenfluss

```
┌─────────────────────────────────────────────────────────────────────┐
│                        KENOBASE V2.0 PIPELINE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  [1] DATA LOADING                                                   │
│  └── data_loader.py: CSV/JSON → DataFrame                           │
│  └── Validierung: Schema-Check, Datum-Parse                         │
│                                                                      │
│  [2] PREPROCESSING                                                   │
│  └── Datum-Filter, Zeitraum-Segmentierung                           │
│  └── Zahlenpool-Generierung (Top-11 pro Periode)                    │
│                                                                      │
│  [3] COMBINATION GENERATION                                          │
│  └── 6er-Kombis aus Zahlenpool                                      │
│  └── Filter: Zehnergruppen-Regel (max 2 pro Gruppe)                 │
│  └── Filter: Summen-Schwelle                                        │
│                                                                      │
│  [4] PATTERN ANALYSIS                                                │
│  └── Duos/Trios/Quatros ermitteln                                   │
│  └── Index-Berechnung (Erscheinungshaeufigkeit)                     │
│  └── Zeitliche Korrelation                                          │
│                                                                      │
│  [5] PHYSICS LAYER (NEU!)                                            │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Gesetz A: Stabilitaetstest                                      │ │
│  │   → stability = 1 - (std(results) / mean(results))              │ │
│  │   → is_law = stability >= 0.9                                   │ │
│  │                                                                  │ │
│  │ Gesetz B: Least-Action-Auswahl                                  │ │
│  │   → action = complexity + instability - performance              │ │
│  │   → Bevorzuge Pipeline mit minimaler Action                      │ │
│  │                                                                  │ │
│  │ Gesetz C: Criticality-Score                                     │ │
│  │   → sensitivity = 1 - |prob - 0.5| * 2                          │ │
│  │   → regime_complexity = count_peaks(distribution)               │ │
│  │   → criticality = sensitivity * regime_complexity               │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  [6] AVALANCHE ASSESSMENT (NEU!)                                     │
│  └── theta = 1 - p^n (Verlustwahrscheinlichkeit)                    │
│  └── State: SAFE (<0.5), MODERATE (0.5-0.75), WARNING (0.75-0.85)   │
│  └── State: CRITICAL (>=0.85) → NO-BET Zone                         │
│                                                                      │
│  [7] OUTPUT & REPORTING                                              │
│  └── JSON/CSV Export                                                │
│  └── Metriken-Dashboard                                             │
│  └── ADR-konformes Logging                                          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Entwicklungsablauf

### 5.1 Setup

```powershell
# Repository klonen (wenn Git-Setup existiert)
git clone <repo-url> kenobase
cd kenobase

# Virtual Environment erstellen
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Dependencies installieren
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Pre-Commit Hooks installieren
pre-commit install
```

### 5.2 Konfiguration

```yaml
# config/default.yaml
project:
  name: kenobase
  version: "2.0.0"

data:
  raw_path: "./data/raw"
  processed_path: "./data/processed"
  results_path: "./data/results"

analysis:
  min_support: 20
  stability_threshold: 0.9
  criticality_warning: 0.7
  criticality_critical: 0.85

physics:
  enable_model_laws: true
  enable_avalanche: true
  least_action_weights:
    complexity: 0.1
    instability: 0.2
    performance: 1.0

combination:
  size: 6
  max_per_decade: 2
  min_sum: 150
```

### 5.3 Run

```powershell
# Vollstaendige Analyse
python scripts/analyze.py --config config/keno.yaml --start-date 2020-01-01

# Backtest
python scripts/backtest.py --config config/keno.yaml --periods 10

# Report generieren
python scripts/report.py --format html --output reports/
```

### 5.4 Test

```powershell
# Alle Tests
pytest tests/ -v

# Mit Coverage
pytest tests/ --cov=kenobase --cov-report=html

# Nur Unit-Tests
pytest tests/unit/ -v

# Spezifischer Test
pytest tests/unit/test_stability.py::test_is_law -v
```

### 5.5 Lint/Format

```powershell
# Formatierung
black kenobase/ tests/
isort kenobase/ tests/

# Linting
ruff check kenobase/ tests/

# Type-Checking
mypy kenobase/
```

---

## 6. Physik-Konzepte (Kernmodule)

### 6.1 Model Law A: Stabilitaet

```python
# kenobase/physics/model_laws.py

def is_law(
    relation: Callable,
    variations: list[dict],
    threshold: float = 0.9
) -> tuple[float, bool]:
    """
    Testet ob eine Relation ein 'Gesetz' ist (ADR-018).

    Eine Relation gilt als Gesetz wenn sie ueber Variationen
    (Zeit, Datenquellen, Parameter) stabil bleibt.

    Args:
        relation: Auswertbare Funktion
        variations: Liste von Parametervarianten
        threshold: Mindest-Stabilitaet (default 0.9)

    Returns:
        (stability_score, is_law)
    """
    results = [relation(**var) for var in variations]
    stability = 1 - (np.std(results) / max(np.mean(results), 1e-6))
    return stability, stability >= threshold
```

**Anwendung auf KENO:**
- Teste ob Zahlen-Muster (z.B. "17 erscheint nach 23") stabil sind
- Nur Muster mit stability >= 0.9 werden als "Gesetze" akzeptiert
- Filtert Noise von echten Regularitaeten

### 6.2 Model Law B: Least-Action

```python
# kenobase/physics/model_laws.py

@dataclass
class PipelineConfig:
    num_features: int
    num_rules: int
    num_special_cases: int
    performance_variance: float
    roi: float

def calculate_pipeline_action(config: PipelineConfig) -> float:
    """
    Berechnet die 'Action' einer Pipeline (ADR-018).

    Niedrigere Action = bessere Pipeline bei gleicher Performance.

    Args:
        config: Pipeline-Konfiguration

    Returns:
        Action-Wert (niedriger ist besser)
    """
    complexity = (
        config.num_features * 0.1
        + config.num_rules * 0.05
        + config.num_special_cases * 0.2
    )
    instability = config.performance_variance
    performance = config.roi

    return complexity + instability - performance
```

**Anwendung auf KENO:**
- Vergleiche verschiedene Analyse-Methoden
- Waehle einfachste Methode bei gleicher Vorhersagekraft
- Vermeidet Overfitting durch Komplexitaets-Penalty

### 6.3 Model Law C: Criticality

```python
# kenobase/physics/model_laws.py

def calculate_criticality(
    probability: float,
    regime_complexity: int
) -> tuple[float, str]:
    """
    Berechnet Criticality-Score (ADR-018/020).

    Args:
        probability: Vorhersage-Wahrscheinlichkeit (0-1)
        regime_complexity: Anzahl Peaks in historischer Verteilung

    Returns:
        (criticality_score, warning_level)
        warning_level: "LOW", "MEDIUM", "HIGH", "CRITICAL"
    """
    sensitivity = 1.0 - abs(probability - 0.5) * 2.0
    criticality = sensitivity * regime_complexity

    if criticality < 0.3:
        level = "LOW"
    elif criticality < 0.5:
        level = "MEDIUM"
    elif criticality < 0.7:
        level = "HIGH"
    else:
        level = "CRITICAL"

    return criticality, level
```

**Anwendung auf KENO:**
- Identifiziere "kritische" Ziehungen (nahe 50% Wahrscheinlichkeit)
- Komplexe Verteilungs-Regimes erhoehen Risiko
- CRITICAL-Ziehungen werden nicht fuer Vorhersagen verwendet

### 6.4 Avalanche-Theorie

```python
# kenobase/physics/avalanche.py

def calculate_theta(precision: float, n_picks: int) -> float:
    """
    Berechnet die 'Neigung' theta einer Kombination (ADR-021).

    theta = Verlustwahrscheinlichkeit = 1 - p^n

    Args:
        precision: Einzelne Pick-Precision (z.B. 0.714)
        n_picks: Anzahl der Picks

    Returns:
        theta (0.0 - 1.0)
    """
    return 1 - (precision ** n_picks)


def get_avalanche_state(theta: float) -> str:
    """
    Bestimmt Avalanche-State basierend auf theta.

    States:
        SAFE:     theta < 0.50 (Verlust < 50%)
        MODERATE: 0.50 <= theta < 0.75
        WARNING:  0.75 <= theta < 0.85
        CRITICAL: theta >= 0.85 (Verlust >= 85%)
    """
    if theta < 0.50:
        return "SAFE"
    elif theta < 0.75:
        return "MODERATE"
    elif theta < 0.85:
        return "WARNING"
    else:
        return "CRITICAL"


def is_profitable(precision: float, avg_odds: float) -> bool:
    """
    Prueft das Fundamental-Theorem: p * q > 1

    Args:
        precision: Historische Trefferquote
        avg_odds: Durchschnittliche Quote

    Returns:
        True wenn p * q > 1 (profitabel)
    """
    return precision * avg_odds > 1.0
```

**Anwendung auf KENO:**
- 6er-Kombination hat theta = 1 - 0.7^6 = 0.88 → CRITICAL!
- Anti-Avalanche: Max 4 Zahlen pro Kombi
- Break-Even nur wenn Precision * Quote > 1

---

## 7. Roadmap

### Phase 1: Foundation (MVP) - 8h

| Task | Beschreibung | Aufwand | Deliverable |
|------|--------------|---------|-------------|
| 1.1 | Projektstruktur anlegen | 1h | Ordner, __init__.py |
| 1.2 | Config-System (YAML) | 2h | config.py, default.yaml |
| 1.3 | Data Loader refactoren | 2h | data_loader.py |
| 1.4 | Unit-Tests Setup | 1h | pytest.ini, conftest.py |
| 1.5 | CI/CD Setup (optional) | 2h | GitHub Actions |

**Definition of Done:**
- [ ] `pip install -e .` funktioniert
- [ ] `pytest tests/unit/` laeuft durch (mind. 5 Tests)
- [ ] Config wird aus YAML geladen

### Phase 2: Core Logic Migration - 10h

| Task | Beschreibung | Aufwand | Deliverable |
|------|--------------|---------|-------------|
| 2.1 | number_pool.py (aus V9) | 2h | Saubere Implementation |
| 2.2 | combination_engine.py | 2h | 6er-Kombi-Generator |
| 2.3 | Zehnergruppen-Filter | 1h | Filter-Funktion |
| 2.4 | frequency.py | 2h | Haeufigkeitsanalyse |
| 2.5 | pattern.py (Duos/Trios) | 3h | BUG-FIX von altem Code |

**Definition of Done:**
- [ ] Alle Module haben Type Hints
- [ ] Alle Module haben Docstrings
- [ ] Unit-Test Coverage >= 80%
- [ ] Duo/Trio-Bug ist behoben und getestet

### Phase 3: Physics Layer - 8h

| Task | Beschreibung | Aufwand | Deliverable |
|------|--------------|---------|-------------|
| 3.1 | model_laws.py | 3h | Laws A/B/C Implementation |
| 3.2 | avalanche.py | 2h | SOC-Metriken |
| 3.3 | metrics.py | 2h | Hurst, Autocorr |
| 3.4 | Integration in Pipeline | 1h | Physics-Step in Runner |

**Definition of Done:**
- [ ] is_law() funktioniert mit Test-Daten
- [ ] calculate_criticality() gibt korrekte Levels
- [ ] Avalanche-States stimmen mit ADR-021 ueberein

### Phase 4: Pipeline & CLI - 6h

| Task | Beschreibung | Aufwand | Deliverable |
|------|--------------|---------|-------------|
| 4.1 | runner.py | 2h | Haupt-Pipeline |
| 4.2 | least_action.py | 1h | Pipeline-Vergleich |
| 4.3 | analyze.py CLI | 2h | argparse/click CLI |
| 4.4 | Output-Formate | 1h | JSON/CSV/HTML Export |

**Definition of Done:**
- [ ] `python scripts/analyze.py --help` zeigt Hilfe
- [ ] Pipeline laeuft end-to-end durch
- [ ] Output ist valides JSON/CSV

### Phase 5: Validation & Backtest - 6h

| Task | Beschreibung | Aufwand | Deliverable |
|------|--------------|---------|-------------|
| 5.1 | backtest.py Script | 2h | Historischer Backtest |
| 5.2 | Metriken-Berechnung | 2h | Precision, Recall, F1 |
| 5.3 | Report-Generator | 2h | HTML/Markdown Report |

**Definition of Done:**
- [ ] Backtest auf 12 Monate Daten
- [ ] Metriken werden korrekt berechnet
- [ ] Report ist lesbar und aussagekraeftig

### Phase 6: Documentation & Polish - 4h

| Task | Beschreibung | Aufwand | Deliverable |
|------|--------------|---------|-------------|
| 6.1 | README.md vervollstaendigen | 1h | Vollstaendiges README |
| 6.2 | ADR-001 schreiben | 1h | Architecture Decision Record |
| 6.3 | Docstrings Review | 1h | Alle Module dokumentiert |
| 6.4 | Final Testing | 1h | Smoke Tests, Edge Cases |

**Definition of Done:**
- [ ] README erklaert Setup und Nutzung
- [ ] ADR-001 dokumentiert Physics-Integration
- [ ] Keine Linter-Warnings

---

## 8. Gesamtaufwand

| Phase | Aufwand | Kumuliert |
|-------|---------|-----------|
| Phase 1: Foundation | 8h | 8h |
| Phase 2: Core Logic | 10h | 18h |
| Phase 3: Physics | 8h | 26h |
| Phase 4: Pipeline | 6h | 32h |
| Phase 5: Validation | 6h | 38h |
| Phase 6: Documentation | 4h | **42h** |

**Gesamt: 42 Stunden**

---

## 9. Offene Fragen + Annahmen

### 9.1 Offene Fragen (KLAREN)

| # | Frage | Impact | Vorgeschlagene Loesung |
|---|-------|--------|------------------------|
| Q1 | Welche Datenquelle ist primaer? | HOCH | Annahme: CSV aus Keno_GPTs/ |
| Q2 | Soll EuroJackpot/Lotto integriert werden? | MITTEL | Annahme: Ja, als separate Configs |
| Q3 | Wie oft werden Daten aktualisiert? | MITTEL | Annahme: Woe

ntlich |
| Q4 | Gibt es Performance-Anforderungen? | NIEDRIG | Annahme: Keine Echtzeit |

### 9.2 Annahmen (MARKIERT)

```
[ANNAHME A1] Die historischen Daten sind vollstaendig und korrekt.
             Verifikation: Stichproben-Check gegen offizielle Webseite.

[ANNAHME A2] Die 111-Prinzip-Hypothese ist testbar.
             Verifikation: Backtest mit klaren Acceptance-Kriterien.

[ANNAHME A3] Physik-Konzepte sind uebertragbar auf Lottozahlen.
             Verifikation: Stabilitaetstest auf Muster anwenden.

[ANNAHME A4] 6er-Kombis sind die richtige Analyseeinheit.
             Verifikation: Vergleich mit 5er und 7er Kombis.
```

---

## 10. Erste 10 Tickets

### Ticket #1: Projektstruktur anlegen
**Prioritaet:** P0 (Blocker)
**Aufwand:** 1h
**Beschreibung:** Erstelle die Ordnerstruktur gemaess Architektur-Plan.
**Acceptance Criteria:**
- [ ] Alle Ordner existieren
- [ ] __init__.py in jedem Package
- [ ] .gitignore konfiguriert
- [ ] requirements.txt angelegt

---

### Ticket #2: Config-System implementieren
**Prioritaet:** P0 (Blocker)
**Aufwand:** 2h
**Beschreibung:** YAML-basiertes Config-System mit Validierung.
**Acceptance Criteria:**
- [ ] default.yaml wird geladen
- [ ] Config-Klasse mit Type Hints
- [ ] Validierung bei ungueltigem Config
- [ ] Override per CLI-Parameter moeglich

---

### Ticket #3: Data Loader refactoren
**Prioritaet:** P0 (Blocker)
**Aufwand:** 2h
**Beschreibung:** Sauberer Data Loader mit Schema-Validierung.
**Acceptance Criteria:**
- [ ] CSV und JSON Support
- [ ] Automatische Datums-Erkennung
- [ ] Schema-Validierung (Spaltennamen, Typen)
- [ ] Unit-Tests fuer Edge Cases

---

### Ticket #4: Zahlenpool-Generator
**Prioritaet:** P1
**Aufwand:** 2h
**Beschreibung:** Migriere generiere_zahlenpool_optimiert() aus V9.
**Acceptance Criteria:**
- [ ] Top-11 pro Zeitraum korrekt
- [ ] Schnittmengen-Logik verifiziert
- [ ] Konfigurierbare Zeitraum-Groesse
- [ ] Unit-Tests mit bekannten Eingaben

---

### Ticket #5: Kombinations-Engine
**Prioritaet:** P1
**Aufwand:** 2h
**Beschreibung:** 6er-Kombinationen mit Filtern generieren.
**Acceptance Criteria:**
- [ ] Zehnergruppen-Filter funktioniert
- [ ] Summen-Filter funktioniert
- [ ] Memory-effizient (Generator statt Liste)
- [ ] Performance-Test mit grossem Pool

---

### Ticket #6: Duo/Trio/Quatro-Fix
**Prioritaet:** P1
**Aufwand:** 3h
**Beschreibung:** Bug in Duo/Trio/Quatro-Berechnung beheben.
**Acceptance Criteria:**
- [ ] Bug-Analyse dokumentiert
- [ ] Korrigierter Algorithmus
- [ ] Manuelle Verifikation mit Beispieldaten
- [ ] Regressionstests

---

### Ticket #7: Model Law A implementieren
**Prioritaet:** P1
**Aufwand:** 2h
**Beschreibung:** is_law() Funktion gemaess ADR-018.
**Acceptance Criteria:**
- [ ] Stabilitaetsberechnung korrekt
- [ ] Threshold konfigurierbar
- [ ] Test mit synthetischen Daten
- [ ] Docstring mit Beispiel

---

### Ticket #8: Criticality-Score implementieren
**Prioritaet:** P2
**Aufwand:** 2h
**Beschreibung:** calculate_criticality() gemaess ADR-018/020.
**Acceptance Criteria:**
- [ ] Sensitivity-Berechnung korrekt
- [ ] Regime-Complexity integriert
- [ ] Warning-Levels stimmen
- [ ] Unit-Tests fuer alle Levels

---

### Ticket #9: Avalanche-States implementieren
**Prioritaet:** P2
**Aufwand:** 2h
**Beschreibung:** Theta-Berechnung und State-Klassifikation.
**Acceptance Criteria:**
- [ ] theta = 1 - p^n korrekt
- [ ] States: SAFE/MODERATE/WARNING/CRITICAL
- [ ] is_profitable() Funktion
- [ ] Integration in Analyse-Output

---

### Ticket #10: Haupt-Pipeline (MVP)
**Prioritaet:** P1
**Aufwand:** 3h
**Beschreibung:** End-to-End Pipeline mit allen Modulen.
**Acceptance Criteria:**
- [ ] Laeuft mit default.yaml durch
- [ ] Output ist valides JSON
- [ ] Fehlerbehandlung fuer fehlende Daten
- [ ] Logging mit vernuenftigen Levels

---

## 11. Glossar

| Begriff | Definition |
|---------|------------|
| **Model Law** | Physik-inspirierte Regel fuer Systemverhalten (ADR-018) |
| **Criticality** | Mass fuer Instabilitaet/Risiko (Gesetz C) |
| **Avalanche** | Kaskadierende Verluste nach kritischer Schwelle |
| **Theta** | Verlustwahrscheinlichkeit einer Kombination |
| **SOC** | Self-Organized Criticality (Sandhaufen-Modell) |
| **111-Prinzip** | Altes Kenobase-Konzept fuer Zahlenpaare |
| **Duo/Trio/Quatro** | 2/3/4-Zahlen-Gruppen die zusammen erscheinen |
| **Zahlenpool** | Gefilterte Menge von Kandidaten-Zahlen |

---

## 12. Referenzen

### Interne Dokumente (v_master_Criticality)
- `AI_COLLABORATION/ARCHITECTURE/ADR_018_MODEL_LAWS_ALPHA_GAMMA.md`
- `AI_COLLABORATION/ARCHITECTURE/ADR_020_CRITICALITY_BASED_FP_DETECTION.md`
- `AI_COLLABORATION/ARCHITECTURE/ADR_021_AVALANCHE_CRITIQUE_COMBI_THEORY.md`

### Externe Referenzen
- Bak, P. (1987). "Self-organized criticality: 1/f noise"
- Sornette, D. (2003). "Why Stock Markets Crash"
- Prigogine, I. (1977). "Self-Organization in Nonequilibrium Systems"

---

**Erstellt:** 2025-12-26
**Aktualisiert:** 2025-12-30
**Version:** 2.2.0
**Autor:** Lead Architect (Claude Code)
**Status:** PRODUCTION - V2 Birthday-Avoidance validiert auf 2025 Daten

### Changelog

| Version | Datum | Aenderungen |
|---------|-------|-------------|
| 2.2.0 | 2025-12-30 | V2 Birthday-Avoidance Strategie, 2025 Validation, daily_recommendation.py |
| 2.1.0 | 2025-12-29 | Ecosystem-Analyse, Axiom-First Paradigma |
| 2.0.0 | 2025-12-26 | Initial Kenobase V2 mit Physics Layer |
