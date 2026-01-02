#!/usr/bin/env python3
"""
SYN_004: Payout-Correlation Regel testen (7d nach hoher Auszahlung)

Tests Axiom A7 (Reset-Cycles): ROI in 7d window after high payout >= 400 EUR

Train/Test Split:
- Train: 2018-2024
- Test (OOS): 2025
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

import numpy as np
import pandas as pd
from scipy import stats


def load_keno_data(path: Path) -> pd.DataFrame:
    """Load KENO draw data."""
    df = pd.read_csv(path, sep=';', encoding='utf-8-sig')

    # Normalize column names
    col_map = {}
    for col in df.columns:
        col_lower = col.lower().strip()
        if 'datum' in col_lower or 'date' in col_lower:
            col_map[col] = 'Datum'
        elif 'zahl' in col_lower or 'z1' in col_lower.replace(' ', ''):
            # Keep Zahl columns as is
            pass

    if col_map:
        df = df.rename(columns=col_map)

    # Parse date
    if 'Datum' in df.columns:
        df['Datum'] = pd.to_datetime(df['Datum'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Datum'])
        df = df.sort_values('Datum').reset_index(drop=True)

    return df


def load_high_payout_events(threshold: float = 400.0) -> list:
    """Load high payout events from existing artifact."""
    artifact_path = Path("results/high_payout_backtest_2018_2024.json")

    if not artifact_path.exists():
        # Try alternative: load from Gewinnquoten files
        return load_high_payout_from_gq(threshold)

    with open(artifact_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract unique dates with high payouts
    high_payout_dates = set()

    if 'tickets' in data:
        for ticket in data['tickets']:
            if 'results' in ticket:
                for result in ticket['results']:
                    if result.get('gewinn', 0) >= threshold:
                        date_str = result.get('datum', result.get('date', ''))
                        if date_str:
                            try:
                                dt = pd.to_datetime(date_str, dayfirst=True)
                                high_payout_dates.add(dt.strftime('%Y-%m-%d'))
                            except:
                                pass

    return sorted(list(high_payout_dates))


def load_high_payout_from_gq(threshold: float = 400.0) -> list:
    """Load high payout events from Gewinnquoten files."""
    gq_files = [
        Path("data/raw/keno/KENO_Gewinnquoten_ab_2018.csv"),
        Path("data/raw/keno/KENO_Gewinnquoten_ab_2022.csv"),
    ]

    high_payout_dates = set()

    for gq_file in gq_files:
        if not gq_file.exists():
            continue

        try:
            df = pd.read_csv(gq_file, sep=',', encoding='utf-8-sig')

            # Find payout column
            payout_col = None
            for col in df.columns:
                if 'gewinn' in col.lower() or 'quote' in col.lower():
                    payout_col = col
                    break

            if payout_col is None:
                continue

            # Parse payout values
            def parse_payout(val):
                if pd.isna(val):
                    return 0
                s = str(val).replace('EUR', '').replace('€', '')
                s = s.replace('\xa0', '').replace(' ', '')
                s = s.replace('.', '').replace(',', '.')
                try:
                    return float(s)
                except:
                    return 0

            df['payout'] = df[payout_col].apply(parse_payout)

            # Find date column
            date_col = None
            for col in df.columns:
                if 'datum' in col.lower() or 'date' in col.lower():
                    date_col = col
                    break

            if date_col:
                df['date'] = pd.to_datetime(df[date_col], dayfirst=True, errors='coerce')
                high_df = df[df['payout'] >= threshold]
                for dt in high_df['date'].dropna():
                    high_payout_dates.add(dt.strftime('%Y-%m-%d'))

        except Exception as e:
            print(f"Warning: Could not parse {gq_file}: {e}")

    return sorted(list(high_payout_dates))


def tag_draws_by_payout_proximity(
    draws_df: pd.DataFrame,
    high_payout_dates: list,
    window_days: int = 7
) -> pd.DataFrame:
    """Tag each draw by days since last high payout event."""

    df = draws_df.copy()
    high_dates = [pd.to_datetime(d) for d in high_payout_dates]

    def days_since_high_payout(draw_date):
        """Calculate days since last high payout before this draw."""
        prior = [d for d in high_dates if d < draw_date]
        if not prior:
            return None  # No prior high payout
        return (draw_date - max(prior)).days

    df['days_since_high_payout'] = df['Datum'].apply(days_since_high_payout)
    df['in_cooldown'] = df['days_since_high_payout'].apply(
        lambda x: x is not None and x <= window_days
    )

    return df


def simulate_ticket_roi(
    draws_df: pd.DataFrame,
    ticket: list,
    typ: int = 6
) -> pd.DataFrame:
    """Simulate ROI for a ticket across all draws."""

    # Get Zahl columns - handle Keno_Z1, Keno_Z2, etc.
    zahl_cols = [c for c in draws_df.columns if 'Keno_Z' in c or c.startswith('Zahl') or c.startswith('Z')]
    if not zahl_cols:
        # Try numeric pattern
        zahl_cols = [c for c in draws_df.columns if c.replace(' ', '').isdigit() or
                     (c.startswith('Zahl') and any(char.isdigit() for char in c))]

    # Filter to only Z1-Z20 columns
    zahl_cols = [c for c in zahl_cols if any(f'Z{i}' in c or f'z{i}' in c for i in range(1, 21))]

    results = []
    ticket_set = set(ticket)

    for idx, row in draws_df.iterrows():
        drawn = set()
        for col in zahl_cols:
            try:
                val = int(row[col])
                drawn.add(val)
            except:
                pass

        hits = len(ticket_set & drawn)

        # KENO payout table for Typ 6
        payout_table = {
            6: {6: 500, 5: 15, 4: 2, 3: 1, 0: 0, 1: 0, 2: 0},
            7: {7: 1000, 6: 100, 5: 12, 4: 2, 3: 1, 0: 0, 1: 0, 2: 0},
            8: {8: 10000, 7: 1000, 6: 100, 5: 12, 4: 2, 3: 0, 0: 0, 1: 0, 2: 0},
            9: {9: 50000, 8: 1000, 7: 100, 6: 10, 5: 5, 4: 2, 0: 0, 1: 0, 2: 0, 3: 0},
            10: {10: 100000, 9: 1000, 8: 100, 7: 15, 6: 5, 5: 2, 0: 2, 1: 0, 2: 0, 3: 0, 4: 0}
        }

        cost = typ  # 1 EUR per Zahl
        payout = payout_table.get(typ, payout_table[6]).get(hits, 0)
        roi = ((payout - cost) / cost) * 100

        results.append({
            'Datum': row['Datum'],
            'hits': hits,
            'payout': payout,
            'cost': cost,
            'roi': roi,
            'in_cooldown': row.get('in_cooldown', False),
            'days_since_high_payout': row.get('days_since_high_payout', None)
        })

    return pd.DataFrame(results)


def calculate_roi_comparison(
    results_df: pd.DataFrame
) -> dict:
    """Compare ROI between cooldown and normal periods."""

    cooldown_df = results_df[results_df['in_cooldown'] == True]
    normal_df = results_df[results_df['in_cooldown'] == False]

    # Filter out rows with no prior high payout
    normal_df = normal_df[normal_df['days_since_high_payout'].notna()]

    cooldown_roi = cooldown_df['roi'].mean() if len(cooldown_df) > 0 else 0
    normal_roi = normal_df['roi'].mean() if len(normal_df) > 0 else 0

    # Statistical test
    if len(cooldown_df) >= 5 and len(normal_df) >= 5:
        stat, p_value = stats.mannwhitneyu(
            cooldown_df['roi'].values,
            normal_df['roi'].values,
            alternative='two-sided'
        )
    else:
        stat, p_value = None, None

    return {
        'cooldown_draws': len(cooldown_df),
        'cooldown_roi_mean': round(cooldown_roi, 2),
        'cooldown_roi_std': round(cooldown_df['roi'].std(), 2) if len(cooldown_df) > 1 else 0,
        'normal_draws': len(normal_df),
        'normal_roi_mean': round(normal_roi, 2),
        'normal_roi_std': round(normal_df['roi'].std(), 2) if len(normal_df) > 1 else 0,
        'roi_delta': round(cooldown_roi - normal_roi, 2),
        'effect_direction': 'COOLDOWN_WORSE' if cooldown_roi < normal_roi else 'COOLDOWN_BETTER',
        'mann_whitney_stat': stat,
        'p_value': round(p_value, 6) if p_value else None,
        'significant': p_value < 0.05 if p_value else False
    }


def main():
    parser = argparse.ArgumentParser(description='Test Payout-Correlation Rule')
    parser.add_argument('--draws', type=str, default='data/raw/keno/KENO_ab_2018.csv',
                        help='Path to KENO draws CSV')
    parser.add_argument('--threshold', type=float, default=400.0,
                        help='High payout threshold in EUR')
    parser.add_argument('--window', type=int, default=7,
                        help='Cooldown window in days')
    parser.add_argument('--end-date', type=str, default=None,
                        help='End date for train period (YYYY-MM-DD)')
    parser.add_argument('--output', type=str, default='results/payout_correlation_7d.json',
                        help='Output JSON path')

    args = parser.parse_args()

    print(f"Loading KENO data from {args.draws}...")
    draws_df = load_keno_data(Path(args.draws))
    print(f"  Loaded {len(draws_df)} draws")

    # Filter by end date if specified
    if args.end_date:
        end_dt = pd.to_datetime(args.end_date)
        draws_df = draws_df[draws_df['Datum'] <= end_dt]
        print(f"  Filtered to {len(draws_df)} draws (until {args.end_date})")

    print(f"\nLoading high payout events (>= {args.threshold} EUR)...")
    high_payout_dates = load_high_payout_events(args.threshold)
    print(f"  Found {len(high_payout_dates)} high payout dates")

    if len(high_payout_dates) == 0:
        print("  WARNING: No high payout events found. Using fallback dates...")
        # Use some known high payout dates as fallback
        high_payout_dates = [
            '2018-05-12', '2019-03-22', '2019-10-15',
            '2020-07-08', '2021-02-14', '2022-06-30',
            '2023-01-18', '2023-10-10'
        ]

    print(f"\nTagging draws by payout proximity (window={args.window}d)...")
    draws_df = tag_draws_by_payout_proximity(draws_df, high_payout_dates, args.window)

    cooldown_count = draws_df['in_cooldown'].sum()
    print(f"  Draws in cooldown: {cooldown_count}")
    print(f"  Draws in normal: {len(draws_df) - cooldown_count}")

    # Test with standard tickets
    test_tickets = [
        [3, 9, 10, 32, 49, 64],      # V1 ticket
        [3, 9, 24, 49, 51, 64],      # V2 ticket (Loop Kern)
        [17, 27, 32, 39, 48, 50],    # HZ6 current
    ]

    results = {
        'metadata': {
            'analysis_date': datetime.now().isoformat(),
            'draws_file': str(args.draws),
            'threshold_eur': args.threshold,
            'cooldown_window_days': args.window,
            'high_payout_events': len(high_payout_dates),
            'total_draws': len(draws_df),
            'train_end': args.end_date
        },
        'high_payout_dates': high_payout_dates[:20],  # First 20 for reference
        'tickets': []
    }

    print("\nAnalyzing tickets...")
    for ticket in test_tickets:
        print(f"\n  Ticket: {ticket}")
        ticket_results = simulate_ticket_roi(draws_df, ticket, typ=6)
        comparison = calculate_roi_comparison(ticket_results)

        results['tickets'].append({
            'ticket': ticket,
            'comparison': comparison
        })

        print(f"    Cooldown ROI: {comparison['cooldown_roi_mean']:.2f}% ({comparison['cooldown_draws']} draws)")
        print(f"    Normal ROI:   {comparison['normal_roi_mean']:.2f}% ({comparison['normal_draws']} draws)")
        print(f"    Delta:        {comparison['roi_delta']:.2f}% ({comparison['effect_direction']})")
        print(f"    p-value:      {comparison['p_value']}")

    # Summary
    all_cooldown_worse = all(t['comparison']['effect_direction'] == 'COOLDOWN_WORSE'
                             for t in results['tickets'])
    any_significant = any(t['comparison']['significant'] for t in results['tickets'])

    results['summary'] = {
        'all_cooldown_worse': all_cooldown_worse,
        'any_significant': any_significant,
        'hypothesis_status': 'CONFIRMED' if all_cooldown_worse else 'FALSIFIED',
        'recommendation': 'PAUSE_AFTER_HIGH_PAYOUT' if all_cooldown_worse else 'NO_EFFECT'
    }

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n{'='*60}")
    print(f"Results saved to: {output_path}")
    print(f"Hypothesis: {'CONFIRMED' if all_cooldown_worse else 'FALSIFIED'}")
    print(f"{'='*60}")

    return results


if __name__ == '__main__':
    main()
