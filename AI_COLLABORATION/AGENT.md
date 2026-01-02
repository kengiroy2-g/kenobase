# AGENT.md - Verbindliche Analyse-Regeln

## KRITISCH: Vor jeder Analyse lesen!

---

## 1. VERBOTEN (Pattern-First)

```
NIEMALS:
├── Zahlenfrequenzen analysieren ohne Kontext
├── "Heisse" oder "kalte" Zahlen suchen
├── Statistische Anomalien als Strategie nutzen
├── Erwartungswert-Abweichungen interpretieren
└── Daten → Muster → Interpretation
```

**Warum:** Das System wurde von Experten gegen diese Ansaetze immunisiert.
Es ist ein Milliarden-Geschaeft. Naive Pattern-Suche SCHEITERT IMMER.

---

## 2. PFLICHT (Axiom-First)

```
IMMER:
├── Wirtschaftliche Constraints ZUERST identifizieren
├── Axiome schriftlich fixieren BEVOR Code geschrieben wird
├── Vorhersagen aus Axiomen ABLEITEN
├── Vorhersagen an Daten TESTEN (nicht umgekehrt!)
└── Frage: WANN spielen? (nicht: welche Zahlen)
```

### Die 7 Axiome

| ID | Axiom | Anwendung |
|----|-------|-----------|
| A1 | House-Edge (50%) | System MUSS langfristig profitabel sein |
| A2 | Dauerscheine | Spieler nutzen feste Kombinationen |
| A3 | Attraktivitaet | Kleine Gewinne MUESSEN regelmaessig sein |
| A4 | Paar-Garantie | Zahlenpaare sichern Spielerbindung |
| A5 | Pseudo-Zufall | Jede Zahl muss in Periode erscheinen |
| A6 | Regionale Verteilung | Gewinne pro Bundesland |
| A7 | Reset-Zyklen | System "spart" nach Jackpots |

---

## 3. OEKOSYSTEM-BETRACHTUNG

### Deutsche Lotterien = Verbundenes System

```
KENO ←→ Lotto 6aus49 ←→ Gluecksspirale ←→ Toto
         ↑                    ↑
         └── Gleiche Spieler ─┘
         └── Aehnliche Zahlen ─┘
         └── Gemeinsame Balance ─┘
```

### EuroJackpot = SEPARAT

EuroJackpot ist NICHT Teil des deutschen Oekosystems:
- Internationale Kontrolle
- Andere Spielerschaft
- Eigene Wirtschaftslogik

→ IMMER separat analysieren!

---

## 4. HYPOTHESEN-PROTOKOLL

### Vor dem Test

1. **Axiom-Basis angeben**: Welche Axiome stuetzen die Hypothese?
2. **Vorhersage formulieren**: Was GENAU erwarten wir zu sehen?
3. **Nullmodell definieren**: Was waere bei echtem Zufall?
4. **Akzeptanzkriterien**: Wann ist Hypothese bestaetigt/falsifiziert?

### Beispiel

```yaml
Hypothese: ECO-001 Jackpot-Kompensation
Axiom-Basis: [A1_house_edge, A4_total_balance]
Vorhersage: |
  Nach KENO-Jackpot hat Lotto in den naechsten
  7 Tagen weniger GK1/GK2 Gewinner als normal.
Nullmodell: Zufaellige Jackpot-Verteilung
Akzeptanz: Korrelation < -0.15 bei p < 0.05
```

---

## 5. METHODISCHE REIHENFOLGE

```
┌─────────────────────────────────────────────────────────┐
│ 1. AXIOME                                               │
│    └── Welche wirtschaftlichen Constraints gelten?      │
├─────────────────────────────────────────────────────────┤
│ 2. VORHERSAGEN                                          │
│    └── Was folgt logisch aus den Axiomen?               │
├─────────────────────────────────────────────────────────┤
│ 3. DATEN                                                │
│    └── Welche Daten brauchen wir zum Testen?            │
├─────────────────────────────────────────────────────────┤
│ 4. TEST                                                 │
│    └── Vorhersage bestaetigt oder falsifiziert?         │
├─────────────────────────────────────────────────────────┤
│ 5. STRATEGIE                                            │
│    └── Nur bei bestaetigten Hypothesen!                 │
└─────────────────────────────────────────────────────────┘
```

---

## 6. PERIODEN: Triviale existieren NICHT

### VERBOTEN (zu offensichtlich)

```
Diese Perioden wurden ELIMINIERT:
├── 7 Tage (Woche)
├── 14 Tage (2 Wochen)
├── 30/31 Tage (Monat)
├── 90 Tage (Quartal)
└── 365 Tage (Jahr)
```

### MOEGLICH (versteckt)

| Typ | Beispiele | Warum |
|-----|-----------|-------|
| **Primzahl-basiert** | 11, 13, 17, 23, 29, 37 Tage | Keine Teiler, ueberlappt nie mit Wochen |
| **Irrational** | sqrt(2)*7 ≈ 9.9, phi*10 ≈ 16.2 | Driftet, kein Vielfaches |
| **Event-getriggert** | X Tage nach Jackpot | Zustandsabhaengig, keine feste Periode |
| **Ueberlagert** | 11 + 17 Tage gleichzeitig | Interferenz-Muster |
| **Phasenverschoben** | KENO → 3.5 Tage → Lotto | Gleiche Frequenz, zeitversetzt |

### Analyse-Methoden

```
FALSCH: FFT mit 7/30 Tage Peaks suchen
RICHTIG: Lomb-Scargle → Wavelet → EMD
```

---

## 7. TRANSFORMATION VOR ANALYSE

Rohe Zahlen analysieren ist sinnlos. Stattdessen:

| Transformation | Beschreibung |
|----------------|--------------|
| Summen-Signatur | Summe aller gezogenen Zahlen |
| Dekaden-Vektor | [D1, D2, D3, ...] Zahlen pro Dekade |
| Gerade/Ungerade | Ratio auf [-1, +1] normalisiert |
| Spread-Index | (Max-Min) / Maximum |
| Sequenz-Brueche | Anzahl Luecken in sortierter Reihe |

---

## 7. DURCHBRUCH-BEISPIEL

### WL-003 Jackpot-Cooldown (+466% ROI)

```
Axiom A1 (House-Edge) + Axiom A7 (Reset-Zyklen)
    ↓
Vorhersage: Nach Jackpot = System muss sparen
    ↓
Test: 30 Tage nach GK10_10 → -66% ROI
    ↓
Strategie: NICHT spielen in Cooldown-Phase
    ↓
Ergebnis: +466.6% ROI
```

**Kern-Einsicht:** Die Frage war WANN spielen, nicht WELCHE Zahlen.

---

## 8. WARNUNG

```
┌─────────────────────────────────────────────────────────┐
│                    ! ACHTUNG !                          │
│                                                         │
│  Wenn eine Analyse "einfache Muster" findet,            │
│  ist sie mit hoher Wahrscheinlichkeit FALSCH.           │
│                                                         │
│  Das System wurde GEGEN solche Muster konzipiert.       │
│  Nur wirtschaftliche Constraints sind ausnutzbar.       │
└─────────────────────────────────────────────────────────┘
```

---

## 9. REFERENZEN

- `CLAUDE.md` - Vollstaendige Projektdokumentation
- `AI_COLLABORATION/PLANS/ecosystem_analysis_plan.yaml` - Oekosystem-Analyse Plan
- `docs/METHODIK_SUPER_MODEL.md` - Super-Model Dokumentation
- `AI_COLLABORATION/BACKLOG/KENOBASE_ISSUES.md` - Issue-Tracking
