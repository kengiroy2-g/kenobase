##### Tage count bis jackpot
# Zählungen = wie oft kam eine Zahl bis jackpot 
#Counts = index von Zahlungen
#################### 
# duo,trio,und quatro berechnung implementiert
# Problem  jede Schleife die gesamte Tabelle durchläuft, statt nur die darunterliegenden Zeilen zu durchlaufen ist gelöst

import csv
from collections import Counter



# Dateipfade definieren
input_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\eurojackpo_bereinigt_for_GPT.csv"
intermediate_output_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\analyse_EJ_ziehungen_01.csv"
final_output_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\analyse_EJ_ziehungen_v5_lot49.csv"



def read_draws(file_path):
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file, delimiter=';')
        draws = [row for row in csv_reader]
    return draws

def process_draws_for_target(draws, target_index):
    target_numbers = set(map(int, draws[target_index][1:]))
    counters = {number: 0 for number in target_numbers}
    draws_count = 0

    # Startet die Schleife von der nächsten Ziehung nach target_index
    for draw in draws[target_index + 1:]:
        if draw[0] == 'Datum':
            continue
        numbers = list(map(int, draw[1:]))
        draws_count += 1
        for number in numbers:
            if number in target_numbers:
                counters[number] += 1
        if all(count >= 1 for count in counters.values()):
            break

    counters_str = ','.join([f"[{num}: {count}]" for num, count in counters.items()])
    counts_only_str = ','.join([str(count) for count in counters.values()])
    return draws_count, counters_str, counts_only_str

def generate_intermediate_results():
    draws = read_draws(input_file_path)
    results = []

    for index in range(len(draws)):
        if draws[index][0] == 'Datum':
            continue
        draws_count, counters_str, counts_only_str = process_draws_for_target(draws, index)
        results_row = draws[index] + [draws_count, counters_str, counts_only_str]
        results.append(results_row)

    with open(intermediate_output_file_path, mode='w', newline='') as file:
        csv_writer = csv.writer(file, delimiter=';')
        header = draws[0] + ['Anzahl Ziehungen', 'Zählungen', 'Counts']
        csv_writer.writerow(header)
        for result_row in results:
            csv_writer.writerow(result_row)

def document_simultaneous_appearances(draws):
    results = []
    for index, draw in enumerate(draws):
        try:
            target_numbers = set(map(int, draw[1:8]))
        except ValueError:
            continue

        appearances = {"Duo": [], "Trio": [], "Quatro": []}

        # Startet die Schleife von der nächsten Ziehung nach der aktuellen
        for other_draw in draws[index + 1:]:
            try:
                numbers = set(map(int, other_draw[1:8]))
            except ValueError:
                continue

            intersection = target_numbers.intersection(numbers)
            if len(intersection) >= 2:
                if len(intersection) == 2:
                    appearances["Duo"].append(intersection)
                elif len(intersection) == 3:
                    appearances["Trio"].append(intersection)
                elif len(intersection) == 4:
                    appearances["Quatro"].append(intersection)

        results_row = draw + [
            ';'.join(["[" + ','.join(map(str, combo)) + "]" for combo in appearances["Duo"]]),
            ';'.join(["[" + ','.join(map(str, combo)) + "]" for combo in appearances["Trio"]]),
            ';'.join(["[" + ','.join(map(str, combo)) + "]" for combo in appearances["Quatro"]])
        ]
        results.append(results_row)

    return results

def main():
    generate_intermediate_results()
    draws = read_draws(intermediate_output_file_path)
    results = document_simultaneous_appearances(draws)

    with open(final_output_file_path, mode='w', newline='') as file:
        csv_writer = csv.writer(file, delimiter=';')
        header = ['Datum', 'S1', 'S2', 'z1', 'z2', 'z3', 'z4', 'z5', 'Anzahl Ziehungen', 'Zählungen', 'Counts', 'Duo', 'Trio', 'Quatro']
        csv_writer.writerow(header)
        for result_row in results:
            csv_writer.writerow(result_row)

if __name__ == "__main__":
    main()
