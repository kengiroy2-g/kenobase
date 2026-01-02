##### Fuktion EJ wird aufgerufen
#################### 
# duo,trio,und quatro berechnung implementiert

import csv
from collections import Counter
import subprocess

# Dateipfad der CSV-Datei
input_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\analyse_EJ_ziehungen_0.csv"
output_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\analyse_EJ_ziehungen_v3_lotto.csv"


def read_draws(file_path):
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file, delimiter=';')
        next(csv_reader)  # Kopfzeile überspringen
        draws = [row for row in csv_reader]
    return draws

def document_simultaneous_appearances(draws):
    results = []
    for draw in draws:
        if draw[8] == "0":  # Prüfen, ob "Anzahl Ziehungen" gleich "0" ist
            results_row = draw + [["0,0"], ["0,0"], ["0,0"]]
        else:
            target_numbers = set(map(int, draw[1:8]))  # Zielzahlen der aktuellen Ziehung
            appearances = {"Duo": [], "Trio": [], "Quatro": []}

            for other_draw in draws:
                numbers = set(map(int, other_draw[1:8]))
                intersection = target_numbers.intersection(numbers)
                match_count = len(intersection)

                if match_count >= 2:
                    draw_counter = Counter(numbers)
                    match_details = [num for num in intersection if draw_counter[num] > 1]

                    for num in match_details:
                        match_count += draw_counter[num] - 1

                    if match_count == 2:
                        appearances["Duo"].append(intersection)
                    elif match_count == 3:
                        appearances["Trio"].append(intersection)
                    elif match_count == 4:
                        appearances["Quatro"].append(intersection)

            results_row = draw + [
                ';'.join(["[" + ','.join(map(str, combo)) + "]" for combo in appearances["Duo"]]),
                ';'.join(["[" + ','.join(map(str, combo)) + "]" for combo in appearances["Trio"]]),
                ';'.join(["[" + ','.join(map(str, combo)) + "]" for combo in appearances["Quatro"]])
            ]
        results.append(results_row)
    
    return results

def main():
    subprocess.run(["python", "00_DataAnalyse_EJ.py"])
    draws = read_draws(input_file_path)
    results = document_simultaneous_appearances(draws)

    with open(output_file_path, mode='w', newline='') as file:
        csv_writer = csv.writer(file, delimiter=';')
        header = ['Datum', 'S1', 'S2', 'z1', 'z2', 'z3', 'z4', 'z5', 'Anzahl Ziehungen', 'Zählungen', 'Counts', 'Duo', 'Trio', 'Quatro']
        csv_writer.writerow(header)
        for result_row in results:
            csv_writer.writerow(result_row)

if __name__ == "__main__":
    main()
