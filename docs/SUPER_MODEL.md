# KENOBASE SUPER-MODELL V1.0

**Erstellt:** 2025-12-29
**Paradigma:** Multi-KI Synthese (3 parallele KI-Analysen)
**Status:** HISTORISCH / DEPRECATED (ROI-Claims nicht mehr gueltig)

**WICHTIG (Quoten/ROI):**
- Single Source of Truth fuer KENO-Auszahlungen ist `kenobase/core/keno_quotes.py`.
- Diese V1.0 Datei enthaelt ROI-Zahlen aus einer frueheren Phase (teilweise falsche/inkonsistente Quoten-Tabelle).
- Aktuelle, reproduzierbare Ergebnisse stehen in `results/` (z.B. `results/super_model_test_2025.json` und `results/super_model_comparison_summary.md`).

---

## Executive Summary

Das Super-Modell kombiniert die Erkenntnisse von **3 parallel arbeitenden KIs**. Die konkrete ROI-Performance ist *nicht* aus dieser Datei zu entnehmen; nutze dafuer die aktuellen Backtest-Artefakte unter `results/`.

| Metrik | Wert |
|--------|------|
| Getestete Kombinationen | 256 |
| Beste Komponenten | 3 von 8 |
| Backtests (aktuell) | `results/super_model_test_2025.json` |

---

## Die 3 KI-Quellen

### KI #1: Dynamic Recommendation System

**Haupt-Erkenntnisse:**
- Jackpot-Warnung: 30 Tage Cooldown nach GK10_10
- Optimale Tickets pro Typ
- Position-Exclusion Regeln (100% Accuracy)
- Korrelierte Absenzen

**Beste Einzelkomponente (historisch):** Jackpot-Warning

### KI #2: Position Rule Layer

**Haupt-Erkenntnisse:**
- Wilson-LB Scoring fuer Position-Regeln
- Position-Praeferenzen (z.B. Zahl 49 @ Pos 1: +59%)
- Walk-Forward Backtest Methodik

**Beitrag zum Super-Modell:** Exclusion-Rules Validierung

### KI #3: Number Group Model

**Haupt-Erkenntnisse:**
- Near-Miss vs Jackpot Strategien
- Temporale Anomalien (Monats-Start/Ende)
- Paar-Synergien
- Wochentags-Favoriten
- Anti-Birthday Zahlen

**Beitrag zum Super-Modell:** Anti-Birthday Komponente

---

## Beste Modell-Konfiguration

### Aktive Komponenten (3 von 8)

```python
BEST_MODEL = {
    "jackpot_warning": True,     # KRITISCH - 30 Tage Cooldown
    "exclusion_rules": True,     # 100% Accuracy Regeln
    "anti_birthday": True,       # Zahlen >31 bevorzugen

    # DEAKTIVIERT (kein Mehrwert):
    "temporal": False,
    "weekday": False,
    "sum_context": False,
    "pair_synergy": False,
    "correlated_absence": False,  # VERSCHLECHTERT sogar!
}
```

### Warum nur 3 Komponenten?

Die Analyse zeigt, dass **Jackpot-Warning** der mit Abstand wichtigste Faktor ist:

| Komponenten-Kombination | ROI |
|-------------------------|-----|
| jackpot_warning allein | +466.6% |
| jackpot_warning + exclusion_rules | +466.9% |
| jackpot_warning + exclusion_rules + anti_birthday | **+467.4%** |
| Alle 8 Komponenten | +467.2% |

Zusaetzliche Komponenten bringen keinen signifikanten Mehrwert, wenn die Jackpot-Warning bereits aktiv ist.

---

## Komponenten im Detail

### 1. Jackpot-Warning (KRITISCH)

```
Regel: Wenn letzter GK10_10 Jackpot < 30 Tage her -> NICHT SPIELEN

Grund: Post-Jackpot Perioden haben -66% ROI vs normale Perioden

Effekt:
  - Uebersprungen: 296 Tage (16% aller Ziehungen)
  - ROI-Verbesserung: +116 Prozentpunkte
```

### 2. Exclusion-Rules

```
Trigger -> Exclude Zahlen (100% Accuracy):

  (4, 17)  -> [70]
  (24, 2)  -> [22]
  (4, 14)  -> [25]
  (14, 7)  -> [38]
  (5, 2)   -> [13]
  (68, 20) -> [65]
  (50, 4)  -> [64]
  (1, 8)   -> [33]
```

### 3. Anti-Birthday

```
Bevorzuge Zahlen >31 fuer weniger Gewinner-Teilung:

  [33, 35, 36, 37, 40, 41, 42, 49, 51, 52, 53, 56, 57, 59, 64, 66, 69]

Grund: Weniger Spieler waehlen diese Zahlen
       -> Bei Gewinn weniger Teilung
       -> Hoeherer effektiver ROI
```

---

## Performance-Vergleich

### Super-Modell vs Einzelne KI-Modelle

| Modell | Typ 9 ROI | Typ 8 ROI | Typ 10 ROI |
|--------|-----------|-----------|------------|
| **Super-Modell** | **+467.4%** | **+144.5%** | **+256.9%** |
| KI #1 (mit JP-Warnung) | +351.0% | +271.4% | +189.0% |
| KI #2 (Position Rules) | +399.7% | - | - |
| KI #3 (Number Groups) | +399.1% | - | - |

### Einzelkomponenten-Vergleich

| Komponente | ROI (allein) | Rang |
|------------|--------------|------|
| jackpot_warning | +466.6% | 1 |
| exclusion_rules | +399.7% | 2 |
| temporal | +399.1% | 3-7 |
| weekday | +399.1% | 3-7 |
| sum_context | +399.1% | 3-7 |
| pair_synergy | +399.1% | 3-7 |
| anti_birthday | +399.1% | 3-7 |
| correlated_absence | +213.5% | 8 |

---

## Optimale Tickets (Super-Modell)

### Typ 9 (Bester ROI: +467.4%)

```
Basis: [3, 9, 10, 20, 24, 36, 49, 51, 64]
Mit Exclusion + Anti-Birthday Anpassung
```

### Typ 8 (ROI: +144.5%)

```
Basis: [3, 20, 24, 27, 36, 49, 51, 64]
```

### Typ 10 (ROI: +256.9%)

```
Basis: [2, 3, 9, 10, 20, 24, 36, 49, 51, 64]
```

---

## Verwendung

```python
from scripts.super_model_synthesis import SuperModel

# Modell initialisieren
model = SuperModel()
model.set_active_components([
    "jackpot_warning",
    "exclusion_rules",
    "anti_birthday"
])

# Kontext erstellen
context = {
    "date": datetime.now(),
    "prev_positions": [...],  # Gestrige Positionen
    "prev_numbers": [...],    # Gestrige Zahlen
    "jackpot_dates": [...],   # Liste aller GK10_10 Jackpots
}

# Pruefen ob spielen
should_skip, reason = model.should_skip(context)
if should_skip:
    print(f"NICHT SPIELEN: {reason}")
else:
    # Ticket generieren
    ticket, metadata = model.generate_ticket(keno_type=9, context=context)
    print(f"Ticket: {ticket}")
```

---

## Strategische Empfehlungen

### Anwendung (Hinweis)

Dieses Dokument ist historisch und enthaelt keine gueltige Spiel-/Kapital-Empfehlung.
Nutze die aktuellen Backtests unter `results/` und die Quoten aus `kenobase/core/keno_quotes.py`.

---

## Limitationen

1. **Backtest-Bias:** Historische Performance ist keine Garantie
2. **Sample Size:** Nur 11 Jackpot-Events fuer Cooldown-Analyse
3. **Markt-Aenderungen:** System koennte sich aendern
4. **Quote-Aenderungen:** KENO-Quoten koennen angepasst werden

---

## Changelog

- **2025-12-29:** Super-Modell V1.0 erstellt
  - 256 Kombinationen getestet
  - Beste Konfiguration: 3 Komponenten
  - ROI +467.4% (Typ 9)

---

*Generiert durch Kenobase V2.2 - Multi-KI Synthese*
