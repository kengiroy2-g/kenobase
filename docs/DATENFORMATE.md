# DATENFORMATE - Deutsche Lotterien

**Version:** 1.0
**Erstellt:** 2025-12-29
**Zweck:** Einheitliche Datenformate fuer alle deutschen Lotterien

---

## ORDNERSTRUKTUR

```
data/
├── raw/                          # Rohdaten (heruntergeladen)
│   ├── keno/
│   │   ├── KENO_ab_2018.csv
│   │   └── KENO_ab_2022_bereinigt.csv
│   ├── lotto/
│   │   └── lotto_6aus49_ab_2018.csv
│   ├── eurojackpot/
│   │   └── eurojackpot_ab_2018.csv
│   ├── gluecksspirale/
│   │   └── gluecksspirale_ab_2018.csv
│   └── plus5/
│       └── plus5_ab_2018.csv
│
└── processed/                    # Bereinigte Daten
    ├── keno/
    ├── lotto/
    └── eurojackpot/
```

---

## 1. KENO

### 1.1 Spielregeln
- **Zahlenbereich:** 1-70
- **Gezogene Zahlen:** 20
- **Spieltypen:** Typ 2 bis Typ 10 (Anzahl gewaehlter Zahlen)
- **Ziehungen:** Taeglich
- **Zusatzspiel:** Plus 5 (5-stellige Gewinnzahl)

### 1.2 Datenformat

```csv
Datum;Keno_Z1;Keno_Z2;Keno_Z3;Keno_Z4;Keno_Z5;Keno_Z6;Keno_Z7;Keno_Z8;Keno_Z9;Keno_Z10;Keno_Z11;Keno_Z12;Keno_Z13;Keno_Z14;Keno_Z15;Keno_Z16;Keno_Z17;Keno_Z18;Keno_Z19;Keno_Z20;Keno_Plus5;Keno_Spieleinsatz
01.01.2018;29;51;28;1;50;27;34;32;21;63;61;26;42;68;48;65;6;19;64;11;32646;304.198,00
```

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| Datum | DD.MM.YYYY | Ziehungsdatum |
| Keno_Z1-Z20 | int (1-70) | Gezogene Zahlen in Ziehungsreihenfolge |
| Keno_Plus5 | int (5-stellig) | Plus5 Gewinnzahl |
| Keno_Spieleinsatz | float | Tageseinsatz in EUR (mit Komma) |

### 1.3 Gewinnquoten (fest)

```python
KENO_QUOTES = {
    # Typ: {Treffer: Quote}
    2: {2: 6, 1: 0, 0: 0},
    3: {3: 16, 2: 1, 0: 0},
    4: {4: 22, 3: 2, 2: 1, 0: 0},
    5: {5: 100, 4: 7, 3: 2, 0: 0},
    6: {6: 500, 5: 15, 4: 5, 3: 1, 0: 0},
    7: {7: 1000, 6: 100, 5: 12, 4: 4, 3: 1, 0: 0},
    8: {8: 10000, 7: 1000, 6: 100, 5: 10, 4: 2, 0: 0},
    9: {9: 50000, 8: 5000, 7: 500, 6: 50, 5: 10, 4: 2, 0: 0},
    10: {10: 100000, 9: 10000, 8: 1000, 7: 100, 6: 15, 5: 5, 0: 2}
}
```

### 1.4 Bereinigungsscript

```bash
python scripts/clean_keno_csv.py data/raw/keno/ROHDATEN.csv data/raw/keno/KENO_bereinigt.csv
```

---

## 2. LOTTO 6aus49

### 2.1 Spielregeln
- **Zahlenbereich:** 1-49
- **Gezogene Zahlen:** 6 + Superzahl (0-9)
- **Ziehungen:** Mittwoch und Samstag
- **Zusatzspiele:** Spiel 77, Super 6

### 2.2 Datenformat

```csv
Datum;L1;L2;L3;L4;L5;L6;Superzahl;Spiel77;Super6;Jackpot_EUR
01.01.2018;3;15;22;31;42;49;7;1234567;654321;5000000
```

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| Datum | DD.MM.YYYY | Ziehungsdatum |
| L1-L6 | int (1-49) | Lottozahlen (sortiert) |
| Superzahl | int (0-9) | Superzahl |
| Spiel77 | int (7-stellig) | Spiel77 Gewinnzahl |
| Super6 | int (6-stellig) | Super6 Gewinnzahl |
| Jackpot_EUR | int | Jackpot-Stand in EUR |

### 2.3 Gewinnquoten (Parimutuel - variabel)

```python
# Durchschnittliche Quoten (Richtwerte)
LOTTO_AVG_QUOTES = {
    (6, True):  10000000,  # 6 Richtige + Superzahl (Jackpot)
    (6, False):  1000000,  # 6 Richtige
    (5, True):     50000,  # 5 + Superzahl
    (5, False):     3000,  # 5 Richtige
    (4, True):      200,   # 4 + Superzahl
    (4, False):      50,   # 4 Richtige
    (3, True):       20,   # 3 + Superzahl
    (3, False):      10,   # 3 Richtige
    (2, True):        5,   # 2 + Superzahl
}
```

### 2.4 Bereinigung

```python
# Erwartetes Rohformat (von lotto.de)
# Datum;Lottozahlen;SZ;Spiel77;Super6;Jackpot
# 01.01.2018;3 15 22 31 42 49;7;1234567;654321;5.000.000

def clean_lotto_csv(input_path: str, output_path: str):
    """Bereinigt Lotto 6aus49 CSV."""
    # 1. Zahlen aus String extrahieren
    # 2. Header normalisieren
    # 3. Jackpot-Format bereinigen (Punkte entfernen)
    pass
```

---

## 3. EUROJACKPOT

### 3.1 Spielregeln
- **Zahlenbereich:** 1-50 (Hauptzahlen) + 1-12 (Eurozahlen)
- **Gezogene Zahlen:** 5 + 2
- **Ziehungen:** Dienstag und Freitag
- **Teilnehmende Laender:** 18 europaeische Laender

### 3.2 Datenformat

```csv
Datum;E1;E2;E3;E4;E5;Euro1;Euro2;Jackpot_EUR
01.01.2018;5;12;23;34;45;3;8;10000000
```

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| Datum | DD.MM.YYYY | Ziehungsdatum |
| E1-E5 | int (1-50) | Hauptzahlen (sortiert) |
| Euro1-Euro2 | int (1-12) | Eurozahlen (sortiert) |
| Jackpot_EUR | int | Jackpot-Stand in EUR |

### 3.3 Gewinnquoten (Parimutuel)

```python
EUROJACKPOT_AVG_QUOTES = {
    (5, 2): 90000000,  # Jackpot
    (5, 1):  1000000,
    (5, 0):   100000,
    (4, 2):     5000,
    (4, 1):      200,
    (4, 0):      100,
    (3, 2):       50,
    (2, 2):       20,
    (3, 1):       15,
    (3, 0):       10,
    (1, 2):       10,
    (2, 1):        8,
}
```

---

## 4. GLUECKSSPIRALE

### 4.1 Spielregeln
- **Los-Nummer:** 7-stellig
- **Gewinnklassen:** 7 (von hinten nach vorne geprueft)
- **Ziehungen:** Samstag
- **Besonderheit:** Rentengewinne moeglich

### 4.2 Datenformat

```csv
Datum;Gewinnzahl;Rente_Anzahl;Jackpot_EUR
01.01.2018;1234567;2;2500000
```

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| Datum | DD.MM.YYYY | Ziehungsdatum |
| Gewinnzahl | int (7-stellig) | Gewinnzahl |
| Rente_Anzahl | int | Anzahl der Rentengewinner |
| Jackpot_EUR | int | Jackpot-Stand |

### 4.3 Gewinnklassen

```python
GLUECKSSPIRALE_QUOTES = {
    7: 2100000,  # 7 Richtige (7500 EUR/Monat Rente oder Sofortauszahlung)
    6: 100000,
    5: 5000,
    4: 500,
    3: 50,
    2: 10,
    1: 0,  # Kein Gewinn bei 1 Richtiger (von hinten)
}
```

---

## 5. PLUS 5 (KENO Zusatzspiel)

### 5.1 Spielregeln
- **Gewinnzahl:** 5-stellig (00000-99999)
- **Pruefung:** Von hinten nach vorne
- **Ziehungen:** Taeglich (zusammen mit KENO)

### 5.2 In KENO integriert

Plus5 ist bereits in `Keno_Plus5` Spalte enthalten.

### 5.3 Gewinnquoten (fest)

```python
PLUS5_QUOTES = {
    5: 5000,   # 5 Richtige
    4: 500,    # 4 Richtige (von hinten)
    3: 50,     # 3 Richtige
    2: 5,      # 2 Richtige
    1: 2,      # 1 Richtige
    0: 0,
}
```

---

## 6. DATENQUELLEN

### 6.1 Offizielle Quellen

| Lotterie | URL | Format |
|----------|-----|--------|
| KENO | https://www.lotto.de/keno/zahlen-quoten | HTML (Scraping) |
| Lotto 6aus49 | https://www.lotto.de/lotto-6aus49/zahlen-quoten | HTML |
| EuroJackpot | https://www.eurojackpot.de/zahlen-quoten | HTML |
| Gluecksspirale | https://www.lotto.de/gluecksspirale/zahlen-quoten | HTML |

### 6.2 Archiv-Quellen

```
Lotto.de Archiv:
  - KENO: Ab 2004
  - Lotto: Ab 1955
  - EuroJackpot: Ab 2012
  - Gluecksspirale: Ab 1971
```

### 6.3 Scraping-Script

```bash
# KENO scrapen (letzte 30 Tage)
python scripts/scrape_lotto_de.py --recent 30 --output data/raw/keno

# Bestimmter Zeitraum
python scripts/scrape_lotto_de.py --start 2024-01-01 --end 2024-12-31
```

---

## 7. BEREINIGUNGSPIPELINE

### 7.1 Allgemeiner Ablauf

```
1. Rohdaten herunterladen/scrapen
   -> data/raw/{game}/ROHDATEN.csv

2. Bereinigungsscript ausfuehren
   -> data/raw/{game}/{game}_bereinigt.csv

3. Validierung durchfuehren
   -> data/processed/{game}/{game}_validated.csv
```

### 7.2 Generisches Bereinigungsscript

```python
# scripts/clean_lottery_csv.py

def clean_lottery_csv(
    input_path: str,
    output_path: str,
    game_type: str  # "keno", "lotto", "eurojackpot"
):
    """
    Generische Bereinigung fuer alle Lotterien.

    Schritte:
    1. Encoding korrigieren (UTF-8)
    2. Header normalisieren
    3. Leerzeichen entfernen
    4. Datumsformat validieren
    5. Zahlen validieren
    6. Garbage-Zeilen entfernen
    """
    pass
```

### 7.3 Validierung

```python
def validate_lottery_data(df: pd.DataFrame, game_type: str) -> bool:
    """
    Validiert bereinigte Daten.

    Checks:
    1. Keine doppelten Daten
    2. Zahlen im gueltigen Bereich
    3. Keine fehlenden Werte
    4. Chronologische Reihenfolge
    """
    pass
```

---

## 8. BEISPIEL-WORKFLOW

### 8.1 Neue KENO-Daten hinzufuegen

```bash
# 1. Rohdaten ablegen
cp ~/Downloads/keno_2025.csv data/raw/keno/

# 2. Bereinigen
python scripts/clean_keno_csv.py \
    data/raw/keno/keno_2025.csv \
    data/raw/keno/KENO_2025_bereinigt.csv

# 3. Validieren
python -c "
import pandas as pd
df = pd.read_csv('data/raw/keno/KENO_2025_bereinigt.csv', sep=';')
print(f'Zeilen: {len(df)}')
print(f'Zeitraum: {df.Datum.min()} - {df.Datum.max()}')
"

# 4. Analyse starten
python scripts/test_super_model_2025.py
```

### 8.2 Lotto 6aus49 analysieren

```bash
# 1. Daten ablegen
cp ~/Downloads/lotto_archiv.csv data/raw/lotto/

# 2. Bereinigen (neues Script noetig)
python scripts/clean_lotto_csv.py \
    data/raw/lotto/lotto_archiv.csv \
    data/raw/lotto/lotto_6aus49_bereinigt.csv

# 3. Analyse-Scripts anpassen und ausfuehren
# (siehe docs/METHODIK_SUPER_MODEL.md Kapitel 9)
```

---

*Datenformate-Dokumentation V1.0*
*Kenobase - Multi-Lotterie Framework*
