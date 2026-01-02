
# Pfad zur Ihrer CSV-Datei
# file_path = 'C:\\Users\\Admin1\\Downloads\\KENO_ab_2018.csv (1)\\KENO_ab_2018.csv'

import pandas as pd
from matplotlib.dates import DateFormatter
import seaborn as sns

import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

file_path = 'C:\\Users\\Admin1\\Downloads\\KENO_ab_2018.csv (1)\\Formatted_Date_Filtered_KENO_ab_2018 - Kopie.csv'

# Parsing the CSV file correctly
keno_data = pd.read_csv(file_path, sep=';', parse_dates=['Datum'])

# Extracting the drawn numbers and converting them to a long format for easier analysis
numbers_columns = [f'z{i}' for i in range(1, 21)]
melted_keno_data = keno_data.melt(id_vars=['Datum'], value_vars=numbers_columns, var_name='Ziehungsnummer', value_name='Gezogene Zahl')

# Adding time-based columns
melted_keno_data['Jahr'] = melted_keno_data['Datum'].dt.year
melted_keno_data['Monat'] = melted_keno_data['Datum'].dt.month
melted_keno_data['Woche'] = melted_keno_data['Datum'].dt.isocalendar().week
melted_keno_data['Tag'] = melted_keno_data['Datum'].dt.day

# Frequency analysis
frequency_by_day = melted_keno_data.groupby(['Tag', 'Gezogene Zahl']).size().unstack(fill_value=0)
frequency_by_week = melted_keno_data.groupby(['Woche', 'Gezogene Zahl']).size().unstack(fill_value=0)
frequency_by_month = melted_keno_data.groupby(['Monat', 'Gezogene Zahl']).size().unstack(fill_value=0)
frequency_by_year = melted_keno_data.groupby(['Jahr', 'Gezogene Zahl']).size().unstack(fill_value=0)

# Plotting function
def plot_frequency(data, title, xlabel, ylabel):
    plt.figure(figsize=(15, 6))
    sns.heatmap(data, cmap='viridis')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()

# Plotting the frequencies
plot_frequency(frequency_by_day, 'Häufigkeit der gezogenen Zahlen pro Tag', 'Gezogene Zahl', 'Tag')
plot_frequency(frequency_by_week, 'Häufigkeit der gezogenen Zahlen pro Woche', 'Gezogene Zahl', 'Woche')
plot_frequency(frequency_by_month, 'Häufigkeit der gezogenen Zahlen pro Monat', 'Gezogene Zahl', 'Monat')
plot_frequency(frequency_by_year, 'Häufigkeit der gezogenen Zahlen pro Jahr', 'Gezogene Zahl', 'Jahr')

# Export function for data and plots
def export_data_and_plots(data, filename):
    csv_filename = f'C:\\Users\\Admin1\\Downloads\\KENO_ab_2018.csv (1)\\{filename}.csv'
    plot_filename = f'C:\\Users\\Admin1\\Downloads\\KENO_ab_2018.csv (1)\\{filename}.png'

    # Export data to CSV
    data.to_csv(csv_filename)

    # Export plot to PNG
    plt.figure(figsize=(15, 6))
    sns.heatmap(data, cmap='viridis')
    plt.title(filename)
    plt.xlabel('Gezogene Zahl')
    plt.ylabel(filename.split('_')[2])
    plt.savefig(plot_filename)

    return csv_filename, plot_filename

# Exporting data and plots for further analysis
csv_day, plot_day = export_data_and_plots(frequency_by_day, 'frequency_by_day')
csv_week, plot_week = export_data_and_plots(frequency_by_week, 'frequency_by_week')
csv_month, plot_month = export_data_and_plots(frequency_by_month, 'frequency_by_month')
csv_year, plot_year = export_data_and_plots(frequency_by_year, 'frequency_by_year')

csv_day, plot_day, csv_week, plot_week, csv_month, plot_month, csv_year, plot_year
