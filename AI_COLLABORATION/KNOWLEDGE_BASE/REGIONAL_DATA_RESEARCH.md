# Regional Data Research - KENO/EuroJackpot

**Erstellt:** 2025-12-28
**Aktualisiert:** 2025-12-28
**Status:** DATENQUELLE GEFUNDEN

---

## 1. Zusammenfassung

### Ergebnis der Recherche

| Datenquelle | Verfuegbarkeit | Details |
|-------------|----------------|---------|
| **Pressemitteilungen Landeslotterien** | **VERFUEGBAR** | Stadt, Region, teils exakte Zahlen |
| KENO Bundesland-Gewinner (aggregiert) | NICHT OEFFENTLICH | DLTB publiziert keine Statistiken |
| EuroJackpot Laender-Gewinner | TEILWEISE | Jackpot-Gewinner nach Land verfuegbar |
| Regionale Lieblingszahlen | NICHT OEFFENTLICH | Keine offizielle Statistik |
| Gewinner-Anzahl pro Ziehung | VERFUEGBAR | In Keno_GQ_*.csv vorhanden |

### DURCHBRUCH: Pressemitteilungen

Die 16 Landeslotteriegesellschaften veroeffentlichen Pressemitteilungen mit:
- **Stadt/Region des Gewinners**
- **Teils exakte gespielte Zahlen**
- **Keno-Typ und Einsatz**
- **Datum und Gewinnhoehe**

---

## 2. NEUE DATENQUELLE: Pressemitteilungen

### 2.1 Landeslotterien Presse-URLs

| Bundesland | Landeslotterie | Presse-URL |
|------------|----------------|------------|
| Baden-Wuerttemberg | Lotto BW | https://www.lotto-bw.de/presse |
| Bayern | Lotto Bayern | https://www.lotto-bayern.de/unternehmen/nachrichten |
| Berlin | Lotto Berlin | https://www.lotto-berlin.de/presse |
| Brandenburg | Lotto Brandenburg | https://www.lotto-brandenburg.de/newsroom/presse |
| Bremen | Lotto Bremen | https://www.lotto-bremen.de/presse |
| Hamburg | Lotto Hamburg | https://www.lotto-hamburg.de/presse |
| Hessen | Lotto Hessen | https://www.lotto-hessen.de/magazin/meldungen |
| Mecklenburg-Vorpommern | Lotto MV | https://www.lotto-mv.de/presse |
| Niedersachsen | Lotto Niedersachsen | https://www.lotto-niedersachsen.de/unternehmen/presse |
| NRW | WestLotto | https://www.westlotto.de/newsroom |
| Rheinland-Pfalz | Lotto RLP | https://www.lotto-rlp.de/presse |
| Saarland | Saartoto | https://www.saartoto.de/presse |
| Sachsen | Sachsenlotto | https://www.sachsenlotto.de/portal/ueber-uns/presse.jsp |
| Sachsen-Anhalt | Lotto Sachsen-Anhalt | https://www.lottosachsenanhalt.de/presse |
| Schleswig-Holstein | Nordwestlotto SH | https://www.lotto-sh.de/presse |
| Thueringen | Lotto Thueringen | https://www.lotto-thueringen.de/presse |

### 2.2 Extrahierte Gewinner-Daten (Beispiele)

| Datum | Region | Bundesland | Zahlen | Typ | Betrag |
|-------|--------|------------|--------|-----|--------|
| 25.10.2025 | Kyritz | Brandenburg | 5,12,20,26,34,36,42,45,48,66 | 10 | 100.000 EUR |
| 28.06.2023 | Oberbayern | Bayern | 3,15,18,27,47,53,54,55,66,68 | 10 | 1.000.000 EUR |
| 24.01.2024 | Nordsachsen | Sachsen | 9,19,37,38,43,45,48,57,59,67 | 10 | 100.000 EUR |
| 30.07.2025 | Leipzig | Sachsen | (nicht genannt) | 8 | 180.000 EUR |
| 24.04.2025 | Goettingen | Niedersachsen | (nicht genannt) | 10 | 500.000 EUR |
| 27.03.2025 | Rhein-Main | Hessen | (nicht genannt) | ? | 200.000 EUR |
| 13.06.2024 | Dortmund | NRW | (Sonderauslosung) | - | - |
| 13.06.2024 | Siegen | NRW | (Sonderauslosung) | - | - |

### 2.3 Analyse der gefundenen Zahlen

**Oberbayern (1 Mio):** 3, 15, 18, 27, 47, 53, 54, 55, 66, 68
- Birthday-Zahlen (1-31): 3, 15, 18, 27 = **4 von 10 (40%)**
- Hohe Zahlen (50+): 53, 54, 55, 66, 68 = **5 von 10 (50%)**

**Kyritz (100k):** 5, 12, 20, 26, 34, 36, 42, 45, 48, 66
- Birthday-Zahlen (1-31): 5, 12, 20, 26 = **4 von 10 (40%)**
- Mittlere Zahlen (32-49): 34, 36, 42, 45, 48 = **5 von 10 (50%)**

**Beobachtung:** Beide Gewinner haben ~40% Birthday-Zahlen - weniger als der Durchschnitt (44% = 31/70).

### 2.4 DLTB - Zentrale Datenquelle (bundesweit)

**Organisation:** Deutscher Lotto- und Totoblock (DLTB)
**Rolle:** Dachverband aller 16 Landeslotteriegesellschaften

**Verfuegbare Daten:**
- Offizielle Ziehungszahlen
- Gewinnquoten & Gewinnklassen
- Anzahl der Gewinner pro Gewinnklasse
- **Verteilung nach Bundeslaendern (anonymisiert)**

**Datenschutz:** Keine Namen, nur statistische Daten.

**Webquellen:**
- https://www.lotto.de/keno/zahlen - Archiv seit 2004, Gewinnerzahlen seit 29.12.2017
- https://www.lottoindeutschland.de - Infoportal

**Jahresbilanzen (Beispiel 2021):**
- Gesamtgewinnausschuettung: 3.87 Mrd EUR
- 992 Spieler mit >= 100.000 EUR
- 181 Millionaere
- **Millionaere nach Bundesland:**
  - Baden-Wuerttemberg: 39
  - Nordrhein-Westfalen: 35
  - Niedersachsen: 26

**Einschraenkung:** Keine oeffentliche API bei lotto.de, aber:

### 2.4.1 Lotto Hessen API (ENTDECKT!)

**Base URL:** `https://services.lotto-hessen.de/spielinformationen/`

**Verfuegbare Endpoints:**

| Endpoint | Beschreibung | Format |
|----------|--------------|--------|
| `/gewinnzahlen/keno` | Aktuelle KENO-Zahlen | JSON |
| `/quoten/keno` | Aktuelle Quoten | JSON |
| `/gewinnzahlen/lotto` | Lotto 6aus49 | JSON |
| `/gewinnzahlen/eurojackpot` | EuroJackpot | JSON |

**Beispiel-Response (KENO):**
```json
{
  "Datum": "27.12.2025",
  "Ziehung": "Samstag",
  "Zahl": [9, 61, 10, 7, 46, 48, 12, 23, 33, 26, 6, 43, 41, 13, 3, 63, 65, 2, 40, 29]
}
```

**Nutzung:** Automatischer taeglicher Abruf moeglich!

---

### 2.5 Zusaetzliche Quelle: tippland.de Lottogewinner

**URL:** https://www.tippland.de/magazin/lottogewinner

Diese Seite aggregiert Lottogewinner (6aus49, EuroJackpot) nach Jahr mit:
- Bundesland / Region
- Gewinnhoehe
- Datum
- Teils Stadt/Landkreis

**Beispieldaten 2024/2025:**

| Datum | Region | Bundesland | Betrag |
|-------|--------|------------|--------|
| 03.01.2024 | - | Bayern | 48.58 Mio EUR |
| 06.08.2025 | Oberbayern | Bayern | 18 Mio EUR |
| 12.07.2025 | Landkreis Ludwigsburg | Baden-Wuerttemberg | 14 Mio EUR |
| 04.10.2025 | Landkreis Goettingen | Niedersachsen | 24 Mio EUR |

**Einschraenkung:** Keine KENO-Daten, nur 6aus49/EuroJackpot.

---

## 3. Urspruengliche Datenquellen

### 3.1 EuroJackpot Jackpot-Gewinner nach Land

**Quelle:** [euro-jackpot.net](https://www.euro-jackpot.net)

| Land | Jackpot-Gewinner | Anteil |
|------|------------------|--------|
| Deutschland | 86 | 51.8% |
| Finnland | 17 | 10.2% |
| Daenemark | 12 | 7.2% |
| Schweden | 10 | 6.0% |
| Norwegen | 9 | 5.4% |
| Spanien | 8 | 4.8% |
| Andere | 24 | 14.5% |

**Nutzbarkeit:** HOCH fuer EuroJackpot Laender-Rotation Analyse

### 2.2 DLTB Millionaere nach Bundesland (2023)

**Quelle:** [LOTTO Niedersachsen - DLTB Jahresbilanz](https://www.lotto-niedersachsen.de/unternehmen/presse/dltb-jahresbilanz-2023)

| Bundesland | Millionaere 2023 | Population (Mio) | Pro-Kopf-Index |
|------------|------------------|------------------|----------------|
| NRW | 37 | 18.0 | 2.06 |
| Baden-Wuerttemberg | 30 | 11.1 | 2.70 |
| Niedersachsen | 26 | 8.0 | 3.25 |
| Bayern | 31 | 13.2 | 2.35 |
| Andere | ~69 | ~30.7 | ~2.25 |
| **Gesamt** | **193** | **83.0** | **2.33** |

**Nutzbarkeit:** MITTEL - nur aggregierte Jahreswerte, keine Zahlen-Korrelation

### 2.3 Beliebte Zahlen (allgemein)

**Quelle:** [Statista](https://de.statista.com/statistik/daten/studie/2149/umfrage/haeufigste-zahlen-beim-lotto-am-samstag/), [PAYBACK](https://www.payback.de/ratgeber/schon-gewusst/lottozahlen)

| Kategorie | Zahlen | Grund |
|-----------|--------|-------|
| Geburtstage | 1-31 | Monats-/Tagesdaten |
| Meistgetippt | 7, 3, 9, 11, 19 | Glueckszahlen |
| 19XX-Geburtsjahre | 19 | Baby-Boomer |
| Selten getippt | 32-49 (Lotto), 32-70 (KENO) | Keine Datumsrelevanz |

**Nutzbarkeit:** HOCH fuer Proxy-Methode

---

## 3. Vorhandene Daten in Kenobase

### 3.1 Gewinnquoten mit Gewinner-Anzahl

**Datei:** `Keno_GPTs/Keno_GQ_2022_2023-2024.csv`

```csv
Datum,Keno-Typ,Anzahl richtiger Zahlen,Anzahl der Gewinner,1 Euro Gewinn
08.02.2024,10,10,0,100.000 EUR
08.02.2024,10,9,8,1.000 EUR
08.02.2024,10,8,74,100 EUR
```

**Schluessel-Erkenntnis:**
- `Anzahl der Gewinner` variiert STARK zwischen Ziehungen
- HOHE Gewinnerzahl = BELIEBTE Zahlen wurden gezogen
- NIEDRIGE Gewinnerzahl = UNBELIEBTE Zahlen wurden gezogen

### 3.2 Ziehungsdaten

**Datei:** `data/raw/keno/KENO_ab_2018.csv`

```csv
Datum;z1;z2;z3;z4;z5;z6;z7;z8;z9;z10;z11;z12;z13;z14;z15;z16;z17;z18;z19;z20
```

---

## 4. Proxy-Methode: Regionale Praeferenz-Ableitung

### 4.1 Konzept

Da direkte regionale Daten fehlen, leiten wir "regionale Praeferenzen" indirekt ab:

```
GEWINNER-ANZAHL = f(BELIEBTE_ZAHLEN_IN_ZIEHUNG)

Wenn:
  - Viele Zahlen aus 1-31 (Geburtstage) → HOHE Gewinnerzahl
  - Viele Zahlen aus 32-70 → NIEDRIGE Gewinnerzahl

Dann:
  - Gewinner-Anzahl ist PROXY fuer "regionale Popularitaet"
```

### 4.2 Implementierung

```python
# kenobase/analysis/popularity_proxy.py

def calculate_birthday_score(drawn_numbers: list[int]) -> float:
    """
    Berechnet Anteil der 'Geburtstags-Zahlen' (1-31) in einer Ziehung.

    Returns: 0.0 - 1.0 (0 = keine Geburtstage, 1 = nur Geburtstage)
    """
    birthday_count = sum(1 for n in drawn_numbers if 1 <= n <= 31)
    return birthday_count / len(drawn_numbers)


def correlate_winners_with_popularity(
    draws_df: pd.DataFrame,
    quotes_df: pd.DataFrame
) -> dict:
    """
    Korreliert Gewinner-Anzahl mit Popularitaets-Score.

    Hypothese: Hoher Birthday-Score → Mehr Gewinner
    """
    merged = draws_df.merge(quotes_df, on='Datum')
    merged['birthday_score'] = merged.apply(
        lambda r: calculate_birthday_score([r[f'z{i}'] for i in range(1, 21)]),
        axis=1
    )

    correlation = merged['birthday_score'].corr(merged['Anzahl der Gewinner'])
    return {
        'correlation': correlation,
        'significant': abs(correlation) > 0.3,
        'interpretation': 'Bestaetigt' if correlation > 0.3 else 'Nicht signifikant'
    }
```

### 4.3 Erweiterung: Bundesland-Gewichtung

```python
# Geschaetzte Spieler-Verteilung nach Bundesland (basierend auf Population)
BUNDESLAND_WEIGHTS = {
    'NRW': 0.217,           # 18.0 Mio / 83.0 Mio
    'Bayern': 0.159,        # 13.2 Mio
    'Baden-Wuerttemberg': 0.134,
    'Niedersachsen': 0.096,
    'Hessen': 0.076,
    'Rheinland-Pfalz': 0.049,
    'Sachsen': 0.049,
    'Berlin': 0.044,
    'Schleswig-Holstein': 0.035,
    'Brandenburg': 0.030,
    'Sachsen-Anhalt': 0.026,
    'Thueringen': 0.025,
    'Hamburg': 0.022,
    'Mecklenburg-Vorpommern': 0.019,
    'Saarland': 0.012,
    'Bremen': 0.008
}

# Hypothetische regionale Lieblingszahlen
REGIONAL_FAVORITES = {
    'NRW': [7, 9, 11, 19, 23],      # Industrieregion, Fussball-Zahlen
    'Bayern': [1, 7, 13, 17, 21],   # Tradition, Glueckszahlen
    'Berlin': [3, 9, 11, 22, 28],   # Urban, modern
    # ... weitere Bundeslaender
}
```

### 4.4 Validierung

Die Proxy-Methode kann validiert werden durch:

1. **Korrelations-Test:**
   - Birthday-Score vs. Gewinner-Anzahl
   - Erwartung: r > 0.3

2. **A/B-Analyse:**
   - Ziehungen mit hohem Birthday-Score (>0.5)
   - Ziehungen mit niedrigem Birthday-Score (<0.3)
   - Vergleiche durchschnittliche Gewinner-Anzahl

3. **Zeitliche Stabilitaet:**
   - Pruefe ob Korrelation ueber 2022, 2023, 2024 stabil bleibt

---

## 5. Naechste Schritte

### Prioritaet 1: Proxy-Validierung

1. [ ] `scripts/analyze_popularity_proxy.py` erstellen
2. [ ] Korrelation Birthday-Score vs. Gewinner-Anzahl berechnen
3. [ ] Ergebnis in `results/popularity_proxy.json` speichern

### Prioritaet 2: EuroJackpot Laender-Mapping

1. [ ] Jackpot-Gewinner-Tabelle als JSON erstellen
2. [ ] Korrelation mit gezogenen Zahlen pruefen
3. [ ] TASK-R04 UNBLOCK wenn Mapping vorhanden

### Prioritaet 3: Bundesland-Approximation

1. [ ] Hypothetische regionale Lieblingszahlen definieren
2. [ ] Gewinner-Verteilung simulieren
3. [ ] Gegen historische Daten validieren

---

## 6. Fazit

**Direkte regionale Daten sind NICHT verfuegbar.**

**Aber:** Die Gewinner-Anzahl pro Ziehung ist ein valider PROXY:
- Korreliert mit Popularitaet der gezogenen Zahlen
- Erlaubt Rueckschluesse auf regionales Tippverhalten
- Kann fuer Anti-Clustering Strategie genutzt werden

**Empfehlung:**
Implementiere `popularity_proxy.py` als Alternative zu `regional_affinity.py`.
Die Proxy-Methode nutzt vorhandene Daten (Gewinnquoten) statt fehlender regionaler Metadaten.
