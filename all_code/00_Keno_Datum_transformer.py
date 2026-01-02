# ce Programm  a pour but de convertir la date ds les Webscrappin-CSV de Lotto RLP
#file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Keno_Gewinnquote_2023.csv"

#output_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\KENO_Quote_gefiltert.csv"


# 
import pandas as pd
from datetime import datetime

# Pfad zur CSV-Datei für Tabelle 1 und Tabelle 2
file_path_tab1 = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\keno_RohData_02_2024.csv"
file_path_tab2 = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\keno_Plus5_2023.csv"
# Funktion zur Korrektur des Datumsformats
# Funktion zur Korrektur des Datumsformats
def correct_date(date_str):
    # Entfernen des Wochentages und eventueller Leerzeichen
    date_without_day = date_str.split(',')[1].strip() if ',' in date_str else date_str.strip()
    # Sicherstellen, dass nur ein Punkt am Ende steht, bevor das Jahr hinzugefügt wird
    cleaned_date_str = date_without_day.rstrip('.') + '.2024'  # Entfernen aller Punkte am Ende und Hinzufügen von '.2023'
    # Rückgabe des korrigierten Datums als String
    return datetime.strptime(cleaned_date_str, '%d.%m.%Y').strftime('%d.%m.%Y')

# Funktion zum Einlesen und Korrigieren der Daten für beide Tabellen
def process_and_save(file_path, output_file_name, columns, date_col='Datum'):
    data = pd.read_csv(file_path)
    data[date_col] = data[date_col].apply(lambda x: correct_date(x))
    # Speichern der korrigierten Daten in eine neue CSV-Datei
    data.to_csv(output_file_name, index=False,encoding='utf-8-sig')

# Verarbeitung für Tabelle 1
process_and_save(file_path_tab1, "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Keno_GQ_02-2024.csv", ['Datum', 'Keno-Typ', 'Anzahl richtiger Zahlen', 'Anzahl der Gewinner', '1 Euro Gewinn'])

# Verarbeitung für Tabelle 2
#process_and_save(file_path_tab2, "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Plus5_GQ_2023.csv", ['Datum', 'Gewinnklasse', 'Anzahl der Gewinner', 'Gewinnquote'])

print("Daten wurden verarbeitet und gespeichert.")







