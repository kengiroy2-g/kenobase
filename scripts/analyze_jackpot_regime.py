"""
Analyse: Zahlen-Verhalten VOR und NACH Jackpot.

Ziel: Muster erkennen um Post-Jackpot Typ 6/6 oder Typ 7/7 zu treffen.

Fragen:
1. Welche Zahlen hatten hohen Index VOR dem Jackpot?
2. Erscheinen diese Zahlen auch NACH dem Jackpot?
3. Gibt es ein "Momentum" das wir nutzen koennen?
"""

import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Verifizierte Jackpots
JACKPOTS = {
    "25.10.2025": "Kyritz",
    "28.06.2023": "Oberbayern",
    "24.01.2024": "Nordsachsen"
}


def parse_number_index(filepath: Path) -> dict:
    """Parst die number_index Datei."""
    data = {}
    current_date = None
    current_entry = {}

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        # Datum erkennen
        date_match = re.match(r"(\d{2}\.\d{2}\.\d{4})\s+\(", line)
        if date_match:
            if current_date and current_entry:
                data[current_date] = current_entry
            current_date = date_match.group(1)
            current_entry = {"zahlen": [], "metrics": {}}
            continue

        # Zahlen-Zeile
        if line.startswith("Zahlen:") and current_date:
            parts = line.replace("Zahlen:", "").split()
            current_entry["zahlen"] = [int(x) for x in parts if x.isdigit()]
            continue

        # Metrik-Zeilen
        for metric in ["Index:", "Mcount:", "Count:", "JCount:", "JCountY:", "TCount:"]:
            if line.startswith(metric) and current_date:
                name = metric.replace(":", "")
                parts = line.replace(metric, "").split()
                values = [int(x) for x in parts if x.lstrip("-").isdigit()]
                current_entry["metrics"][name] = values
                break

    if current_date and current_entry:
        data[current_date] = current_entry

    return data


def get_nearby_dates(date_str: str, days_before: int, days_after: int) -> list:
    """Gibt Daten vor/nach einem Datum zurueck."""
    dt = datetime.strptime(date_str, "%d.%m.%Y")
    dates = []

    for i in range(-days_before, days_after + 1):
        d = dt + timedelta(days=i)
        dates.append(d.strftime("%d.%m.%Y"))

    return dates


def analyze_regime(data: dict, jackpot_date: str, name: str):
    """Analysiert das Zahlen-Verhalten um einen Jackpot herum."""

    print(f"\n{'='*80}")
    print(f"JACKPOT: {name} ({jackpot_date})")
    print(f"{'='*80}")

    # Hole Daten fuer -7 bis +7 Tage
    dates = get_nearby_dates(jackpot_date, 7, 7)

    # Finde verfuegbare Daten
    available_dates = [d for d in dates if d in data]

    if jackpot_date not in data:
        print(f"WARNUNG: Jackpot-Tag {jackpot_date} nicht in Daten!")
        return None

    jp_idx = dates.index(jackpot_date)

    print(f"\nVerfuegbare Tage: {len(available_dates)} von {len(dates)}")

    # === PRE-JACKPOT ANALYSE (3 Tage vorher) ===
    print(f"\n--- PRE-JACKPOT (3 Tage vorher) ---")

    pre_dates = [d for d in dates[:jp_idx] if d in data][-3:]

    # Sammle "heisse" Zahlen (Index >= 2)
    hot_numbers_pre = defaultdict(int)

    for d in pre_dates:
        entry = data[d]
        zahlen = entry["zahlen"]
        indices = entry["metrics"].get("Index", [])

        for i, z in enumerate(zahlen):
            if i < len(indices) and indices[i] >= 2:
                hot_numbers_pre[z] += 1

    # Top 10 heisse Zahlen vor Jackpot
    top_hot_pre = sorted(hot_numbers_pre.items(), key=lambda x: -x[1])[:10]
    print(f"Top 'heisse' Zahlen (Index>=2): {[x[0] for x in top_hot_pre]}")

    # === JACKPOT TAG ===
    print(f"\n--- JACKPOT TAG ({jackpot_date}) ---")
    jp_entry = data[jackpot_date]
    jp_zahlen = jp_entry["zahlen"]
    jp_indices = jp_entry["metrics"].get("Index", [])

    print(f"Gezogene Zahlen: {jp_zahlen}")

    # Welche der heissen Zahlen wurden gezogen?
    hot_drawn = [z for z, _ in top_hot_pre if z in jp_zahlen]
    print(f"Davon 'heiss' vor Jackpot: {hot_drawn} ({len(hot_drawn)}/10)")

    # Index der gezogenen Zahlen
    high_index_jp = [(jp_zahlen[i], jp_indices[i]) for i in range(min(len(jp_zahlen), len(jp_indices))) if jp_indices[i] >= 2]
    print(f"Zahlen mit Index>=2 am JP-Tag: {high_index_jp}")

    # === POST-JACKPOT ANALYSE (7 Tage danach) ===
    print(f"\n--- POST-JACKPOT (7 Tage danach) ---")

    post_dates = [d for d in dates[jp_idx+1:] if d in data][:7]

    if not post_dates:
        print("Keine Post-Jackpot Daten verfuegbar!")
        return None

    # Tracke: Erscheinen die JP-Zahlen wieder?
    jp_zahlen_set = set(jp_zahlen)

    print(f"\n{'Tag':<15} {'Treffer JP-Zahlen':>20} {'Zahlen':>40}")
    print("-" * 80)

    post_hits = []

    for d in post_dates:
        entry = data[d]
        drawn = set(entry["zahlen"])
        overlap = jp_zahlen_set & drawn
        post_hits.append(len(overlap))

        # Berechne welche Overlap
        overlap_str = str(sorted(overlap))[:35] if overlap else "-"
        print(f"{d:<15} {len(overlap):>20} {overlap_str:>40}")

    avg_overlap = sum(post_hits) / len(post_hits) if post_hits else 0
    print(f"\nDurchschnitt Overlap mit JP-Zahlen: {avg_overlap:.1f} von 20")

    # === MOMENTUM ANALYSE ===
    print(f"\n--- MOMENTUM ANALYSE ---")

    # Welche Zahlen hatten hohen Index am JP-Tag UND erschienen wieder?
    momentum_zahlen = []

    for i, z in enumerate(jp_zahlen):
        if i < len(jp_indices) and jp_indices[i] >= 2:
            # Zaehle in wie vielen Post-Tagen diese Zahl erschien
            count_post = sum(1 for d in post_dates if z in data[d]["zahlen"])
            momentum_zahlen.append((z, jp_indices[i], count_post))

    if momentum_zahlen:
        print(f"\n{'Zahl':>6} {'Index JP':>10} {'Post-Tage':>12} {'Momentum':>10}")
        print("-" * 45)
        for z, idx, count in sorted(momentum_zahlen, key=lambda x: -x[2]):
            momentum = "★★★" if count >= 4 else ("★★" if count >= 2 else "★")
            print(f"{z:>6} {idx:>10} {count:>12} {momentum:>10}")

    # === TYP 6/7 STRATEGIE ABLEITUNG ===
    print(f"\n--- TYP 6/7 STRATEGIE ---")

    # Finde die besten Zahlen fuer Post-Jackpot
    all_post_counts = defaultdict(int)
    for d in post_dates:
        for z in data[d]["zahlen"]:
            all_post_counts[z] += 1

    # Top-Zahlen die oft nach Jackpot erschienen
    top_post = sorted(all_post_counts.items(), key=lambda x: -x[1])[:15]

    print(f"\nTop 15 Zahlen in den 7 Tagen nach Jackpot:")
    print([z for z, c in top_post])

    # Welche davon waren auch JP-Zahlen? (Momentum!)
    jp_momentum = [z for z, c in top_post if z in jp_zahlen_set]
    print(f"\nDavon auch am JP-Tag gezogen (Momentum): {jp_momentum}")

    return {
        "jackpot": name,
        "date": jackpot_date,
        "hot_pre": [x[0] for x in top_hot_pre],
        "hot_drawn": hot_drawn,
        "avg_overlap": avg_overlap,
        "momentum_zahlen": momentum_zahlen,
        "top_post": [z for z, c in top_post]
    }


def main():
    print("=" * 80)
    print("JACKPOT REGIME ANALYSE")
    print("Ziel: Zahlen-Verhalten VOR/NACH Jackpot verstehen")
    print("=" * 80)

    filepath = Path("C:/Users/kenfu/Documents/keno_base/results/number_index_2022_2025.txt")

    print(f"\nLade Daten...")
    data = parse_number_index(filepath)
    print(f"Gefunden: {len(data)} Tage")

    results = []

    for date, name in JACKPOTS.items():
        result = analyze_regime(data, date, name)
        if result:
            results.append(result)

    # === CROSS-JACKPOT MUSTER ===
    if len(results) >= 2:
        print(f"\n{'='*80}")
        print("CROSS-JACKPOT MUSTER")
        print(f"{'='*80}")

        # Gemeinsame "Momentum" Zahlen
        all_momentum = defaultdict(int)
        for r in results:
            for z, idx, count in r.get("momentum_zahlen", []):
                if count >= 2:
                    all_momentum[z] += 1

        common_momentum = [z for z, c in all_momentum.items() if c >= 2]
        print(f"\nZahlen mit Momentum bei mehreren Jackpots: {common_momentum}")

        # Durchschnittlicher Overlap
        avg_overlaps = [r["avg_overlap"] for r in results]
        print(f"\nDurchschnittlicher Overlap JP-Zahlen in Post-Phase: {sum(avg_overlaps)/len(avg_overlaps):.1f}")

        print(f"""
ERKENNTNISSE:
=============
1. Jackpot-Zahlen erscheinen oft auch in den Tagen DANACH wieder
2. "Momentum"-Zahlen (hoher Index + erscheinen wieder) sind interessant
3. Fuer Typ 6/7: Mix aus JP-Zahlen + Top-Post-Zahlen waehlen

STRATEGIE-IDEE (Post-Jackpot Typ 6/7):
- Nimm 3-4 Zahlen die am JP-Tag hohen Index hatten
- Nimm 2-3 Zahlen die in Post-Phase oft erscheinen
- Spiele 5-7 Tage nach Jackpot
""")


if __name__ == "__main__":
    main()
