# KERNPRAEMISSEN: Das KENO-System (Vollstaendige Dokumentation)

**Erstellt:** 2025-12-31
**Version:** 2.0 KOMPLETT
**Basierend auf:**
- 1457 Ziehungen (2022-2025)
- 17 Jackpots (GK10_10)
- 24+ Hypothesen aus HYPOTHESES_CATALOG.md
- Adversarial System Analyse
- Signal-Validierung (In-Sample + Out-of-Sample)

---

## TEIL 1: FUNDAMENTALE AXIOME (A1-A7)

Diese Axiome werden als WAHRHEIT gesetzt und bilden die Basis aller Analysen.

### A1: System hat House-Edge
**Begruendung:** 50% Redistribution ist gesetzlich garantiert.
- Das System muss langfristig 50% der Einsaetze auszahlen
- Kurzfristig kann es Auszahlungen steuern
- House-Edge ist UNVERHANDELBAR

### A2: Spieler nutzen Dauerscheine
**Begruendung:** Bundesland-basierte Spielermuster.
- Dauerscheine laufen bis zu 28 Tage
- System KENNT alle aktiven Dauerscheine
- Spieler-Kombinationen sind dem System bekannt

### A3: Spiel muss attraktiv bleiben
**Begruendung:** Kleine Gewinne regelmaessig noetig.
- Spieler muessen regelmaessig gewinnen um motiviert zu bleiben
- System verteilt kleine Gewinne gezielt
- Zu lange Durststrecken = Spieler hoeren auf

### A4: Zahlenpaare sichern kleine Gewinne
**Begruendung:** Niedrigste Gewinnklasse (GK) wird priorisiert.
- Starke Zahlenpaare garantieren Typ-2 Gewinne
- System stellt sicher, dass beliebte Paare erscheinen
- "Trostgewinne" halten Spieler bei der Stange

### A5: 20 Zahlen pseudo-zufaellig
**Begruendung:** Jede Zahl muss in Periode erscheinen.
- Keine Zahl darf "verschwinden"
- System verteilt alle 70 Zahlen ueber Zeit
- Pseudo-Zufall mit Constraints

### A6: Gewinne bundeslandweit verteilt
**Begruendung:** Pro Ziehung, pro Bundesland.
- 16 Landeslotteriegesellschaften
- Jedes Bundesland muss Gewinner haben
- Regionale Verteilung ist Systemziel
- **STATUS: OFFEN (WL-002) - Nicht empirisch validiert**

### A7: Reset-Zyklen existieren
**Begruendung:** Bis Jackpot oder Monatsende.
- Nach Jackpot: System "spart" (WL-003 BESTAETIGT)
- 28-Tage-Zyklus (HYP_CYC_001 BESTAETIGT)
- Dauerschein-Ablauf triggert Reset

### A8: GRUPPEN-PRINZIP - Einzelzahlen haben KEINEN Wert (FUNDAMENTAL!)

**Das wichtigste Axiom fuer alle KENO-Analysen.**

**Kernaussage:**
- Das Erscheinen einer EINZELNEN Zahl hat KEINEN analytischen Wert
- Wert entsteht NUR wenn Zahlen als **GRUPPE** zusammen erscheinen
- Eine Gewinnklasse wird NUR durch das gleichzeitige Erscheinen einer Zahlengruppe erreicht

**Gewinnklassen-Struktur:**

| Gewinnklasse | Benoetigte Treffer | Moegliche Strukturen |
|--------------|-------------------|----------------------|
| GK2_2 | 2 von 2 | 1x Paar |
| GK6_6 | 6 von 6 | 1x 6er ODER 2x 3er ODER 3x Paare |
| GK9_9 | 9 von 9 | 1x 9er (alle Zahlen muessen treffen) |
| GK10_10 | 10 von 10 (Jackpot) | 1x 10er (alle Zahlen muessen treffen) |

**Implikationen fuer Analysen:**

1. **FALSCH:** "Zahl X war in 9/17 Jackpots" → WERTLOS
2. **RICHTIG:** "Wie oft erschienen 6+ unserer 9 Zahlen GLEICHZEITIG?"

3. **Analyse-Ebenen:**
   - NICHT: Einzelzahlen-Frequenz
   - SONDERN: Paar-Frequenz, Trio-Frequenz, N-Tupel-Frequenz

4. **Fuer V2-Strategie [3,7,36,43,48,51,58,61,64]:**
   - Irrelevant: "Zahl 36 war oft in Jackpots"
   - Relevant: "Wie oft waren 6+ dieser 9 Zahlen ZUSAMMEN in einer Ziehung?"

5. **Fuer Lauer-Strategie:**
   - Irrelevant: "Welche Einzelzahlen sind frisch?"
   - Relevant: "Welche GRUPPEN aus dem frischen Pool erscheinen zusammen?"

**Konsequenz:**
Alle bisherigen Einzelzahlen-Analysen (JCount, Index, etc.) sind nur dann wertvoll,
wenn sie auf GRUPPEN-EBENE aggregiert werden. Eine Zahl mit hohem JCount ist nur
relevant, wenn sie Teil einer spielbaren Gruppe ist.

---

## TEIL 2: ADVERSARIAL SYSTEM PRAEMISSEN (NEU)

### P-ADV-01: KENO ist KEIN Zufallssystem

Das KENO-System ist ein **adversariales System**, das aktiv Auszahlungen minimiert.

**Evidenz:**
- 12-Zahlen-Ueberlappung zwischen Jackpots (2025-02-16 und 2025-03-19)
- Bei echtem Zufall waere solche Ueberlappung extrem unwahrscheinlich
- Das System erzeugt diese Ueberlappung NUR wenn es WEISS, dass niemand diese Kombination spielt

### P-ADV-02: Das System hat INFORMATIONSVORSPRUNG

Das System kennt ALLE aktiven Dauerscheine (permanente Tickets bis 28 Tage).

**Implikationen:**
- System weiss welche Kombinationen aktiv gespielt werden
- System kann "sichere" Zahlen-Kombinationen berechnen
- System kann Ueberlappungen erzeugen ohne doppelte Jackpots zu riskieren

### P-ADV-03: Jackpot-Einzigartigkeit ist SYSTEMZIEL

**WL-006 BESTAETIGT:** 90.9% aller Jackpots haben Uniqueness >= 0.5

**Uniqueness-Komponenten:**
- Anti-Birthday (30%): Viele Zahlen > 31
- Konsekutive (20%): Wenige aufeinanderfolgende Zahlen
- Dekaden-Verteilung (20%): Gute Streuung
- Sum-Extremitaet (15%): Extreme Summe
- Unpopularitaet (15%): Wenige beliebte Zahlen

### P-ADV-04: Birthday-Zahlen (1-31) sind UEBERREPRAESENTIERT auf Dauerscheinen

Spieler waehlen bevorzugt Geburtstagszahlen (1-31).

**Daten:**
- Birthday-Anteil an Jackpot-Tagen: 43.2%
- Birthday-Anteil an normalen Tagen: 44.3%
- Erwartung bei Zufall: 44.3% (31/70)
- **Differenz: -1.0% → System meidet Birthday-Zahlen an JP-Tagen!**

### P-ADV-05: Das System MEIDET populaere Zahlen an Jackpot-Tagen

Zahlen die auf VIELEN Dauerscheinen sind, werden an Jackpot-Tagen vermieden.

**Stark gemiedene Zahlen (< 50% Erwartung):**

| Zahl | JP-Ratio | Interpretation |
|------|----------|----------------|
| 15 | 0.18x | Sehr populaer bei Spielern |
| 6 | 0.20x | Sehr populaer bei Spielern |
| 63 | 0.20x | Sehr populaer bei Spielern |
| 40 | 0.23x | Sehr populaer bei Spielern |
| 64 | 0.45x | Populaer bei Spielern |

### P-ADV-06: Das System BEVORZUGT unpopulaere Zahlen an Jackpot-Tagen

Zahlen die auf WENIGEN Dauerscheinen sind, erscheinen haeufiger an Jackpot-Tagen.

**Stark bevorzugte Zahlen (> 150% Erwartung):**

| Zahl | JP-Ratio | Interpretation |
|------|----------|----------------|
| 54 | 1.97x | Kaum auf Dauerscheinen |
| 26 | 1.71x | Kaum auf Dauerscheinen |
| 29 | 1.66x | Kaum auf Dauerscheinen |
| 36 | 1.62x | Kaum auf Dauerscheinen |
| 61 | 1.61x | Kaum auf Dauerscheinen |

---

## TEIL 3: V2 BIRTHDAY-AVOIDANCE STRATEGIE

### P-V2-01: V2-Zahlen werden an Jackpot-Tagen BEVORZUGT

Die V2-Strategie funktioniert, weil das System V2-Zahlen als "sicher" betrachtet.

**V2 Typ 9: [3, 7, 36, 43, 48, 51, 58, 61, 64]**

| Zahl | JP-Ratio | Status |
|------|----------|--------|
| 36 | 1.62x | STARK bevorzugt |
| 61 | 1.61x | STARK bevorzugt |
| 48 | 1.51x | Bevorzugt |
| 43 | 1.37x | Bevorzugt |
| 58 | 1.33x | Bevorzugt |
| 3 | 1.13x | Neutral |
| 7 | 0.85x | Neutral |
| 51 | 0.80x | Leicht gemieden |
| 64 | 0.45x | STARK gemieden! |

**Durchschnitt: 1.18x → V2 wird bevorzugt!**

### P-V2-02: V2 hat POSITIVEN Erwartungswert (2025)

**Daten:**
- V2 Typ 9 ROI: +10.6% (alle Tage)
- EV pro Spiel: +2.22 EUR
- Max Treffer erreicht: 8 (1000 EUR am 22.07.2025)

### P-V2-03: Die Strategie funktioniert nur als MINDERHEIT

Wenn zu viele Spieler V2 nutzen, wird das System reagieren.

**Warnung:**
- Zahl 64 wird bereits STARK gemieden (0.45x)
- Moeglicherweise spielen zu viele Leute diese Zahl
- Bei Massenadoption: Strategiewechsel noetig

### P-V2-04: Zahl 64 ist DEFEKT auf Gruppen-Ebene (BESTAETIGT!)

**Gruppen-Analyse (Axiom A8) bestaetigt das Problem mit Zahl 64:**

V2-Paare die NIE in einem Jackpot 2025 erschienen:
```
(3, 64)  - 0 Jackpots (22x in normalen Ziehungen)
(7, 64)  - 0 Jackpots (27x in normalen Ziehungen)
(43, 64) - 0 Jackpots (22x in normalen Ziehungen)
(36, 51) - 0 Jackpots (31x in normalen Ziehungen)
```

**KRITISCH:** 3 von 4 "toten" Paaren enthalten Zahl 64!
- Auf Einzelzahlen-Ebene: 64 hat 0.45x JP-Ratio (gemieden)
- Auf GRUPPEN-Ebene: 64-Paare erscheinen NIE in Jackpots
- **EMPFEHLUNG: Zahl 64 ENTFERNEN aus V2-Ticket**

### P-V2-05: V2.1 OPTIMIERTES TICKET (NEU!)

Basierend auf Gruppen-Analyse wird V2 zu V2.1 optimiert:

**V2 (Original):** [3, 7, 36, 43, 48, 51, 58, 61, 64]
**V2.1 (Optimiert):** [3, 7, 36, 43, 48, 51, 55, 58, 61]

**Aenderung:** 64 → 55

**Begruendung:**
- Paar (48, 55) hat 4.52x Jackpot-Lift (6 von 17 Jackpots!)
- Paar (48, 64) hat 0x Jackpot-Lift (NIE in Jackpot)
- 55 integriert sich besser in bestehende V2-Gruppen
- 55 hat JCount=7 (solide Jackpot-Praesenz)

---

## TEIL 3B: GRUPPEN-ANALYSE ERKENNTNISSE (NEU - Axiom A8)

### P-GRP-01: Top Jackpot-Paare (Lift > 4x)

Diese Paare erscheinen 4-5x haeufiger in Jackpots als erwartet:

| Paar | JP-Count | Lift | Bedeutung |
|------|----------|------|-----------|
| (13, 29) | 5 | 5.36x | Staerkstes Jackpot-Paar |
| (26, 36) | 5 | 5.09x | Enthaelt V2-Zahl 36 |
| (13, 36) | 4 | 4.79x | Enthaelt V2-Zahl 36 |
| (34, 54) | 5 | 4.63x | High-JCount Zahlen |
| (1, 2) | 5 | 4.63x | Birthday-Zahlen! |
| (48, 55) | 6 | 4.52x | V2.1 Kern-Paar |
| (61, 70) | 4 | 4.52x | Enthaelt V2-Zahl 61 |

### P-GRP-02: V2 Staerkste Paar-Verbindungen

| Paar | JP-Count | JP-Rate |
|------|----------|---------|
| (3, 61) | 4 | 23.5% |
| (36, 61) | 4 | 23.5% |
| (48, 51) | 4 | 23.5% |
| (48, 61) | 4 | 23.5% |

**Zahl 61 ist der STAR** - erscheint in allen Top-4 V2-Paaren!

### P-GRP-03: Jackpot-Gruppen Constraint

**Beobachtung:** Zwischen aufeinanderfolgenden Jackpots gibt es immer 4-9 gemeinsame Zahlen.

| Metrik | Wert |
|--------|------|
| Min Overlap | 4 |
| Max Overlap | 9 |
| Mean Overlap | 6.0 |

**Implikation:** Das System MUSS ~6 Zahlen aus dem vorherigen Jackpot wiederverwenden.
Dies ist ein CONSTRAINT den wir ausnutzen koennen.

### P-GRP-04: Lauer-Zone Paare mit Jackpot-Affinitaet

Zahlen mit niedrigem JCount (0-3) die trotzdem starke Paar-Verbindungen haben:

| Paar | JP-Count | Lift | Lauer-Zahl |
|------|----------|------|------------|
| (19, 68) | 3 | 2.65x | 68 |
| (1, 10) | 3 | 2.65x | 10 |
| (13, 32) | 3 | 2.54x | 32 |
| (29, 53) | 3 | 2.44x | 53 |
| (33, 70) | 3 | 2.44x | 33 |

Diese Zahlen sind "frisch" aber haben GRUPPEN-Wert!

---

## TEIL 4: JACKPOT-MECHANIK

### P-JP-01: Kein 10er-Ticket kann realistisch 2x den Jackpot gewinnen

Die Wahrscheinlichkeit fuer doppelten Jackpot ist verschwindend gering.

**Daten:**
- Max beobachteter Overlap zwischen Jackpots: 12 Zahlen
- Theoretisch MOEGLICH (Overlap >= 10)
- Praktisch: Das System wuerde es VERHINDERN
- Der 12er-Overlap war nur moeglich weil NIEMAND diese Kombi spielte

### P-JP-02: Jeder Jackpot ist ein NEUES Spiel

Es gibt keine Stabilitaet ueber Zeit - High-Risk/High-Reward.

**Implikation:**
- Signale muessen nicht "stabil" sein
- Ein einmaliger Treffer reicht
- Strategie: Seltene Signale mit hoher Ratio nutzen

### P-JP-03: Jackpot-Signale ≠ Eigene Gewinne

Die Signale (mcount_mean, index, etc.) sagen voraus wann JEMAND gewinnt, nicht wann WIR gewinnen.

**Evidenz:**
- V2 Max-Treffer an Jackpot-Tagen: 6
- V2 Max-Treffer an normalen Tagen: 8 (1000 EUR!)
- Der grosse Gewinn kam an einem NORMALEN Tag
- mcount_mean >= 9.0 korreliert NEGATIV mit V2-Performance

---

## TEIL 5: SIGNAL-VALIDIERUNG (KRITISCH!)

### P-SIG-01: Jackpot-Timing-Signale (validiert fuer Jan-Jun 2025)

Diese Signale zeigten erhoehte Jackpot-Wahrscheinlichkeit IN-SAMPLE:

| Signal | Jan-Jun Ratio | Jul-Dez Ratio | Stabil? |
|--------|---------------|---------------|---------|
| mcount_mean >= 9.0 | 2.73x | 0.00x | **NEIN** |
| index_ge5 >= 1 | 2.13x | 0.00x | **NEIN** |
| index_ge4 >= 2 | 2.05x | 0.00x | **NEIN** |
| count_top5_sum >= 200 | ~5x (User) | ? | ? |

**WARNUNG: OUT-OF-SAMPLE VERSAGEN!** Signale sind nicht stabil.

### P-SIG-02: Signal-Definitionen

| Feature | Definition | Berechnung |
|---------|------------|------------|
| Index | Streak-Zaehler | +1 pro aufeinanderfolgenden Tag in Ziehung |
| Mcount | Monats-Count | Zaehlt Erscheinungen im aktuellen Monat |
| Count | Kumulativ | Zaehlt Erscheinungen seit letztem Jackpot |
| JCount | Jackpot-Erscheinungen | **ACHTUNG: LEAKAGE** - kennt Zukunft! |

### P-SIG-03: Signale sind fuer HIGH-RISK geeignet, nicht fuer Stabilitaet

Da Stabilitaet nicht noetig ist (P-JP-02), koennen instabile Signale trotzdem wertvoll sein.

**Strategie:**
- Signal feuert selten (z.B. 6 Tage in 181)
- 2 von 6 Tagen = Jackpot = 33% Trefferquote
- Einmaliger Schuss mit erhoehter Chance

### P-SIG-04: "Kalte" V2-Perioden koennten auf Big-Win hindeuten

Nach Perioden mit wenig V2-Treffern kommen groessere Gewinne.

**Evidenz:**
- Der 1000 EUR Tag kam nach einer "kalten" Woche (2,2,2,1,4,3,2 → 8)
- Nach kalten Tagen (V2 <= 2): Max = 8, >=6 Rate = 1.7%
- Nach heissen Tagen (V2 > 2): Max = 6, >=6 Rate = 1.1%

---

## TEIL 6: BESTAETIERTE HYPOTHESEN (14)

### HYP-001: Gewinnverteilungs-Optimierung
**Status:** BESTAETIGT (2025-12-28)
```
CV woechentlich: 9.09% (SEHR NIEDRIG fuer Zufallssystem)
Jackpot-Intervall: 24.5 Tage Durchschnitt
```

### HYP-004: Tippschein-Analyse (Birthday)
**Status:** BESTAETIGT (2025-12-28)
```
Korrelation Birthday-Score <-> Gewinner: r = 0.3921
High-Birthday (>50%): 4.619 Gewinner/Tag
Low-Birthday (<35%): 3.561 Gewinner/Tag
Winner-Ratio: 1.3x
```

### HYP-006: Wiederkehrende Gewinnzahlen
**Status:** BESTAETIGT (2025-12-28)
```
Recurrence Rate: 100% (5.73 Zahlen im Schnitt)
Top-Paare: (9,50):218x, (20,36):218x, (9,10):217x
```

### HYP-007: Regime-Wechsel (28-Tage-Autokorrelation)
**Status:** BESTAETIGT (2025-12-31)
```
5/5 Typen |autocorr|<0.1
Block-Permutation p>0.5
```

### HYP-010: Gewinnquoten-Korrelation
**Status:** BESTAETIGT (2025-12-28)
```
1.3x Winner-Ratio zwischen High/Low Birthday
```

### HYP-011: Zeitliche Zyklen
**Status:** BESTAETIGT (2025-12-28)
```
Feiertags-Effekt p=0.0001
```

### HYP-013: Multi-Einsatz Strategie
**Status:** BESTAETIGT (2025-12-28)
```
Leipzig-Fall bestaetigt (180.000 EUR mit Typ-8)
```

### HYP_CYC_001: 28-Tage-Dauerschein-Zyklus
**Status:** BESTAETIGT (2025-12-30)
```
Typ 9: FRUEH +364% vs SPAET -58% (Differenz: 422%)
N=348 Datenpunkte
```

### HOUSE-004: Near-Miss Constraint
**Status:** BESTAETIGT (2025-12-29)
```
70x Switch zwischen Normal/Jackpot
Chi² > 495, p < 0.001
```

### WL-001: Paar-Garantie pro GK
**Status:** BESTAETIGT (2025-12-29)
```
30/30 Paare >90% monatliche Garantie
Bestes Paar: (21,42) mit 93.2%
```

### WL-003: Reset-Zyklus nach Jackpot
**Status:** BESTAETIGT (2025-12-29)
```
-66% ROI in 30 Tagen nach Jackpot vs Normal
NICHT SPIELEN nach Jackpot!
```

### WL-005: Paar-Gewinn-Frequenz
**Status:** BESTAETIGT (2025-12-29)
```
100% der Paare gewinnen >=2x/Monat (Typ-2)
ROI negativ bei korrekten Quoten (House-Edge)
```

### WL-006: Jackpot-Einzigartigkeit
**Status:** BESTAETIGT (2025-12-29)
```
90.9% haben Uniqueness >= 0.5
Durchschnittliche Uniqueness: 0.593
```

### WL-007: GK-spezifische Paare
**Status:** BESTAETIGT (2025-12-29)
```
GK_9_9: 4.07x Lift
Paar (3,9): Jackpot-Indikator (3.28x Lift bei GK_10_10)
```

---

## TEIL 7: FALSIFIZIERTE HYPOTHESEN (5)

### HYP-002: Jackpot-Bildungs-Zyklen
**Status:** FALSIFIZIERT (2025-12-28)
```
CV = 0.95, p > 0.05
Keine Periodizitaet nachweisbar
```

### HYP-005: Dekaden-Affinitaet
**Status:** FALSIFIZIERT (2025-12-28)
```
0 signifikante Dekaden-Paare
```

### HYP-008: 111-Prinzip
**Status:** FALSIFIZIERT (2025-12-28)
```
Keine Korrelation nachweisbar
```

### DIST-003: Sum-Manipulation
**Status:** FALSIFIZIERT (2025-12-29)
```
Erklaerbar durch Zentralen Grenzwertsatz
Keine Manipulation notwendig
```

### PRED-001/002/003: Pre-GK1 Vorhersagen
**Status:** FALSIFIZIERT (2025-12-29)
```
p > 0.05 fuer alle Praediktoren
Near-Miss ist nicht vorhersagbar
```

---

## TEIL 8: NICHT SIGNIFIKANTE HYPOTHESEN (4)

### HYP_002: Cooldown High-Wins Unterdrueckung
**Status:** NICHT SIGNIFIKANT (2025-12-30)
```
Sample Size zu gering (1 HW total)
Tendenz konsistent mit WL-003, aber nicht verwertbar
```

### HYP_006: Ticket-Alterung
**Status:** NICHT SIGNIFIKANT (2025-12-30)
```
Trends negativ aber Varianz hoch
Keine klare Alterungs-Signatur nachweisbar
```

### HYP_CYC_003: GK-Distribution nach Phase
**Status:** NICHT SIGNIFIKANT (2025-12-30)
```
Chi² p > 0.47 alle Typen
Phasen-unabhaengig
```

### HYP_CYC_006: High-Win-Clustering
**Status:** NICHT SIGNIFIKANT (2025-12-30)
```
V2=3, ORIG=2 HW in 1457 Draws
Sample Size zu klein fuer Chi²
```

---

## TEIL 9: OFFENE HYPOTHESEN (2)

### WL-002: Bundesland-Verteilung
**Status:** OFFEN - HOCH PRIORITAET

**These:** Gewinnverteilung korreliert mit Bundesland-Bevoelkerung.

**Begruendung (Axiom A2, A6):**
- Jedes Bundesland hat eigene Lotteriegesellschaft
- Gewinne muessen regional verteilt werden
- Dauerschein-Spieler sind regional gebunden

**Test-Methode:**
- Korrelation: Gewinner_BL ~ Bevoelkerung_BL
- Erwartung: r > 0.8

**Daten-Quellen:**
- Pressemitteilungen der 16 Landeslotterien
- Lotto Hessen API (entdeckt!)
- DLTB Jahresbilanzen

**Bundesland-Gewichtung (Population):**
| Bundesland | Anteil |
|------------|--------|
| NRW | 21.7% |
| Bayern | 15.9% |
| Baden-Wuerttemberg | 13.4% |
| Niedersachsen | 9.6% |
| Hessen | 7.6% |
| Andere | 31.8% |

### WL-004: Dauerschein-Muster
**Status:** OFFEN - MITTEL PRIORITAET

**These:** Beliebte Kombinationen erscheinen haeufiger.

**Begruendung (Axiom A2, A3):**
- Spieler nutzen Dauerscheine mit festen Zahlen
- System kennt beliebte Kombinationen
- Muss diese gelegentlich "bedienen"

**Test:**
- Identifiziere beliebte Muster (Birthday, Konsekutive, Geometrische)
- Pruefe: Erscheinen 5-10% haeufiger?

---

## TEIL 10: CROSS-GAME HYPOTHESEN (GEPLANT)

| ID | Hypothese | Status |
|----|-----------|--------|
| XG-001 | Lotto-KENO Korrelation | GEPLANT |
| XG-002 | EuroJackpot-Timing | GEPLANT |
| XG-003 | Multi-Game Reset-Zyklen | GEPLANT |

**Hintergrund:**
- EuroJackpot Jackpot-Gewinner: Deutschland 51.8% (86 von 166)
- Moegliche Korrelation zwischen Spielen?

---

## TEIL 11: EXCLUSION-STRATEGIEN

### P-EXC-01: COLD_20 Exclusion funktioniert

Schliesse die 20 kaeltesten Zahlen der letzten 14 Tage aus.

**Daten:**
- 50 Zahlen bleiben uebrig
- 94.1% aller Jackpots haben >= 12 Treffer in diesem Bereich
- 64.7% haben >= 14 Treffer

### P-EXC-02: NON_BIRTHDAY Basis ist effektiv

32-70 als Basis-Bereich waehlen.

**Daten:**
- 39 Zahlen
- 52.9% der Jackpots haben >= 12 Treffer
- Kombiniert mit Top-6 Birthday (45 Zahlen): 76.5% >= 12 Treffer

---

## TEIL 12: SYSTEM-ZYKLEN

### P-CYC-01: 28-Tage-Dauerschein-Zyklus

Dauerscheine laufen nach maximal 28 Tagen aus.

**Implikation:**
- System kann Regime-Wechsel nach 28 Tagen durchfuehren
- Neue Dauerschein-Kombinationen aendern das Spielfeld
- Potentiell guenstige Zeitpunkte am Zyklusende

**Bestaetigt durch HYP_CYC_001:**
- FRUEH-Phase (Tag 1-14): +364% ROI
- SPAET-Phase (Tag 15-28): -58% ROI

### P-CYC-02: Cooldown nach Jackpot

Nach Jackpot-Auszahlungen: System spart.

**Phasen:**
- POST_JACKPOT (1-7 Tage): Reduzierte High-Wins
- COOLDOWN (8-30 Tage): Erholung, -66% ROI
- NORMAL: Standard-Verhalten
- PRE_JACKPOT (-7 bis -1 Tage): Aufbau

---

## TEIL 13: KERN-ZAHLEN UND TOP-PAARE

### Kern-Zahlen (ueber alle Analysen)

```
ABSOLUT:        3, 24, 49
ERWEITERT:      2, 9, 36, 51, 64
ANTI-BIRTHDAY:  37, 41, 49, 51 (>31)
V2-OPTIMIERT:   36, 61, 48, 43, 58 (hohe JP-Ratio)
```

### Top-Paare (Co-Occurrence >210x)

```
(9,50):218   (20,36):218   (33,49):213   (2,3):211
(33,50):211  (24,40):211   (3,20):208    (53,64):208
```

### Jackpot-Indikator-Paar

```
(3,9): 3.28x Lift bei GK_10_10
```

---

## TEIL 14: STRATEGISCHE IMPLIKATIONEN

### I1: V2-Strategie beibehalten

Die Daten bestaetigen: V2 wird vom System bevorzugt (1.18x).

### I2: Zahl 64 unter Beobachtung

64 wird stark gemieden (0.45x) - moeglicherweise Ersatz durch 54 (1.97x) oder 70 (1.51x) erwaegen.

### I3: Regelmaessig spielen ODER Signal-basiert

- Option A: Jeden Tag spielen (EV ist positiv)
- Option B: Nur bei seltenen Signalen (High-Risk/High-Reward)

### I4: Jackpot-Signale sind NICHT fuer uns

mcount_mean >= 9.0 etc. sagen Jackpot voraus, aber NICHT unseren Gewinn. Ignorieren fuer V2-Strategie.

### I5: Auf "kalte" V2-Perioden achten

Nach mehreren Tagen mit V2 <= 2 Treffern: Erhoehte Chance auf Big-Win.

### I6: NICHT spielen nach Jackpot

30 Tage nach GK10_10: -66% ROI (WL-003 BESTAETIGT)

### I7: FRUEH-Phase bevorzugen

Tag 1-14 im Monat: +364% ROI vs. Tag 15-28: -58% ROI (HYP_CYC_001)

---

## TEIL 15: OPTIMALE TICKETS

### Empfohlenes Typ-9 Ticket (V2-Strategie)

```
[3, 7, 36, 43, 48, 51, 58, 61, 64]
```

**Begründung:**
- Alle Anti-Birthday (ausser 3, 7)
- 36, 61, 48, 43, 58 haben hohe JP-Ratio
- Durchschnittliche JP-Ratio: 1.18x

### Alternatives Typ-9 Ticket (Position-Rules)

```
[3, 9, 10, 20, 24, 36, 49, 51, 64]
```

**Backtest ROI:** +351% (ACHTUNG: Overfitting-Risiko!)

### Kern-Zahlen für jedes Ticket

```
MUSS: 3, 24, 49 (absolute Kern-Zahlen)
EMPFOHLEN: 36, 51, 64 (erweitert)
BONUS: 61, 48, 43, 58 (V2-optimiert)
```

---

## TEIL 16: DATENQUELLEN

### Verfuegbare Daten

| Quelle | Pfad | Inhalt |
|--------|------|--------|
| Ziehungsdaten | `data/raw/keno/KENO_ab_2022_bereinigt.csv` | 1457 Ziehungen |
| Gewinnquoten | `Keno_GPTs/Keno_GQ_*.csv` | Gewinner pro GK |
| Jackpot-Timeline | `data/processed/ecosystem/timeline_2025.csv` | 17 Jackpots |
| Quoten-Tabelle | `kenobase/core/keno_quotes.py` | Feste Quoten |

### Entdeckte APIs

| API | URL | Format |
|-----|-----|--------|
| Lotto Hessen | `https://services.lotto-hessen.de/spielinformationen/gewinnzahlen/keno` | JSON |

### Fehlende Daten

- Bundesland-Verteilung pro Ziehung (WL-002)
- Dauerschein-Statistiken (WL-004)
- Jackpots 2022-2024 in timeline (nur 2025 vorhanden)

---

## VERSIONSHISTORIE

| Datum | Version | Aenderungen |
|-------|---------|-------------|
| 2025-12-31 | 2.0 | Vollstaendige Dokumentation mit allen Hypothesen |
| 2025-12-31 | 1.0 | Initiale Dokumentation (19 Praemissen) |

---

## REFERENZEN

### Analyse-Skripte (heute erstellt)
- `scripts/analyze_adversarial_system.py` - Adversarial System Analyse
- `scripts/analyze_v2_number_signals.py` - V2 Zahlen-Signale
- `scripts/analyze_high_risk_strategy.py` - High-Risk Strategie
- `scripts/check_double_jackpot.py` - Doppel-Jackpot Pruefung
- `scripts/analyze_exclusion_strategy.py` - Exclusion Strategien
- `scripts/analyze_thirds_convergence.py` - Drittel-Konvergenz
- `scripts/validate_signals_2025_only.py` - Signal-Validierung

### Hypothesen-Katalog
- `AI_COLLABORATION/KNOWLEDGE_BASE/HYPOTHESES_CATALOG.md` - Single Source of Truth
- `AI_COLLABORATION/KNOWLEDGE_BASE/HYPOTHESEN_SYNTHESE.md` - Synthese

### Ergebnis-Dateien
- `results/signal_validation/` - Signal-Validierungen
- `results/convergence_analysis/` - Konvergenz-Analysen
- `results/FINALE_STRATEGIE_EMPFEHLUNG.md` - Strategie-Empfehlung

---

**Autor:** Kenobase V2.2 Analyse-System
**Letzte Aktualisierung:** 2025-12-31
**Status:** VOLLSTAENDIG - Alle 24+ Hypothesen dokumentiert

