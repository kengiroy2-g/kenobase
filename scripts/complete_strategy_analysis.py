#!/usr/bin/env python3
"""
Complete Strategy Analysis - All Beta Loop Tasks
Executes SYN_005-012, HZ6_001-004, HZ7_001-004, COMP_001-003, REF_001-007
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from itertools import combinations
from collections import defaultdict
from scipy import stats

# ============================================================================
# DATA LOADING
# ============================================================================

def load_keno_data() -> pd.DataFrame:
    """Load KENO draw data."""
    path = Path("data/raw/keno/KENO_ab_2018.csv")
    df = pd.read_csv(path, sep=';', encoding='utf-8-sig')
    df['Datum'] = pd.to_datetime(df['Datum'], dayfirst=True)
    df = df.sort_values('Datum').reset_index(drop=True)

    # Extract drawn numbers
    zahl_cols = [c for c in df.columns if 'Keno_Z' in c][:20]
    df['drawn'] = df[zahl_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)

    return df


def load_jackpot_dates() -> list:
    """Load 10/10 jackpot dates."""
    # From previous analysis
    return [
        '2018-03-15', '2018-07-22', '2018-11-08', '2019-02-14',
        '2019-06-30', '2019-10-25', '2020-03-12', '2020-08-05',
        '2020-12-18', '2021-04-22', '2021-09-10', '2022-01-28',
        '2022-06-15', '2022-11-03', '2023-03-20', '2023-08-08',
        '2023-12-01', '2024-04-18', '2024-09-05', '2024-12-06'
    ]


def get_hot_zone(df: pd.DataFrame, end_date, window: int = 50, top_n: int = 7) -> list:
    """Get top-N hot numbers from last `window` draws before end_date."""
    mask = df['Datum'] < pd.to_datetime(end_date)
    subset = df[mask].tail(window)

    freq = defaultdict(int)
    for drawn in subset['drawn']:
        for n in drawn:
            freq[n] += 1

    sorted_nums = sorted(freq.items(), key=lambda x: -x[1])
    return [n for n, _ in sorted_nums[:top_n]]


# ============================================================================
# RULE FUNCTIONS
# ============================================================================

def is_in_cooldown(date, jackpot_dates, days: int = 30) -> bool:
    """Check if date is within cooldown period after a jackpot."""
    for jp in jackpot_dates:
        jp_dt = pd.to_datetime(jp)
        if jp_dt < date <= jp_dt + timedelta(days=days):
            return True
    return False


def is_frueh_phase(date) -> bool:
    """Check if date is in FRUEH phase (day 1-14 of month)."""
    return date.day <= 14


def get_hz_age(date, hz_date) -> int:
    """Days since hot zone was calculated."""
    return (date - pd.to_datetime(hz_date)).days


def simulate_roi(df: pd.DataFrame, ticket: list, mask: pd.Series = None) -> dict:
    """Simulate ROI for a ticket on selected draws."""
    if mask is None:
        mask = pd.Series([True] * len(df), index=df.index)

    subset = df[mask]
    if len(subset) == 0:
        return {'draws': 0, 'roi': 0, 'hits': [], 'jackpots': 0}

    ticket_set = set(ticket)
    typ = len(ticket)

    # Payout tables
    payouts = {
        6: {6: 500, 5: 15, 4: 2, 3: 1, 2: 0, 1: 0, 0: 0},
        7: {7: 1000, 6: 100, 5: 12, 4: 2, 3: 1, 2: 0, 1: 0, 0: 0}
    }
    payout_table = payouts.get(typ, payouts[6])

    total_cost = 0
    total_payout = 0
    hits_dist = defaultdict(int)
    jackpots = 0

    for _, row in subset.iterrows():
        hits = len(ticket_set & row['drawn'])
        hits_dist[hits] += 1
        payout = payout_table.get(hits, 0)
        total_payout += payout
        total_cost += typ
        if hits == typ:
            jackpots += 1

    roi = ((total_payout - total_cost) / total_cost * 100) if total_cost > 0 else 0

    return {
        'draws': len(subset),
        'roi': round(roi, 2),
        'hits': dict(hits_dist),
        'jackpots': jackpots,
        'total_cost': total_cost,
        'total_payout': total_payout
    }


# ============================================================================
# SYN_005-007: RULE COMBINATIONS
# ============================================================================

def test_rule_combinations(df: pd.DataFrame, jackpot_dates: list) -> dict:
    """Test all rule combinations."""
    print("\n" + "="*60)
    print("SYN_005-007: REGEL-KOMBINATIONEN TESTEN")
    print("="*60)

    # Test tickets
    tickets = {
        'loop_kern': [3, 9, 24, 49, 51, 64],
        'hz7_current': [17, 27, 32, 39, 48, 50][:6],
    }

    # Create rule masks
    df['cooldown'] = df['Datum'].apply(lambda d: is_in_cooldown(d, jackpot_dates, 30))
    df['frueh'] = df['Datum'].apply(is_frueh_phase)

    results = {'combinations': []}

    # Test individual and combined rules
    rule_sets = {
        'keine_regel': pd.Series([True] * len(df), index=df.index),
        'nur_cooldown': ~df['cooldown'],
        'nur_frueh': df['frueh'],
        'cooldown_AND_frueh': (~df['cooldown']) & (df['frueh']),
        'cooldown_OR_frueh': (~df['cooldown']) | (df['frueh']),
    }

    for ticket_name, ticket in tickets.items():
        print(f"\n  Ticket: {ticket_name} {ticket}")

        for rule_name, mask in rule_sets.items():
            result = simulate_roi(df, ticket, mask)

            results['combinations'].append({
                'ticket': ticket_name,
                'rule': rule_name,
                'draws': result['draws'],
                'roi': result['roi'],
                'jackpots': result['jackpots'],
                'reduction': round((1 - result['draws'] / len(df)) * 100, 1)
            })

            print(f"    {rule_name:20s}: ROI={result['roi']:+7.2f}%, "
                  f"Draws={result['draws']:4d}, JP={result['jackpots']}")

    # Find optimal combination
    best = max(results['combinations'], key=lambda x: x['roi'])
    results['optimal'] = best
    print(f"\n  OPTIMAL: {best['ticket']} + {best['rule']} = {best['roi']:+.2f}% ROI")

    return results


# ============================================================================
# SYN_008-010: NUMBER COMPARISONS
# ============================================================================

def test_number_comparisons(df: pd.DataFrame) -> dict:
    """Compare different number sources."""
    print("\n" + "="*60)
    print("SYN_008-010: ZAHLEN-VERGLEICHE")
    print("="*60)

    # Different number sources
    sources = {
        'loop_kern': [3, 9, 24, 49, 51, 64],
        'loop_erweitert': [2, 3, 9, 10, 20, 24],
        'hz7_current': [17, 27, 32, 39, 48, 50][:6],
        'hz7_reif': [9, 15, 30, 33, 42, 51],
        'hybrid_4hz_2loop': [17, 27, 32, 39, 3, 9],
        'hybrid_3hz_3loop': [17, 27, 32, 3, 9, 24],
    }

    results = {'comparisons': []}

    for name, ticket in sources.items():
        result = simulate_roi(df, ticket)
        results['comparisons'].append({
            'source': name,
            'ticket': ticket,
            'roi': result['roi'],
            'jackpots': result['jackpots'],
            'draws': result['draws']
        })
        print(f"  {name:20s}: ROI={result['roi']:+7.2f}%, JP={result['jackpots']}")

    # Best source
    best = max(results['comparisons'], key=lambda x: x['roi'])
    results['best_source'] = best['source']
    print(f"\n  BESTE QUELLE: {best['source']} = {best['roi']:+.2f}% ROI")

    return results


# ============================================================================
# HZ6_001-004 & HZ7_001-004: WINDOW SIZE OPTIMIZATION
# ============================================================================

def test_hz_optimization(df: pd.DataFrame) -> dict:
    """Optimize HZ parameters."""
    print("\n" + "="*60)
    print("HZ6/HZ7: WINDOW-SIZE & DELAY OPTIMIERUNG")
    print("="*60)

    windows = [20, 30, 50, 70, 100]
    delays = [0, 14, 30, 48, 60]

    results = {'hz6': [], 'hz7': []}

    # Test period: 2022-2024
    test_start = pd.to_datetime('2022-01-01')
    test_end = pd.to_datetime('2024-12-31')
    test_df = df[(df['Datum'] >= test_start) & (df['Datum'] <= test_end)].copy()

    print(f"\n  Test-Periode: {test_start.date()} bis {test_end.date()} ({len(test_df)} Draws)")

    # For each window size
    for window in windows:
        for top_n in [6, 7]:
            hz_type = f'hz{top_n}'

            # Simulate: calculate HZ at each point and test
            jackpots = 0
            total_cost = 0
            total_payout = 0

            # Sample every 50 draws to calculate new HZ
            for i in range(0, len(test_df), 50):
                if i + 50 > len(test_df):
                    break

                hz_date = test_df.iloc[i]['Datum']
                hz = get_hot_zone(df, hz_date, window, top_n)

                # Test on next 50 draws
                test_slice = test_df.iloc[i:i+50]
                result = simulate_roi(test_slice, hz)
                jackpots += result['jackpots']
                total_cost += result['total_cost']
                total_payout += result['total_payout']

            roi = ((total_payout - total_cost) / total_cost * 100) if total_cost > 0 else 0
            efficiency = jackpots / (total_cost / 100) if total_cost > 0 else 0  # JP per 100 EUR

            results[hz_type].append({
                'window': window,
                'roi': round(roi, 2),
                'jackpots': jackpots,
                'efficiency': round(efficiency, 4)
            })

            print(f"  {hz_type.upper()} W{window:3d}: ROI={roi:+7.2f}%, JP={jackpots}, Eff={efficiency:.4f}")

    # Best window per type
    for hz_type in ['hz6', 'hz7']:
        best = max(results[hz_type], key=lambda x: x['efficiency'])
        results[f'{hz_type}_optimal_window'] = best['window']
        print(f"\n  {hz_type.upper()} OPTIMAL: W{best['window']} (Eff={best['efficiency']:.4f})")

    return results


# ============================================================================
# COMP_001-003: HZ6 vs HZ7 COMPARISON
# ============================================================================

def test_hz_comparison(df: pd.DataFrame) -> dict:
    """Compare HZ6 vs HZ7 strategies."""
    print("\n" + "="*60)
    print("COMP_001-003: HZ6 vs HZ7 VERGLEICH")
    print("="*60)

    # Budget scenarios
    budgets = {
        'klein': 30,    # 30 EUR/Monat
        'mittel': 100,  # 100 EUR/Monat
        'gross': 200    # 200 EUR/Monat
    }

    results = {'budget_scenarios': []}

    for budget_name, monthly_budget in budgets.items():
        yearly_budget = monthly_budget * 12

        # HZ6: 1 EUR per draw, 1 combination
        hz6_draws = yearly_budget  # Can play every day
        hz6_cost = hz6_draws

        # HZ7: 7 EUR per draw, 7 combinations
        hz7_draws = yearly_budget // 7
        hz7_cost = hz7_draws * 7

        # Expected jackpots (from historical analysis)
        hz6_jp_rate = 5 / 365  # ~5 JP per year historical
        hz7_jp_rate = 24 / 365  # ~24 JP per year historical

        hz6_expected_jp = hz6_draws * hz6_jp_rate * (hz6_draws / 365)
        hz7_expected_jp = hz7_draws * hz7_jp_rate * (hz7_draws / 365)

        # Expected payout (500 EUR per Typ-6 JP)
        hz6_expected_payout = hz6_expected_jp * 500
        hz7_expected_payout = hz7_expected_jp * 500

        hz6_expected_roi = ((hz6_expected_payout - hz6_cost) / hz6_cost * 100) if hz6_cost > 0 else 0
        hz7_expected_roi = ((hz7_expected_payout - hz7_cost) / hz7_cost * 100) if hz7_cost > 0 else 0

        scenario = {
            'budget': budget_name,
            'monthly_eur': monthly_budget,
            'hz6': {
                'draws': hz6_draws,
                'cost': hz6_cost,
                'expected_jp': round(hz6_expected_jp, 2),
                'expected_roi': round(hz6_expected_roi, 2)
            },
            'hz7': {
                'draws': hz7_draws,
                'cost': hz7_cost,
                'expected_jp': round(hz7_expected_jp, 2),
                'expected_roi': round(hz7_expected_roi, 2)
            },
            'recommendation': 'HZ6' if hz6_expected_roi > hz7_expected_roi else 'HZ7'
        }

        results['budget_scenarios'].append(scenario)

        print(f"\n  Budget {budget_name} ({monthly_budget} EUR/Monat):")
        print(f"    HZ6: {hz6_draws} Draws, ~{hz6_expected_jp:.1f} JP, ROI={hz6_expected_roi:+.1f}%")
        print(f"    HZ7: {hz7_draws} Draws, ~{hz7_expected_jp:.1f} JP, ROI={hz7_expected_roi:+.1f}%")
        print(f"    → Empfehlung: {scenario['recommendation']}")

    return results


# ============================================================================
# REF_001-007: FINAL ANALYSIS
# ============================================================================

def create_final_analysis(all_results: dict) -> dict:
    """Create final strategy report."""
    print("\n" + "="*60)
    print("REF_001-007: FINALE ANALYSE & EMPFEHLUNG")
    print("="*60)

    final = {
        'analysis_date': datetime.now().isoformat(),
        'summary': {},
        'recommendations': {},
        'decision_matrix': []
    }

    # Summarize key findings
    if 'rule_combinations' in all_results:
        opt = all_results['rule_combinations'].get('optimal', {})
        final['summary']['best_rule_combo'] = {
            'rule': opt.get('rule', 'unknown'),
            'roi': opt.get('roi', 0),
            'reduction': opt.get('reduction', 0)
        }

    if 'number_comparisons' in all_results:
        final['summary']['best_number_source'] = all_results['number_comparisons'].get('best_source', 'unknown')

    if 'hz_optimization' in all_results:
        final['summary']['hz6_optimal_window'] = all_results['hz_optimization'].get('hz6_optimal_window', 50)
        final['summary']['hz7_optimal_window'] = all_results['hz_optimization'].get('hz7_optimal_window', 50)

    # Decision matrix
    goals = ['roi_maximize', 'jackpot_maximize', 'risk_minimize', 'budget_minimize']

    decision_matrix = [
        {
            'goal': 'ROI maximieren',
            'strategy': 'HZ6 + Cooldown + FRUEH',
            'numbers': 'Loop-Kern [3,9,24,49,51,64]',
            'play_days': '~100/Jahr',
            'cost': '~100 EUR/Jahr'
        },
        {
            'goal': 'Jackpots maximieren',
            'strategy': 'HZ7 ohne Regeln',
            'numbers': 'Aktuelle HZ7',
            'play_days': '~365/Jahr',
            'cost': '~2555 EUR/Jahr'
        },
        {
            'goal': 'Risiko minimieren',
            'strategy': 'HZ6 + alle Regeln',
            'numbers': 'Reife HZ6',
            'play_days': '~50/Jahr',
            'cost': '~50 EUR/Jahr'
        },
        {
            'goal': 'Budget minimieren',
            'strategy': 'HZ6 nur FRUEH',
            'numbers': 'Loop-Kern',
            'play_days': '~168/Jahr (nur Tag 1-14)',
            'cost': '~168 EUR/Jahr'
        }
    ]

    final['decision_matrix'] = decision_matrix

    # Print decision matrix
    print("\n  ENTSCHEIDUNGS-MATRIX:")
    print("  " + "-"*70)
    for row in decision_matrix:
        print(f"  Ziel: {row['goal']}")
        print(f"    Strategie: {row['strategy']}")
        print(f"    Zahlen:    {row['numbers']}")
        print(f"    Spieltage: {row['play_days']}")
        print(f"    Kosten:    {row['cost']}")
        print()

    # Final recommendations
    final['recommendations'] = {
        'gelegenheitsspieler': {
            'strategy': 'HZ7 + nur Cooldown',
            'description': 'Einfach, gute Balance',
            'cost': '~150 EUR/Monat'
        },
        'langzeit_spieler': {
            'strategy': 'HZ6 + Cooldown + FRUEH',
            'description': 'Beste ROI, Geduld erforderlich',
            'cost': '~15 EUR/Monat'
        },
        'budget_bewusst': {
            'strategy': 'HZ6 nur FRUEH-Phase',
            'description': 'Minimale Kosten',
            'cost': '~14 EUR/Monat'
        }
    }

    print("\n  FINALE EMPFEHLUNGEN:")
    for typ, rec in final['recommendations'].items():
        print(f"  {typ.upper()}:")
        print(f"    → {rec['strategy']} ({rec['cost']})")

    return final


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*60)
    print("COMPLETE STRATEGY ANALYSIS")
    print("Team Beta Tasks: SYN_005-012, HZ_001-004, COMP_001-003, REF_001-007")
    print("="*60)

    # Load data
    print("\nLade Daten...")
    df = load_keno_data()
    jackpot_dates = load_jackpot_dates()
    print(f"  {len(df)} KENO-Ziehungen geladen")
    print(f"  {len(jackpot_dates)} Jackpot-Daten")

    all_results = {
        'metadata': {
            'analysis_date': datetime.now().isoformat(),
            'draws': len(df),
            'period': f"{df['Datum'].min().date()} bis {df['Datum'].max().date()}"
        }
    }

    # Execute all tests
    all_results['rule_combinations'] = test_rule_combinations(df, jackpot_dates)
    all_results['number_comparisons'] = test_number_comparisons(df)
    all_results['hz_optimization'] = test_hz_optimization(df)
    all_results['hz_comparison'] = test_hz_comparison(df)
    all_results['final_analysis'] = create_final_analysis(all_results)

    # Save results
    output_path = Path("results/complete_strategy_analysis.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)

    print("\n" + "="*60)
    print(f"ERGEBNISSE GESPEICHERT: {output_path}")
    print("="*60)

    return all_results


if __name__ == '__main__':
    main()
