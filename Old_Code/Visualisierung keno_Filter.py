import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Dateipfad der CSV-Datei
file_path = 'C:\\Users\\Admin1\\Downloads\\KENO_ab_2018.csv (1)\\KENO_ab_2018.csv'

# Laden und Vorverarbeiten der Daten
keno_data = pd.read_csv(file_path, sep=';', parse_dates=['Datum'])
numbers_columns = [f'z{i}' for i in range(1, 21)]
melted_keno_data = keno_data.melt(id_vars=['Datum'], value_vars=numbers_columns, var_name='Ziehungsnummer', value_name='Gezogene Zahl')
melted_keno_data['Jahr'] = melted_keno_data['Datum'].dt.year
melted_keno_data['Monat'] = melted_keno_data['Datum'].dt.month
melted_keno_data['Woche'] = melted_keno_data['Datum'].dt.isocalendar().week


# Funktion zum Plotten der Häufigkeiten
def plot_frequency(data, title, xlabel, ylabel):
    plt.figure(figsize=(18, 9))
    sns.heatmap(data, cmap='viridis')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()

# Funktion zum Exportieren der Daten und Diagramme
def export_data_and_plots(data, filename):
    csv_filename = f'C:\\Users\\Admin1\\Downloads\\KENO_ab_2018.csv (1)\\{filename}.csv'
    plot_filename = f'C:\\Users\\Admin1\\Downloads\\KENO_ab_2018.csv (1)\\{filename}.png'

    # Exportieren als CSV
    data.to_csv(csv_filename)

    # Exportieren als Diagramm
    plt.figure(figsize=(15, 6))
    sns.heatmap(data, cmap='viridis')
    plt.title(filename)
    plt.xlabel('Gezogene Zahl')
    plt.ylabel(filename.split('_')[2])
    plt.savefig(plot_filename)

    return csv_filename, plot_filename

# Analyse für einen spezifischen Zeitraum
def analyze_period(start_date, end_date):
    period_data = melted_keno_data[(melted_keno_data['Datum'] >= start_date) & (melted_keno_data['Datum'] <= end_date)]
    frequency_period = period_data.groupby(['Woche', 'Gezogene Zahl']).size().unstack(fill_value=0)
    return frequency_period

# Zusätzliche Funktion zur Analyse der täglichen Häufigkeit
def analyze_daily_frequency(start_date, end_date):
    period_data = melted_keno_data[(melted_keno_data['Datum'] >= start_date) & (melted_keno_data['Datum'] <= end_date)]
    frequency_daily = period_data.groupby(['Datum', 'Gezogene Zahl']).size().unstack(fill_value=0)
    return frequency_daily

# Beispiel: Analyse von Juni 2022 bis Januar 2023
start_date = '2022-06-01'
end_date = '2023-01-31'
frequency_period_data = analyze_period(start_date, end_date)
plot_frequency(frequency_period_data, 'Wöchentliche Häufigkeit von Juni 2022 bis Januar 2023', 'Gezogene Zahl', 'Woche')
csv_filename, plot_filename = export_data_and_plots(frequency_period_data, 'frequency_period_juni2022_januar2023')

# Tägliche Häufigkeit für den gewählten Zeitraum analysieren und exportieren
frequency_daily_data = analyze_daily_frequency(start_date, end_date)
plot_frequency(frequency_daily_data, 'Tägliche Häufigkeit von Juni 2022 bis Januar 2023', 'Gezogene Zahl', 'Datum')
csv_daily_frequency, plot_daily_frequency = export_data_and_plots(frequency_daily_data, 'frequency_daily_juni2022_januar2023')
