# Kenobase V2.0 - Data Sources Documentation

**Erstellt:** 2025-12-27
**Status:** AKTIV

---

## Uebersicht

Dieses Dokument beschreibt alle Datenquellen im Keno_GPTs Ordner, deren Struktur, Herkunft und die Scripts die sie generieren.

---

## 1. Verzeichnisstruktur

```
Keno_GPTs/
├── [Root] - Hauptdateien fuer Analyse
├── Old/ - Aeltere Versionen und Archive
├── Daten/ - Statistikdateien fuer alle Spiele
├── Originale/ - Rohdaten vom Scraping
├── Kenogpts_2/ - Kombinatorik-Ergebnisse
└── selenium-4.17.2/ - Selenium Library
```

---

## 2. Datei-Kategorien

### 2.1 KENO Ziehungsdaten (Draw Data)

| Datei | Beschreibung | Spalten | Quelle |
|-------|--------------|---------|--------|
| `KENO_Ziehungen_2023_GPT.csv` | Vollstaendige Ziehungsdaten | Datum, z1-z20, Plus-5, Spieleinsatz | Web-Scraping |
| `KENO_Ziehungen_2023-2024_GPT.csv` | Erweitert 2023-2024 | wie oben | Web-Scraping |
| `Keno_Ziehung2023_+_Restbetrag_v2.CSV` | Mit Finanzanalyse | + Total_gewinner, Total_Auszahlung, Restbetrag, Kasse | Berechnet |
| `data/raw/keno/KENO_ab_2018.csv` | Hauptdatei fuer Backtest | Datum, z1-z20, Plus-5 | Archiv |

**Format (Ziehungsdaten):**
```csv
Datum;z1;z2;z3;z4;z5;z6;z7;z8;z9;z10;z11;z12;z13;z14;z15;z16;z17;z18;z19;z20;Plus-5;Spieleinsatz
01.01.2023;6;65;25;19;58;31;20;2;5;38;68;27;59;56;21;63;3;28;43;14;3320;342.774,00
```

### 2.2 Gewinnquoten (Prize Tiers)

| Datei | Beschreibung | Spalten | Quelle |
|-------|--------------|---------|--------|
| `Keno_GQ_2023.csv` | KENO Quoten 2023 | Datum, Keno-Typ, Richtige, Gewinner, Quote | Web-Scraping |
| `Keno_GQ_2024.csv` | KENO Quoten 2024 | wie oben | Web-Scraping |
| `Keno_GQ_2022_2023-2024.csv` | Kombiniert | wie oben | Aggregiert |
| `Plus5_GQ_2023.csv` | Plus5 Quoten | Datum, Gewinnklasse (1-5), Gewinner, Quote | Web-Scraping |
| `KENO_Quote_details_2023.csv` | Detaillierte Quoten | Extended Format | Web-Scraping |

**Format (Gewinnquoten):**
```csv
Datum,Keno-Typ,Anzahl richtiger Zahlen,Anzahl der Gewinner,1 Euro Gewinn
01.01.2023,10,10,0,100.000,00 €
01.01.2023,10,9,1,10.000,00 €
```

### 2.3 Pattern-Analyse Dateien

| Datei | Beschreibung | Generiert von | Zweck |
|-------|--------------|---------------|-------|
| `KENO_10K.csv` | Wiederholte Zahlen Tracking | 00_KENO_ALL_V3.py | Pattern-Erkennung |
| `KENO_10K1.csv` | Variante 1 | 00_KENO_ALL_V3.py | Analyse |
| `KENO_10K2.csv` | Variante 2 | 00_KENO_ALL_V3.py | Analyse |
| `10-9_CheckNumbers_z120.csv` | Cross-Check zwischen Ziehungen | 00_KENO_ALL_V3.py | Korrelation |
| `10-9_KGDaten_gefiltert.csv` | Gewinnklasse 1 Analyse | 00_KENO_ALL_V3.py | GK1-Muster |
| `10-9_NumbertoCheck.csv` | Zahlen fuer Validierung | 00_KENO_ALL_V3.py | Verifizierung |
| `10-9_Liste_GK1_Treffer.csv` | GK1 Treffer-Liste | 00_KENO_ALL_V3.py | Historie |

**Format (Pattern-Analyse):**
```csv
Datum;Anzahl Treffer;z1;z2;z3;z4;z5;z6;z7;z8;z9;z10;z11;z12;Anzahl-wiederholte-zahlen;Wiederholte Zahlen
02.01.2024;7;4;7;18;19;33;44;47;;;;;;0;
```

### 2.4 Andere Spiele

| Datei | Spiel | Beschreibung |
|-------|-------|--------------|
| `eurojackpot_archiv.csv` | EuroJackpot | Archiv-Daten |
| `eurojackpot_archiv_bereinigt.csv` | EuroJackpot | Bereinigt |
| `Lotto_archiv_bereinigt.csv` | Lotto 6aus49 | Bereinigt |

---

## 3. Unterverzeichnisse

### 3.1 Daten/ (Statistik-Hub)

| Datei | Spiel | Zeitraum |
|-------|-------|----------|
| `KENO_Stats_ab-2018.csv` | KENO | 2018+ |
| `KENO_Stats_ab-2004.csv` | KENO | 2004+ |
| `EuroJackpot_Stats_ab-2018.csv` | EuroJackpot | 2018+ |
| `Lotto_Archiv_ab-1955.csv` | Lotto | 1955+ |
| `lotto_Stats_ab-2018.csv` | Lotto | 2018+ |
| `Glueck_Spirale_Stats_ab-2018.csv` | GlueckSpirale | 2018+ |
| `Toto_6aus45_Stats_ab-2018.csv` | Toto | 2018+ |
| `Keno_GQ_2022_2023-2024_stats.csv` | KENO GQ | 2022-2024 |

### 3.2 Originale/ (Rohdaten)

| Datei | Beschreibung |
|-------|--------------|
| `KENO_ab_2004.csv` | Original KENO Archiv seit 2004 |
| `keno_Scrapping_RohData2022.csv` | Rohes Scraping 2022 |
| `keno_scrapping_RohData_2024.csv` | Rohes Scraping 2024 |
| `lottozahlen_archiv.csv` | Original Lotto Archiv |

### 3.3 Old/ (Archiv)

Aeltere Versionen und Backups der Hauptdateien.

### 3.4 Kenogpts_2/ (Kombinatorik)

Enthaelt `ergebnisse_v6-*.csv` Dateien - Kombinatorik-Berechnungen fuer Pattern-Matching.

---

## 4. Generierungs-Scripts

### 4.1 Web-Scraping (Keno_Webscrapping_Code.md)

**Funktion:** Scrapt Gewinnquoten von lotto-rlp.de
**Quelle:** https://www.lotto-rlp.de/keno/quoten
**Output:** Keno_GQ_*.csv, KENO_Quote_*.csv

```python
# Hauptfunktion
def scrape_keno_data_for_type(driver, date_url, keno_type, date_text):
    # Scrapt alle Keno-Typen (2-10) fuer ein Datum
    # Extrahiert: Gewinner, Quoten, Euro-Werte
```

**Verwendung:**
```bash
# Erfordert ChromeDriver
python scripts/scrape_quotes.py --year 2024 --output Keno_GQ_2024.csv
```

### 4.2 Pattern-Analyse (00_KENO_ALL_V3.py)

**Funktion:** Analysiert Ziehungsmuster und Wiederholungen
**Input:** KENO_Ziehungen_*.csv, Keno_GQ_*.csv
**Output:** 10-9_*.csv, KENO_10K*.csv

**Konfiguration:**
```python
file_config = {
    "gewinnquoten_path": "Keno_GQ_2023.csv",
    "ziehungen_path": "KENO_Ziehungen_2023_GPT.csv",
    "filtered_data_path": "10-9_KGDaten_gefiltert.csv",
    "numbertocheck_path": "10-9_NumbertoCheck.csv",
    "checknumbers_path": "10-9_CheckNumbers.csv",
    "liste_gk1_treffer_path": "10-9_Liste_GK1_Treffer.csv"
}
```

---

## 5. Datenfluss-Diagramm

```
[lotto-rlp.de]
       |
       v (Selenium Scraping)
[Keno_GQ_*.csv, KENO_Quote_*.csv]
       |
       v (Manuell / Konsolidierung)
[KENO_Ziehungen_*_GPT.csv]
       |
       +---> [00_KENO_ALL_V3.py]
       |            |
       |            v
       |     [10-9_*.csv, KENO_10K*.csv]
       |
       +---> [kenobase DataLoader]
                    |
                    v
              [Backtest/Analyse]
```

---

## 6. Update-Prozess

### 6.1 Manueller Prozess (Aktuell)

1. **Gewinnquoten scrapen:**
   ```bash
   python scripts/scrape_quotes.py --year 2024
   ```

2. **Pattern-Analyse ausfuehren:**
   ```bash
   python Keno_GPTs/00_KENO_ALL_V3.py
   ```

3. **Daten konsolidieren:**
   - Neue Ziehungen zu KENO_ab_2018.csv hinzufuegen
   - Deduplizierung pruefen

### 6.2 Automatisierter Prozess (Geplant - ISSUE-001)

Siehe `scripts/master_update.py` (NEU).

---

## 7. Wichtige Hinweise

### 7.1 Encoding
- Alle CSV-Dateien: UTF-8 oder Windows-1252
- Dezimaltrennzeichen: Komma (,) in deutschen Dateien
- Feldtrennzeichen: Semikolon (;) oder Komma (,)

### 7.2 Datumsformate
- Hauptformat: DD.MM.YYYY (z.B. 01.01.2023)
- Einige Dateien: YYYY-MM-DD

### 7.3 Zahlenformate
- Spieleinsatz: "342.774,00" (deutsches Format)
- Quoten: "5.000,00 EUR"

---

## 8. Pattern-Hypothesen

### 8.1 Regionale Gewinnverteilung (Konzept)

**Hypothese:** KENO-Gewinne werden absichtlich nach Bundeslaendern verteilt, basierend auf:
- Einwohnerzahl
- Anzahl aktiver Spieler
- Optimierung der Auszahlungsquote (min. 50% behalten)

**Kern-Idee:**
Wenn die Gewinnverteilung so gestaltet ist, dass Spieler "suechtig bleiben" (psychologische Verstärkung),
dann koennten Ziehungen mit maximalen Einzelgewinnen (z.B. 4 von 6 richtig)
die meistgezogenen Zahlen des entsprechenden "bevorzugten" Bundeslandes enthalten.

**Analyse-Dateien:**
| Datei | Zweck |
|-------|-------|
| `Keno_GQ_2022_2023-2024.csv` | Gewinnquoten mit Gewinner-Anzahl |
| `10-9_KGDaten_gefiltert.csv` | Gefilterte Gewinnklasse-1 Daten |
| `10-9_Liste_GK1_Treffer.csv` | Historie der GK1 Treffer |

**Pattern-Logik:**
```
1. Identifiziere Ziehungen mit ungewoehnlich hoher Einzelgewinner-Anzahl
2. Korreliere mit gezogenen Zahlen
3. Suche regionale Muster (falls Bundesland-Daten verfuegbar)
4. Hypothese: Diese Zahlen sind "bevorzugt" fuer zukuenftige Ziehungen
```

**Relevante Spalten in Keno_GQ_*.csv:**
- `Datum` - Ziehungsdatum
- `Keno-Typ` - Spielvariante (2-10)
- `Anzahl richtiger Zahlen` - Gewinnklasse
- `Anzahl der Gewinner` - Schluessel fuer die Analyse!
- `1 Euro Gewinn` - Quote

**Datenumfang:**
- `Keno_GQ_2022_2023-2024.csv`: 27.685 Zeilen (2022-2024)

---

## 9. Referenz-Tabelle: Datei -> Script -> Zweck

| Datei | Generiert von | Zweck | Update-Frequenz |
|-------|---------------|-------|-----------------|
| KENO_Ziehungen_*.csv | Web-Scraping | Rohdaten | Taeglich |
| Keno_GQ_*.csv | scrape_quotes.py | Gewinnquoten | Taeglich |
| KENO_10K*.csv | 00_KENO_ALL_V3.py | Pattern | Nach Update |
| 10-9_*.csv | 00_KENO_ALL_V3.py | Analyse | Nach Update |
| KENO_ab_2018.csv | Manual/Merge | Backtest-Basis | Woechentlich |

---

## Changelog

- 2025-12-27: Initiale Erstellung nach Keno_GPTs Analyse
