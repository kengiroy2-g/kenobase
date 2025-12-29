"""
Number Frequency Context Analysis for KENO.

Analyzes which numbers (1-70) appear more frequently in different contexts:
- Global frequency
- Jackpot days (GK1 winners)
- Temporal context (month start vs end)
- Birthday vs non-birthday numbers

Grundannahme: Das System ist manipuliert. Wir suchen Muster.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from itertools import combinations


def load_keno_data(filepath: str) -> pd.DataFrame:
    """Load KENO drawing data."""
    df = pd.read_csv(filepath, sep=';', encoding='utf-8')

    # Parse date
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y')

    # Extract number columns (Keno_Z1 to Keno_Z20)
    number_cols = [f'Keno_Z{i}' for i in range(1, 21)]

    return df, number_cols


def load_gk1_data(filepath: str) -> pd.DataFrame:
    """Load GK1 (Gewinnklasse 1) jackpot data."""
    df = pd.read_csv(filepath, sep=',', encoding='utf-8')
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y')
    return df


def analyze_global_frequency(df: pd.DataFrame, number_cols: list) -> dict:
    """Analyze global frequency for each number 1-70."""

    # Count appearances for each number
    frequency = defaultdict(int)

    for _, row in df.iterrows():
        for col in number_cols:
            num = row[col]
            if pd.notna(num):
                frequency[int(num)] += 1

    total_draws = len(df)
    expected = 20/70 * total_draws  # ~639.14 for 2237 draws

    result = {}
    for num in range(1, 71):
        freq = frequency[num]
        deviation = freq - expected
        deviation_pct = (deviation / expected) * 100

        if freq > 680:
            status = "HOT"
        elif freq < 600:
            status = "COLD"
        else:
            status = "NORMAL"

        result[num] = {
            "frequency": freq,
            "expected": round(expected, 2),
            "deviation": round(deviation, 2),
            "deviation_pct": round(deviation_pct, 2),
            "status": status
        }

    return result, total_draws


def analyze_jackpot_context(df: pd.DataFrame, gk1_df: pd.DataFrame, number_cols: list) -> dict:
    """Analyze frequency on jackpot days vs normal days."""

    # Get jackpot dates
    jackpot_dates = set(gk1_df['Datum'].dt.date)

    # Split data into jackpot and normal days
    jackpot_freq = defaultdict(int)
    normal_freq = defaultdict(int)
    jackpot_days = 0
    normal_days = 0

    for _, row in df.iterrows():
        is_jackpot = row['Datum'].date() in jackpot_dates

        if is_jackpot:
            jackpot_days += 1
            for col in number_cols:
                num = row[col]
                if pd.notna(num):
                    jackpot_freq[int(num)] += 1
        else:
            normal_days += 1
            for col in number_cols:
                num = row[col]
                if pd.notna(num):
                    normal_freq[int(num)] += 1

    result = {}
    for num in range(1, 71):
        jp_freq = jackpot_freq[num]
        nm_freq = normal_freq[num]

        # Calculate rate per day
        jp_rate = jp_freq / max(jackpot_days, 1)
        nm_rate = nm_freq / max(normal_days, 1)

        # Lift: how much more likely on jackpot days
        lift = jp_rate / max(nm_rate, 0.001)

        result[num] = {
            "jackpot_freq": jp_freq,
            "normal_freq": nm_freq,
            "jackpot_rate": round(jp_rate, 4),
            "normal_rate": round(nm_rate, 4),
            "lift": round(lift, 4),
            "jackpot_preference": "HIGH" if lift > 1.2 else ("LOW" if lift < 0.8 else "NEUTRAL")
        }

    return result, jackpot_days, normal_days


def analyze_temporal_context(df: pd.DataFrame, number_cols: list) -> dict:
    """Analyze frequency by month period (start vs end)."""

    # Month start: days 1-5
    # Month end: days 25-31
    # Middle: days 6-24

    start_freq = defaultdict(int)
    end_freq = defaultdict(int)
    middle_freq = defaultdict(int)

    start_days = 0
    end_days = 0
    middle_days = 0

    for _, row in df.iterrows():
        day = row['Datum'].day

        if day <= 5:
            start_days += 1
            target = start_freq
        elif day >= 25:
            end_days += 1
            target = end_freq
        else:
            middle_days += 1
            target = middle_freq

        for col in number_cols:
            num = row[col]
            if pd.notna(num):
                target[int(num)] += 1

    result = {}
    for num in range(1, 71):
        st_freq = start_freq[num]
        en_freq = end_freq[num]
        md_freq = middle_freq[num]

        # Calculate rates
        st_rate = st_freq / max(start_days, 1)
        en_rate = en_freq / max(end_days, 1)
        md_rate = md_freq / max(middle_days, 1)

        # Overall rate for comparison
        overall_rate = (st_freq + en_freq + md_freq) / (start_days + end_days + middle_days)

        # Determine preference
        max_rate = max(st_rate, en_rate, md_rate)
        if st_rate == max_rate and st_rate > overall_rate * 1.1:
            preference = "MONTH_START"
        elif en_rate == max_rate and en_rate > overall_rate * 1.1:
            preference = "MONTH_END"
        else:
            preference = "NO_PREFERENCE"

        result[num] = {
            "month_start_freq": st_freq,
            "month_end_freq": en_freq,
            "month_middle_freq": md_freq,
            "start_rate": round(st_rate, 4),
            "end_rate": round(en_rate, 4),
            "middle_rate": round(md_rate, 4),
            "temporal_preference": preference
        }

    return result, start_days, end_days, middle_days


def analyze_birthday_effect(global_freq: dict) -> dict:
    """Analyze birthday numbers (1-31) vs non-birthday (32-70)."""

    birthday_nums = list(range(1, 32))
    non_birthday_nums = list(range(32, 71))

    birthday_freqs = [global_freq[n]["frequency"] for n in birthday_nums]
    non_birthday_freqs = [global_freq[n]["frequency"] for n in non_birthday_nums]

    birthday_avg = np.mean(birthday_freqs)
    non_birthday_avg = np.mean(non_birthday_freqs)

    birthday_std = np.std(birthday_freqs)
    non_birthday_std = np.std(non_birthday_freqs)

    # Expected is same for both groups
    expected = global_freq[1]["expected"]

    return {
        "birthday_numbers": {
            "range": "1-31",
            "count": len(birthday_nums),
            "avg_frequency": round(birthday_avg, 2),
            "std_frequency": round(birthday_std, 2),
            "vs_expected_pct": round((birthday_avg - expected) / expected * 100, 2)
        },
        "non_birthday_numbers": {
            "range": "32-70",
            "count": len(non_birthday_nums),
            "avg_frequency": round(non_birthday_avg, 2),
            "std_frequency": round(non_birthday_std, 2),
            "vs_expected_pct": round((non_birthday_avg - expected) / expected * 100, 2)
        },
        "birthday_effect": round(birthday_avg - non_birthday_avg, 2),
        "birthday_effect_significant": abs(birthday_avg - non_birthday_avg) > 15
    }


def find_number_clusters(df: pd.DataFrame, number_cols: list, min_support: int = 100) -> list:
    """Find pairs of numbers that appear together frequently."""

    pair_counts = defaultdict(int)

    for _, row in df.iterrows():
        numbers = []
        for col in number_cols:
            num = row[col]
            if pd.notna(num):
                numbers.append(int(num))

        # Count all pairs
        for pair in combinations(sorted(numbers), 2):
            pair_counts[pair] += 1

    total_draws = len(df)

    # Calculate expected co-occurrence
    # Probability of both appearing: (20/70) * (19/69) = ~7.86%
    expected_cooccurrence = total_draws * (20/70) * (19/69)

    # Find significant pairs
    significant_pairs = []
    for pair, count in pair_counts.items():
        if count > expected_cooccurrence * 1.15:  # 15% above expected
            lift = count / expected_cooccurrence
            significant_pairs.append({
                "pair": list(pair),
                "count": count,
                "expected": round(expected_cooccurrence, 2),
                "lift": round(lift, 4)
            })

    # Sort by lift
    significant_pairs.sort(key=lambda x: x["lift"], reverse=True)

    return significant_pairs[:50]  # Top 50 pairs


def calculate_predictability_score(num: int, global_data: dict, jackpot_data: dict,
                                   temporal_data: dict) -> float:
    """Calculate a predictability score for each number."""

    score = 0.0

    # Factor 1: Deviation from expected (hot/cold)
    deviation_pct = abs(global_data[num]["deviation_pct"])
    if deviation_pct > 5:
        score += deviation_pct * 0.3

    # Factor 2: Jackpot preference
    lift = jackpot_data[num]["lift"]
    if lift > 1.2 or lift < 0.8:
        score += abs(lift - 1.0) * 20

    # Factor 3: Temporal preference
    temporal_pref = temporal_data[num]["temporal_preference"]
    if temporal_pref != "NO_PREFERENCE":
        score += 10

    return round(score, 2)


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types."""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)


def main():
    """Main analysis function."""

    # Paths
    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2018.csv"
    gk1_path = base_path / "Keno_GPTs/10-9_KGDaten_gefiltert.csv"
    output_path = base_path / "results"

    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)

    print("Loading data...")
    df, number_cols = load_keno_data(str(keno_path))
    gk1_df = load_gk1_data(str(gk1_path))

    print(f"KENO data: {len(df)} drawings")
    print(f"GK1 data: {len(gk1_df)} jackpot events")

    # A) Global Frequency
    print("\nAnalyzing global frequency...")
    global_freq, total_draws = analyze_global_frequency(df, number_cols)

    # B) Jackpot Context
    print("Analyzing jackpot context...")
    jackpot_data, jp_days, nm_days = analyze_jackpot_context(df, gk1_df, number_cols)

    # C) Temporal Context
    print("Analyzing temporal context...")
    temporal_data, st_days, en_days, md_days = analyze_temporal_context(df, number_cols)

    # D) Birthday Effect
    print("Analyzing birthday effect...")
    birthday_data = analyze_birthday_effect(global_freq)

    # Find clusters
    print("Finding number clusters...")
    clusters = find_number_clusters(df, number_cols)

    # Calculate predictability scores
    print("Calculating predictability scores...")
    predictability = {}
    for num in range(1, 71):
        score = calculate_predictability_score(num, global_freq, jackpot_data, temporal_data)
        predictability[num] = score

    # Create ranking
    ranking = sorted(predictability.items(), key=lambda x: x[1], reverse=True)

    # Compile full results
    numbers_detail = {}
    for num in range(1, 71):
        numbers_detail[str(num)] = {
            "number": num,
            "global": global_freq[num],
            "jackpot_context": jackpot_data[num],
            "temporal_context": temporal_data[num],
            "predictability_score": predictability[num]
        }

    # Summary statistics
    hot_numbers = [n for n in range(1, 71) if global_freq[n]["status"] == "HOT"]
    cold_numbers = [n for n in range(1, 71) if global_freq[n]["status"] == "COLD"]

    jackpot_favored = [n for n in range(1, 71) if jackpot_data[n]["jackpot_preference"] == "HIGH"]

    month_start_favored = [n for n in range(1, 71) if temporal_data[n]["temporal_preference"] == "MONTH_START"]
    month_end_favored = [n for n in range(1, 71) if temporal_data[n]["temporal_preference"] == "MONTH_END"]

    result = {
        "metadata": {
            "analysis_date": datetime.now().isoformat(),
            "total_drawings": total_draws,
            "expected_frequency_per_number": round(20/70 * total_draws, 2),
            "data_source": "KENO_ab_2018.csv",
            "date_range": {
                "start": df['Datum'].min().strftime('%Y-%m-%d'),
                "end": df['Datum'].max().strftime('%Y-%m-%d')
            }
        },
        "summary": {
            "hot_numbers": {
                "threshold": ">680",
                "count": len(hot_numbers),
                "numbers": sorted(hot_numbers)
            },
            "cold_numbers": {
                "threshold": "<600",
                "count": len(cold_numbers),
                "numbers": sorted(cold_numbers)
            },
            "jackpot_context": {
                "jackpot_days": jp_days,
                "normal_days": nm_days,
                "jackpot_favored_numbers": sorted(jackpot_favored)
            },
            "temporal_context": {
                "month_start_days": st_days,
                "month_end_days": en_days,
                "month_middle_days": md_days,
                "month_start_favored": sorted(month_start_favored),
                "month_end_favored": sorted(month_end_favored)
            },
            "birthday_effect": birthday_data
        },
        "predictability_ranking": [
            {"rank": i+1, "number": num, "score": score}
            for i, (num, score) in enumerate(ranking[:20])
        ],
        "number_clusters": {
            "description": "Pairs that appear together more than 15% above expected",
            "expected_cooccurrence": round(total_draws * (20/70) * (19/69), 2),
            "top_pairs": clusters
        },
        "numbers_detail": numbers_detail
    }

    # Write output
    output_file = output_path / "number_frequency_context.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)

    print(f"\nResults written to: {output_file}")

    # Print summary
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)

    print(f"\nTotal drawings analyzed: {total_draws}")
    print(f"Expected frequency per number: {round(20/70 * total_draws, 2)}")

    print(f"\nHOT numbers (>680): {hot_numbers}")
    print(f"COLD numbers (<600): {cold_numbers}")

    print(f"\nJackpot-favored numbers: {jackpot_favored}")

    print(f"\nMonth-start favored: {month_start_favored}")
    print(f"Month-end favored: {month_end_favored}")

    print(f"\nBirthday effect: {birthday_data['birthday_effect']}")
    print(f"  Birthday avg: {birthday_data['birthday_numbers']['avg_frequency']}")
    print(f"  Non-birthday avg: {birthday_data['non_birthday_numbers']['avg_frequency']}")

    print(f"\nTop 10 predictable numbers:")
    for i, (num, score) in enumerate(ranking[:10]):
        status = global_freq[num]["status"]
        jp_pref = jackpot_data[num]["jackpot_preference"]
        print(f"  {i+1}. Number {num}: score={score:.2f}, status={status}, jackpot={jp_pref}")

    print(f"\nTop 10 number pairs (clusters):")
    for i, pair in enumerate(clusters[:10]):
        print(f"  {i+1}. {pair['pair']}: count={pair['count']}, lift={pair['lift']:.3f}")


if __name__ == "__main__":
    main()
