import pandas as pd

def analyze_lottery_data(file_path):
    # Daten aus der CSV-Datei laden
    df = pd.read_csv(file_path, delimiter=';', usecols=[i for i in range(21)], parse_dates=["Datum"])
    
    # Einteilung der Daten in drei Zeiträume mit jeweils 10 Ziehungen
    periods = {
        'Zeitraum_1': df.iloc[0:10],
        'Zeitraum_2': df.iloc[10:20],
        'Zeitraum_3': df.iloc[20:30]
    }

    # Häufigkeitsanalyse pro Zeitraum
    frequency_analysis = {}
    for period, data in periods.items():
        counts = data.iloc[:, 1:].apply(pd.Series.value_counts, axis=1).sum(axis=0).sort_values(ascending=False)
        frequency_analysis[period] = counts

    # Gesamthäufigkeitsanalyse
    all_periods_data = pd.concat(periods.values())
    total_counts = all_periods_data.iloc[:, 1:].apply(pd.Series.value_counts, axis=1).sum(axis=0).sort_values(ascending=False)

    # Ermittlung der Top 11 Zahlen pro Zeitraum
    top_11_each_period = {period: freq.head(11) for period, freq in frequency_analysis.items()}

    # Schnittmengen zwischen den Top 11 Listen jedes Zeitraums und den Top 20 der Gesamtanalyse
    top_11_20_intersections = {
        period: freq.index.intersection(total_counts.head(20).index) 
        for period, freq in top_11_each_period.items()
    }

    # Kombinieren der Schnittmengen ohne Duplikate
    combined_top_11_20_intersection = set().union(*top_11_20_intersections.values())

    # Kombinierte Schnittmenge aller paarweisen Top-11 der Zeiträume
    pairwise_top_11_intersection = set().union(
        set(top_11_each_period['Zeitraum_1'].index).intersection(top_11_each_period['Zeitraum_2'].index),
        set(top_11_each_period['Zeitraum_1'].index).intersection(top_11_each_period['Zeitraum_3'].index),
        set(top_11_each_period['Zeitraum_2'].index).intersection(top_11_each_period['Zeitraum_3'].index)
    )

    return frequency_analysis, top_11_each_period, top_11_20_intersections, combined_top_11_20_intersection, pairwise_top_11_intersection




# Verwendung des Skripts (ersetzen Sie 'file_path' mit dem Pfad zu Ihrer CSV-Datei)
file_path =  "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\00_Keno_6-Kombi_Analyse\\KENO_ab_2018 - Kopie.csv"
results = analyze_lottery_data(file_path)
print(results)
