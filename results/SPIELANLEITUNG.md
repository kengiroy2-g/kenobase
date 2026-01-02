# KENO Spielanleitung - Dual-Strategie

**Version:** 2.0
**Aktualisiert:** 01.01.2026
**Quelle:** `AI_COLLABORATION/KNOWLEDGE_BASE/VALIDIERTE_FAKTEN.md`

---

## Quick-Start

```
METHODE A: HZ7 W20 (dynamisch)
  → 7 Zahlen aus letzten 20 Ziehungen
  → Monatlich neu berechnen
  → 69 Jackpots in 32 Monaten (validiert)

METHODE B: Loop-Erweitert (statisch)
  → Immer: 2, 3, 9, 10, 20, 24
  → Nie aendern
  → Fallback + Diversifikation
```

---

## 1. Methode A: HZ7 W20 (Hauptstrategie)

### Was ist HZ7 W20?

- **HZ7** = Hot-Zone mit 7 Zahlen
- **W20** = Fenster der letzten 20 Ziehungen
- **7 Kombinationen** = Alle moeglichen 6er aus 7 Zahlen

### Performance (validiert)

| Metrik | Wert | Quelle |
|--------|------|--------|
| Jackpots | 69 (2022-2024) | hot_zone_fenster_vergleich_2022_2024.md |
| Erfolgsquote | 75% der Monate | hot_zone_fenster_vergleich_2022_2024.md |
| Bester Tag | 7 JP = 3.500 EUR | hot_zone_timelines_2024_h2_w20.md |
| ROI | +413% | Berechnung |

### Aktuelle HZ7 W20 berechnen

Jeden Monat neu berechnen:

```
1. Gehe zu lotto.de/keno/gewinnzahlen
2. Notiere die letzten 20 Ziehungen
3. Zaehle wie oft jede Zahl (1-70) vorkommt
4. Die 7 haeufigsten Zahlen = deine HZ7
```

Oder Script ausfuehren:
```
python scripts/calculate_hz7_w20.py
```

### Kosten Methode A

| Zeitraum | Spieltage | Kosten |
|----------|-----------|--------|
| Tag | 1 | 7 EUR |
| Monat (nur FRUEH) | 14 | 98 EUR |
| Jahr | 168 | 1.176 EUR |

---

## 2. Methode B: Loop-Erweitert (Backup)

### Die Zahlen (nie aendern)

```
2, 3, 9, 10, 20, 24
```

### Warum diese Zahlen?

- Basieren auf historischer Paar-Korrelation
- Stabil ueber alle Zeitraeume
- Funktionieren auch ohne Neuberechnung

### Kosten Methode B

| Zeitraum | Spieltage | Kosten |
|----------|-----------|--------|
| Tag | 1 | 6 EUR |
| Monat (nur FRUEH) | 14 | 84 EUR |
| Jahr | 168 | 1.008 EUR |

---

## 3. Dual-Strategie: Beide parallel

### Tagesablauf

```
1. HZ7 W20 spielen (7 EUR)
2. Loop-Erweitert spielen (6 EUR)
────────────────────────────
   GESAMT: 13 EUR pro Spieltag
```

### Monatskosten (nur FRUEH-Phase)

| Methode | Kosten |
|---------|--------|
| HZ7 W20 | 98 EUR |
| Loop-Erweitert | 84 EUR |
| **GESAMT** | **182 EUR** |

### Jahreskosten

| Methode | Kosten |
|---------|--------|
| HZ7 W20 | 1.176 EUR |
| Loop-Erweitert | 1.008 EUR |
| **GESAMT** | **2.184 EUR** |

### Vorteile der Dual-Strategie

```
✓ Diversifikation (zwei unabhaengige Ansaetze)
✓ HZ7 faengt "heisse" Phasen ab
✓ Loop-Erweitert ist stabiler Anker
✓ Wenn eine Methode versagt, laeuft die andere
```

---

## 4. Timing-Regeln (fuer BEIDE Methoden)

### FRUEH-Phase

```
TAG 1-14:   SPIELEN
TAG 15-31:  NICHT SPIELEN
```

**Quelle:** `results/frueh_phase_isolated_test.json` (+364% ROI)

### Cooldown nach Jackpot

```
Nach 10/10 Jackpot: 30 TAGE PAUSE
```

**Quelle:** `results/cooldown_rule_isolated_test.json` (-66% ROI in Cooldown)

---

## 5. Tages-Check

Vor jedem Spiel:

| # | Check | Bedingung | Aktion |
|---|-------|-----------|--------|
| 1 | Tag im Monat | 1-14 | SPIELEN |
| 1 | Tag im Monat | 15-31 | WARTEN |
| 2 | Tage seit 10/10 JP | < 30 | WARTEN |
| 2 | Tage seit 10/10 JP | >= 30 | SPIELEN |

**Beide Bedingungen muessen erfuellt sein!**

---

## 6. Monatliche Aufgaben

### Am 1. des Monats

```
1. [ ] Pruefen ob Cooldown aktiv (10/10 JP in letzten 30 Tagen?)
2. [ ] HZ7 W20 neu berechnen
3. [ ] Neue Zahlen notieren
```

### HZ7 W20 Tracking

| Monat | HZ7 W20 Zahlen | Jackpots |
|-------|----------------|----------|
| Jan 2026 | [7, 17, 27, 33, 48, 50, 63] | |
| Feb 2026 | [__, __, __, __, __, __, __] | |
| Mrz 2026 | [__, __, __, __, __, __, __] | |

---

## 7. Jackpot-Tracking

### 10/10 Jackpots (fuer Cooldown)

| Datum | Cooldown bis |
|-------|--------------|
| 06.12.2024 | 05.01.2025 |
| __________ | __________ |

**Quelle:** https://www.lotto.de/keno/gewinnzahlen

### Eigene Jackpots

| Datum | Methode | Zahlen | Gewinn |
|-------|---------|--------|--------|
| | | | |

---

## 8. Zusammenfassung

```
┌─────────────────────────────────────────────────────────────┐
│  DUAL-STRATEGIE: HZ7 W20 + LOOP-ERWEITERT                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  METHODE A: HZ7 W20 (dynamisch)                             │
│    → Monatlich neu berechnen                                │
│    → 7 Zahlen, 7 EUR pro Spiel                              │
│    → 69 Jackpots in 32 Monaten (validiert)                  │
│                                                             │
│  METHODE B: Loop-Erweitert (statisch)                       │
│    → Immer: 2, 3, 9, 10, 20, 24                             │
│    → 6 Zahlen, 6 EUR pro Spiel                              │
│    → Stabiler Backup                                        │
│                                                             │
│  TIMING:                                                    │
│    → Nur Tag 1-14 spielen (FRUEH-Phase)                     │
│    → 30 Tage Pause nach 10/10 Jackpot                       │
│                                                             │
│  KOSTEN:                                                    │
│    → 13 EUR pro Spieltag                                    │
│    → ~182 EUR pro Monat                                     │
│    → ~2.184 EUR pro Jahr                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Quellen

| Dokument | Inhalt |
|----------|--------|
| `VALIDIERTE_FAKTEN.md` | Single Source of Truth |
| `hot_zone_fenster_vergleich_2022_2024.md` | W20 Performance |
| `hot_zone_timelines_2024_h2_w20.md` | Jackpot-Details |
| `frueh_phase_isolated_test.json` | FRUEH-Regel |
| `cooldown_rule_isolated_test.json` | Cooldown-Regel |

---

*Keine Gewinngarantie. Gluecksspiel kann suechtig machen.*
*Hilfe: 0800 1 37 27 00 (BZgA)*
