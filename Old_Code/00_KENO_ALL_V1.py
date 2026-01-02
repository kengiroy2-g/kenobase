# ce programme selectionne tous les Tirage avec gewinnklasse1 et 
# recherche leur apparition repetitive  dans les autres Tirage avec Gewinnklasse1 avec leur date de tirage comme element commun

import pandas as pd

# Schritt 1: Filterung und Sortierung der KENO-Gewinnquoten
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
    print('Daten wurden erfolgreich in KGDaten_gefiltert.csv gespeichert.')
    return output_data

# Schritt 2: Einlesen der Keno-Ziehungsdaten und Filterung
def filter_keno_drawings(ziehungen_path, filtered_data):
    keno_data = pd.read_csv(ziehungen_path, sep=';')
    keno_data['Datum'] = pd.to_datetime(keno_data['Datum'], format='%d.%m.%Y').dt.strftime('%d.%m.%Y')
    filtered_drawings = keno_data[keno_data['Datum'].isin(filtered_data['Datum'])]
    filtered_drawings.to_csv("C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\NumbertoCheck.csv", index=False)
    print('Gefilterte Ziehungsdaten wurden in NumbertoCheck.csv gespeichert.')
    return filtered_drawings

# Schritte 3 bis 5: Überprüfung der Ziehungen auf Treffer

# Schritte 3 bis 5: Überprüfung der Ziehungen auf Treffer
def check_keno_numbers(csv_path):
    # Überprüfen, ob die CSV-Datei korrekt gelesen wird
    try:
        keno_data = pd.read_csv(csv_path, sep=',')
    except Exception as e:
        raise Exception(f"Fehler beim Einlesen der CSV-Datei: {e}")
    
    # Überprüfen, ob die 'Datum'-Spalte existiert
    if 'Datum' not in keno_data.columns:
        raise KeyError("Die Spalte 'Datum' wurde nicht in der CSV-Datei gefunden. Bitte überprüfen Sie die Spaltennamen.")
    
    # Konvertierung der Datumsspalte in ein datetime-Format
    keno_data['Datum'] = pd.to_datetime(keno_data['Datum'], format='%d.%m.%Y')

    # Ergebnisliste
    results = []

    # Durchlaufen jeder Ziehung in "NumbertoCheck.csv"
    for index, row in keno_data.iterrows():
        # Extrahieren der gezogenen Zahlen für die aktuelle Zeile
        drawn_numbers = set(row.loc['z1':'z20'].dropna().astype(int))
        
        # Durchlaufen aller Zeilen in "NumbertoCheck.csv" für den Vergleich
        for index_compare, row_compare in keno_data.iterrows():
            # Zu prüfende Zahlen extrahieren
            numbers_to_check = set(row_compare.loc['z1':'z20'].dropna().astype(int))
            
            # Vergleichen der gezogenen Zahlen mit den zu prüfenden Zahlen
            matches = drawn_numbers.intersection(numbers_to_check)
            
            # Wenn mindestens 3 Treffer, füge zum Ergebnis hinzu
            if len(matches) >= 3:
                results.append({
                    'Datum': row['Datum'].strftime('%d.%m.%Y'),
                    'Date_Check': row_compare['Datum'].strftime('%d.%m.%Y'),  # Datum der aktuellen Zeile
                    'Anzahl Treffer': len(matches),
                    'Treffer-Zahlen': ', '.join(map(str, matches))
                })

    # Ergebnisse in DataFrame umwandeln und in CSV-Datei speichern
    results_df = pd.DataFrame(results)
    
    results_df.to_csv("C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\CheckNumbers.csv", index=False)
    print('Treffer wurden in CheckNumbers.csv gespeichert.')
    return results_df


# Schritt 6: Zusammenführen der Daten und Speichern
def merge_data_and_save(filtered_data, results_df):
    filtered_data['Datum'] = pd.to_datetime(filtered_data['Datum'], format='%d.%m.%Y')
    results_df['Datum'] = pd.to_datetime(results_df['Datum'], format='%d.%m.%Y')
    merged_data = pd.merge(filtered_data, results_df, on='Datum')
    merged_data.to_csv("C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Liste_GK1_Treffer.csv", index=False)
    print('Zusammengeführte Daten wurden in Liste_GK1_Treffer.csv gespeichert.')

# Pfade zu den CSV-Dateien
gewinnquoten_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Keno_GQ_2023.csv"
ziehungen_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\KENO_Ziehungen_2023_GPT.csv"
# Pfad zur CSV-Datei "NumbertoCheck.csv"
csv_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\NumbertoCheck.csv"

# Ausführen der Funktion

# Ausführung der Funktionen


filtered_data = filter_and_sort_keno_data(gewinnquoten_path)
filter_keno_drawings(ziehungen_path, filtered_data)
check_keno_numbers(csv_path)
results_df = check_keno_numbers(csv_path)
merge_data_and_save(filtered_data, results_df)

# Einlesen der CSV-Datei "Liste_GK1_Treffer.csv"
data = pd.read_csv("C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Liste_GK1_Treffer.csv")

# Datumsspalte neu formatieren
data['Datum'] = pd.to_datetime(data['Datum']).dt.strftime('%d.%m.%Y')

# Ergebnisse in CSV-Datei speichern
data.to_csv("C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Liste_GK1_Treffer.csv", index=False)

print('Das Datumsformat in "Liste_GK1_Treffer.csv" wurde erfolgreich geändert.')

print("Der Prozess wurde erfolgreich abgeschlossen.")



