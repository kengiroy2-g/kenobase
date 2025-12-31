# Ultimative Typ-6 Strategie

**Ziel:** 6/6 Treffer = 500 EUR Jackpot
**Basiert auf:** Alle Analysen 2022-2025

---

## Strategie-Uebersicht

```
┌─────────────────────────────────────────────────────────────────┐
│                    TYP-6 GEWINN-STRATEGIE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. WANN SPIELEN?                                               │
│     ├── NICHT nach 10/10 Jackpot (30 Tage warten)              │
│     ├── NICHT in ersten 48 Tagen nach Hot-Zone Ermittlung      │
│     └── OPTIMAL: 48-60 Tage nach Ermittlung                    │
│                                                                 │
│  2. WELCHE ZAHLEN?                                              │
│     ├── Hot-Zone W50: Top-7 aus letzten 50 Ziehungen           │
│     ├── ODER kombiniert mit Rang 29-35 (kuerzere Wartezeit)    │
│     └── 7 Zahlen waehlen → C(7,6) = 7 Kombinationen            │
│                                                                 │
│  3. WIE LANGE SPIELEN?                                          │
│     ├── Max 120 Tage mit gleichen Zahlen                       │
│     ├── Nach 2x Treffer: 7-9 Monate Pause                      │
│     └── Nach hoher Auszahlung: Hot-Zone neu berechnen          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Schritt 1: WANN spielen?

### NICHT spielen wenn:

| Bedingung | Wartezeit | Grund |
|-----------|-----------|-------|
| Nach 10/10 Jackpot | 30 Tage | System "spart" (WL-003: -66% ROI) |
| Direkt nach Hot-Zone Ermittlung | 48 Tage | Zahlen "kuehlen ab" |
| Nach 2x Treffer mit gleichen Zahlen | 7-9 Monate | Ausgleichs-Mechanismus |
| Nach hoher Tagesauszahlung (>130k EUR) | 7-14 Tage | Hot-Zone wird modifiziert |

### OPTIMAL spielen:

| Phase | Zeitraum | Begruendung |
|-------|----------|-------------|
| **48-60 Tage** nach Ermittlung | Optimales Fenster | Hoechste Jackpot-Rate |
| **FRUEH-Phase** im 28-Tage-Zyklus | Tag 1-14 | +422% ROI vs SPAET (HYP_CYC_001) |

---

## Schritt 2: WELCHE Zahlen?

### Methode A: Hot-Zone W50 (Empfohlen)

```python
# Top-7 aus letzten 50 Ziehungen
Hot-Zone = Top-7 haeufigste Zahlen der letzten 50 Ziehungen
```

**Performance:** 47 Unique Tage, 65 Jackpots, 1.38 JP/Tag

### Methode B: Hot-Zone W20 (Mehr Tage, weniger JP/Tag)

```python
# Top-7 aus letzten 20 Ziehungen
Hot-Zone = Top-7 haeufigste Zahlen der letzten 20 Ziehungen
```

**Performance:** 57 Unique Tage, 69 Jackpots, 1.21 JP/Tag

### Methode C: Kombiniert (Experimentell)

```python
# Mix aus Hot (Rang 1-7) und Warm (Rang 29-35)
# Rang 29-35 hat kuerzeren Median-Abstand (213 vs 247 Tage)
Zahlen = 4 aus Top-7 + 3 aus Rang 29-35
```

---

## Schritt 3: Ticket-Konstruktion

### 7 Zahlen → 7 Kombinationen

Mit 7 Zahlen erhaeltst du automatisch 7 verschiedene 6er-Kombinationen:

```
Beispiel Hot-Zone: [3, 17, 24, 36, 49, 51, 64]

Kombination 1: [3, 17, 24, 36, 49, 51]    (ohne 64)
Kombination 2: [3, 17, 24, 36, 49, 64]    (ohne 51)
Kombination 3: [3, 17, 24, 36, 51, 64]    (ohne 49)
Kombination 4: [3, 17, 24, 49, 51, 64]    (ohne 36)
Kombination 5: [3, 17, 36, 49, 51, 64]    (ohne 24)
Kombination 6: [3, 24, 36, 49, 51, 64]    (ohne 17)
Kombination 7: [17, 24, 36, 49, 51, 64]   (ohne 3)
```

**Einsatz:** 7 x 1 EUR = 7 EUR pro Ziehung

---

## Schritt 4: Timing-Kalender

### Monatlicher Ablauf

```
Tag 1-14:   FRUEH-Phase → SPIELEN (beste ROI)
Tag 15-28:  SPAET-Phase → PAUSE (schlechte ROI)
Tag 29-31:  Monatsende → Hot-Zone neu berechnen
```

### Nach Jackpot-Event (10/10)

```
Tag 0:      Jackpot passiert
Tag 1-30:   PAUSE (System spart)
Tag 31-48:  Beobachten (Hot-Zone stabilisiert sich)
Tag 49-60:  SPIELEN (optimales Fenster)
```

---

## Schritt 5: Ausstiegs-Regeln

| Event | Aktion |
|-------|--------|
| 1x Jackpot getroffen | Weiterspielen moeglich |
| 2x Jackpot getroffen | 7-9 Monate Pause mit diesen Zahlen |
| 120 Tage ohne Treffer | Hot-Zone neu berechnen |
| Hohe Tagesauszahlung (>130k) | 7-14 Tage Pause |

---

## Zusammenfassung: Die Formel

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   GEWINN-FORMEL TYP-6:                                         │
│                                                                 │
│   1. Hot-Zone ermitteln (W50 oder W20)                         │
│   2. 48-60 Tage warten                                         │
│   3. In FRUEH-Phase (Tag 1-14) spielen                         │
│   4. NICHT nach 10/10 Jackpot (30 Tage warten)                 │
│   5. Nach 2x Treffer: 7-9 Monate Pause                         │
│   6. Nach 120 Tagen: Neu berechnen                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Erwartete Performance

| Metrik | W50 | W20 |
|--------|-----|-----|
| Unique Jackpot-Tage (2022-2024) | 47 | 57 |
| Total Jackpots | 65 | 69 |
| JP pro Tag | **1.38** | 1.21 |
| Median Wartezeit | **247 Tage** | 267 Tage |
| Erfolgsquote (Monate mit JP) | 71% | 75% |

---

## Risiko-Hinweis

- **House-Edge existiert** (Axiom A1)
- **Keine Garantie** - nur statistische Optimierung
- **Langfristig negativer ROI** bei festen Quoten
- Diese Strategie maximiert die **Jackpot-Wahrscheinlichkeit**, nicht den ROI

---

## Quick-Start Checkliste

- [ ] Letzten 10/10 Jackpot pruefen (30 Tage Abstand?)
- [ ] Hot-Zone berechnen (Top-7 aus W50)
- [ ] 48-60 Tage seit letzter Ermittlung?
- [ ] Aktueller Tag im 28-Tage-Zyklus (Tag 1-14 = FRUEH?)
- [ ] Keine hohe Auszahlung gestern (>130k)?
- [ ] → Wenn alle JA: SPIELEN!

---

*Erstellt: 31.12.2025*
*Basiert auf: CORE-001, WL-003, HYP_CYC_001, Hot-Zone Analysen*
