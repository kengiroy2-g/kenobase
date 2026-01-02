#################### 
# duo,trio,und quatro berechnung

####################

import csv
from itertools import combinations

import csv
from collections import Counter

# Dateipfad der CSV-Datei
input_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\eurojackpo_bereinigt_for_GPT.csv"
output_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\analyse_EJ_ziehungen_v2.csv"





# Ziehungsdaten einlesen
def read_draws(file_path):
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file, delimiter=';')
        next(csv_reader)  # Kopfzeile überspringen
        draws = [row for row in csv_reader]
    return draws

# Gleichzeitige Erscheinungen für jede Ziehungsreihe dokumentieren
def document_simultaneous_appearances(draws):
    results = []
    for target_index, target_draw in enumerate(draws):
        target_numbers = set(map(int, target_draw[1:]))  # Zielzahlen der aktuellen Ziehung
        appearances = {"Duo": [], "Trio": [], "Quatro": []}

        for draw in draws[target_index + 1:]:
            numbers = set(map(int, draw[1:]))
            intersection = target_numbers.intersection(numbers)
            match_count = len(intersection)

            # Zählen der Übereinstimmungen unter Berücksichtigung von Duplikaten
            if match_count >= 2:
                draw_counter = Counter(numbers)
                match_details = [num for num in intersection if draw_counter[num] > 1]

                # Anpassen der Übereinstimmungszahl für Duplikate
                for num in match_details:
                    match_count += draw_counter[num] - 1

                # Kategorisieren der Übereinstimmungen
                if match_count == 2:
                    appearances["Duo"].append(intersection)
                elif match_count == 3:
                    appearances["Trio"].append(intersection)
                elif match_count >= 4:
                    appearances["Quatro"].append(intersection)

        # Formatieren der Ergebnisse als Strings
        results_row = target_draw + [
            ';'.join(["[" + ','.join(map(str, combo)) + "]" for combo in appearances["Duo"]]),
            ';'.join(["[" + ','.join(map(str, combo)) + "]" for combo in appearances["Trio"]]),
            ';'.join(["[" + ','.join(map(str, combo)) + "]" for combo in appearances["Quatro"]])
        ]
        results.append(results_row)
    
    return results

# Hauptfunktion, die die Ergebnisse auch in eine CSV-Datei schreibt
def main():
    draws = read_draws(input_file_path)
    results = document_simultaneous_appearances(draws)

    # Ergebnisse in eine neue CSV-Datei schreiben
    with open(output_file_path, mode='w', newline='') as file:
        csv_writer = csv.writer(file, delimiter=';')
        header = ['Datum', 'S1', 'S2', 'z1', 'z2', 'z3', 'z4', 'z5', 'Duo', 'Trio', 'Quatro']
        csv_writer.writerow(header)
        for result_row in results:
            csv_writer.writerow(result_row)

if __name__ == "__main__":
    main()
