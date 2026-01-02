import pandas as pd


# ce programme permet de verifier combien de fois une Liste de Numero donne ont ete tire dans und periode predefinit
#Zusammenfassend extrahiert, korrigiert und filtert das Programm Daten aus einer Keno-Gewinnquoten-CSV-Datei, 
# berechnet die Tage zwischen den Gewinnen der höchsten Klasse für spezifische Keno-Typen und speichert das Ergebnis in einer neuen Datei.


def check_keno_numbers(csv_path, numbers_to_check, start_date, end_date):
    # Einlesen der CSV-Datei
    keno_data = pd.read_csv(csv_path, sep=';')

    # Konvertierung der Datumsspalte in ein datetime-Format
    keno_data['Datum'] = pd.to_datetime(keno_data['Datum'], format='%d.%m.%Y')

    # Filtern der Daten für den gewünschten Zeitraum
    filtered_data = keno_data[(keno_data['Datum'] >= pd.to_datetime(start_date, format='%d.%m.%Y')) & 
                              (keno_data['Datum'] <= pd.to_datetime(end_date, format='%d.%m.%Y'))]

    # Ergebnisliste
    results = []

    # Durchlaufen jeder Ziehung im gefilterten Zeitraum
    for index, row in filtered_data.iterrows():
        # Extrahieren der gezogenen Zahlen
        drawn_numbers = set(row.loc['z1':'z20'])

        # Vergleichen mit den zu prüfenden Zahlen
        matches = drawn_numbers.intersection(numbers_to_check)

        # Wenn mindestens 5 Treffer, füge zum Ergebnis hinzu                              /////////////////////////////////
        if len(matches) >= 6:
            results.append((row['Datum'].strftime('%d.%m.%Y'), len(matches), matches))

    return results

# Pfad zur CSV-Datei (anpassen für den tatsächlichen Pfad)
csv_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\00_Keno_6-Kombi_Analyse\\KENO_ab_2018 - Kopie.csv"

# Liste der zu prüfenden Zahlen (Beispiel)
numbers_to_check = {8, 10, 16, 26, 29, 31, 35, 39, 42, 45, 55, 57, 59, 61, 62, 66}
#{24,26,9,29, 17, 36, 46,48,6,14,21,30}

# Zeitraum für die Suche definieren (Beispiel)
start_date = '10.03.2024'
end_date = '01.04.2024'

# Ausführen der Funktion
keno_results = check_keno_numbers(csv_path, numbers_to_check, start_date, end_date)

# Ausgabe der Ergebnisse
for date, count, numbers in keno_results:
    print(f"Datum: {date}, Anzahl Treffer: {count}, Treffer-Zahlen: {numbers}")
