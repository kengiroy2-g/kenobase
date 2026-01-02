# Cross-Lottery Coupling Report (KENO / LOTTO / Auswahlwette / Gluecksspirale / Eurowette / EuroJackpot)

**Generated:** 2025-12-29  
**Artefact (JSON):** `results/cross_lottery_coupling.json`

## Ziel

Testen, ob sich im Zahlenverhalten *zwischen* den Spielen robuste Kopplungen finden lassen:
- zeitversetzt (Lag in Tagen) und/oder
- ereignisgetrieben (z.B. Jackpot-Tage).

## Datenbasis (Default Run)

- KENO: `data/raw/keno/KENO_ab_2022_bereinigt.csv` (n=1457)
- LOTTO 6aus49: `data/raw/lotto/LOTTO_ab_2022_bereinigt.csv` (n=416)
- Auswahlwette: `data/raw/auswahlwette/AW_ab_2022_bereinigt.csv` (n=207)
- Gluecksspirale: `data/raw/gluecksspirale/GS_ab_2022_bereinigt.csv` (n=208)
- Eurowette: `data/raw/eurowette/EW_ab_2022_bereinigt.csv` (n=208)
- EuroJackpot: `data/raw/eurojackpot/EJ_ab_2022_bereinigt.csv` (n=404)

## Methoden (Kurz)

### 1) Paar-/Gruppen-These: Pair-Lift + Overlap (nur Zahlenpools)

- Pro Spiel: zaehle Co-Occurrence pro Zahlenpaar und berechne `lift = observed / expected` (uniformes Nullmodell).
- Vergleichbarkeit: KENO-Paare werden auf Range 1..49 eingeschraenkt (damit LOTTO/AW/EJ kompatibel sind; bei EJ wird die 50 ignoriert).
- Overlap-Test: Schnittmenge der Top-200 Paare, Nullmodell via Hypergeometrie.

### 2) Jackpot-Effekt: Overlap KENO vs Jackpot-Tage

- Jackpot-Tage: `Jackpot_Kl1 > 0` (LOTTO) bzw. `Jackpot > 0` (EuroJackpot).
- Metrik: overlap count = |(LOTTO/EJ Zahlen) intersect (KENO Zahlen am selben Datum)|.
- Test: Mann-Whitney-U (diskrete Verteilung).

### 3) Cross-Game Conditional Lifts (Zahl-Ebene)

- Lags: `0,1,2,7` Tage.
- Alignment: pro Target-Ziehung am Datum `t` wird die letzte Source-Ziehung `<= (t - lag)` verwendet.
- Statistik: Fisher Exact Test pro (trigger, target_number) + BH/FDR-Korrektur pro Richtung (Source x Target x Lag).
- Trigger-Typen:
  - `number`: Zahl in Source-Ziehung vorhanden.
  - `keno_position`: KENO `Zahl@Position` als Trigger (nur wenn KENO Source ist).
  - `ordered_value`: positionsbasierte Werte (z.B. Eurowette `T6=1`, Gluecksspirale `Kl1=7`).

## Ergebnisse (Kurz)

### Pair-Overlap (Top-200, Range 1..49)

- KENO vs LOTTO: overlap=32 exp~34.01 p=0.6943
- KENO vs EuroJackpot: overlap=34 exp~34.01 p=0.5363
- LOTTO vs EuroJackpot: overlap=36 exp~34.01 p=0.3743
- KENO vs Auswahlwette: overlap=29 exp~34.01 p=0.8738
- LOTTO vs Auswahlwette: overlap=41 exp~34.01 p=0.09182
- EuroJackpot vs Auswahlwette: overlap=48 exp~34.01 p=0.003443

Interpretation: Fast alles im Rahmen des Zufalls; **EJ vs AW** sticht in diesem einfachen Test heraus.
(Kandidat fuer Follow-up, kein Beweis.)

### Jackpot-Tage vs KENO-Overlap (same-day)

- LOTTO jackpot -> KENO overlap: delta=-0.059 (n_jackpot=68/416), p=0.8202
- EuroJackpot jackpot -> KENO overlap: delta=-0.147 (n_jackpot=59/404), p=0.2668

Interpretation: Kein belastbarer Jackpot-Effekt auf die Overlap-Verteilung (same-day).

### Conditional Lifts (FDR 0.05)

- Signifikante Cross-Game-Regeln (q <= 0.05): 3 (FDR je Richtung)
  - KENO -> Auswahlwette (lag=7): Trigger `11` -> Target `25` (lift=2.412, q=0.0265)
  - EuroJackpot -> KENO (lag=7): Trigger `8` -> Target `61` (lift=0.526, q=0.0481)  [Exclusion-Kandidat]
  - Eurowette -> KENO (lag=2): Trigger `T6=1` -> Target `57` (lift=0.782, q=0.0168) [Exclusion-Kandidat]

Interpretation: Das sind Kandidaten mit Zeitversatz. Durch das Alignment koennen auch Kalender-/Wochentags-Effekte reinspielen;
deshalb ist walk-forward Validierung (Train -> Test, ohne Lookahead) Pflicht.

## Naechste sinnvolle Schritte

1. Pair-Nullmodell verbessern: Pair-Expected aus Marginals (oder Pair-Fisher pro Spiel) statt uniform.
2. State/Regime-Modelle: Split nach Jackpot-/High-Stakes-Phasen, Rolling-Windows, Change-Points.
3. Feature-Level Kopplung statt Zahl-Zahl: Summe, Dekaden, Paritaet, Uniqueness/Anti-Birthday, "Top-Pair-Count".
4. Walk-forward Regel-Mining: Regeln nur aus Vergangenheit minen und auf spaeteren Perioden testen (Leakage vermeiden).
5. Bundesland-Zyklus: ohne echte Winner/Sales by Bundesland ist das nicht direkt testbar.
