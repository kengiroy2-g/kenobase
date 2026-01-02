# HANDOFF: KENO Gewinner-Muster Analyse

**Von:** Claude (Datensammlung & Erstanalyse)
**An:** Naechste KI (Pattern-Architektur & Deep Analysis)
**Datum:** 01.01.2026
**Status:** 3 verifizierte Samples bereit fuer Analyse

---

## 1. VERIFIZIERTE GEWINNER-TIPPSCHEINE

### Rohdaten (alle verifiziert gegen Ziehungsdatenbank)

| # | Datum | Ort | Tippschein-Zahlen | Gewinn | Einsatz | Quelle |
|---|-------|-----|-------------------|--------|---------|--------|
| 1 | 25.10.2025 | Kyritz, Brandenburg | `[5,12,20,26,34,36,42,45,48,66]` | 100.000 EUR | 1 EUR | lotto-brandenburg.de |
| 2 | 28.06.2023 | Oberbayern, Bayern | `[3,15,18,27,47,53,54,55,66,68]` | 1.000.000 EUR | 10 EUR | lotto-bayern.de |
| 3 | 24.01.2024 | Nordsachsen, Sachsen | `[9,19,37,38,43,45,48,57,59,67]` | 100.000 EUR | ? | presseportal.de |

### Ziehungszahlen (20) pro Tag

```python
# 25.10.2025 - Kyritz
drawn_kyritz = [2, 5, 9, 12, 19, 20, 26, 34, 35, 36, 39, 42, 45, 48, 49, 54, 55, 62, 64, 66]
winner_kyritz = [5, 12, 20, 26, 34, 36, 42, 45, 48, 66]
non_winner_kyritz = [2, 9, 19, 35, 39, 49, 54, 55, 62, 64]

# 28.06.2023 - Oberbayern
drawn_bayern = [3, 6, 13, 15, 18, 24, 27, 36, 38, 40, 43, 47, 51, 53, 54, 55, 56, 63, 66, 68]
winner_bayern = [3, 15, 18, 27, 47, 53, 54, 55, 66, 68]
non_winner_bayern = [6, 13, 24, 36, 38, 40, 43, 51, 56, 63]

# 24.01.2024 - Nordsachsen
drawn_sachsen = [3, 7, 9, 12, 13, 16, 17, 19, 21, 36, 37, 38, 43, 45, 48, 52, 54, 57, 59, 67]
winner_sachsen = [9, 19, 37, 38, 43, 45, 48, 57, 59, 67]
non_winner_sachsen = [3, 7, 12, 13, 16, 17, 21, 36, 52, 54]
```

---

## 2. BISHERIGE ANALYSE-ERGEBNISSE

### 2.1 Index-Muster (Streak-Analyse)

**Definition:** Index = Anzahl aufeinanderfolgender Tage, an denen eine Zahl gezogen wurde

**Kyritz 25.10.2025:**
```
Gewinner-Zahlen Index:    [2, 2, 2, 2, 2, 3, 5, 2, 2, 2]  -> Mean: 2.40
Nicht-Gewinner Index:     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  -> Mean: 1.00
Trennung: 100% der Gewinner haben Index >= 2
```

**Oberbayern 28.06.2023:**
```
Gewinner-Zahlen Index:    [1, 3, 1, 1, 2, 1, 1, 3, 1, 1]  -> Mean: 1.50
Nicht-Gewinner Index:     [2, 3, 3, 2, 1, 1, 1, 1, 1, 1]  -> Mean: 1.60
Trennung: KEINE (30% vs 40% mit Index >= 2)
```

**FAZIT:** Index-Muster funktioniert NUR bei Kyritz (Sonderfall: exakt 10 Zahlen mit Index >= 2)

### 2.2 Birthday-Zahlen Analyse

| Fall | Birthday (1-31) | Anteil |
|------|-----------------|--------|
| Kyritz | 4 von 10 | 40% |
| Oberbayern | 4 von 10 | 40% |
| Nordsachsen | 1 von 10 | 10% |
| **Erwartung (Zufall)** | **4.4 von 10** | **44%** |

**BEOBACHTUNG:** Alle 3 Gewinner haben <= Durchschnitt Birthday-Zahlen

### 2.3 Kombinatorik-Analyse (Kyritz)

Aus 20 Ziehungszahlen sind C(20,10) = 184.756 Kombinationen moeglich.

| Metrik | Gewinner | Alle Kombis (Mean) | Z-Score |
|--------|----------|-------------------|---------|
| consecutive_pairs | 0 | 1.19 | -1.36 |
| jp_freq_sum | 53 | 58.51 | -0.92 |
| combo_sum | 334 | 361.18 | -0.61 |
| birthday_count | 4 | 3.50 | +0.46 |

**BEOBACHTUNG:** Keine konsekutiven Paare, niedrige Jackpot-Frequenz

---

## 3. KENO SYSTEM-WISSEN (aus CLAUDE.md)

### 3.1 Die 7 Axiome (MUSS beachten)

| ID | Axiom | Relevanz fuer Muster-Suche |
|----|-------|---------------------------|
| A1 | **House-Edge** | 50% Redistribution - System MUSS profitabel bleiben |
| A2 | **Dauerscheine** | Spieler nutzen feste Kombinationen - System kennt beliebte Muster |
| A3 | **Attraktivitaet** | Kleine Gewinne MUESSEN regelmaessig sein |
| A4 | **Paar-Garantie** | Zahlenpaare sichern Spielerbindung |
| A5 | **Pseudo-Zufall** | Jede Zahl muss in Periode erscheinen |
| A6 | **Regionale Verteilung** | Gewinne pro Bundesland verteilt |
| A7 | **Reset-Zyklen** | System "spart" nach Jackpots |

### 3.2 Axiom-First Paradigma

```
VERBOTEN: Daten -> Statistische Muster suchen -> Interpretation
RICHTIG:  Wirtschaftslogik (Axiome) -> Vorhersagen ableiten -> Daten testen
```

**Kern-Erkenntnis:** Das System wurde von Top-Ingenieuren konzipiert um einfache Pattern-Suche zu verhindern!

### 3.3 Relevante Hypothesen aus CLAUDE.md

1. **Anti-Birthday-Hypothese:** System vermeidet beliebte Zahlen (1-31) bei grossen Auszahlungen
2. **Jackpot-Cooldown:** Nach Jackpot = weniger Gewinne (A7)
3. **Index/Streak-Relevanz:** Zahlen mit laengeren Streaks koennten bevorzugt werden

---

## 4. VERFUEGBARE METRIKEN

### 4.1 Number Index Tracker (taeglich berechnet)

| Metrik | Beschreibung | Datei |
|--------|--------------|-------|
| **Index** | Streak - Tage in Folge gezogen | `results/number_index_*.txt` |
| **Mcount** | Monats-Count | |
| **Count** | Gesamt-Count (Reset nach Jackpot) | |
| **JCount** | Jackpot-Erscheinungen (kumulativ) | |
| **TCount** | Total-Count (nie Reset) | |

### 4.2 GQ-Daten (Gewinnquoten)

| Datei | Inhalt |
|-------|--------|
| `Keno_GPTs/Keno_GQ_2023.csv` | Gewinner-Anzahl pro Ziehung 2023 |
| `Keno_GPTs/Keno_GQ_2024.csv` | Gewinner-Anzahl pro Ziehung 2024 |
| `Keno_GPTs/Keno_GQ_2025.csv` | Gewinner-Anzahl pro Ziehung 2025 |

**Wichtig:** `Anzahl der Gewinner` bei 10/10 zeigt wie viele den Jackpot gewonnen haben

### 4.3 Ziehungsdaten

```
data/raw/keno/KENO_ab_2022_bereinigt.csv  # 2022-2025
Keno_GPTs/Kenogpts_2/Basis_Tab/KENO_ab_2018.csv  # 2018-2024
```

---

## 5. ANALYSE-SCRIPTS (bereits vorhanden)

| Script | Funktion |
|--------|----------|
| `scripts/analyze_jackpot_combinations.py` | Generiert alle C(20,10) Kombis, berechnet Metriken |
| `scripts/number_index_tracker.py` | Berechnet Index/Streak fuer alle Zahlen |
| `scripts/list_all_jackpots.py` | Listet alle 10/10 Jackpot-Tage |

---

## 6. EMPFEHLUNGEN FUER PATTERN-ANALYSE

### 6.1 Was NICHT funktioniert hat

- **Einfaches Index-Kriterium:** Funktioniert nur bei Kyritz (Sonderfall)
- **Einzelne Metriken:** Keine klare Trennung bei Z-Score Analyse

### 6.2 Vielversprechende Ansaetze

1. **Multi-Metrik Kombination:**
   - Index + Birthday + Jackpot-Frequenz kombinieren
   - Gewichtete Score-Funktion entwickeln

2. **Kontext-abhaengige Analyse:**
   - Anzahl Gewinner am Tag (1 vs 10) als Faktor
   - Kyritz hatte 1 Gewinner, Oberbayern hatte 10 Gewinner
   - Hypothese: Bei vielen Gewinnern = weniger selektiv

3. **Zeitliche Muster:**
   - Wochentag-Effekte
   - Post-Jackpot Cooldown pruefen
   - Monats-Zyklen

4. **Dekaden-Verteilung:**
   - 1-10, 11-20, ..., 61-70
   - Gewinner-Kombis vs. Nicht-Gewinner analysieren

5. **Konsekutiv-Vermeidung:**
   - Kyritz hatte 0 konsekutive Paare
   - Pruefen ob das ein Muster ist

### 6.3 Axiom-First Vorhersagen testen

| Axiom | Vorhersage | Test |
|-------|------------|------|
| A2 (Dauerscheine) | Gewinner vermeiden "beliebte" Muster | Birthday-Anteil < 44%? |
| A6 (Regional) | Verteilung nach Bundesland | Korrelation mit Population? |
| A7 (Reset) | Nach Jackpot weniger Gewinne | GQ-Daten analysieren |

---

## 7. WICHTIGE DATEIEN

```
results/jackpot_winner_pattern_analysis.md     # Hauptdokumentation
AI_COLLABORATION/KNOWLEDGE_BASE/REGIONAL_DATA_RESEARCH.md  # Datenquellen
CLAUDE.md                                       # System-Wissen & Axiome
```

---

## 8. OFFENE FRAGEN

1. **Warum funktioniert Index-Muster nur bei Kyritz?**
   - Hypothese: Anzahl verfuegbarer Index>=2 Zahlen ist entscheidend

2. **Gibt es Muster bei "Anzahl der Gewinner"?**
   - Kyritz: 1 Gewinner (selektiv?)
   - Oberbayern: 10 Gewinner (weniger selektiv?)

3. **Jackpot-Frequenz als Kontra-Indikator?**
   - Zahlen die oft bei Jackpots erscheinen = weniger wahrscheinlich?

---

## 9. NAECHSTE SCHRITTE

1. **Alle 3 Samples mit ALLEN verfuegbaren Metriken analysieren**
2. **Gemeinsame Muster identifizieren (was haben alle 3 gemeinsam?)**
3. **Unterschiede zu Nicht-Gewinnern quantifizieren**
4. **Hypothesen aus Axiomen ableiten und testen**
5. **Bei Erfolg: Backtest auf historische Jackpot-Tage**

---

## 10. DURCHBRUCH-ERKENNTNIS (01.01.2026)

### Paradigmenwechsel

**ALTE FRAGE:** "Welche Zahlen waehlt das System fuer den Jackpot?"
**NEUE ERKENNTNIS:** Das System waehlt KEINE spezifischen 10 Zahlen!

```
KENO-Mechanik:
1. System zieht 20 zufaellige Zahlen
2. JEDE 10er-Kombination aus diesen 20 gewinnt (wenn gespielt)
3. C(20,10) = 184.756 moegliche Gewinner-Kombinationen pro Ziehung!
```

### Popularitaets-Analyse

| Fall | Gewinner | Winner-Pop-Score | Non-Winner-Pop-Score | Differenz |
|------|----------|------------------|---------------------|-----------|
| Kyritz | 1 | 10 | 14 | +4 |
| Oberbayern | 10 | 12 | 11 | -1 |
| Nordsachsen | 1 | 11 | 31 | +20 |
| **GESAMT** | | **33** | **56** | **+23** |

**Pop-Score Kriterien:** Birthday +2, Glueckszahl +3, Rund +1, Einstellig +1

### Schlussfolgerung

```
NICHT: "Was wird gezogen?" (alle 20 Zahlen sind gleichwertig)
SONDERN: "Was spielt sonst NIEMAND?" (Vermeidung von Gewinn-Teilung)

Bei VIELEN Gewinnern (Oberbayern=10):
  -> Populaere Zahlen wurden gezogen
  -> Viele Spieler hatten aehnliche Kombinationen

Bei WENIG Gewinnern (Kyritz=1, Nordsachsen=1):
  -> Gewinner waehlte UNPOPULAERE Zahlen
  -> "Schwamm gegen den Strom"
```

### Strategische Implikation

**Gewinnwahrscheinlichkeit:** Nicht beeinflussbar (1:2.1 Mio bei Typ 10)

**Erwartungswert-Optimierung:**
- Waehle UNPOPULAERE Zahlen
- Vermeide: Birthday (1-31), Glueckszahlen (3,7,9,11,13,17,19,21), Runde Zahlen
- Bevorzuge: Hohe Zahlen (50-70), "Langweilige" Zahlen (34-49)

### Offene Validierung

Mit nur 3 Samples ist diese Hypothese NICHT statistisch signifikant.

**Naechster Schritt:**
Analysiere GQ-Daten (Gewinner-Anzahl) ueber alle Ziehungen:
- Korreliert "Anzahl Gewinner" mit Popularitaet der gezogenen Zahlen?
- Wenn ja: Bestaetigte Anti-Popularitaets-Strategie

---

## 11. ALGORITHMISCHE CHECKSUM-ANALYSE (01.01.2026)

### 11.1 Methodik

6 parallele Analyse-Agenten untersuchten die 3 verifizierten Gewinner-Kombinationen auf nicht-menschliche/algorithmische Eigenschaften:

| Agent | Analyse-Bereich | Ergebnis-Datei |
|-------|-----------------|----------------|
| Checksum | Mathematische Checksums | `scripts/analyze_checksum_properties.py` |
| Bit-Muster | Binary/XOR/Popcount | `results/bit_pattern_analysis.json` |
| Zahlentheorie | GCD/Coprime/Fibonacci | `results/number_theory_analysis.json` |
| Geometrie | Grid-Position/Cluster | `results/geometric_analysis.json` |
| Ziffern-Muster | Digit-Frequenz/Palindrome | `results/digit_pattern_analysis.json` |

### 11.2 GEFUNDENE INVARIANTEN (ALLE 3 KOMBINATIONEN)

#### STARK (exakt gleich bei allen 3):

| Eigenschaft | Wert | Bedeutung |
|-------------|------|-----------|
| **Ziffernprodukt mod 9** | **0** | Produkt aller Ziffern (ohne 0) ist durch 9 teilbar |
| **Dekade 00-09** | **1 Zahl** | Exakt eine einstellige Zahl pro Kombination |
| **Dekaden besetzt** | **6 von 7** | Genau 6 Dekaden haben mindestens 1 Zahl |
| **Zeilen genutzt** | **6 von 7** | 85.7% Zeilen-Streuung auf KENO-Spielschein |
| **Drittel-Abdeckung** | **Alle** | Zahlen aus (1-23), (24-46) UND (47-70) |

#### POTENTIELLE CONSTRAINTS:

| Eigenschaft | Bereich | Beobachtung |
|-------------|---------|-------------|
| Summe | 330-430 | Durchschnitt ~387 |
| Spannweite | 58-65 | Max-Min relativ einheitlich |
| Zentroid-Distanz | < 2.0 | Schwerpunkt nahe Grid-Mitte |
| Nachbar-Paare | <= 4 | Wenige direkte Nachbarn |

### 11.3 ZIFFERN-MUSTER (AUFFAELLIG)

| Muster | Befund | Bedeutung |
|--------|--------|-----------|
| Endziffer 1 | **0x** | KEINE Zahl endet auf 1 (11,21,31...fehlen) |
| Ziffer 5 | 10x | Haeufigste Ziffer (1.75x Erwartung) |
| Ziffer 0 | 1x | Seltenste (0.18x Erwartung) |
| Digitale Wurzel 3/9 | 7x/7x | 2x haeufiger als erwartet |
| Aufsteigende Ziffern | 4 Zahlen | 12, 34, 45, 67 |

### 11.4 BIT-MUSTER

| Kombination | XOR | Popcount | Parity |
|-------------|-----|----------|--------|
| Kyritz | 116 | 24 | EVEN |
| Oberbayern | 24 | 34 | EVEN |
| Nordsachsen | 110 | 33 | ODD |

**Befund:** Kein konsistentes XOR/Parity-Muster. Bits 3 und 4 leicht unterrepraesentiert.

### 11.5 ZAHLENTHEORETISCHE EIGENSCHAFTEN

| Eigenschaft | Kyritz | Oberbayern | Nordsachsen |
|-------------|--------|------------|-------------|
| GCD | 1 | 1 | 1 |
| Coprime-Ratio | 20% | 56% | 78% |
| Primzahlen | 1 | 3 | 5 |
| Fibonacci exakt | 5, 34 | 3, 55 | - |
| Collatz avg | 12.7 | **53.5** | 22.8 |

**Anomalie Oberbayern:** Extrem hohe Collatz-Komplexitaet (Zahlen 27, 54, 55 benoetigen >100 Schritte).

### 11.6 GEOMETRISCHE INVARIANTEN

```
Grid-Layout (7x10):
     1  2  3  4  5  6  7  8  9  10
R1 [ 1  2  3  4  5  6  7  8  9  10]
R2 [11 12 13 14 15 16 17 18 19  20]
...
R7 [61 62 63 64 65 66 67 68 69  70]
```

| Eigenschaft | Kyritz | Oberbayern | Nordsachsen | Gemeinsam? |
|-------------|--------|------------|-------------|------------|
| Zeilen genutzt | 6 | 6 | 6 | JA |
| Spalten genutzt | 6 | 6 | 5 | ~JA |
| Diagonalen-Score | 4 | 3 | 5 | 3-5 |
| Zentroid-Distanz | 0.22 | 0.51 | 1.77 | <2.0 |
| Nachbar-Paare | 1 | 2 | 4 | <=4 |

### 11.7 HYPOTHETISCHER VALIDIERUNGS-ALGORITHMUS

```python
def is_valid_keno_winner(combo: list[int]) -> bool:
    """
    Hypothetische Prueffunktion basierend auf gefundenen Invarianten.
    """

    # 1. Ziffernprodukt-Check (EXAKT)
    prod = 1
    for z in combo:
        for d in str(z):
            if d != '0':
                prod *= int(d)
    if prod % 9 != 0:
        return False

    # 2. Genau eine einstellige Zahl (EXAKT)
    if sum(1 for z in combo if z <= 9) != 1:
        return False

    # 3. Alle Drittel besetzt (EXAKT)
    has_1_23 = any(1 <= z <= 23 for z in combo)
    has_24_46 = any(24 <= z <= 46 for z in combo)
    has_47_70 = any(47 <= z <= 70 for z in combo)
    if not (has_1_23 and has_24_46 and has_47_70):
        return False

    # 4. Genau 6 Dekaden besetzt (EXAKT)
    dekaden = set(z // 10 for z in combo)
    if len(dekaden) != 6:
        return False

    # 5. Zeilen-Streuung >= 85% (EXAKT)
    zeilen = set((z-1) // 10 for z in combo)
    if len(zeilen) < 6:
        return False

    return True
```

### 11.8 NICHT GEFUNDENE MUSTER

- Keine konsistente XOR-Checksumme
- Keine Luhn/Fletcher-aehnliche Checksum
- Keine Bit-Parity-Konsistenz
- Keine Primzahl-Constraints
- Keine konsistente Modulo-Summe

### 11.9 EMPFEHLUNG FUER WEITERE ANALYSE

1. **Validierung auf mehr Daten:** Die 5 exakten Invarianten auf ALLE historischen Jackpot-Tage testen
2. **Negative Control:** Pruefen ob zufaellige 10er-Kombinationen die Kriterien SELTENER erfuellen
3. **Spieler-Daten:** Falls verfuegbar - wie oft erfuellen Spieler-Tippscheine diese Kriterien?

---

## 12. ANALYSE-SCRIPTS (NEU ERSTELLT)

| Script | Funktion |
|--------|----------|
| `scripts/analyze_checksum_properties.py` | Mathematische Checksums |
| `scripts/analyze_checksum_deep.py` | Tiefe Checksum-Analyse |
| `scripts/checksum_final_table.py` | Finale Tabelle |
| `scripts/analyze_bit_patterns.py` | Bit-Muster-Analyse |
| `scripts/number_theory_analysis.py` | Zahlentheorie |
| `scripts/analyze_geometric_patterns.py` | Geometrische Muster |
| `scripts/analyze_digit_patterns.py` | Ziffern-Muster |

---

*Erstellt: 01.01.2026*
*Aktualisiert: 01.01.2026 (Algorithmische Checksum-Analyse)*
*Projekt: Kenobase V2.0 - Reverse Engineering*
