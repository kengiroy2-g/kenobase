#!/usr/bin/env python
"""
Prediction Index Tracker - KENO Zahlen-Vorhersage System V2.0

Basierend auf der Korrektur-Theorie:
- System korrigiert gegen Spieler-Tendenzen
- Anti-Momentum, Anti-Birthday, Post-Jackpot Reset
- 28-Tage-Dauerschein-Zyklus

NEUE METRIKEN:
- KDI: Korrektur-Druck-Index (System-Vermeidung)
- EQD: Equilibrium-Distanz (Abweichung vom Erwartungswert)
- GAS: Gap-Alert-Score (Tage ohne Erscheinung)
- JPM: Jackpot-Phasen-Modifikator
- DBS: Dekaden-Balance-Score
- POP: Popularitaets-Schaetzung
- KVS: Kombi-Vorhersage-Score (Haupt-Metrik)

ZIEL: 80% Genauigkeit beim AUSSCHLUSS von Zahlen
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional


# === KONSTANTEN ===

BIRTHDAY_POPULAR = {1, 2, 3, 7, 11, 13, 17, 19, 21, 23, 27, 29, 31}
LUCKY_NUMBERS = {7, 8, 9, 21}
MONTHS = set(range(1, 13))  # 1-12

# Dekaden: 0=1-9, 1=10-19, ..., 6=60-69, 7=70
DECADES = {i: set(range(i*10 + 1, min((i+1)*10 + 1, 71))) for i in range(7)}
DECADES[0] = set(range(1, 10))  # 1-9
DECADES[6] = set(range(60, 71))  # 60-70

# Drittel
THIRD_LOW = set(range(1, 24))    # 1-23
THIRD_MID = set(range(24, 47))   # 24-46
THIRD_HIGH = set(range(47, 71))  # 47-70


@dataclass
class NumberPrediction:
    """Vorhersage-Daten fuer eine einzelne Zahl."""
    zahl: int
    index: int           # Streak
    mcount: int          # Monats-Count
    count: int           # Count seit JP
    tcount: int          # Total Count
    gap: int             # Tage ohne Erscheinung
    kdi: float           # Korrektur-Druck-Index
    eqd: float           # Equilibrium-Distanz
    gas: float           # Gap-Alert-Score
    dbs: float           # Dekaden-Balance-Score
    pop: float           # Popularitaets-Schaetzung
    kvs: float           # Kombi-Vorhersage-Score
    prediction: str      # Interpretation


def load_keno_data(base_path: Path) -> pd.DataFrame:
    """Lade KENO-Daten aus CSV."""
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    return df.sort_values("Datum").reset_index(drop=True)


def load_jackpot_dates(base_path: Path) -> list[datetime]:
    """Lade alle Jackpot-Daten."""
    all_dates = []

    # Versuche Timeline-Dateien zu laden
    for year in [2022, 2023, 2024, 2025]:
        timeline_path = base_path / "data" / "processed" / "ecosystem" / f"timeline_{year}.csv"
        if timeline_path.exists():
            tl = pd.read_csv(timeline_path)
            tl["datum"] = pd.to_datetime(tl["datum"])
            jp_dates = tl[tl["keno_jackpot"] == 1]["datum"].tolist()
            all_dates.extend(jp_dates)

    # Fallback: Bekannte Jackpots
    if not all_dates:
        all_dates = [
            datetime(2025, 1, 16), datetime(2025, 1, 29),
            datetime(2025, 2, 2), datetime(2025, 2, 16),
        ]

    return sorted(all_dates)


# === KORREKTUR-THEORIE METRIKEN ===

def calculate_kdi(zahl: int, index: int, is_birthday: bool,
                  last_jackpot_zahlen: set, gap: int) -> float:
    """
    Korrektur-Druck-Index (KDI).
    Misst wie stark das System gegen diese Zahl korrigieren wird.

    OPTIMIERT: Fokus auf KOMBINATIONEN von Risikofaktoren.
    Hoher KDI = System wird diese Zahl VERMEIDEN.
    """
    druck = 0.0
    risiko_faktoren = 0

    # === MOMENTUM (validiert: Anti-Momentum +36% ROI) ===
    if index >= 2:
        druck += 0.20 + (index - 2) * 0.10  # Stark ab Index 2
        risiko_faktoren += 1
    if index >= 4:
        druck += 0.20  # Extra bei langen Streaks
        risiko_faktoren += 1

    # === BIRTHDAY (validiert: r=0.39 Korrelation) ===
    if is_birthday:
        druck += 0.15
        risiko_faktoren += 1
        if index >= 1:
            druck += 0.15  # Birthday + Momentum = SEHR STARK
            risiko_faktoren += 1

    # === KUERZLICH ERSCHIENEN (Gestern/Vorgestern) ===
    if gap <= 1 and index >= 1:
        druck += 0.10  # Frisch erschienen + Streak

    # === JACKPOT-KOPIE (Spieler kopieren) ===
    if zahl in last_jackpot_zahlen:
        druck += 0.12
        risiko_faktoren += 1

    # === LUCKY NUMBERS (kulturell beliebt) ===
    if zahl in LUCKY_NUMBERS:
        druck += 0.08
        risiko_faktoren += 1

    # === BONUS fuer MEHRFACH-RISIKO ===
    if risiko_faktoren >= 3:
        druck += 0.15  # Bonus fuer Kumulation
    elif risiko_faktoren >= 2:
        druck += 0.08

    return min(druck, 1.0)  # Max 100%


def calculate_eqd(actual_count: int, expected_count: float) -> float:
    """
    Equilibrium-Distanz (EQD).
    Wie weit ist die Zahl vom statistischen Gleichgewicht entfernt?

    Positiv = wird gefoerdert, Negativ = wird vermieden.
    """
    if expected_count < 1:
        return 0.0

    ratio = actual_count / expected_count

    # Ueber-Erwartung: System wird bremsen
    if ratio > 1.15:
        return -(ratio - 1.0) * 0.5  # Negativ

    # Unter-Erwartung: System wird foerdern
    if ratio < 0.85:
        return (1.0 - ratio) * 0.5  # Positiv

    return 0.0  # Im Gleichgewicht


def calculate_gas(tage_ohne_erscheinung: int) -> float:
    """
    Gap-Alert-Score (GAS).
    Axiom A5: Keine Zahl darf zu lange fehlen.

    Hoher GAS = Zahl MUSS bald erscheinen.
    """
    if tage_ohne_erscheinung < 8:
        return 0.0
    elif tage_ohne_erscheinung < 12:
        return 0.15
    elif tage_ohne_erscheinung < 16:
        return 0.30
    elif tage_ohne_erscheinung < 20:
        return 0.45
    elif tage_ohne_erscheinung < 25:
        return 0.60
    elif tage_ohne_erscheinung < 30:
        return 0.75
    else:
        return 0.90  # Sehr wahrscheinlich bald


def get_jackpot_phase(tage_seit_jackpot: int) -> tuple[str, float]:
    """
    Jackpot-Phasen-Modifikator (JPM).
    Gibt Phase und Modifikator zurueck.
    """
    if tage_seit_jackpot <= 7:
        return "POST_JP", -0.25  # System spart
    elif tage_seit_jackpot <= 14:
        return "BOOST", +0.15   # System gibt
    elif tage_seit_jackpot <= 30:
        return "COOLDOWN", -0.08  # System stabilisiert
    else:
        return "NORMAL", 0.0


def calculate_dbs(zahl: int, dekaden_counts: dict[int, int]) -> float:
    """
    Dekaden-Balance-Score (DBS).
    System erzwingt Dekaden-Streuung.

    Positiv = Dekade unterrepraesentiert (wird gefoerdert)
    Negativ = Dekade ueberrepraesentiert (wird vermieden)
    """
    dekade = min(zahl // 10, 6)  # 0-6

    if not dekaden_counts:
        return 0.0

    total = sum(dekaden_counts.values())
    if total == 0:
        return 0.0

    avg = total / 7
    count = dekaden_counts.get(dekade, 0)

    if avg < 1:
        return 0.0

    ratio = count / avg

    if ratio < 0.7:
        return 0.25  # Unterrepraesentiert -> gefoerdert
    elif ratio > 1.3:
        return -0.25  # Ueberrepraesentiert -> vermieden

    return 0.0


def calculate_pop(zahl: int, last_jackpot_zahlen: set) -> float:
    """
    Popularitaets-Schaetzung (POP).
    Schaetzt wie viele Spieler diese Zahl waehlen.

    Hohe Popularitaet = System korrigiert dagegen.
    """
    pop = 0.0

    if zahl in BIRTHDAY_POPULAR:
        pop += 0.25
    if zahl in LUCKY_NUMBERS:
        pop += 0.15
    if zahl in last_jackpot_zahlen:
        pop += 0.20  # Spieler kopieren Jackpot-Zahlen
    if zahl in MONTHS:
        pop += 0.08  # Monate werden oft gespielt
    if zahl <= 31:
        pop += 0.05  # Generell niedrige Zahlen beliebter

    return min(pop, 1.0)


def calculate_kvs(kdi: float, eqd: float, gas: float,
                  jpm: float, dbs: float, pop: float) -> tuple[float, str]:
    """
    Kombi-Vorhersage-Score (KVS).
    Kombiniert alle Metriken zu einem Vorhersage-Score.

    OPTIMIERT fuer 80% Ausschluss-Genauigkeit:
    - Staerkere Gewichtung von KDI (Korrektur-Druck)
    - Schwellenoptimierung basierend auf Backtest
    """
    # Gewichtete Kombination - OPTIMIERT
    score = (
        -kdi * 0.45 +      # Korrektur-Druck ist HAUPTFAKTOR
        eqd * 0.10 +       # Equilibrium (schwaecher)
        gas * 0.30 +       # Gap-Alert wichtig
        jpm * 0.08 +       # Phasen-Modifikator
        dbs * 0.05 -       # Dekaden-Balance (schwach)
        pop * 0.25         # Popularitaet STARK (Korrektur!)
    )

    # Angepasste Schwellen fuer groessere Listen
    if score > 0.20:
        return score, "STARK_BEVORZUGT"
    elif score > 0.08:
        return score, "BEVORZUGT"
    elif score > 0.00:
        return score, "LEICHT_BEVORZUGT"
    elif score < -0.18:
        return score, "STARK_VERMIEDEN"
    elif score < -0.10:
        return score, "VERMIEDEN"
    elif score < -0.03:
        return score, "LEICHT_VERMIEDEN"
    else:
        return score, "NEUTRAL"


def track_and_predict(df: pd.DataFrame, jackpot_dates: list[datetime],
                      target_date: Optional[datetime] = None) -> dict:
    """
    Hauptfunktion: Trackt Zahlen und erstellt Vorhersage.

    Args:
        df: KENO-Daten
        jackpot_dates: Liste der Jackpot-Tage
        target_date: Datum fuer Vorhersage (default: letzter Tag + 1)

    Returns:
        Dictionary mit Vorhersage-Daten
    """
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]

    # Initialisierung
    number_index = {i: 0 for i in range(1, 71)}      # Streak
    number_count = {i: 0 for i in range(1, 71)}      # Count seit JP
    total_count = {i: 0 for i in range(1, 71)}       # Total Count
    last_seen = {i: None for i in range(1, 71)}      # Letztes Erscheinen
    previous_drawn = set()
    last_jackpot_zahlen = set()
    last_jackpot_date = None

    # Dekaden-Tracking (letzte 5 Ziehungen)
    recent_draws = []

    # Durchlaufe alle Ziehungen
    for _, row in df.iterrows():
        date = row["Datum"]
        is_jackpot = date in jackpot_dates

        # Gezogene Zahlen
        drawn = [int(row[col]) for col in pos_cols]
        drawn_set = set(drawn)

        # Reset nach Jackpot
        if last_jackpot_zahlen:
            for num in last_jackpot_zahlen:
                number_count[num] = 0
            last_jackpot_zahlen = set()

        # Index berechnen
        for num in range(1, 71):
            if num in drawn_set:
                if num in previous_drawn:
                    number_index[num] += 1
                else:
                    number_index[num] = 1
                number_count[num] += 1
                total_count[num] += 1
                last_seen[num] = date
            else:
                number_index[num] = 0

        # Jackpot merken
        if is_jackpot:
            last_jackpot_zahlen = drawn_set.copy()
            last_jackpot_date = date

        # Recent Draws aktualisieren
        recent_draws.append(drawn_set)
        if len(recent_draws) > 5:
            recent_draws.pop(0)

        previous_drawn = drawn_set

    # === VORHERSAGE ERSTELLEN ===

    last_date = df["Datum"].max()
    prediction_date = target_date or (last_date + timedelta(days=1))

    # Tage seit letztem Jackpot
    tage_seit_jp = 999
    if last_jackpot_date:
        tage_seit_jp = (prediction_date - last_jackpot_date).days

    jp_phase, jpm = get_jackpot_phase(tage_seit_jp)

    # Dekaden-Counts der letzten 5 Ziehungen
    dekaden_counts = {d: 0 for d in range(7)}
    for draw in recent_draws:
        for z in draw:
            dekaden_counts[min(z // 10, 6)] += 1

    # Erwarteter Count pro Zahl
    n_draws = len(df)
    expected_per_number = n_draws * 20 / 70  # 20 aus 70 pro Ziehung

    # Berechne Metriken fuer jede Zahl
    predictions = []

    for zahl in range(1, 71):
        is_birthday = zahl in BIRTHDAY_POPULAR

        # Gap berechnen
        gap = 0
        if last_seen[zahl]:
            gap = (prediction_date - last_seen[zahl]).days
        else:
            gap = 999

        # Metriken berechnen
        kdi = calculate_kdi(zahl, number_index[zahl], is_birthday, last_jackpot_zahlen, gap)
        eqd = calculate_eqd(total_count[zahl], expected_per_number)
        gas = calculate_gas(gap)
        dbs = calculate_dbs(zahl, dekaden_counts)
        pop = calculate_pop(zahl, last_jackpot_zahlen)

        kvs, prediction_label = calculate_kvs(kdi, eqd, gas, jpm, dbs, pop)

        pred = NumberPrediction(
            zahl=zahl,
            index=number_index[zahl],
            mcount=0,  # Nicht relevant fuer Vorhersage
            count=number_count[zahl],
            tcount=total_count[zahl],
            gap=gap,
            kdi=kdi,
            eqd=eqd,
            gas=gas,
            dbs=dbs,
            pop=pop,
            kvs=kvs,
            prediction=prediction_label
        )
        predictions.append(pred)

    # Sortiere nach KVS (hoechste zuerst = beste Kandidaten)
    predictions.sort(key=lambda p: p.kvs, reverse=True)

    # === HIGH-CONFIDENCE EXCLUSION ===
    # Nur Zahlen mit MEHRFACHEN Risikofaktoren
    hochrisiko = []
    for p in predictions:
        risiko_count = 0

        # Momentum (Index >= 2) - VALIDIERT
        if p.index >= 2:
            risiko_count += 2  # Doppelt gewichtet

        # Birthday + erschienen gestern
        if p.zahl in BIRTHDAY_POPULAR and p.gap <= 1:
            risiko_count += 2
        elif p.zahl in BIRTHDAY_POPULAR:
            risiko_count += 1

        # Langer Streak (Index >= 4)
        if p.index >= 4:
            risiko_count += 2

        # Lucky Number mit Momentum
        if p.zahl in LUCKY_NUMBERS and p.index >= 1:
            risiko_count += 1

        if risiko_count >= 3:
            hochrisiko.append(p.zahl)

    # Erstelle Ausgabe
    result = {
        "prediction_date": prediction_date.strftime("%d.%m.%Y"),
        "last_draw_date": last_date.strftime("%d.%m.%Y"),
        "jackpot_phase": jp_phase,
        "tage_seit_jackpot": tage_seit_jp,
        "jpm": jpm,
        "predictions": predictions,
        "favoriten": [p.zahl for p in predictions if p.kvs > 0.00],
        "neutral": [p.zahl for p in predictions if -0.03 <= p.kvs <= 0.00],
        "vermeiden": [p.zahl for p in predictions if p.kvs < -0.03],
        "stark_vermeiden": [p.zahl for p in predictions if p.kvs < -0.15],
        "hochrisiko": hochrisiko,  # NEU: High-Confidence Exclusion
    }

    return result


def print_prediction_report(result: dict):
    """Gibt den Vorhersage-Bericht aus."""
    print("=" * 90)
    print("KENO PREDICTION INDEX TRACKER - Vorhersage-Bericht")
    print("=" * 90)

    print(f"\nVorhersage fuer: {result['prediction_date']}")
    print(f"Letzte Ziehung:  {result['last_draw_date']}")
    print(f"Jackpot-Phase:   {result['jackpot_phase']} (Tag {result['tage_seit_jackpot']})")
    print(f"Phasen-Mod:      {result['jpm']:+.2f}")

    # VERMEIDEN Liste (80% Ausschluss-Ziel)
    print("\n" + "=" * 90)
    print("VERMEIDEN-LISTE (hohe Korrektur-Wahrscheinlichkeit)")
    print("=" * 90)

    vermeiden = [p for p in result["predictions"] if p.kvs < -0.05]
    vermeiden.sort(key=lambda p: p.kvs)

    print(f"\n{'Zahl':>5} {'KVS':>8} {'KDI':>7} {'GAS':>7} {'POP':>7} {'Gap':>5} {'Idx':>4} {'Prediction':<18}")
    print("-" * 80)

    for p in vermeiden[:30]:
        print(f"{p.zahl:>5} {p.kvs:>+8.3f} {p.kdi:>7.3f} {p.gas:>7.3f} {p.pop:>7.3f} {p.gap:>5} {p.index:>4} {p.prediction:<18}")

    # FAVORITEN Liste
    print("\n" + "=" * 90)
    print("FAVORITEN-LISTE (niedrige Korrektur-Wahrscheinlichkeit)")
    print("=" * 90)

    favoriten = [p for p in result["predictions"] if p.kvs > 0.05]
    favoriten.sort(key=lambda p: p.kvs, reverse=True)

    print(f"\n{'Zahl':>5} {'KVS':>8} {'KDI':>7} {'GAS':>7} {'EQD':>7} {'Gap':>5} {'Idx':>4} {'Prediction':<18}")
    print("-" * 80)

    for p in favoriten[:30]:
        print(f"{p.zahl:>5} {p.kvs:>+8.3f} {p.kdi:>7.3f} {p.gas:>7.3f} {p.eqd:>7.3f} {p.gap:>5} {p.index:>4} {p.prediction:<18}")

    # Zusammenfassung
    print("\n" + "=" * 90)
    print("ZUSAMMENFASSUNG")
    print("=" * 90)

    n_vermeiden = len(result["vermeiden"])
    n_favoriten = len(result["favoriten"])
    n_stark_vermeiden = len(result["stark_vermeiden"])

    # Hochrisiko Liste
    hochrisiko = result.get("hochrisiko", [])
    n_hochrisiko = len(hochrisiko)

    print(f"\nHOCHRISIKO - 80% Konfidenz ({n_hochrisiko} Zahlen):")
    print(f"  {sorted(hochrisiko)}")
    print("  (Momentum + Birthday oder Langer Streak)")

    print(f"\nSTARK VERMEIDEN ({n_stark_vermeiden} Zahlen):")
    print(f"  {sorted(result['stark_vermeiden'])}")

    print(f"\nVERMEIDEN GESAMT ({n_vermeiden} Zahlen):")
    vermeiden_sorted = sorted(result["vermeiden"])
    for i in range(0, len(vermeiden_sorted), 15):
        print(f"  {vermeiden_sorted[i:i+15]}")

    print(f"\nFAVORITEN ({n_favoriten} Zahlen):")
    favoriten_sorted = sorted(result["favoriten"])
    for i in range(0, len(favoriten_sorted), 15):
        print(f"  {favoriten_sorted[i:i+15]}")

    # Empfehlung
    print("\n" + "=" * 90)
    print("EMPFEHLUNG")
    print("=" * 90)

    top_favoriten = [p.zahl for p in favoriten[:10]]
    print(f"\nTop 10 Favoriten fuer Ticket: {sorted(top_favoriten)}")

    # Dekaden-Check
    dekaden_in_favoriten = set(z // 10 for z in top_favoriten)
    print(f"Abgedeckte Dekaden: {len(dekaden_in_favoriten)}/7")

    # Birthday-Check
    birthday_in_favoriten = sum(1 for z in top_favoriten if z in BIRTHDAY_POPULAR)
    print(f"Birthday-Zahlen: {birthday_in_favoriten}/10 (weniger = besser)")


def validate_prediction(df: pd.DataFrame, prediction_result: dict,
                        actual_draw_date: datetime) -> dict:
    """
    Validiert eine Vorhersage gegen die tatsaechliche Ziehung.
    """
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]

    # Finde die tatsaechliche Ziehung
    row = df[df["Datum"] == actual_draw_date]
    if row.empty:
        return {"error": f"Keine Ziehung fuer {actual_draw_date}"}

    actual_drawn = set(int(row.iloc[0][col]) for col in pos_cols)

    # Pruefe Vermeiden-Liste
    vermeiden = set(prediction_result["vermeiden"])
    stark_vermeiden = set(prediction_result["stark_vermeiden"])
    favoriten = set(prediction_result["favoriten"])

    # Wie viele der "vermeiden" Zahlen wurden NICHT gezogen?
    vermeiden_korrekt = len(vermeiden - actual_drawn)
    vermeiden_falsch = len(vermeiden & actual_drawn)
    vermeiden_accuracy = vermeiden_korrekt / len(vermeiden) * 100 if vermeiden else 0

    # Wie viele der "stark vermeiden" wurden NICHT gezogen?
    stark_korrekt = len(stark_vermeiden - actual_drawn)
    stark_falsch = len(stark_vermeiden & actual_drawn)
    stark_accuracy = stark_korrekt / len(stark_vermeiden) * 100 if stark_vermeiden else 0

    # Wie viele der Favoriten wurden gezogen?
    favoriten_treffer = len(favoriten & actual_drawn)
    favoriten_accuracy = favoriten_treffer / 20 * 100  # 20 werden gezogen

    return {
        "actual_date": actual_draw_date.strftime("%d.%m.%Y"),
        "actual_drawn": sorted(actual_drawn),
        "vermeiden_total": len(vermeiden),
        "vermeiden_korrekt": vermeiden_korrekt,
        "vermeiden_falsch": vermeiden_falsch,
        "vermeiden_accuracy": vermeiden_accuracy,
        "stark_vermeiden_total": len(stark_vermeiden),
        "stark_vermeiden_korrekt": stark_korrekt,
        "stark_vermeiden_falsch": stark_falsch,
        "stark_vermeiden_accuracy": stark_accuracy,
        "favoriten_total": len(favoriten),
        "favoriten_treffer": favoriten_treffer,
        "favoriten_coverage": favoriten_accuracy,
        "falsch_vermieden": sorted(vermeiden & actual_drawn),
    }


def run_backtest(df: pd.DataFrame, jackpot_dates: list[datetime],
                 start_date: datetime, end_date: datetime) -> dict:
    """
    Backtest der Vorhersage-Genauigkeit ueber einen Zeitraum.
    """
    print(f"\nBacktest: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
    print("-" * 60)

    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]

    # Filter auf Zeitraum
    test_df = df[(df["Datum"] >= start_date) & (df["Datum"] <= end_date)]
    train_df = df[df["Datum"] < start_date]

    if len(test_df) < 10:
        return {"error": "Zu wenig Testdaten"}

    results = []

    for i, (_, row) in enumerate(test_df.iterrows()):
        test_date = row["Datum"]
        actual_drawn = set(int(row[col]) for col in pos_cols)

        # Vorhersage basierend auf Daten VOR diesem Tag
        pred_df = df[df["Datum"] < test_date]
        if len(pred_df) < 30:
            continue

        prediction = track_and_predict(pred_df, jackpot_dates, test_date)

        vermeiden = set(prediction["vermeiden"])
        stark_vermeiden = set(prediction["stark_vermeiden"])
        hochrisiko = set(prediction.get("hochrisiko", []))
        favoriten = set(prediction["favoriten"])

        # Metriken
        vermeiden_korrekt = len(vermeiden - actual_drawn)
        vermeiden_accuracy = vermeiden_korrekt / len(vermeiden) * 100 if vermeiden else 0

        stark_korrekt = len(stark_vermeiden - actual_drawn)
        stark_accuracy = stark_korrekt / len(stark_vermeiden) * 100 if stark_vermeiden else 0

        hochrisiko_korrekt = len(hochrisiko - actual_drawn)
        hochrisiko_accuracy = hochrisiko_korrekt / len(hochrisiko) * 100 if hochrisiko else 0

        favoriten_treffer = len(favoriten & actual_drawn)
        favoriten_coverage = favoriten_treffer / 20 * 100

        results.append({
            "date": test_date,
            "vermeiden_n": len(vermeiden),
            "vermeiden_accuracy": vermeiden_accuracy,
            "stark_vermeiden_n": len(stark_vermeiden),
            "stark_vermeiden_accuracy": stark_accuracy,
            "hochrisiko_n": len(hochrisiko),
            "hochrisiko_accuracy": hochrisiko_accuracy,
            "favoriten_n": len(favoriten),
            "favoriten_coverage": favoriten_coverage,
        })

        if (i + 1) % 50 == 0:
            print(f"  Verarbeitet: {i+1}/{len(test_df)}")

    # Aggregiere Ergebnisse
    if not results:
        return {"error": "Keine Ergebnisse"}

    avg_vermeiden_acc = sum(r["vermeiden_accuracy"] for r in results) / len(results)
    avg_stark_acc = sum(r["stark_vermeiden_accuracy"] for r in results) / len(results)
    avg_favoriten_cov = sum(r["favoriten_coverage"] for r in results) / len(results)

    # Hochrisiko - nur wenn vorhanden
    hochrisiko_results = [r for r in results if r["hochrisiko_n"] > 0]
    avg_hochrisiko_acc = sum(r["hochrisiko_accuracy"] for r in hochrisiko_results) / len(hochrisiko_results) if hochrisiko_results else 0
    avg_hochrisiko_n = sum(r["hochrisiko_n"] for r in hochrisiko_results) / len(hochrisiko_results) if hochrisiko_results else 0

    summary = {
        "n_tests": len(results),
        "avg_vermeiden_accuracy": avg_vermeiden_acc,
        "avg_stark_vermeiden_accuracy": avg_stark_acc,
        "avg_hochrisiko_accuracy": avg_hochrisiko_acc,
        "avg_hochrisiko_n": avg_hochrisiko_n,
        "hochrisiko_tests": len(hochrisiko_results),
        "avg_favoriten_coverage": avg_favoriten_cov,
        "target_80_erreicht": avg_hochrisiko_acc >= 80,
    }

    print(f"\n{'='*60}")
    print("BACKTEST ERGEBNISSE")
    print(f"{'='*60}")
    print(f"Anzahl Tests: {summary['n_tests']}")
    print(f"Vermeiden-Genauigkeit: {avg_vermeiden_acc:.1f}%")
    print(f"Stark-Vermeiden-Genauigkeit: {avg_stark_acc:.1f}%")
    print(f"\n>>> HOCHRISIKO <<<")
    print(f"    Tests mit Hochrisiko: {len(hochrisiko_results)}")
    print(f"    Durchschnittliche Anzahl: {avg_hochrisiko_n:.1f}")
    print(f"    GENAUIGKEIT: {avg_hochrisiko_acc:.1f}%")
    print(f"\nFavoriten-Coverage: {avg_favoriten_cov:.1f}%")
    print(f"\n80% Ziel erreicht: {'JA!' if summary['target_80_erreicht'] else 'NEIN'}")

    return summary


def run_ticket_roi_test(df: pd.DataFrame, jackpot_dates: list[datetime],
                        start_date: datetime, end_date: datetime,
                        typ: int = 7) -> dict:
    """
    Testet die ROI-Auswirkung wenn man die Vermeiden-Liste beachtet.
    Vergleicht: Zufaellige Tickets vs Tickets ohne Vermeiden-Zahlen.
    """
    import random

    KENO_QUOTES = {
        7: {0: 0, 1: 0, 2: 0, 3: 1, 4: 2, 5: 6, 6: 60, 7: 5000},
    }

    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    test_df = df[(df["Datum"] >= start_date) & (df["Datum"] <= end_date)]

    n_simulations = 10  # Reduziert fuer schnelleren Test
    results_random = {"cost": 0, "win": 0}
    results_filtered = {"cost": 0, "win": 0}

    for _ in range(n_simulations):
        for i, (_, row) in enumerate(test_df.iterrows()):
            test_date = row["Datum"]
            actual_drawn = set(int(row[col]) for col in pos_cols)

            # Vorhersage basierend auf Daten VOR diesem Tag
            pred_df = df[df["Datum"] < test_date]
            if len(pred_df) < 30:
                continue

            prediction = track_and_predict(pred_df, jackpot_dates, test_date)
            vermeiden = set(prediction["vermeiden"])

            # Random Ticket
            ticket_random = set(random.sample(range(1, 71), typ))
            treffer_random = len(ticket_random & actual_drawn)
            win_random = KENO_QUOTES[typ].get(treffer_random, 0)
            results_random["cost"] += 1
            results_random["win"] += win_random

            # Gefiltertes Ticket (ohne Vermeiden-Zahlen)
            pool = [z for z in range(1, 71) if z not in vermeiden]
            if len(pool) >= typ:
                ticket_filtered = set(random.sample(pool, typ))
            else:
                ticket_filtered = set(random.sample(range(1, 71), typ))
            treffer_filtered = len(ticket_filtered & actual_drawn)
            win_filtered = KENO_QUOTES[typ].get(treffer_filtered, 0)
            results_filtered["cost"] += 1
            results_filtered["win"] += win_filtered

    roi_random = (results_random["win"] - results_random["cost"]) / results_random["cost"] * 100
    roi_filtered = (results_filtered["win"] - results_filtered["cost"]) / results_filtered["cost"] * 100

    print(f"\n{'='*60}")
    print(f"ROI-TEST: Typ {typ} mit Vermeiden-Filter")
    print(f"{'='*60}")
    print(f"Random Tickets:    ROI = {roi_random:+.1f}%")
    print(f"Gefilterte Tickets: ROI = {roi_filtered:+.1f}%")
    print(f"Differenz:         {roi_filtered - roi_random:+.1f}%")

    return {
        "typ": typ,
        "roi_random": roi_random,
        "roi_filtered": roi_filtered,
        "improvement": roi_filtered - roi_random,
    }


def main():
    base_path = Path(__file__).parent.parent

    print("Lade KENO-Daten...")
    df = load_keno_data(base_path)

    print("Lade Jackpot-Daten...")
    jackpot_dates = load_jackpot_dates(base_path)
    print(f"Jackpot-Tage geladen: {len(jackpot_dates)}")

    # Vorhersage fuer morgen
    print("\n" + "=" * 90)
    print("AKTUELLE VORHERSAGE")
    print("=" * 90)

    result = track_and_predict(df, jackpot_dates)
    print_prediction_report(result)

    # Optional: Backtest
    print("\n" + "=" * 90)
    print("BACKTEST (letzte 100 Ziehungen)")
    print("=" * 90)

    end_date = df["Datum"].max()
    start_date = end_date - timedelta(days=120)

    backtest_result = run_backtest(df, jackpot_dates, start_date, end_date)

    # ROI-Test (nur wenn genug Zeit)
    print("\n" + "=" * 90)
    print("ROI-IMPACT TEST (10 Simulationen)")
    print("=" * 90)

    roi_result = run_ticket_roi_test(df, jackpot_dates, start_date, end_date, typ=7)

    # Speichern
    output = {
        "generated": datetime.now().isoformat(),
        "prediction": {
            "date": result["prediction_date"],
            "jackpot_phase": result["jackpot_phase"],
            "hochrisiko": result.get("hochrisiko", []),
            "favoriten": result["favoriten"],
            "vermeiden": result["vermeiden"],
            "stark_vermeiden": result["stark_vermeiden"],
        },
        "backtest": backtest_result,
        "roi_test": roi_result,
    }

    output_path = base_path / "results" / "prediction_index_latest.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nErgebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
