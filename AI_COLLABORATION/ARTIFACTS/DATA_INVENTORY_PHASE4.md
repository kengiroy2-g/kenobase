# Daten-Inventar Phase 4

**Erstellt:** 2025-12-29
**Status:** AKTIV

---

## 1. Primaere Datenquellen

### 1.1 KENO Ziehungen
| Datei | Pfad | Format | Zeitraum | Zeilen |
|-------|------|--------|----------|--------|
| KENO_ab_2018.csv | data/raw/keno/ | Semicolon-CSV | 2018-heute | ~2500 |

**Schema:**
```
Datum;Keno_Z1;Keno_Z2;...;Keno_Z20;Keno_Plus5;Keno_Spieleinsatz
01.01.2018;29;51;28;...;11;32646;304.198,00
```

**Spalten:**
- `Datum`: Ziehungsdatum (DD.MM.YYYY)
- `Keno_Z1-Z20`: 20 gezogene Zahlen (1-70)
- `Keno_Plus5`: Plus5 Zusatzzahl
- `Keno_Spieleinsatz`: Gesamteinsatz in EUR

---

### 1.2 KENO Gewinnquoten (Gewinnklassen)
| Datei | Pfad | Format | Zeitraum |
|-------|------|--------|----------|
| Keno_GQ_2022_2023-2024.csv | Keno_GPTs/ | Comma-CSV | 2022-2024 |
| Keno_GQ_2023.csv | Keno_GPTs/ | Comma-CSV | 2023 |
| Keno_GQ_2024.csv | Keno_GPTs/ | Comma-CSV | 2024 |

**Schema:**
```
Datum,Keno-Typ,Anzahl richtiger Zahlen,Anzahl der Gewinner,1 Euro Gewinn
08.02.2024,2,2,275.0,6 EUR
08.02.2024,3,3,438.0,16 EUR
```

**Spalten:**
- `Datum`: Ziehungsdatum
- `Keno-Typ`: Spieltyp (2-10)
- `Anzahl richtiger Zahlen`: Treffer (= Gewinnklasse)
- `Anzahl der Gewinner`: Anzahl Gewinner in dieser GK
- `1 Euro Gewinn`: Gewinn pro 1 EUR Einsatz

**Gewinnklassen pro Typ:**

| Typ | GK1 (Jackpot) | GK2 | GK3 | GK4 | ... |
|-----|---------------|-----|-----|-----|-----|
| 10 | 10/10 | 9/10 | 8/10 | 7/10 | ... |
| 9 | 9/9 | 8/9 | 7/9 | 6/9 | ... |
| 8 | 8/8 | 7/8 | 6/8 | 5/8 | ... |
| ... | ... | ... | ... | ... | ... |
| 2 | 2/2 | 1/2 | 0/2 | - | - |

---

### 1.3 GK1-Events (Jackpot-Daten)
| Datei | Pfad | Format | Inhalt |
|-------|------|--------|--------|
| 10-9_KGDaten_gefiltert.csv | Keno_GPTs/ | Comma-CSV | GK1-Events Typ 9+10 |

**Schema:**
```
Datum,Keno-Typ,Anzahl der Gewinner,Vergangene Tage seit dem letzten Gewinnklasse 1
31.01.2022,10,10.0,0
19.02.2022,9,2.0,19
```

**Spalten:**
- `Datum`: Jackpot-Datum
- `Keno-Typ`: 9 oder 10
- `Anzahl der Gewinner`: Jackpot-Gewinner
- `Vergangene Tage`: Tage seit letztem GK1

**Bekannte GK1-Events:** ~20 (2018-2024)

---

## 2. Cross-Game Datenquellen

### 2.1 EuroJackpot
| Datei | Pfad | Format |
|-------|------|--------|
| eurojackpot_archiv_bereinigt.csv | data/raw/eurojackpot/ | Comma-CSV |

**Schema:**
```
Datum,EJ_Z1,EJ_Z2,EJ_Z3,EJ_Z4,EJ_Z5,EZ1,EZ2
```

### 2.2 Lotto 6aus49
| Datei | Pfad | Format |
|-------|------|--------|
| Lotto_Archiv_ab-1955.csv | data/raw/lotto/ | Comma-CSV |
| lotto_Stats_ab-2018.csv | data/raw/lotto/ | Comma-CSV |

**Schema:**
```
Datum,Lotto_Z1,Lotto_Z2,Lotto_Z3,Lotto_Z4,Lotto_Z5,Lotto_Z6,Superzahl
```

---

## 3. Bundesland-Daten (ZU RECHERCHIEREN)

### 3.1 Bevoelkerungsdaten
| Bundesland | Bevoelkerung (Mio) | Anteil % |
|------------|-------------------|----------|
| Nordrhein-Westfalen | 17.9 | 21.5% |
| Bayern | 13.1 | 15.8% |
| Baden-Wuerttemberg | 11.1 | 13.4% |
| Niedersachsen | 8.0 | 9.6% |
| Hessen | 6.3 | 7.6% |
| Sachsen | 4.1 | 4.9% |
| Rheinland-Pfalz | 4.1 | 4.9% |
| Berlin | 3.7 | 4.4% |
| Schleswig-Holstein | 2.9 | 3.5% |
| Brandenburg | 2.5 | 3.0% |
| Sachsen-Anhalt | 2.2 | 2.6% |
| Thueringen | 2.1 | 2.5% |
| Hamburg | 1.9 | 2.3% |
| Mecklenburg-Vorpommern | 1.6 | 1.9% |
| Saarland | 1.0 | 1.2% |
| Bremen | 0.7 | 0.8% |

**Gesamt:** 83.2 Mio

### 3.2 Lottogesellschaften
| Bundesland | Gesellschaft |
|------------|--------------|
| NRW | Westdeutsche Lotterie |
| Bayern | LOTTO Bayern |
| BW | Staatliche Toto-Lotto |
| ... | ... |

---

## 4. Abgeleitete Daten (zu erstellen)

### 4.1 Paar-Co-Occurrence pro GK
```python
# Output: pairs_per_gk.json
{
    "GK_10_10": {  # Typ 10, 10 Treffer
        "(2,3)": {"count": 218, "expected": 176, "lift": 1.24},
        ...
    },
    "GK_10_9": {  # Typ 10, 9 Treffer (Near-Miss)
        "(9,50)": {"count": 95, "expected": 80, "lift": 1.19},
        ...
    },
    ...
}
```

### 4.2 GK-Backtest pro Paar
```python
# Output: pair_backtest.json
{
    "(2,3)": {
        "months_with_win": 12,
        "total_months": 12,
        "win_rate": 1.0,
        "avg_wins_per_month": 2.4
    },
    ...
}
```

### 4.3 Bundesland-Verteilung
```python
# Output: bundesland_distribution.json
{
    "2024-01-01": {
        "NRW": {"winners": 45, "expected": 42, "ratio": 1.07},
        "Bayern": {"winners": 32, "expected": 31, "ratio": 1.03},
        ...
    },
    ...
}
```

---

## 5. Daten-Qualitaet

| Datei | Vollstaendigkeit | Fehler | Status |
|-------|-----------------|--------|--------|
| KENO_ab_2018.csv | 100% | 0 | OK |
| Keno_GQ_*.csv | 95% | Luecken | PRUEFEN |
| 10-9_KGDaten.csv | 100% | 0 | OK |
| eurojackpot_*.csv | 100% | 0 | OK |
| Lotto_*.csv | 100% | 0 | OK |

---

## 6. Loader-Funktionen

```python
# kenobase/core/data_loader.py

def load_keno_draws(path: str = "data/raw/keno/KENO_ab_2018.csv") -> pd.DataFrame:
    """Laedt KENO Ziehungen."""

def load_gewinnquoten(path: str = "Keno_GPTs/Keno_GQ_2022_2023-2024.csv") -> pd.DataFrame:
    """Laedt Gewinnquoten pro Gewinnklasse."""

def load_gk1_events(path: str = "Keno_GPTs/10-9_KGDaten_gefiltert.csv") -> pd.DataFrame:
    """Laedt GK1 (Jackpot) Events."""

def load_eurojackpot(path: str = "data/raw/eurojackpot/eurojackpot_archiv_bereinigt.csv") -> pd.DataFrame:
    """Laedt EuroJackpot Ziehungen."""

def load_lotto(path: str = "data/raw/lotto/Lotto_Archiv_ab-1955.csv") -> pd.DataFrame:
    """Laedt Lotto 6aus49 Ziehungen."""
```

---

*Daten-Inventar Phase 4 - Kenobase V2.2*
