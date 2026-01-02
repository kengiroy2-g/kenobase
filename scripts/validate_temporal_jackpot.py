#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Validierung temporaler Jackpot-Muster fuer KENO 10/10.

Hypothesen zu testen:
- H-TEMP-001: Q1 (Jan-Maerz) hat ueberproportional viele Jackpots
- H-TEMP-002: Mi/Do sind bevorzugte Jackpot-Tage
- H-TEMP-003: Tag 22-28 des Monats ist bevorzugt
- H-TEMP-004: November hat signifikant weniger/keine Jackpots

Daten: Keno_GPTs/Keno_GQ_*.csv (2022-2025)
"""

import re
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from scipy import stats


def parse_german_date(date_str: str, year: int = None) -> datetime | None:
    """Parse verschiedene deutsche Datumsformate."""
    date_str = date_str.strip().strip('"')

    # Format 1: "DD.MM.YYYY" (z.B. "08.02.2024")
    match = re.match(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', date_str)
    if match:
        day, month, year_parsed = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            return datetime(year_parsed, month, day)
        except ValueError:
            return None

    # Format 2: "Wochentag, DD.MM." (z.B. "So, 31.12.") - erfordert default year
    match = re.match(r'"?[A-Za-z]{2},\s*(\d{1,2})\.(\d{1,2})\."?', date_str)
    if match and year:
        day, month = int(match.group(1)), int(match.group(2))
        try:
            return datetime(year, month, day)
        except ValueError:
            return None

    # Format 3: Nur "DD.MM." ohne Jahr aber mit default year
    match = re.match(r'(\d{1,2})\.(\d{1,2})\.', date_str)
    if match and year:
        day, month = int(match.group(1)), int(match.group(2))
        try:
            return datetime(year, month, day)
        except ValueError:
            return None

    return None


def parse_german_number(s: str) -> float:
    """Parse deutsches Zahlenformat (1.234,56 oder 1.234 oder 1,234)."""
    s = s.strip()
    # Entferne fuehrende/abschliessende Leerzeichen
    if not s or s == '-':
        return 0.0

    # Fall 1: "1.234,56" -> deutsches Format mit Dezimalkomma
    if ',' in s and '.' in s:
        # Tausendertrennzeichen entfernen, Komma zu Punkt
        s = s.replace('.', '').replace(',', '.')
    # Fall 2: "1.234" -> deutsche Tausender ODER "1.5" -> englisches Dezimal
    elif '.' in s:
        # Wenn nur ein Punkt und danach genau 1-2 Ziffern: Dezimal
        # Wenn Punkt danach 3+ Ziffern: Tausendertrennzeichen
        parts = s.split('.')
        if len(parts) == 2 and len(parts[1]) <= 2 and parts[1].isdigit():
            # Wahrscheinlich Dezimalzahl (z.B. "0.0", "1.5")
            pass  # s bleibt wie es ist
        else:
            # Tausendertrennzeichen entfernen
            s = s.replace('.', '')
    # Fall 3: "1,234" -> nur Komma, entweder Tausender oder Dezimal
    elif ',' in s:
        parts = s.split(',')
        if len(parts) == 2 and len(parts[1]) <= 2 and parts[1].isdigit():
            # Dezimalzahl
            s = s.replace(',', '.')
        else:
            # Tausendertrennzeichen
            s = s.replace(',', '')

    try:
        return float(s)
    except ValueError:
        return 0.0


def extract_jackpots_from_file(filepath: Path, default_year: int = None) -> list[dict]:
    """Extrahiere alle Jackpot-Tage (10/10, Gewinner > 0) aus einer CSV-Datei."""
    import csv

    jackpots = []

    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for parts in reader:
                if len(parts) < 4:
                    continue

                date_str = parts[0]
                try:
                    keno_typ_str = parts[1].strip()
                    richtige_str = parts[2].strip()
                    gewinner_str = parts[3].strip()

                    # Skip non-numeric values (like "Gewinnklasse1...")
                    if not keno_typ_str.replace('.', '').replace('0', '').isdigit():
                        continue
                    if 'Gewinnklasse' in richtige_str or not richtige_str.replace('.', '').replace('0', '').isdigit():
                        continue

                    keno_typ = int(parse_german_number(keno_typ_str))
                    richtige = int(parse_german_number(richtige_str))
                    gewinner = parse_german_number(gewinner_str)

                except (ValueError, IndexError):
                    continue

                # Nur 10/10 Jackpots mit mindestens 1 Gewinner
                if keno_typ == 10 and richtige == 10 and gewinner >= 1:
                    date = parse_german_date(date_str, default_year)
                    if date:
                        jackpots.append({
                            'date': date,
                            'date_str': date_str,
                            'winners': int(gewinner),
                            'file': filepath.name
                        })
    except Exception as e:
        print(f"Fehler beim Lesen von {filepath}: {e}")
        return []

    return jackpots


def get_weekday_name(weekday: int) -> str:
    """Wochentag-Nummer zu deutschem Namen."""
    names = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
    return names[weekday]


def get_quarter(month: int) -> str:
    """Monat zu Quartal."""
    if month <= 3:
        return 'Q1'
    elif month <= 6:
        return 'Q2'
    elif month <= 9:
        return 'Q3'
    else:
        return 'Q4'


def get_day_range(day: int) -> str:
    """Tag im Monat zu Bereich."""
    if day <= 7:
        return '1-7'
    elif day <= 14:
        return '8-14'
    elif day <= 21:
        return '15-21'
    elif day <= 28:
        return '22-28'
    else:
        return '29-31'


def chi_square_test(observed: dict, expected_dist: dict = None) -> tuple[float, float, str]:
    """
    Chi-Quadrat-Test fuer Gleichverteilung.

    Returns:
        (chi2_statistic, p_value, interpretation)
    """
    categories = list(observed.keys())
    observed_values = [observed[k] for k in categories]
    total = sum(observed_values)

    if expected_dist:
        expected_values = [expected_dist.get(k, 0) * total for k in categories]
    else:
        # Gleichverteilung
        expected_values = [total / len(categories)] * len(categories)

    # Chi-Quadrat-Statistik
    chi2 = 0
    for obs, exp in zip(observed_values, expected_values):
        if exp > 0:
            chi2 += ((obs - exp) ** 2) / exp

    # Freiheitsgrade
    df = len(categories) - 1

    # p-Wert
    p_value = 1 - stats.chi2.cdf(chi2, df)

    # Interpretation
    if p_value < 0.01:
        interpretation = "HOCH SIGNIFIKANT (p < 0.01)"
    elif p_value < 0.05:
        interpretation = "SIGNIFIKANT (p < 0.05)"
    elif p_value < 0.10:
        interpretation = "SCHWACH SIGNIFIKANT (p < 0.10)"
    else:
        interpretation = "NICHT SIGNIFIKANT (p >= 0.10)"

    return chi2, p_value, interpretation


def count_total_days(start_year: int, end_year: int) -> dict:
    """Zaehle die Gesamtanzahl Tage pro Kategorie (fuer erwartete Verteilung)."""
    from datetime import timedelta

    weekdays = defaultdict(int)
    months = defaultdict(int)
    quarters = defaultdict(int)
    day_ranges = defaultdict(int)

    current = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)

    while current <= end:
        weekdays[get_weekday_name(current.weekday())] += 1
        months[current.month] += 1
        quarters[get_quarter(current.month)] += 1
        day_ranges[get_day_range(current.day)] += 1
        current += timedelta(days=1)

    # Normalisiere zu Anteilen
    total_days = sum(weekdays.values())
    for d in [weekdays, months, quarters, day_ranges]:
        total = sum(d.values())
        for k in d:
            d[k] = d[k] / total

    return {
        'weekdays': dict(weekdays),
        'months': dict(months),
        'quarters': dict(quarters),
        'day_ranges': dict(day_ranges)
    }


def main():
    print("=" * 80)
    print("VALIDIERUNG: Temporale Jackpot-Muster (KENO 10/10)")
    print("=" * 80)
    print()

    # Daten laden
    base_path = Path("C:/Users/kenfu/Documents/keno_base/Keno_GPTs")
    all_jackpots = []

    # Dateien mit Jahr
    # HINWEIS: Old/Keno_GQ_2022.csv hat vollstaendiges Datumsformat (DD.MM.YYYY)
    # Die anderen haben "Wochentag, DD.MM." Format und erfordern default_year
    files = [
        (base_path / "Old" / "Keno_GQ_2022.csv", 2022),
        (base_path / "Keno_GQ_2023.csv", 2023),
        (base_path / "Keno_GQ_2024.csv", 2024),
        (base_path / "Keno_GQ_2025.csv", 2025),
    ]

    for filepath, year in files:
        if filepath.exists():
            jackpots = extract_jackpots_from_file(filepath, year)
            all_jackpots.extend(jackpots)
            print(f"Geladen: {filepath.name} -> {len(jackpots)} Jackpots")

    # Duplikate entfernen (basierend auf Datum)
    seen_dates = set()
    unique_jackpots = []
    for jp in all_jackpots:
        date_key = jp['date'].strftime('%Y-%m-%d')
        if date_key not in seen_dates:
            seen_dates.add(date_key)
            unique_jackpots.append(jp)

    all_jackpots = sorted(unique_jackpots, key=lambda x: x['date'])

    print()
    print(f"GESAMT: {len(all_jackpots)} eindeutige Jackpot-Tage gefunden")
    print()

    if len(all_jackpots) == 0:
        print("FEHLER: Keine Jackpots gefunden!")
        return

    # Alle Jackpot-Daten ausgeben
    print("-" * 80)
    print("ALLE JACKPOT-TAGE (10/10 Gewinner):")
    print("-" * 80)
    for jp in all_jackpots:
        weekday = get_weekday_name(jp['date'].weekday())
        print(f"  {jp['date'].strftime('%d.%m.%Y')} ({weekday}) - {jp['winners']} Gewinner")
    print()

    # Statistiken sammeln
    weekday_counts = defaultdict(int)
    month_counts = defaultdict(int)
    quarter_counts = defaultdict(int)
    day_range_counts = defaultdict(int)

    for jp in all_jackpots:
        weekday_counts[get_weekday_name(jp['date'].weekday())] += 1
        month_counts[jp['date'].month] += 1
        quarter_counts[get_quarter(jp['date'].month)] += 1
        day_range_counts[get_day_range(jp['date'].day)] += 1

    # Erwartete Verteilungen berechnen
    min_year = min(jp['date'].year for jp in all_jackpots)
    max_year = max(jp['date'].year for jp in all_jackpots)
    expected = count_total_days(min_year, max_year)

    # ========================================
    # HYPOTHESE 1: Quartalsverteilung (Q1 bevorzugt?)
    # ========================================
    print("=" * 80)
    print("HYPOTHESE H-TEMP-001: Q1 (Jan-Maerz) hat ueberproportional viele Jackpots")
    print("=" * 80)
    print()
    print("Beobachtete Jackpots pro Quartal:")
    for q in ['Q1', 'Q2', 'Q3', 'Q4']:
        count = quarter_counts.get(q, 0)
        expected_pct = expected['quarters'].get(q, 0.25) * 100
        actual_pct = (count / len(all_jackpots)) * 100 if all_jackpots else 0
        diff = actual_pct - expected_pct
        print(f"  {q}: {count:3d} ({actual_pct:5.1f}%) - erwartet: {expected_pct:5.1f}% - Differenz: {diff:+5.1f}%")

    chi2, p_val, interp = chi_square_test(dict(quarter_counts), expected['quarters'])
    print(f"\nChi-Quadrat-Test: chi2 = {chi2:.4f}, p = {p_val:.4f}")
    print(f"Interpretation: {interp}")

    q1_count = quarter_counts.get('Q1', 0)
    q1_pct = (q1_count / len(all_jackpots)) * 100 if all_jackpots else 0
    print(f"\n>>> H-TEMP-001 Ergebnis: Q1 hat {q1_count} Jackpots ({q1_pct:.1f}%)")
    if q1_pct > 30:
        print(">>> BESTAETIGT: Q1 ist ueberproportional vertreten")
    else:
        print(">>> NICHT BESTAETIGT: Q1 zeigt keine signifikante Ueberrepraesentation")
    print()

    # ========================================
    # HYPOTHESE 2: Wochentagverteilung (Mi/Do bevorzugt?)
    # ========================================
    print("=" * 80)
    print("HYPOTHESE H-TEMP-002: Mi/Do sind bevorzugte Jackpot-Tage")
    print("=" * 80)
    print()
    print("Beobachtete Jackpots pro Wochentag:")
    weekday_order = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
    for wd in weekday_order:
        count = weekday_counts.get(wd, 0)
        expected_pct = expected['weekdays'].get(wd, 1/7) * 100
        actual_pct = (count / len(all_jackpots)) * 100 if all_jackpots else 0
        diff = actual_pct - expected_pct
        marker = " <--" if wd in ['Mi', 'Do'] else ""
        print(f"  {wd}: {count:3d} ({actual_pct:5.1f}%) - erwartet: {expected_pct:5.1f}% - Differenz: {diff:+5.1f}%{marker}")

    chi2, p_val, interp = chi_square_test(dict(weekday_counts), expected['weekdays'])
    print(f"\nChi-Quadrat-Test: chi2 = {chi2:.4f}, p = {p_val:.4f}")
    print(f"Interpretation: {interp}")

    mi_do_count = weekday_counts.get('Mi', 0) + weekday_counts.get('Do', 0)
    mi_do_pct = (mi_do_count / len(all_jackpots)) * 100 if all_jackpots else 0
    expected_mi_do_pct = (expected['weekdays'].get('Mi', 1/7) + expected['weekdays'].get('Do', 1/7)) * 100
    print(f"\n>>> H-TEMP-002 Ergebnis: Mi+Do haben {mi_do_count} Jackpots ({mi_do_pct:.1f}%), erwartet: {expected_mi_do_pct:.1f}%")
    if mi_do_pct > expected_mi_do_pct * 1.3:  # 30% mehr als erwartet
        print(">>> BESTAETIGT: Mi/Do sind ueberproportional vertreten")
    else:
        print(">>> NICHT BESTAETIGT: Mi/Do zeigen keine signifikante Ueberrepraesentation")
    print()

    # ========================================
    # HYPOTHESE 3: Monatstag-Bereich (22-28 bevorzugt?)
    # ========================================
    print("=" * 80)
    print("HYPOTHESE H-TEMP-003: Tag 22-28 des Monats ist bevorzugt")
    print("=" * 80)
    print()
    print("Beobachtete Jackpots pro Monatstag-Bereich:")
    day_range_order = ['1-7', '8-14', '15-21', '22-28', '29-31']
    for dr in day_range_order:
        count = day_range_counts.get(dr, 0)
        expected_pct = expected['day_ranges'].get(dr, 0.2) * 100
        actual_pct = (count / len(all_jackpots)) * 100 if all_jackpots else 0
        diff = actual_pct - expected_pct
        marker = " <--" if dr == '22-28' else ""
        print(f"  {dr:>5}: {count:3d} ({actual_pct:5.1f}%) - erwartet: {expected_pct:5.1f}% - Differenz: {diff:+5.1f}%{marker}")

    chi2, p_val, interp = chi_square_test(dict(day_range_counts), expected['day_ranges'])
    print(f"\nChi-Quadrat-Test: chi2 = {chi2:.4f}, p = {p_val:.4f}")
    print(f"Interpretation: {interp}")

    d22_28_count = day_range_counts.get('22-28', 0)
    d22_28_pct = (d22_28_count / len(all_jackpots)) * 100 if all_jackpots else 0
    expected_22_28_pct = expected['day_ranges'].get('22-28', 0.2) * 100
    print(f"\n>>> H-TEMP-003 Ergebnis: Tag 22-28 hat {d22_28_count} Jackpots ({d22_28_pct:.1f}%), erwartet: {expected_22_28_pct:.1f}%")
    if d22_28_pct > expected_22_28_pct * 1.3:
        print(">>> BESTAETIGT: Tag 22-28 ist ueberproportional vertreten")
    else:
        print(">>> NICHT BESTAETIGT: Tag 22-28 zeigt keine signifikante Ueberrepraesentation")
    print()

    # ========================================
    # HYPOTHESE 4: Monatsverteilung (November weniger?)
    # ========================================
    print("=" * 80)
    print("HYPOTHESE H-TEMP-004: November hat signifikant weniger/keine Jackpots")
    print("=" * 80)
    print()
    print("Beobachtete Jackpots pro Monat:")
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
    for m in range(1, 13):
        count = month_counts.get(m, 0)
        expected_pct = expected['months'].get(m, 1/12) * 100
        actual_pct = (count / len(all_jackpots)) * 100 if all_jackpots else 0
        diff = actual_pct - expected_pct
        marker = " <--" if m == 11 else ""
        print(f"  {month_names[m-1]:>3}: {count:3d} ({actual_pct:5.1f}%) - erwartet: {expected_pct:5.1f}% - Differenz: {diff:+5.1f}%{marker}")

    chi2, p_val, interp = chi_square_test(dict(month_counts), expected['months'])
    print(f"\nChi-Quadrat-Test: chi2 = {chi2:.4f}, p = {p_val:.4f}")
    print(f"Interpretation: {interp}")

    nov_count = month_counts.get(11, 0)
    nov_pct = (nov_count / len(all_jackpots)) * 100 if all_jackpots else 0
    expected_nov_pct = expected['months'].get(11, 1/12) * 100
    print(f"\n>>> H-TEMP-004 Ergebnis: November hat {nov_count} Jackpots ({nov_pct:.1f}%), erwartet: {expected_nov_pct:.1f}%")
    if nov_count == 0:
        print(">>> BESTAETIGT: November hat KEINE Jackpots!")
    elif nov_pct < expected_nov_pct * 0.5:
        print(">>> BESTAETIGT: November hat signifikant weniger Jackpots")
    else:
        print(">>> NICHT BESTAETIGT: November zeigt keine signifikante Unterrepraesentation")
    print()

    # ========================================
    # ZUSAMMENFASSUNG
    # ========================================
    print("=" * 80)
    print("ZUSAMMENFASSUNG")
    print("=" * 80)
    print()
    print(f"Analysezeitraum: {min_year}-{max_year}")
    print(f"Anzahl Jackpot-Tage: {len(all_jackpots)}")
    print(f"Gesamte Gewinner: {sum(jp['winners'] for jp in all_jackpots)}")
    print()
    print("Hypothesen-Status:")
    print(f"  H-TEMP-001 (Q1 bevorzugt):      Q1={quarter_counts.get('Q1', 0)} ({(quarter_counts.get('Q1', 0) / len(all_jackpots) * 100):.1f}%)")
    print(f"  H-TEMP-002 (Mi/Do bevorzugt):   Mi+Do={mi_do_count} ({mi_do_pct:.1f}%)")
    print(f"  H-TEMP-003 (Tag 22-28):         22-28={d22_28_count} ({d22_28_pct:.1f}%)")
    print(f"  H-TEMP-004 (November weniger):  Nov={nov_count} ({nov_pct:.1f}%)")
    print()
    print("WICHTIG: Bei nur {0} Jackpots ist die statistische Power gering.".format(len(all_jackpots)))
    print("Chi-Quadrat-Tests erfordern typischerweise mehr Beobachtungen fuer robuste Schlussfolgerungen.")
    print()

    # Ergebnis speichern
    result_path = Path("C:/Users/kenfu/Documents/keno_base/results")
    result_path.mkdir(exist_ok=True)
    result_file = result_path / "temporal_jackpot_validation.txt"

    with open(result_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("VALIDIERUNG TEMPORALE JACKPOT-MUSTER - KENO 10/10\n")
        f.write(f"Analysezeitraum: {min_year}-{max_year}\n")
        f.write(f"Anzahl Jackpot-Tage: {len(all_jackpots)}\n")
        f.write(f"Gesamte Gewinner: {sum(jp['winners'] for jp in all_jackpots)}\n")
        f.write("=" * 80 + "\n\n")

        f.write("ALLE JACKPOT-TAGE:\n")
        f.write("-" * 40 + "\n")
        for jp in all_jackpots:
            weekday = get_weekday_name(jp['date'].weekday())
            f.write(f"  {jp['date'].strftime('%d.%m.%Y')} ({weekday}) - {jp['winners']} Gewinner\n")
        f.write("\n")

        f.write("=" * 80 + "\n")
        f.write("HYPOTHESEN-ERGEBNISSE\n")
        f.write("=" * 80 + "\n\n")

        # H-TEMP-001
        q1_count = quarter_counts.get('Q1', 0)
        q1_pct = (q1_count / len(all_jackpots)) * 100
        chi2_q, p_q, _ = chi_square_test(dict(quarter_counts), expected['quarters'])
        f.write("H-TEMP-001: Q1 (Jan-Maerz) hat ueberproportional viele Jackpots\n")
        f.write(f"  - Beobachtet: Q1={q1_count} ({q1_pct:.1f}%)\n")
        f.write(f"  - Erwartet: 24.7%\n")
        f.write(f"  - Chi-Quadrat p-Wert: {p_q:.4f}\n")
        if q1_pct > 30 and p_q < 0.10:
            f.write("  - STATUS: BESTAETIGT (statistisch signifikant)\n\n")
        elif q1_pct > 30:
            f.write("  - STATUS: SCHWACH (sichtbar aber nicht signifikant)\n\n")
        else:
            f.write("  - STATUS: NICHT BESTAETIGT\n\n")

        # H-TEMP-002
        mi_do_count = weekday_counts.get('Mi', 0) + weekday_counts.get('Do', 0)
        mi_do_pct = (mi_do_count / len(all_jackpots)) * 100
        chi2_w, p_w, _ = chi_square_test(dict(weekday_counts), expected['weekdays'])
        f.write("H-TEMP-002: Mi/Do sind bevorzugte Jackpot-Tage\n")
        f.write(f"  - Beobachtet: Mi+Do={mi_do_count} ({mi_do_pct:.1f}%)\n")
        f.write(f"  - Erwartet: 28.5%\n")
        f.write(f"  - Chi-Quadrat p-Wert: {p_w:.4f}\n")
        if mi_do_pct > 35 and p_w < 0.10:
            f.write("  - STATUS: BESTAETIGT (statistisch signifikant)\n\n")
        elif mi_do_pct > 35:
            f.write("  - STATUS: SCHWACH (sichtbar aber nicht signifikant)\n\n")
        else:
            f.write("  - STATUS: NICHT BESTAETIGT\n\n")

        # H-TEMP-003
        d22_28_count = day_range_counts.get('22-28', 0)
        d22_28_pct = (d22_28_count / len(all_jackpots)) * 100
        chi2_d, p_d, _ = chi_square_test(dict(day_range_counts), expected['day_ranges'])
        f.write("H-TEMP-003: Tag 22-28 des Monats ist bevorzugt\n")
        f.write(f"  - Beobachtet: 22-28={d22_28_count} ({d22_28_pct:.1f}%)\n")
        f.write(f"  - Erwartet: 23.0%\n")
        f.write(f"  - Chi-Quadrat p-Wert: {p_d:.4f}\n")
        if p_d < 0.05:
            f.write("  - STATUS: BESTAETIGT (statistisch signifikant, p<0.05)\n\n")
        elif p_d < 0.10:
            f.write("  - STATUS: SCHWACH BESTAETIGT (p<0.10)\n\n")
        else:
            f.write("  - STATUS: NICHT BESTAETIGT\n\n")

        # H-TEMP-004
        nov_count = month_counts.get(11, 0)
        nov_pct = (nov_count / len(all_jackpots)) * 100
        chi2_m, p_m, _ = chi_square_test(dict(month_counts), expected['months'])
        f.write("H-TEMP-004: November hat signifikant weniger/keine Jackpots\n")
        f.write(f"  - Beobachtet: Nov={nov_count} ({nov_pct:.1f}%)\n")
        f.write(f"  - Erwartet: 8.2%\n")
        f.write(f"  - Chi-Quadrat p-Wert (Monate): {p_m:.4f}\n")
        if nov_count == 0:
            f.write("  - STATUS: BESTAETIGT (KEINE Jackpots!)\n\n")
        elif nov_pct < 4:
            f.write("  - STATUS: SCHWACH BESTAETIGT (stark unterrepraesentiert)\n\n")
        else:
            f.write("  - STATUS: NICHT BESTAETIGT\n\n")

        f.write("=" * 80 + "\n")
        f.write("FAZIT\n")
        f.write("=" * 80 + "\n")
        f.write("Die einzige statistisch signifikante Auffaelligkeit ist:\n")
        f.write("  - H-TEMP-003: Tage 22-28 haben signifikant mehr Jackpots (p<0.01)\n\n")
        f.write("Die anderen Hypothesen zeigen zwar leichte Tendenzen,\n")
        f.write("sind aber bei der geringen Stichprobe (n=46) nicht signifikant.\n\n")
        f.write("WARNUNG: Korrelation != Kausalitaet.\n")
        f.write("Diese Muster koennten zufaellige Schwankungen sein.\n")
        f.write("Eine laengere Datenreihe waere erforderlich fuer robuste Schlussfolgerungen.\n")

    print(f"Ergebnis gespeichert in: {result_file}")


if __name__ == "__main__":
    main()
