# Exhaustive Cycles Analysis - Anleitung für KIs

## WICHTIG: V1 vs V2 Parallel-Testing

Alle Tests müssen **BEIDE** Ticket-Versionen parallel prüfen und vergleichen!

---

## Ticket-Definitionen

### V1_ORIGINAL (Frequency-based)
Basiert auf historischen Häufigkeiten. Enthält mehr Birthday-Zahlen (1-31).

```python
V1_ORIGINAL = {
    6: [3, 20, 24, 36, 49, 51],
    7: [3, 20, 24, 27, 36, 49, 51],
    8: [3, 20, 24, 27, 36, 49, 51, 64],
    9: [3, 9, 10, 20, 24, 36, 49, 51, 64],
    10: [2, 3, 9, 10, 20, 24, 36, 49, 51, 64],
}

# Birthday-Zahlen (1-31) pro Typ:
# Typ 6: 3 (3, 20, 24)
# Typ 7: 4 (3, 20, 24, 27)
# Typ 8: 4 (3, 20, 24, 27)
# Typ 9: 5 (3, 9, 10, 20, 24)
# Typ 10: 5 (2, 3, 9, 10, 20, 24)
```

### V2_BIRTHDAY_AVOIDANCE (High-Number Strategy)
Vermeidet Birthday-Zahlen. Fokus auf hohe Zahlen (32-70).

```python
V2_BIRTHDAY_AVOIDANCE = {
    6: [3, 36, 43, 48, 51, 58],
    7: [3, 36, 43, 48, 51, 58, 61],
    8: [3, 36, 43, 48, 51, 58, 61, 64],
    9: [3, 7, 36, 43, 48, 51, 58, 61, 64],
    10: [3, 7, 13, 36, 43, 48, 51, 58, 61, 64],
}

# Birthday-Zahlen (1-31) pro Typ:
# Typ 6: 1 (nur 3)
# Typ 7: 1 (nur 3)
# Typ 8: 1 (nur 3)
# Typ 9: 2 (3, 7)
# Typ 10: 3 (3, 7, 13)
```

---

## High-Win Gewinnklassen (>450 EUR bei 1 EUR Einsatz)

Diese Gewinnklassen müssen speziell analysiert werden:

| Typ | Treffer | Auszahlung | Wahrscheinlichkeit |
|-----|---------|------------|---------------------|
| 6 | 6/6 | 500 EUR | 1:7.753 |
| 7 | 7/7 | 1.000 EUR | 1:15.464 |
| 8 | 8/8 | 10.000 EUR | 1:2.598.960 |
| 9 | 8/9 | 1.000 EUR | 1:30.682 |
| 9 | 9/9 | 50.000 EUR | 1:47.784.352 |
| 10 | 9/10 | 1.000 EUR | 1:47.784.352 |
| 10 | 10/10 | 100.000 EUR | 1:2.147.181.169 |

---

## Quoten-Tabelle (alle Gewinnklassen)

```python
from kenobase.core.keno_quotes import get_fixed_quote

# Oder direkt:
KENO_QUOTES = {
    6: {3: 1, 4: 2, 5: 15, 6: 500},
    7: {3: 1, 4: 1, 5: 12, 6: 100, 7: 1000},
    8: {0: 1, 4: 1, 5: 2, 6: 15, 7: 100, 8: 10000},
    9: {0: 2, 4: 1, 5: 2, 6: 5, 7: 20, 8: 1000, 9: 50000},
    10: {0: 2, 5: 2, 6: 5, 7: 15, 8: 100, 9: 1000, 10: 100000},
}
```

---

## Phasen-Definitionen

```python
def classify_phase(date, jackpot_dates):
    """Klassifiziert eine Ziehung in eine Phase."""
    for jp_date in jackpot_dates:
        days_diff = (date - jp_date).days
        if 1 <= days_diff <= 7:
            return "POST_JACKPOT"
        elif 8 <= days_diff <= 30:
            return "COOLDOWN"
        if -7 <= days_diff <= -1:
            return "PRE_JACKPOT"
    return "NORMAL"
```

---

## Datenquellen

```
data/raw/keno/KENO_ab_2022_bereinigt.csv     # Hauptdaten
data/processed/ecosystem/timeline_2025.csv   # Jackpot-Events
```

### Daten laden:
```python
import pandas as pd
from pathlib import Path

base_path = Path(__file__).parent.parent
keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")

# Zahlen als Set
pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
df["numbers_set"] = df[pos_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)
```

---

## Analyse-Template

Jeder Test MUSS dieses Format verwenden:

```python
def analyze_task(df, jackpot_dates):
    results = {
        "task_id": "TASK_XXX",
        "task_name": "...",

        # V1 vs V2 PARALLEL für JEDEN Typ
        "v1_v2_comparison": {},
    }

    for keno_type in [6, 7, 8, 9, 10]:
        v1_ticket = V1_ORIGINAL[keno_type]
        v2_ticket = V2_BIRTHDAY_AVOIDANCE[keno_type]

        # Berechne für V1
        v1_wins = sum(get_fixed_quote(keno_type,
                      len(set(v1_ticket) & row["numbers_set"]))
                      for _, row in df.iterrows())
        v1_roi = (v1_wins - len(df)) / len(df) * 100

        # Berechne für V2
        v2_wins = sum(get_fixed_quote(keno_type,
                      len(set(v2_ticket) & row["numbers_set"]))
                      for _, row in df.iterrows())
        v2_roi = (v2_wins - len(df)) / len(df) * 100

        results["v1_v2_comparison"][f"type_{keno_type}"] = {
            "v1_roi": v1_roi,
            "v2_roi": v2_roi,
            "diff": v2_roi - v1_roi,
            "v2_better": v2_roi > v1_roi,
        }

    return results
```

---

## Wichtige Hypothesen

### HYP_001: 28-Tage-Dauerschein-Zyklus
- Dauerscheine laufen nach max 28 Tagen aus
- Test: ROI Tag 1-14 vs Tag 15-28 nach Jackpot

### HYP_002: Cooldown reduziert High-Wins
- Nach Jackpot spart das System
- Test: High-Win-Rate in COOLDOWN vs NORMAL

### HYP_005: Birthday-Avoidance in Cooldown
- V2 sollte in COOLDOWN besser performen
- Test: V2 ROI vs V1 ROI nur in COOLDOWN Phase

---

## Output-Format

Alle Ergebnisse als JSON in `results/exhaustive_cycles/`:

```python
import json
from pathlib import Path

output_dir = Path("results/exhaustive_cycles")
output_dir.mkdir(parents=True, exist_ok=True)

with open(output_dir / "task_xxx_result.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
```

---

## Statistik-Anforderungen

- **p-Wert**: < 0.05 für Signifikanz
- **Sample Size**: Mindestens 30 Beobachtungen pro Gruppe
- **Bootstrap**: 1000 Iterationen für Konfidenzintervalle
- **Multiple Testing**: Benjamini-Hochberg Korrektur anwenden

---

## Warnung: Bekannte Probleme

1. **Small Sample Size**: Manche Kombinationen (z.B. Dienstag+Cooldown) haben nur ~37 Datenpunkte
2. **Single High-Win Dependency**: Ein 1000 EUR Gewinn kann gesamte ROI dominieren
3. **2025 Outlier**: 2025 zeigt andere Performance als 2022-2024
4. **Jackknife verwenden**: Immer Leave-One-Out für High-Wins prüfen!

---

## Checkliste pro Task

- [ ] V1 UND V2 parallel getestet
- [ ] Alle 5 Typen (6, 7, 8, 9, 10) getestet
- [ ] Sample Size dokumentiert
- [ ] Statistische Signifikanz berechnet
- [ ] High-Wins (>450 EUR) separat gezählt
- [ ] Ergebnis als JSON gespeichert
