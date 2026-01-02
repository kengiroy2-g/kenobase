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
from concurrent.futures import ThreadPoolExecutor, as_completed

# Dateipfade definieren
input_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\eurojackpo_bereinigt_for_GPT.csv"
second_input_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\Lotto_kombi.csv"
final_output_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\final_analysis.csv"

def read_draws(file_path):
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file, delimiter=';')
        draws = [row for row in csv_reader if row and row[0] != 'Datum']
    return draws

def analyze_draws(draw, target_numbers):
    counters = Counter(target_numbers)
    draws_count = 0
    appearances = {"Duo": [], "Trio": [], "Quatro": []}

    for other_draw in draw:
        numbers = set(map(int, filter(lambda x: x.isdigit(), other_draw)))
        draws_count += 1
        intersection = target_numbers.intersection(numbers)

        if len(intersection) >= 2:
            appearances["Duo"].append(intersection)
        if len(intersection) >= 3:
            appearances["Trio"].append(intersection)
        if len(intersection) == 4:
            appearances["Quatro"].append(intersection)

        for number in numbers:
            if number in counters:
                counters[number] += 1

        if all(count >= 1 for count in counters.values()):
            break

    counts_str = ','.join([f"{num}: {counters[num]}" for num in counters])
    return draws_count, counts_str, appearances

def generate_final_results(draws, second_draws):
    results = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(analyze_draws, draws, set(map(int, draw))) for draw in second_draws[1:]]
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Analyzing Draws"):
            draws_count, counts_str, appearances = future.result()
            appearances_str = {
                key: ';'.join(["[" + ','.join(map(str, combo)) + "]" for combo in value])
                for key, value in appearances.items()
            }
            results.append([draws_count, counts_str, appearances_str['Duo'], appearances_str['Trio'], appearances_str['Quatro']])

    with open(final_output_file_path, mode='w', newline='') as file:
        csv_writer = csv.writer(file, delimiter=';')
        header = ['Anzahl Ziehungen', 'Zählungen', 'Duo', 'Trio', 'Quatro']
        csv_writer.writerow(header)
        for result_row in results:
            csv_writer.writerow(result_row)

def main():
    draws = read_draws(input_file_path)
    second_draws = read_draws(second_input_file_path)
    generate_final_results(draws, second_draws)

if __name__ == "__main__":
    main()
