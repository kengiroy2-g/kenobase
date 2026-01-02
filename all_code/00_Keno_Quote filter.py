# ce Programm  a pour but de filtrer les "Quote de keno" ouvre  un CSV , convertit la date ds le bon format et filtre les resultat selon les critere predefinit
#file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Keno_Gewinnquote_2023.csv"

#output_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\KENO_Quote_gefiltert.csv"

import pandas as pd
from datetime import datetime

# Pfad zur CSV-Datei
file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Keno_Gewinnquote_2023.csv"

# Daten einlesen
data = pd.read_csv(file_path)

# Korrektur des Datumsformats unter Berücksichtigung doppelter Punkte
def correct_date(date_str):
    # Entfernen von Leerzeichen und Korrektur für doppelte Punkte
    cleaned_date_str = date_str.strip().replace('..', '.') + '2023'
    # Rückgabe des korrigierten Datums
    return datetime.strptime(cleaned_date_str, '%d.%m.%Y')

data['Datum'] = data['Datum'].apply(lambda x: correct_date(x))

# Filtern nach Gewinnklasse 1 für Keno-Typen 10, 09, und 08 mit mindestens 1 Gewinner
filtered_data = data[(data['Keno-Typ'].isin([10, 9, 8])) & (data['Anzahl richtiger Zahlen'] == data['Keno-Typ']) & (data['Anzahl der Gewinner'] >= 1)]

# Nach Datum sortieren
filtered_data = filtered_data.sort_values(by='Datum')

# Berechnung der Tage seit dem letzten Gewinnklasse 1 Ereignis
filtered_data['Vergangene Tage'] = (filtered_data['Datum'] - filtered_data['Datum'].shift()).fillna(pd.Timedelta(seconds=0)).dt.days

# Auswahl der relevanten Spalten und Umbenennung für die Ausgabe
output_data = filtered_data[['Datum', 'Keno-Typ', 'Anzahl der Gewinner', 'Vergangene Tage']]
output_data.columns = ['Datum', 'Keno-Typ', 'Anzahl der Gewinner', 'Vergangene Tage seit dem letzten Gewinnklasse 1']

# Speichern der gefilterten Daten in einer neuen CSV-Datei
output_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\KENO_Quote_gefiltert.csv"
output_data.to_csv(output_file_path, index=False, date_format='%d.%m.%Y')

print(f'Daten wurden erfolgreich in {output_file_path} gespeichert.')

