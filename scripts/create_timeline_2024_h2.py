#!/usr/bin/env python
"""
Erstellt Hot-Zone Timelines fuer Juli - Dezember 2024
"""

import pandas as pd
from pathlib import Path
from collections import defaultdict
from itertools import combinations
import re
from datetime import datetime

# Lade KENO-Daten
BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"

df = pd.read_csv(DATA_FILE, sep=';', encoding='utf-8')
df['datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', errors='coerce')

zahl_cols = [f'Keno_Z{i}' for i in range(1, 21)]
df['zahlen'] = df[zahl_cols].apply(lambda row: [int(x) for x in row if pd.notna(x)], axis=1)
df = df.dropna(subset=['datum']).sort_values('datum').reset_index(drop=True)


def parse_german_int(s):
    s = str(s).strip()
    if re.match(r'^\d+\.0$', s):
        return int(float(s))
    s = s.replace('.', '')
    try:
        return int(s)
    except:
        return 0


def load_gq_jackpots(year):
    filepath = BASE_DIR / "Keno_GPTs" / f"Keno_GQ_{year}.csv"
    if not filepath.exists():
        return []

    gq = pd.read_csv(filepath, encoding='utf-8')
    gq.columns = ['Datum', 'Keno_Typ', 'Richtige', 'Anzahl_Gewinner', 'Gewinn']
    gq['Keno_Typ'] = pd.to_numeric(gq['Keno_Typ'], errors='coerce')
    gq['Richtige'] = pd.to_numeric(gq['Richtige'], errors='coerce')
    gq = gq[(gq['Keno_Typ'] == 10) & (gq['Richtige'] == 10)]
    gq['Anzahl_Gewinner'] = gq['Anzahl_Gewinner'].apply(parse_german_int)
    gq = gq[gq['Anzahl_Gewinner'] > 0]

    jackpots = []
    for _, row in gq.iterrows():
        match = re.search(r'(\d+)\.(\d+)\.', str(row['Datum']))
        if match:
            day, month = int(match.group(1)), int(match.group(2))
            date_obj = datetime(year, month, day)
            jackpots.append({
                'date': date_obj,
                'datum_str': f'{day:02d}.{month:02d}.{year}',
                'gewinner': row['Anzahl_Gewinner']
            })
    return jackpots


def get_hot_zone(df, end_date, window=50):
    hist = df[df['datum'] <= end_date].tail(window)
    freq = defaultdict(int)
    for zahlen in hist['zahlen']:
        for num in zahlen:
            freq[num] += 1
    sorted_nums = sorted(freq.items(), key=lambda x: -x[1])
    return [n for n, _ in sorted_nums[:7]]


# Lade 10/10 Jackpots
jackpots_10_10 = load_gq_jackpots(2024) + load_gq_jackpots(2025)
jackpots_10_10.sort(key=lambda x: x['date'])

# Hot-Zones und Analyse
months_2024 = [
    ('JULI 2024', '2024-06-30', 'Jun 2024', 7, 1),
    ('AUGUST 2024', '2024-07-31', 'Jul 2024', 8, 2),
    ('SEPTEMBER 2024', '2024-08-31', 'Aug 2024', 9, 3),
    ('OKTOBER 2024', '2024-09-30', 'Sep 2024', 10, 4),
    ('NOVEMBER 2024', '2024-10-31', 'Okt 2024', 11, 5),
    ('DEZEMBER 2024', '2024-11-30', 'Nov 2024', 12, 6),
]

md_content = """# Hot-Zone Timelines: Juli - Dezember 2024

Analyse der Hot-Zones und ihrer Jackpot-Performance bis Dezember 2025.
- **Typ 6 (6/6 = 500€)** - unsere Hot-Zone Treffer
- **Typ 10 (10/10 = 100.000€)** - echte KENO-System Auszahlungen

---

"""

all_results = []

for month_name, end_date, short_name, month_num, timeline_num in months_2024:
    hz = sorted(get_hot_zone(df, end_date))
    groups = list(combinations(hz, 6))

    start_date = pd.Timestamp(f'2024-{month_num:02d}-01')
    end_test = pd.Timestamp('2025-12-31')

    test_df = df[(df['datum'] >= start_date) & (df['datum'] <= end_test)]

    training_date = pd.Timestamp(end_date)

    jackpot_events = []
    for _, row in test_df.iterrows():
        drawn = set(row['zahlen'])
        date_str = row['datum'].strftime('%d.%m.%Y')

        for group in groups:
            group_set = set(group)
            hits = len(drawn & group_set)

            if hits == 6:
                months_diff = (row['datum'].year - training_date.year) * 12 + (row['datum'].month - training_date.month)
                jackpot_events.append({
                    'datum': row['datum'],
                    'datum_str': date_str,
                    'gruppe': list(group),
                    'months_after': months_diff
                })

    relevant_10_10 = [jp for jp in jackpots_10_10 if jp['date'] >= start_date and jp['date'] <= end_test]
    for jp in relevant_10_10:
        months_diff = (jp['date'].year - training_date.year) * 12 + (jp['date'].month - training_date.month)
        jp['months_after'] = months_diff

    all_results.append({
        'month_name': month_name,
        'short_name': short_name,
        'end_date': end_date,
        'hot_zone': hz,
        'jackpots': jackpot_events,
        'jackpots_10_10': relevant_10_10,
        'total_hits': len(jackpot_events),
        'unique_days': len(set(jp['datum_str'] for jp in jackpot_events)),
    })

    # Timeline erstellen
    md_content += f"""## TIMELINE {timeline_num}: {month_name}

```
{'='*78}
TIMELINE: Hot-Zone -> Jackpots
{'='*78}

Hot-Zone {hz} festgestellt: {end_date}

     {short_name}                                                      Dez 2025
        |                                                              |
        v                                                              v
"""

    if len(jackpot_events) == 0:
        md_content += """   -----*--------------------------------------------------------------*-----
        |                                                              |
     Training                     KEINE JACKPOTS                      Ende
"""
    else:
        # Timeline mit Jackpots
        md_content += "   -----*"
        for i, jp in enumerate(jackpot_events[:4]):
            md_content += "----------*"
        md_content += "-" * max(10, 60 - len(jackpot_events[:4])*10) + "*-----\n"
        md_content += "        |"
        for i, jp in enumerate(jackpot_events[:4]):
            md_content += "            |"
        md_content += "\n"

        md_content += "     Training"
        for i, jp in enumerate(jackpot_events[:4]):
            md_content += f"    {i+1}. Jackpot"
        md_content += "\n"

        if len(jackpot_events) > 0:
            md_content += "                 "
            for i, jp in enumerate(jackpot_events[:4]):
                md_content += jp['datum_str'] + "        "
            md_content += "\n"

    md_content += f"""
   Typ 6 Jackpots (6/6 = 500€):      {len(jackpot_events)}
"""

    for jp in jackpot_events:
        md_content += f"     * {jp['datum_str']} (+{jp['months_after']} Mo)  - Gruppe: {jp['gruppe']}\n"

    md_content += """
   --------------------------------------------------------------------------
   Echte KENO 10/10 Jackpots (100.000€) im Testzeitraum:
"""

    for jp in relevant_10_10:
        md_content += f"     * {jp['datum_str']} (+{jp['months_after']} Mo)  - {jp['gewinner']} Gewinner\n"

    md_content += """```

---

"""

# Zusammenfassung
md_content += """## Zusammenfassung

### Typ 6 (6/6 = 500€) - Unsere Hot-Zone

| Monat | Hot-7 Zahlen | Jackpots | Zeitspanne |
|-------|--------------|----------|------------|
"""

total_jackpots = 0
successful = 0
for r in all_results:
    hz_str = str(r['hot_zone'])
    if r['total_hits'] > 0:
        min_mo = min(jp['months_after'] for jp in r['jackpots'])
        max_mo = max(jp['months_after'] for jp in r['jackpots'])
        zeitspanne = f"+{min_mo} bis +{max_mo} Monate" if min_mo != max_mo else f"+{min_mo} Monate"
        successful += 1
    else:
        zeitspanne = "-"
    md_content += f"| {r['month_name']} | {hz_str} | {r['total_hits']} | {zeitspanne} |\n"
    total_jackpots += r['total_hits']

md_content += f"| **TOTAL** | | **{total_jackpots}** | |\n"

md_content += """
### Typ 10 (10/10 = 100.000€) - Echte KENO-System Auszahlungen

| Datum | Gewinner | Bemerkung |
|-------|----------|-----------|
"""

# Unique 10/10 Jackpots (ab Juli 2024)
seen_dates = set()
unique_10_10 = []
for jp in jackpots_10_10:
    if jp['date'] >= datetime(2024, 7, 1) and jp['datum_str'] not in seen_dates:
        unique_10_10.append(jp)
        seen_dates.add(jp['datum_str'])

unique_10_10.sort(key=lambda x: x['date'])
total_winners = 0
max_winners = 0
max_date = ""

for jp in unique_10_10:
    bemerkung = ""
    if jp['gewinner'] > max_winners:
        max_winners = jp['gewinner']
        max_date = jp['datum_str']
    md_content += f"| {jp['datum_str']} | {jp['gewinner']} | {bemerkung} |\n"
    total_winners += jp['gewinner']

md_content += f"| **TOTAL** | **{total_winners}** | |\n"

fruehester = "+6 Monate (November-Zone)"
spaetester = "+15 Monate (Juli-Zone)"

md_content += f"""
---

## Erkenntnisse

### Typ 6 (unsere Strategie)
- **Erfolgsquote:** {successful} von 6 Hot-Zones ({successful*100//6}%) produzierten Jackpots
- **Fruehester Jackpot:** {fruehester}
- **Spaetester Jackpot:** {spaetester}
- **Beste Monate:** Juli & November 2024 (je 2 Jackpots)

### Typ 10 (echte KENO Jackpots)
- **Juli-Dezember 2024:** {len([jp for jp in unique_10_10 if jp['date'].year == 2024])} Ereignisse
- **2025:** {len([jp for jp in unique_10_10 if jp['date'].year == 2025])} Ereignisse
- **Maximum:** {max_winners} Gewinner am {max_date}

---

*Erstellt: {datetime.now().strftime('%d.%m.%Y')}*
"""

# Speichern
output_file = BASE_DIR / "results" / "hot_zone_timelines_2024_h2.md"
output_file.parent.mkdir(exist_ok=True)
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f"Datei gespeichert: {output_file}")
print()
print("=" * 70)
print("ZUSAMMENFASSUNG")
print("=" * 70)
print()
for r in all_results:
    status = "X" if r['total_hits'] > 0 else "-"
    print(f"{r['month_name']}: {r['hot_zone']} -> {r['total_hits']} Jackpots [{status}]")
print()
print(f"TOTAL: {total_jackpots} Jackpots aus {successful} von 6 Hot-Zones ({successful*100//6}%)")
