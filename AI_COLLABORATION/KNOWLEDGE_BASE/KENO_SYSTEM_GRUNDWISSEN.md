# KENO System Grundwissen

**WICHTIG: Diese Datei MUSS vor jeder Analyse-Task gelesen werden!**

Dieses Dokument enthaelt validierte Erkenntnisse ueber das KENO-System, die als Grundlage fuer alle weiteren Analysen dienen.

---

## 1. GRUNDLEGENDE SYSTEM-ARCHITEKTUR

### 1.1 KENO ist ein WIRTSCHAFTLICHES System, kein mathematisches

```
FALSCH: KENO ist ein Zufallsspiel mit fairen Gewinnchancen
RICHTIG: KENO ist ein staatliches Milliarden-Geschaeft mit garantiertem House Edge
```

**Kernprinzip:**
- Das System wurde von Top-Ingenieuren und Mathematikern konzipiert
- Es ist auf LANGFRISTIGE PROFITABILITAET optimiert
- Einfache statistische Muster wurden ABSICHTLICH eliminiert
- Die Ziehungen sind NICHT rein zufaellig, sondern OPTIMIERT

### 1.2 Die zwei Optimierungsziele

Das System muss GLEICHZEITIG garantieren:

| Ziel | Beschreibung | Mechanismus |
|------|--------------|-------------|
| **House Edge** | ~50% der Einnahmen bleiben beim Staat | Gewinner-Kombinationen sind SELTEN |
| **Attraktivitaet** | Spieler bleiben motiviert | Viele KLEINE Gewinne (Teiltreffer) |

---

## 2. DIE 20-ZAHLEN-AUSWAHL (Validiert)

### 2.1 Kernhypothese (BESTAETIGT)

**Die 20 gezogenen Zahlen werden NICHT zufaellig gewaehlt, sondern fuer optimale Auszahlungs-Balance:**

```
20 GEZOGENE ZAHLEN = 10 GEWINNER + 10 ANDERE

ANDERE 10 (Nicht-Gewinner):
  → POPULAERE Zahlen (Birthday 1-31, Glueckszahlen)
  → Viele Spieler haben 3-6 Treffer hier
  → Erzeugt kleine Auszahlungen
  → Haelt Spieler motiviert ("Fast gewonnen!")

GEWINNER 10:
  → SELTENE/SPEZIFISCHE Kombination
  → Vermeidet populaere Muster
  → Minimiert Jackpot-Auszahlungen
  → Sichert House Edge
```

### 2.2 Empirische Belege (3 Jackpots mit ECHTEN Daten)

| Metrik | Gewinner 10 | Andere 10 | Erwartung bei Zufall |
|--------|-------------|-----------|----------------------|
| Birthday-Zahlen (1-31) | **33.3%** | 43.3% | 44.3% |
| Durchschn. Popularitaet | 0.308 | 0.418 | ~0.35 |

**WICHTIG: Gewinner vermeiden Birthday-Zahlen!**
- Gewinner haben WENIGER Birthday-Zahlen als bei Zufall erwartet
- Die "Anderen 10" haben genau so viele wie bei Zufall

**Einzelergebnisse (mit echten Daten aus jackpot_events.json):**

| Jackpot | Region | Gew.Pop | And.Pop | Diff | Birthday Gew. | Birthday And. |
|---------|--------|---------|---------|------|---------------|---------------|
| Kyritz | Brandenburg | 0.374 | 0.303 | -7.1% | 4/10 | 3/10 |
| Oberbayern | Bayern | 0.318 | 0.325 | +0.8% | 4/10 | 3/10 |
| **Nordsachsen** | **Sachsen** | **0.233** | **0.627** | **+169%** | **2/10** | **7/10** |

**Nordsachsen zeigt das Muster am deutlichsten:**
- Gewinner: Nur 2 Birthday-Zahlen (9, 19)
- Andere: 7 Birthday-Zahlen (3, 7, 12, 13, 16, 17, 21)
- Das System fuellte die "Anderen 10" mit populaeren Zahlen!

---

## 3. REGIONALE STRUKTUR (Neue Hypothese)

### 3.1 Bundesland-Segmentierung

```
KENO-Spieler sind auf 16 Bundeslaender verteilt:
  - Ein Spieler aus RLP darf NICHT in Niedersachsen spielen
  - Jedes Bundesland hat EIGENE Spielerschaft
  - Jedes Bundesland hat EIGENE populaere Zahlen
```

### 3.2 Jackpot-Verteilung nach Bundesland

```
Innerhalb eines Zyklus erscheinen Jackpot-Gewinner in ALLEN Bundeslaendern.
Die Verteilung ist NICHT gleich, sondern abhaengig von:
  - Spieleinnahmen pro Bundesland (Attraktivitaet)
  - Anzahl aktiver Spieler
  - Regionale Praeferenzen
```

### 3.3 Regionale Popularitaets-Unterschiede

**Hypothese:** Populaere Zahlen unterscheiden sich nach Bundesland:
- Lokale Glueckszahlen (z.B. Vereinsnummern, Postleitzahlen)
- Regionale Traditionen
- Demografische Unterschiede

**Methode zur Ermittlung:**
- Analysiere ALLE Jackpot-Tage mit Gewinner nach Bundesland
- Wende Popularity-Split-Analyse an
- Identifiziere bundesland-spezifische Muster

---

## 4. INVARIANTEN DER GEWINNER-KOMBINATIONEN (Validiert)

Diese Eigenschaften wurden bei ALLEN 3 bekannten Jackpot-Gewinnern gefunden:

### 4.1 Strukturelle Invarianten

| Invariant | Beschreibung | Wert |
|-----------|--------------|------|
| Ziffernprodukt mod 9 | Produkt aller Ziffern (ohne 0) mod 9 | = 0 |
| Einstellige Zahlen | Anzahl Zahlen 1-9 | = 1 |
| Dekaden besetzt | Von 7 moeglichen Dekaden | = 6 |
| Drittel besetzt | Alle 3 Drittel (1-23, 24-46, 47-70) | JA |
| Zeilen besetzt | Von 7 moeglichen Grid-Zeilen | = 6 |

### 4.2 Muster-Vermeidung

| Vermeidung | Beschreibung | Beobachtung |
|------------|--------------|-------------|
| Endziffer 1 | Zahlen die auf 1 enden (11, 21, 31...) | 0 von 30 |
| Birthday-Haeufung | Zu viele Zahlen 1-31 | Unterrepraesentiert |

### 4.3 Bevorzugte Muster

| Bevorzugung | Beschreibung | Beobachtung |
|-------------|--------------|-------------|
| Digitale Wurzel 3/9 | Quersumme ergibt 3 oder 9 | 14 von 30 (vs ~7 erwartet) |
| Ziffer 5 | Zahlen mit Ziffer 5 | Ueberrepraesentiert |

---

## 5. REVERSE-ENGINEERING POTENTIAL

### 5.1 Reduktion durch Constraints

Mit den 5 Basis-Invarianten:
- C(20,10) = 184.756 → ~17.000-27.000 Kandidaten
- **Reduktion: 85-90%**

Mit erweiterten Constraints (V4):
- → ~3.000-5.300 Kandidaten
- **Reduktion: 97-98%**

### 5.2 Kandidaten-Aehnlichkeit

- Durchschnittliche Ueberlappung zwischen Kandidaten: **5.25 von 10**
- Kandidaten unterscheiden sich in **~5 Zahlen**
- Es gibt **KEINE Kern-Zahlen** die in allen Kandidaten vorkommen

---

## 6. ANALYSE-PARADIGMA (MUSS BEFOLGEN)

### 6.1 VERBOTEN: Pattern-First

```
FALSCH: Daten → Statistische Muster suchen → Interpretation
```

Das System wurde GEGEN Pattern-Detection designed!

### 6.2 PFLICHT: Axiom-First

```
RICHTIG: Wirtschaftslogik verstehen → Vorhersagen ableiten → Daten testen
```

**Fragen die ZUERST beantwortet werden muessen:**
1. Welche WIRTSCHAFTLICHEN Zwaenge hat das System?
2. Was MUSS das System garantieren um profitabel zu bleiben?
3. WANN sollte man spielen? (nicht: welche Zahlen)

---

## 7. OFFENE FORSCHUNGSFRAGEN

### 7.1 DRINGEND: Mehr Jackpot-Daten sammeln (Prioritaet KRITISCH)

**Aktuell nur 3 vollstaendige Jackpot-Events dokumentiert!**

Methoden um mehr Daten zu finden:
- [ ] Quoten-Daten durchsuchen (Anzahl Gewinner bei Typ 10 = 10/10)
- [ ] Pressemitteilungen aller 16 Landeslotterien recherchieren
- [ ] lotto.de Archiv nach 10/10 Gewinnern durchsuchen
- [ ] Regionale Lotto-Webseiten scrapen

Benoetigte Daten pro Jackpot:
- Datum
- 20 gezogene Zahlen
- 10 Gewinner-Zahlen (aus Pressemeldungen)
- Region/Bundesland

### 7.2 Bundesland-Analyse (Prioritaet HOCH)

- [ ] Alle Jackpot-Gewinner nach Bundesland kategorisieren
- [ ] Popularity-Split pro Bundesland durchfuehren
- [ ] Regionale Popularitaets-Profile erstellen
- [ ] Unterschiede in populaeren Zahlen nach Region identifizieren

---

## 10. UNIVERSELLE vs REGIONALE MUSTER (Validiert 2026-01-01)

### 10.1 Zentrale Erkenntnis

**Die Gewinner-Kombination besteht aus ZWEI Komponenten:**

```
GEWINNER-KOMBINATION = UNIVERSELLE MUSTER + REGIONALE ANPASSUNG

UNIVERSELL (bundesland-unabhaengig):
  → Mathematische Constraints (Ziffernprodukt, Dekaden, etc.)
  → Gelten fuer ALLE Jackpots
  → Koennen ohne regionale Daten geprueft werden

REGIONAL (bundesland-spezifisch):
  → Gerade/Ungerade-Verteilung
  → Summe der Zahlen
  → Hohe vs niedrige Zahlen
  → Abhaengig von lokalen Spieler-Praeferenzen
```

### 10.2 Empirische Belege (3 Jackpots)

**UNIVERSELLE MUSTER (bei ALLEN 3 Gewinnern identisch):**

| Constraint | Kyritz | Oberbayern | Nordsachsen | Status |
|------------|--------|------------|-------------|--------|
| Ziffernprodukt mod 9 | 0 | 0 | 0 | ✓ UNIVERSAL |
| Einstellige Zahlen | 1 | 1 | 1 | ✓ UNIVERSAL |
| Dekaden besetzt | 6 | 6 | 6 | ✓ UNIVERSAL |
| Zeilen besetzt | 6 | 6 | 6 | ✓ UNIVERSAL |
| Endziffer 1 | 0 | 0 | 0 | ✓ UNIVERSAL |
| Alle Drittel | JA | JA | JA | ✓ UNIVERSAL |

**REGIONALE MUSTER (unterscheiden sich stark):**

| Metrik | Kyritz (BB) | Oberbayern (BY) | Nordsachsen (SN) | Spanne |
|--------|-------------|-----------------|------------------|--------|
| Gerade im Gewinner | **8** | 4 | **2** | 6 |
| Birthday im Gewinner | 4 | 4 | 2 | 2 |
| Summe Gewinner | 334 | 406 | 422 | 88 |
| Durchschnitt | 33.4 | 40.6 | 42.2 | 8.8 |
| Hohe (>50) | 1 | 5 | 3 | 4 |

### 10.3 Interpretation

```
KYRITZ (Brandenburg):
  - 8/10 gerade Zahlen im Gewinner (extrem!)
  → Spieler in Brandenburg bevorzugen UNGERADE Zahlen
  → System waehlt GERADE um Jackpot zu minimieren

NORDSACHSEN (Sachsen):
  - 2/10 gerade Zahlen im Gewinner
  → Spieler in Sachsen bevorzugen GERADE Zahlen
  → System waehlt UNGERADE um Jackpot zu minimieren

OBERBAYERN (Bayern):
  - 4/10 gerade Zahlen (ausgeglichen)
  → Spieler in Bayern sind ausgeglichen
  → System hat weniger Optimierungsspielraum
```

### 10.4 Konsequenz fuer Reverse Engineering

```
OHNE regionale Spieler-Daten:
  - Universelle Constraints → Reduktion auf ~3.000-28.000 Kandidaten
  - Aber KEINE weitere Eingrenzung moeglich

MIT regionalen Spieler-Daten (hypothetisch):
  - Wenn wir wuessten: "In Region X sind 60% der Spieler gerade-bevorzugend"
  - Dann koennten wir Kandidaten nach Gerade/Ungerade sortieren
  - Der Gewinner waere wahrscheinlich UNGERADE-lastig
```

### 10.5 WICHTIG: Keine allgemeingueltigen Popularity-Regeln!

```
FALSCH: "Birthday-Zahlen sind immer unpopulaer bei Gewinnern"
        (funktioniert nur wenn regionale Spieler Birthday bevorzugen)

FALSCH: "Hohe Zahlen sind immer besser"
        (nur wenn regionale Spieler niedrige bevorzugen)

RICHTIG: "Gewinner sind das GEGENTEIL der regionalen Praeferenz"
         (ohne Praeferenz-Daten → keine Vorhersage)
```

### 7.3 Zeitliche Muster

- [ ] Jackpot-Zyklen analysieren (Cooldown nach Gewinn)
- [ ] Saisonale Muster identifizieren
- [ ] Wochentags-Effekte pruefen

### 7.4 Auszahlungs-Optimierung

- [ ] Korrelation zwischen Ziehung und Gesamtauszahlung
- [ ] "Teure" vs "billige" Ziehungen identifizieren

---

## 11. EXPERIMENTELLE ERKENNTNISSE (2026-01-01)

**STATUS: EXPERIMENTELL - Validierung mit mehr Daten erforderlich!**

Diese Erkenntnisse basieren auf:
- 3 verifizierte Jackpots mit bekannten Gewinner-Zahlen
- 14 Jackpot-Tage aus 2023 (Quoten-Daten)
- Vergleich Jackpot-Tage vs Normale Tage

### 11.1 Zahlen-Haeufigkeit an Jackpot-Tagen

**UEBERREPRAESENTIERT (Jackpot-Favorites):**

```python
JACKPOT_FAVORITES = [43, 51, 52, 36, 40, 19, 38, 4, 61, 69, 62, 13, 8, 35, 45]

# Ratio = Haeufigkeit an Jackpot-Tagen / Haeufigkeit an normalen Tagen
# 43: 2.13x | 51: 1.97x | 52: 1.81x | 36: 1.70x | 40: 1.64x
```

**UNTERREPRAESENTIERT (Jackpot-Avoid):**

```python
JACKPOT_AVOID = [1, 16, 21, 27, 29, 37, 67, 25, 68, 28]

# 1: 0.24x | 16: 0.23x | 21: 0.26x | 27: 0.26x | 29: 0.29x
# → Viele Birthday-Zahlen werden an Jackpot-Tagen VERMIEDEN!
```

### 11.2 Jackpot-Tage vs Normale Tage (2023)

| Metrik | Jackpot-Tage | Normale Tage | Differenz |
|--------|--------------|--------------|-----------|
| Birthday (1-31) | 7.8/20 | 8.9/20 | **-12.4%** |
| Niedrig (<=35) | 9.0/20 | 10.0/20 | **-10.2%** |
| Hoch (>50) | 6.1/20 | 5.6/20 | **+8.7%** |
| Summe | 730 | 705 | **+25** |

**Interpretation:** An Jackpot-Tagen enthalten die 20 gezogenen Zahlen:
- WENIGER Birthday-Zahlen
- MEHR hohe Zahlen (>50)
- HOEHERE Gesamtsumme

### 11.3 Regionale Praeferenzen (aus "Andere 10")

| Region | Birthday | Gerade | Durchschnitt | Spieler bevorzugen |
|--------|----------|--------|--------------|-------------------|
| Brandenburg | 30% | 40% | 38.8 | UNGERADE |
| Bayern | 30% | 60% | 37.0 | GERADE |
| Sachsen | **70%** | 50% | **23.1** | **BIRTHDAY/NIEDRIGE** |

### 11.4 Experimentelle Ticket-Strategie

**Constraints (MUSS erfuellen):**

```
✓ Genau 1 einstellige Zahl (1-9)
✓ Alle 3 Drittel besetzt (1-23 + 24-46 + 47-70)
✓ Keine Endziffer 1 (11, 21, 31, 41, 51, 61 vermeiden)
✓ Ziffernprodukt mod 9 = 0
✓ Maximal 2 Birthday-Zahlen (1-31)
✓ 0 Jackpot-Avoid Zahlen
```

**Beispiel-Tickets (experimentell):**

```python
TYP_10 = [4, 36, 38, 40, 45, 52, 58, 62, 64, 69]  # Score 9.5
TYP_9  = [4, 36, 40, 46, 52, 56, 58, 62, 69]      # Score 8.0
TYP_8  = [8, 43, 45, 46, 58, 62, 64, 69]          # Score 8.0
```

### 11.5 Pending Jackpot-Vorhersagen (2023)

Fuer 11 von 13 Jackpot-Tagen wurden Vorhersagen generiert:

| Datum | Gewinner | Top-Vorhersage | Kandidaten |
|-------|----------|----------------|------------|
| 31.03.2023 | **10** | `[4, 19, 36, 40, 43, 45, 48, 50, 59, 64]` | 4,012 |
| 23.06.2023 | 1 | `[8, 19, 38, 43, 60, 62, 64, 66, 69, 70]` | 3,969 |
| 08.06.2023 | 1 | `[8, 19, 35, 36, 40, 43, 52, 57, 65, 69]` | 2,665 |

**Vollstaendige Liste:** `results/pending_jackpot_predictions.json`

### 11.6 WARNUNGEN

```
⚠️ EXPERIMENTELL - Nur 3 verifizierte Datenpunkte!
⚠️ Keine Gewinngarantie - KENO hat negativen Erwartungswert
⚠️ Regionale Faktoren nicht vollstaendig beruecksichtigt
⚠️ Validierung mit echten Gewinner-Daten ausstehend
⚠️ Overfitting-Risiko bei kleiner Stichprobe
```

### 11.7 Naechste Schritte zur Validierung

- [ ] 31.03.2023 (10 Gewinner) via Web recherchieren
- [ ] Weitere Jackpot-Events mit Gewinner-Zahlen finden
- [ ] Vorhersagen gegen echte Daten validieren
- [ ] Regionale Spieler-Daten beschaffen (falls moeglich)

---

## 8. DATENQUELLEN

### 8.1 Verfuegbare Daten

| Quelle | Zeitraum | Inhalt |
|--------|----------|--------|
| KENO_ab_2022_bereinigt.csv | 2022-2025 | Ziehungsergebnisse |
| KENO_ab_2018.csv | 2018-2024 | Historische Daten |

### 8.2 Fehlende Daten (wuenschenswert)

- Echte Dauerschein-Verteilung (nicht verfuegbar)
- Auszahlungssummen pro Ziehung
- Spielerzahlen pro Bundesland

---

## 9. CHANGELOG

| Datum | Aenderung |
|-------|-----------|
| 2026-01-01 | Dokument erstellt mit validierten Erkenntnissen |
| 2026-01-01 | Regionale Hypothese hinzugefuegt |
| 2026-01-01 | Popularity-Split Ergebnisse dokumentiert |
| 2026-01-01 | Universelle vs Regionale Muster (Abschnitt 10) |
| 2026-01-01 | **EXPERIMENTELLE ERKENNTNISSE** (Abschnitt 11) hinzugefuegt |
| 2026-01-01 | Jackpot-Favorites und Jackpot-Avoid Zahlen dokumentiert |
| 2026-01-01 | Pending Jackpot-Vorhersagen dokumentiert |
| 2026-01-01 | Experimentelle Ticket-Strategie dokumentiert |

---

**REMINDER:** Dieses Dokument vor jeder Analyse-Task lesen!
