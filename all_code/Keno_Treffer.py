import pandas as pd

def check_keno_numbers(csv_path, numbers_to_check):
    # Einlesen der CSV-Datei
    keno_data = pd.read_csv(csv_path, sep=';')

    # Ergebnisliste
    results = []

    # Durchlaufen jeder Ziehung
    for index, row in keno_data.iterrows():
        # Extrahieren der gezogenen Zahlen
        drawn_numbers = set(row.loc['z1':'z20'])

        # Vergleichen mit den zu prüfenden Zahlen
        matches = drawn_numbers.intersection(numbers_to_check)

        # Wenn mindestens 5 Treffer, füge zum Ergebnis hinzu
        if len(matches) >=6:
            results.append((row['Datum'], len(matches), matches))

    return results

# Pfad zur CSV-Datei (anpassen für den tatsächlichen Pfad)
csv_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\KENO_ab_2018 - Kopie.csv"

# Liste der zu prüfenden Zahlen (Beispiel)
numbers_to_check = {1, 9, 10, 11, 17, 21, 32, 34, 36, 51}

# Ausführen der Funktion
keno_results = check_keno_numbers(csv_path, numbers_to_check)

# Ausgabe der Ergebnisse
for date, count, numbers in keno_results:
    print(f"Datum: {date}, Anzahl Treffer: {count}, Treffer-Zahlen: {numbers}")
