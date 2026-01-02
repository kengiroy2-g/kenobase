##################################################

# In Version 2 ,V2,wurde  die Pfad- und Dateinamenkonfiguration in das file_config Dictionary verschoben. 
# Dadurch können die Pfade und Dateinamen im Dictionary einfach angepasst, ohne den restlichen Code anpassen zu müssen.

#########################################################
# ce programme selectionne tous les Tirage avec gewinnklasse1 et 
# recherche leur apparition repetitive  dans les autres Tirage avec Gewinnklasse1 avec leur date de tirage comme element commun

import pandas as pd

# Konfigurationsobjekt für Dateipfade und Dateinamen
file_config = {
    "gewinnquoten_path": "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Keno_GQ_2023.csv",
    
    "ziehungen_path": "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\KENO_Ziehungen_2023_GPT.csv",
    
    "filtered_data_path": "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\10-9_KGDaten_gefiltert.csv", # "1-2-3" represente les kenotyp utiliser lors du filtrage ayant lieu ds la funktion filter_and_sort_keno_data
    # Contient les resultat du filtrage de  tous les Tirage d'une Periode Precise qui ont une apparition d'un GK1
    
    "numbertocheck_path": "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\10-9_NumbertoCheck.csv",# enthält alle Ziehungen wo ein vordefinierte gewinnklasse (zb GK1 kenoty10) eingetroffen ist
    "checknumbers_path": "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\10-9_CheckNumbers.csv",#Datum,Date_Check,Anzahl Treffer,Treffer-Zahlen | verifie les Treffer dun tirage mit GK1 ds tous les autre tirage GK1
    "liste_gk1_treffer_path": "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\10-9_Liste_GK1_Treffer.csv"# Contient la füsion de KGDaten_gefiltert & CheckNumbers
}

# Schritt 1: Filterung und Sortierung der KENO-Gewinnquoten
def filter_and_sort_keno_data(file_path):
    data = pd.read_csv(file_path)
    data['Datum'] = pd.to_datetime(data['Datum'], format='%d.%m.%Y')
    filtered_data = data[(data['Keno-Typ'].isin([10, 9, ])) &
                         (data['Anzahl richtiger Zahlen'] == data['Keno-Typ']) &
                         (data['Anzahl der Gewinner'] >= 5)]
    filtered_data = filtered_data.sort_values(by='Datum')
    filtered_data['Vergangene Tage'] = (filtered_data['Datum'] - filtered_data['Datum'].shift(1)).dt.days.fillna(0).astype(int)
    filtered_data['Datum'] = filtered_data['Datum'].dt.strftime('%d.%m.%Y')  # Konvertierung in das gewünschte Format
    output_data = filtered_data[['Datum', 'Keno-Typ', 'Anzahl der Gewinner', 'Vergangene Tage']]
    output_data.columns = ['Datum', 'Keno-Typ', 'Anzahl der Gewinner', 'Vergangene Tage seit dem letzten Gewinnklasse 1']
    output_data.to_csv(file_config['filtered_data_path'], index=False)
    print('Daten wurden erfolgreich in KGDaten_gefiltert.csv gespeichert.')
    return output_data

# Schritt 2: Einlesen der Keno-Ziehungsdaten und Filterung
def filter_keno_drawings(ziehungen_path, filtered_data):
    keno_data = pd.read_csv(ziehungen_path, sep=';')
    keno_data['Datum'] = pd.to_datetime(keno_data['Datum'], format='%d.%m.%Y').dt.strftime('%d.%m.%Y')
    filtered_drawings = keno_data[keno_data['Datum'].isin(filtered_data['Datum'])]
    filtered_drawings.to_csv(file_config['numbertocheck_path'], index=False)
    print('Gefilterte Ziehungsdaten wurden gespeichert.')
    return filtered_drawings

# Schritt 3 bis 5: Überprüfung der Ziehungen auf Treffer
def check_keno_numbers(csv_path):
    try:
        keno_data = pd.read_csv(csv_path, sep=',')
    except Exception as e:
        raise Exception(f"Fehler beim Einlesen der CSV-Datei: {e}")
    
    if 'Datum' not in keno_data.columns:
        raise KeyError("Die Spalte 'Datum' wurde nicht in der CSV-Datei gefunden.")
    
    keno_data['Datum'] = pd.to_datetime(keno_data['Datum'], format='%d.%m.%Y')
    results = []

    for index, row in keno_data.iterrows():
        drawn_numbers = set(row.loc['z1':'z20'].dropna().astype(int))
        for index_compare, row_compare in keno_data.iterrows():
            numbers_to_check = set(row_compare.loc['z1':'z20'].dropna().astype(int))
            matches = drawn_numbers.intersection(numbers_to_check)
            if len(matches) >= 3:
                results.append({
                    'Datum': row['Datum'].strftime('%d.%m.%Y'),
                    'Date_Check': row_compare['Datum'].strftime('%d.%m.%Y'),
                    'Anzahl Treffer': len(matches),
                    'Treffer-Zahlen': ', '.join(map(str, matches))
                })
                
    results_df = pd.DataFrame(results)
    results_df.to_csv(file_config['checknumbers_path'], index=False)
    print('Treffer wurden gespeichert.')
    return results_df

# Schritt 6: Zusammenführen der Daten und Speichern
def merge_data_and_save(filtered_data, results_df):
    filtered_data['Datum'] = pd.to_datetime(filtered_data['Datum'], format='%d.%m.%Y')
    results_df['Datum'] = pd.to_datetime(results_df['Datum'], format='%d.%m.%Y')
    merged_data = pd.merge(filtered_data, results_df, on='Datum')
    merged_data.to_csv(file_config['liste_gk1_treffer_path'], index=False)
    print('Zusammengeführte Daten wurden gespeichert.')

# Ausführung der Funktionen
filtered_data = filter_and_sort_keno_data(file_config['gewinnquoten_path'])
filter_keno_drawings(file_config['ziehungen_path'], filtered_data)
results_df = check_keno_numbers(file_config['numbertocheck_path'])
merge_data_and_save(filtered_data, results_df)

# Einlesen der finalen CSV-Datei und Datumsspalte neu formatieren
data = pd.read_csv(file_config['liste_gk1_treffer_path'])
data['Datum'] = pd.to_datetime(data['Datum']).dt.strftime('%d.%m.%Y')
data.to_csv(file_config['liste_gk1_treffer_path'], index=False)
print('Das Datumsformat wurde erfolgreich geändert. Der Prozess wurde erfolgreich abgeschlossen.')
