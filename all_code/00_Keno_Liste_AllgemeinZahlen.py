#import pandas as pd

    # output_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\KGDaten_gefiltert.csv"
    
    # csv_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Keno_GQ_2023.csv"  # Pfad zur CSV-Datei anpassen
    
    # filtered_csv_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\KGDaten_gefiltert.csv"
    # original_csv_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\KENO_Ziehungen_2023_GPT.csv"
    #, encoding='utf-8-sig'
    
from datetime import datetime
import pandas as pd

# Teil 1: Filterung und Sortierung der KENO-Gewinnquoten
def filter_and_sort_keno_data(file_path):
    data = pd.read_csv(file_path)
    data['Datum'] = pd.to_datetime(data['Datum'], format='%d.%m.%Y')
    filtered_data = data[(data['Keno-Typ'].isin([10, 9, 8])) & 
                         (data['Anzahl richtiger Zahlen'] == data['Keno-Typ']) & 
                         (data['Anzahl der Gewinner'] >= 1)]
    filtered_data = filtered_data.sort_values(by='Datum')
    filtered_data['Vergangene Tage'] = (filtered_data['Datum'] - filtered_data['Datum'].shift(1)).dt.days.fillna(0).astype(int)
    filtered_data['Datum'] = filtered_data['Datum'].dt.strftime('%d.%m.%Y')  # Konvertierung in das gewünschte Format
    output_data = filtered_data[['Datum', 'Keno-Typ', 'Anzahl der Gewinner', 'Vergangene Tage']]
    output_data.columns = ['Datum', 'Keno-Typ', 'Anzahl der Gewinner', 'Vergangene Tage seit dem letzten Gewinnklasse 1']
    output_data.to_csv("C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\KGDaten_gefiltert.csv", index=False)
    print('Schritt 1 abgeschlossen: Daten wurden erfolgreich in KGDaten_gefiltert.csv gespeichert.')

# Teil 2: Überprüfung der KENO-Ziehungsdaten und Zusammenführung der Ergebnisse
def check_keno_numbers_and_merge_results(ziehungen_path, filtered_data_path):
    keno_data = pd.read_csv(ziehungen_path, sep=';', parse_dates=['Datum'], dayfirst=True)
    keno_data['Datum'] = keno_data['Datum'].dt.strftime('%d.%m.%Y')  # Konvertierung in das gewünschte Format
    filtered_keno_data = pd.read_csv(filtered_data_path)
    # Keine Notwendigkeit, Datum zu konvertieren, da es bereits im korrekten Format ist
    merged_data = pd.merge(keno_data, filtered_keno_data, on='Datum', how='inner')

    results = []
    for index, row in merged_data.iterrows():
        drawn_numbers = set(row.loc['z1':'z20'].dropna().values)
        numbers_to_check = drawn_numbers  # In diesem Beispiel verwenden wir die gezogenen Zahlen als zu überprüfende Zahlen
        matches = drawn_numbers.intersection(numbers_to_check)
        if len(matches) >= 3:
            results.append({'Datum': row['Datum'], 'Keno-Typ': row['Keno-Typ'], 'Anzahl der Gewinner': row['Anzahl der Gewinner'], 'Vergangene Tage seit dem letzten Gewinnklasse 1': row['Vergangene Tage seit dem letzten Gewinnklasse 1'], 'Treffer': len(matches), 'Treffer-Zahlen': list(matches)})
    
    results_df = pd.DataFrame(results)
    results_df.to_csv("C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Liste_GK1_Treffer.csv", index=False)
    print('Schritt 2 abgeschlossen: Die überprüften Daten wurden erfolgreich in Liste_GK1_Treffer.csv gespeichert.')


file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Keno_GQ_2023.csv"
ziehungen_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\KENO_Ziehungen_2023_GPT.csv"

filter_and_sort_keno_data(file_path)
check_keno_numbers_and_merge_results(ziehungen_path, "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\KGDaten_gefiltert.csv")

#
    #output_data.to_csv("C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\KGDaten_gefiltert.csv", index=False, date_format='%Y-%m-%d')

    #results_df.to_csv("C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Liste_GK1_Treffer.csv", index=False, date_format='%Y-%m-%d')

# file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Keno_GQ_2023.csv"
# ziehungen_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\KENO_Ziehungen_2023_GPT.csv"

# filter_and_sort_keno_data(file_path)
# check_keno_numbers_and_merge_results(ziehungen_path, "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\KGDaten_gefiltert.csv")
