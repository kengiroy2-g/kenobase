##### Tage count bis jackpot
# Zählungen = wie oft kam eine Zahl bis jackpot 
#Counts = index von Zahlungen
#################### 
# duo,trio,und quatro berechnung implementiert
# Problem  jede Schleife die gesamte Tabelle durchläuft, statt nur die darunterliegenden Zeilen zu durchlaufen ist gelöst




# import csv
# from collections import Counter

# # Dateipfade definieren
# input_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\eurojackpo_bereinigt_for_GPT.csv"
# second_input_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\Lotto_kombi.csv"  # Pfad zur zweiten CSV-Datei
# intermediate_output_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\analyse_EJ_ziehungen_011.csv"
# final_output_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\analyse_EJ_ziehungen_v55_lot49.csv"


import csv
from collections import Counter
from tqdm import tqdm



# Dateipfade definieren
input_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\eurojackpo_bereinigt_for_GPT.csv"
second_input_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\Lotto_kombi.csv"
intermediate_output_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\analyse_EJ_ziehungen_011.csv"
final_output_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\analyse_EJ_ziehungen_v55_lot49.csv"

def read_draws(file_path):
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file, delimiter=';')
        draws = [row for row in csv_reader]
    return draws

def read_second_draws(file_path):
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file, delimiter=';')
        second_draws = [row for row in csv_reader]
    return second_draws

def generate_intermediate_results(draws, second_draws):
    results = []

    for second_draw in tqdm(second_draws[1:], desc="Processing second draws"):
        target_numbers = set(map(int, filter(None, second_draw)))
        for index, draw in enumerate(draws[1:]):
            if draw and draw[0] == 'Datum':
                continue
            draws_count, counters_str, counts_only_str = process_draws_for_target(draws, index, target_numbers)
            results_row = second_draw + [str(draws_count), counters_str, counts_only_str]
            results.append(results_row)

    with open(intermediate_output_file_path, mode='w', newline='') as file:
        csv_writer = csv.writer(file, delimiter=';')
        header = ['c0','c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'Anzahl Ziehungen', 'Zählungen', 'Counts']
        csv_writer.writerow(header)
        for result_row in results:
            csv_writer.writerow(result_row)

def process_draws_for_target(draws, target_index, target_numbers):
    if target_index >= len(draws):
        return 0, '', ''

    counters = {number: 0 for number in target_numbers}
    draws_count = 0

    for draw in draws[target_index + 1:]:
        if draw and draw[0] == 'Datum':
            continue
        numbers = set(map(int, filter(lambda x: x.isdigit(), draw[1:])))
        draws_count += 1
        for number in numbers:
            if number in target_numbers:
                counters[number] += 1
        if all(count >= 1 for count in counters.values()):
            break
    else:
        draws_count = 0

    counters_str = ','.join([f"[{num}: {count}]" for num, count in counters.items()])
    counts_only_str = ','.join([str(count) for count in counters.values()])
    return draws_count, counters_str, counts_only_str

def document_simultaneous_appearances(draws):
    results = []
    for draw in tqdm(draws, desc="Documenting appearances"):
        if draw and draw[0] == 'Datum':
            continue
        try:
            target_numbers = set(map(int, draw[1:8]))
        except ValueError:
            continue

        appearances = {"Duo": [], "Trio": [], "Quatro": []}
        for other_draw in draws:
            if other_draw and other_draw[0] == 'Datum':
                continue
            try:
                numbers = set(map(int, other_draw[1:8]))
            except ValueError:
                continue

            intersection = target_numbers.intersection(numbers)
            if len(intersection) == 2:
                appearances["Duo"].append(intersection)
            if len(intersection) == 3:
                appearances["Trio"].append(intersection)
            if len(intersection) == 4:
                appearances["Quatro"].append(intersection)

        results_row = draw + [
            ';'.join(["[" + ','.join(map(str, combo)) + "]" for combo in appearances["Duo"]]),
            ';'.join(["[" + ','.join(map(str, combo)) + "]" for combo in appearances["Trio"]]),
            ';'.join(["[" + ','.join(map(str, combo)) + "]" for combo in appearances["Quatro"]])
        ]
        results.append(results_row)
    
    return results

def main():
    draws = read_draws(input_file_path)
    second_draws = read_second_draws(second_input_file_path)
    generate_intermediate_results(draws, second_draws)
    draws = read_draws(intermediate_output_file_path)
    results = document_simultaneous_appearances(draws)

    with open(final_output_file_path, mode='w', newline='') as file:
        csv_writer = csv.writer(file, delimiter=';')
        header = ['C0','c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'Anzahl Ziehungen', 'Zählungen', 'Counts', 'Duo', 'Trio', 'Quatro']
        csv_writer.writerow(header)
        for result_row in results:
            csv_writer.writerow(result_row)

if __name__ == "__main__":
    main()
