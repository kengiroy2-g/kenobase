# STRATEGIE-SYNTHESE V4.0 - Vollstaendige Analyse

**Erstellt:** 01.01.2026
**Basierend auf:**
- KERNPRAEMISSEN_KENO_SYSTEM.md (14 bestaetigte Hypothesen)
- METHODIK_SUPER_MODEL.md (256 Kombinationen getestet)
- FINALE_STRATEGIE_SYNTHESE.md (Loop + HZ)
- hot_zone_fenster_vergleich_2022_2024.md (69 Jackpots W20)
- abkuehlungs_theorie_test.md (48-60 Tage optimal)
- reife_hotzones.md (Multi-Jackpot Potential)

---

## TEIL 1: WIE DAS KENO-SYSTEM FUNKTIONIERT (Ground Truth)

### 1.1 Fundamentale System-Eigenschaften

| Eigenschaft | Beschreibung | Quelle |
|-------------|--------------|--------|
| **Adversarial** | System minimiert aktiv Auszahlungen | P-ADV-01 |
| **Informationsvorsprung** | Kennt alle aktiven Dauerscheine (bis 28 Tage) | P-ADV-02 |
| **House-Edge** | 50% Redistribution gesetzlich garantiert | Axiom A1 |
| **Uniqueness-Praeferenz** | Jackpots bevorzugen "einzigartige" Kombinationen | WL-006 (90.9%) |
| **Near-Miss Constraint** | Unterdrueckt hohe Trefferquoten | HOUSE-004 |
| **Gruppen-Prinzip** | Nur GRUPPEN haben Wert, nicht Einzelzahlen | Axiom A8 |

### 1.2 System-Zyklen

| Zyklus | Beschreibung | Effekt | Quelle |
|--------|--------------|--------|--------|
| **28-Tage-Dauerschein** | Dauerscheine laufen nach max 28 Tagen aus | Regime-Wechsel | HYP_CYC_001 |
| **FRUEH-Phase (Tag 1-14)** | Neuer Monat = neue Dauerscheine | +364% ROI | HYP_CYC_001 |
| **SPAET-Phase (Tag 15-28)** | Alte Dauerscheine laufen aus | -58% ROI | HYP_CYC_001 |
| **Jackpot-Cooldown** | Nach GK10_10: System "spart" | -66% ROI fuer 30 Tage | WL-003 |

### 1.3 Zahlen-Praeferenzen des Systems

**An Jackpot-Tagen GEMIEDEN (populaere Zahlen):**
| Zahl | JP-Ratio | Interpretation |
|------|----------|----------------|
| 15 | 0.18x | Sehr populaer |
| 6 | 0.20x | Sehr populaer |
| 63 | 0.20x | Sehr populaer |
| 40 | 0.23x | Sehr populaer |
| 64 | 0.45x | Populaer |

**An Jackpot-Tagen BEVORZUGT (unpopulaere Zahlen):**
| Zahl | JP-Ratio | Interpretation |
|------|----------|----------------|
| 54 | 1.97x | Kaum auf Dauerscheinen |
| 26 | 1.71x | Kaum auf Dauerscheinen |
| 29 | 1.66x | Kaum auf Dauerscheinen |
| 36 | 1.62x | Kaum auf Dauerscheinen |
| 61 | 1.61x | Kaum auf Dauerscheinen |

---

## TEIL 2: ALLE STRATEGIEN IM UEBERBLICK

### 2.1 Hot-Zone Strategien

| Strategie | Zahlen | Fenster | Jackpots | Kosten | Delay |
|-----------|--------|---------|----------|--------|-------|
| **HZ7 W20** | Top-7 aus 20 Ziehungen | 20 | 69 (32 Mo) | 7 EUR | 0 Tage* |
| **HZ7 W50** | Top-7 aus 50 Ziehungen | 50 | 65 (32 Mo) | 7 EUR | 48-60 Tage |
| **HZ6 W20** | Top-6 aus 20 Ziehungen | 20 | ~5 | 1 EUR | 0 Tage |
| **HZ6 W50** | Top-6 aus 50 Ziehungen | 50 | ~5 | 1 EUR | 0 Tage |

*WICHTIG: W20 = sofort spielen laut Test (29 vs 30 JP fast identisch)

### 2.2 Loop/Super-Model Strategien

| Strategie | Zahlen | Typ | ROI | Basis |
|-----------|--------|-----|-----|-------|
| **Loop-Kern** | [3, 9, 24, 49, 51, 64] | 6 | Negativ | Paar-Korrelation |
| **Loop-Erweitert** | [2, 3, 9, 10, 20, 24] | 6 | Negativ | Historische Analyse |
| **V2 Birthday-Avoidance** | [3, 7, 36, 43, 48, 51, 58, 61, 64] | 9 | +10.6%* | Anti-Birthday |
| **Super-Model Optimal** | [3, 9, 10, 20, 24, 36, 49, 51, 64] | 9 | +351%* | Position-Rules |

*WARNUNG: Overfitting-Risiko, OOS nicht bestaetigt

### 2.3 Reife Hot-Zones (Multi-Jackpot)

| Kategorie | Regel | Optimales Fenster |
|-----------|-------|-------------------|
| **1 Jackpot gehabt** | 2. Jackpot erwartet | 48-120 Tage nach 1. JP |
| **2+ Jackpots gehabt** | Pause, dann wieder spielbar | 7-9 Monate nach letztem JP |

---

## TEIL 3: WIDERSPRUCHE IN DER DOKUMENTATION

### 3.1 Widerspruch: Wartezeit W20

| Dokument | Aussage |
|----------|---------|
| VALIDIERTE_FAKTEN.md | W20 = 0 Tage (sofort spielen) |
| HYPOTHESES_CATALOG.md | 0-48 Tage = Warten, 48-60 = Spielen |
| abkuehlungs_theorie_test.md | 48-60 Tage BESTE, aber 0 Tage fast gleich (29 vs 30 JP) |

**LOESUNG:** Die 48-60 Tage Regel gilt fuer **Multi-Jackpot-Timing** (nach dem ERSTEN Jackpot mit einer HZ), NICHT fuer das initiale Spielen einer neuen HZ.

### 3.2 Widerspruch: HZ6 vs HZ7

| Metrik | HZ6 | HZ7 | Besser? |
|--------|-----|-----|---------|
| Effizienz (JP/EUR) | 5.00 | 3.43 | HZ6 |
| Absolute Jackpots | 5 | 24 | HZ7 |
| Wartezeit | 0 Tage | 48 Tage* | HZ6 |
| Kosten/Monat | 30 EUR | 210 EUR | HZ6 |
| Erfolgsquote | 16% | 52% | HZ7 |

*48 Tage gilt nur fuer W50/W100, nicht fuer W20!

**LOESUNG:** Beide haben ihre Berechtigung - HZ6 fuer Budget-Spieler, HZ7 fuer Jackpot-Maximierung.

### 3.3 Widerspruch: ROI vs Jackpot Optimierung

| Ziel | Optimale Strategie | Problem |
|------|-------------------|---------|
| ROI maximieren | Loop + alle Timing-Regeln | Weniger Jackpots (Regel-Ueberladung) |
| Jackpots maximieren | HZ7 ohne Regeln | Schlechtere ROI |

**LOESUNG:** Cooldown-Regel ist der EINZIGE Filter der sich lohnt (-66% ROI Vermeidung ohne grosse Jackpot-Reduktion).

---

## TEIL 4: SYNTHESE - OPTIMIERTE STRATEGIE

### 4.1 Die Drei Saeulen

```
┌─────────────────────────────────────────────────────────────────────┐
│              OPTIMIERTE STRATEGIE (V4.0)                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  SAEULE 1: ZAHLEN (WAS spielen)                                    │
│  ────────────────────────────────                                   │
│  Primaer:   HZ7 W20 (dynamisch, monatlich neu)                     │
│  Backup:    Loop-Erweitert [2, 3, 9, 10, 20, 24] (statisch)        │
│  Optional:  Reife HZ (wenn 1 JP in 48-120 Tagen)                   │
│                                                                     │
│  SAEULE 2: TIMING (WANN spielen)                                   │
│  ────────────────────────────────                                   │
│  MUSS:      30 Tage nach 10/10 JP = NICHT SPIELEN (WL-003)         │
│  EMPFOHLEN: Tag 1-14 im Monat (FRUEH-Phase, +364% ROI)             │
│  OPTIONAL:  48-60 Tage nach 1. HZ-Jackpot fuer 2. JP               │
│                                                                     │
│  SAEULE 3: RISIKO-MANAGEMENT                                       │
│  ────────────────────────────────                                   │
│  Dual-Play: HZ7 + Loop-Erweitert parallel (13 EUR/Tag)             │
│  Budget:    Max 182 EUR/Monat (14 Spieltage x 13 EUR)              │
│  Keine:     Regel-Ueberladung (verpasst Jackpots!)                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Timing-Entscheidungsbaum

```
                    ┌─────────────────┐
                    │   HEUTE IST     │
                    │    [DATUM]      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Tage seit       │
                    │ letztem 10/10   │
                    │ Jackpot?        │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         ≤30 Tage       >30 Tage      Unbekannt
              │              │              │
              ▼              ▼              ▼
       ╔═══════════╗  ┌──────────────┐  ┌─────────────┐
       ║ NICHT     ║  │ Tag im       │  │ Annehmen:   │
       ║ SPIELEN   ║  │ Monat?       │  │ Kein        │
       ║ (WL-003)  ║  └──────┬───────┘  │ Cooldown    │
       ╚═══════════╝         │          └──────┬──────┘
                             │                 │
              ┌──────────────┼──────────────┐  │
              │              │              │  │
          Tag 1-14      Tag 15-28      Tag 29-31
              │              │              │
              ▼              ▼              ▼
       ╔═══════════╗  ┌───────────┐  ┌───────────┐
       ║ SPIELEN   ║  │ OPTIONAL  │  │ WARTEN    │
       ║ (FRUEH)   ║  │ Weniger   │  │ Neuer     │
       ║ +364% ROI ║  │ profitabel│  │ Monat     │
       ╚═══════════╝  └───────────┘  └───────────┘
```

### 4.3 Zahlen-Hierarchie

```
PRIORITAET 1: HZ7 W20 (Monatlich berechnen)
────────────────────────────────────────────
Aktuell (Jan 2026): [7, 17, 27, 33, 48, 50, 63]
Quelle: Top-7 aus letzten 20 Ziehungen
Performance: 69 Jackpots in 32 Monaten (75% Erfolgsquote)

PRIORITAET 2: Loop-Erweitert (Statisch)
────────────────────────────────────────────
Zahlen: [2, 3, 9, 10, 20, 24]
Grund: Stabiler Backup, historisch validiert
Kosten: 1 EUR/Tag (Typ 6)

PRIORITAET 3: Reife HZ (Situativ)
────────────────────────────────────────────
Wann: Wenn eine HZ bereits 1 Jackpot hatte und 48-120 Tage vergangen sind
Aktuell reif:
  - [9, 15, 30, 33, 38, 55, 57] (55d seit JP - OPTIMAL)
  - [6, 8, 14, 15, 16, 48, 51] (64d seit JP - OPTIMAL)
  - [3, 12, 15, 28, 29, 51, 65] (90d seit JP - OPTIMAL)

PRIORITAET 4: V2 Birthday-Avoidance (Experten)
────────────────────────────────────────────
Zahlen: [3, 7, 36, 43, 48, 51, 58, 61, 64]
Warnung: Zahl 64 wird vom System gemieden (0.45x JP-Ratio)
Alternative: Zahl 64 durch 55 ersetzen (V2.1)
```

---

## TEIL 5: KONKRETE SPIELANLEITUNG

### 5.1 Taegliche Routine

```
MORGENS:
1. [ ] Pruefen: Wann war letzter 10/10 Jackpot? (lotto.de)
2. [ ] Wenn <30 Tage: HEUTE NICHT SPIELEN
3. [ ] Wenn >30 Tage: Weiter zu Schritt 4
4. [ ] Pruefen: Welcher Tag im Monat?
5. [ ] Tag 1-14: SPIELEN (FRUEH-Phase)
6. [ ] Tag 15-28: Optional (geringere ROI)
7. [ ] Tag 29-31: Warten auf neuen Monat

BEIM SPIELEN:
1. [ ] HZ7 W20 Zahlen bereit? (monatlich berechnen)
2. [ ] Tipp 1: KENO Typ 7 mit HZ7 W20 Zahlen (7 EUR)
3. [ ] Tipp 2: KENO Typ 6 mit Loop-Erweitert (6 EUR)
4. [ ] GESAMT: 13 EUR
```

### 5.2 Monatliche Aufgaben

```
AM 1. DES MONATS:
1. [ ] Letzte 20 Ziehungen sammeln (lotto.de)
2. [ ] Top-7 Zahlen berechnen (Frequenz zaehlen)
3. [ ] Neue HZ7 W20 notieren
4. [ ] Pruefen: Gab es 10/10 JP in letzten 30 Tagen?
5. [ ] Reife HZ pruefen (1 JP vor 48-120 Tagen?)

SCRIPT:
python scripts/calculate_hz7_w20.py
```

### 5.3 Kosten-Uebersicht

| Zeitraum | Spieltage | HZ7 W20 | Loop-Erweitert | GESAMT |
|----------|-----------|---------|----------------|--------|
| Tag | 1 | 7 EUR | 6 EUR | **13 EUR** |
| Monat (FRUEH nur) | 14 | 98 EUR | 84 EUR | **182 EUR** |
| Monat (alle Tage) | 30 | 210 EUR | 180 EUR | **390 EUR** |
| Jahr (FRUEH nur) | 168 | 1.176 EUR | 1.008 EUR | **2.184 EUR** |

---

## TEIL 6: ERWARTETE PERFORMANCE

### 6.1 Historische Daten (2022-2024)

| Metrik | HZ7 W20 | Loop-Erweitert | Kombination |
|--------|---------|----------------|-------------|
| Jackpots (32 Mo) | 69 | ~10* | ~79 |
| JP pro Monat | 2.16 | ~0.31 | ~2.47 |
| Erfolgsquote | 75% | 70%* | ~80%* |
| Kosten/Monat | 98-210 EUR | 84-180 EUR | 182-390 EUR |

*Schaetzung basierend auf Loop-Analyse

### 6.2 Theoretisches ROI

**WARNUNG:** Alle positiven ROI-Werte basieren auf Backtests. House-Edge garantiert langfristig negative ROI bei korrekten Quoten.

| Szenario | Erwartung |
|----------|-----------|
| Ohne Regeln | Negativ (-50% bis -70%) |
| Mit Cooldown-Regel | Weniger negativ (-40% bis -60%) |
| Mit FRUEH-Phase | +364% vs SPAET (relativ, nicht absolut) |
| Jackpot-Treffer | +500 EUR pro 6/6 |

---

## TEIL 7: REGELN DIE SICH LOHNEN

### 7.1 Ranking der Regeln

| Rang | Regel | Effekt | Kosten | Empfehlung |
|------|-------|--------|--------|------------|
| 1 | **Cooldown (30d nach JP)** | -66% ROI vermeiden | Keine | **MUSS** |
| 2 | **FRUEH-Phase (Tag 1-14)** | +364% ROI | -50% Spieltage | **EMPFOHLEN** |
| 3 | HZ-Delay (48-60d) | +1 JP Differenz | Wartezeit | OPTIONAL |
| 4 | Alle Regeln kombiniert | -100% Jackpots | -77% Spieltage | **NICHT** |

### 7.2 Warum Regel-Ueberladung schadet

```
Spieltage ohne Regeln:  ~960 Tage (32 Monate)
Spieltage mit Cooldown: ~740 Tage (-23%)
Spieltage mit FRUEH:    ~480 Tage (-50%)
Spieltage mit ALLEN:    ~200 Tage (-77%)

Problem: Bei -77% Spieltagen verpasst man mehr Jackpots
         als man durch bessere ROI gewinnt!
```

---

## TEIL 8: ZUSAMMENFASSUNG

### Die optimale Strategie ist:

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   1. ZAHLEN: HZ7 W20 + Loop-Erweitert parallel                     │
│                                                                     │
│   2. TIMING: Nur Cooldown-Regel (30d nach 10/10)                   │
│              FRUEH-Phase (Tag 1-14) bevorzugen                     │
│                                                                     │
│   3. KOSTEN: 13 EUR pro Spieltag                                   │
│              ~182 EUR pro Monat (nur FRUEH)                        │
│              ~2.184 EUR pro Jahr                                   │
│                                                                     │
│   4. KEINE REGEL-UEBERLADUNG!                                      │
│      (Wartezeit, alle Regeln kombiniert = schadet)                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Aktuelle Zahlen (Januar 2026):

```
HZ7 W20:        [7, 17, 27, 33, 48, 50, 63]
Loop-Erweitert: [2, 3, 9, 10, 20, 24]
```

---

## ANHANG: Quellen

| Dokument | Inhalt |
|----------|--------|
| KERNPRAEMISSEN_KENO_SYSTEM.md | System-Verhalten, 14 Hypothesen |
| METHODIK_SUPER_MODEL.md | 256 Kombinationen, 8 Komponenten |
| FINALE_STRATEGIE_SYNTHESE.md | Loop + HZ Kombination |
| hot_zone_fenster_vergleich_2022_2024.md | W20: 69 JP, 75% Erfolg |
| abkuehlungs_theorie_test.md | 48-60 Tage optimal, 4 Mo NICHT bestaetigt |
| reife_hotzones.md | Multi-Jackpot Potenzial |
| HYPOTHESEN_SYNTHESE.md | 13 bestaetigte, 5 falsifizierte Hypothesen |

---

*Kenobase Strategie-Synthese V4.0 - 01.01.2026*
*Synthese aus: Super-Model + Loop-Analyse + Hot-Zone Methodik*
