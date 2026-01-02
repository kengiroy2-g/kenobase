#################### 
# duo,trio,und quatro hinzugefügt aber Fehlerhaft

####################

import csv
from itertools import combinations


# Dateipfad der CSV-Datei
input_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\eurojackpo_bereinigt_for_GPT.csv"
output_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\analyse_EJ_ziehungenv1.csv"


# Ziehungsdaten einlesen
def read_draws(file_path):
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file, delimiter=';')
        draws = [row for row in csv_reader]
    return draws

# Kombinationen prüfen und String erstellen
def check_combinations(numbers, target_numbers, combo_size):
    combo_counts = []
    for combo in combinations(target_numbers, combo_size):
        if all(num in numbers for num in combo):
            combo_counts.append(combo)
    return ','.join(['[' + ','.join(map(str, combo)) + ']' for combo in combo_counts]) if combo_counts else '[0,0]'

# Ziehungen für eine bestimmte Zielreihe verarbeiten
def process_draws_for_target(draws, target_index):
    target_numbers = set(map(int, draws[target_index][1:]))  # Zielzahlen der aktuellen Ziehung
    counters = {number: 0 for number in target_numbers}
    duo_counts, trio_counts, quatro_counts = "", "", ""
    draws_count = 0

    # Initialisiere eine Variable, um zu prüfen, ob alle Zahlen mindestens einmal gezogen wurden
    all_numbers_drawn = False

    while not all_numbers_drawn:
        for draw in draws[target_index + 1:]:
            if draw[0] == 'Datum':  # Überspringe die Kopfzeile
                continue
            numbers = set(map(int, draw[1:]))
            draws_count += 1

            # Zähler und Kombinationen aktualisieren
            for number in numbers:
                if number in target_numbers:
                    counters[number] += 1
            
            # Kombinationen prüfen und speichern
            duo_counts += check_combinations(numbers, target_numbers, 2)
            trio_counts += check_combinations(numbers, target_numbers, 3)
            quatro_counts += check_combinations(numbers, target_numbers, 4)

            # Prüfen, ob alle Zahlen mindestens einmal gezogen wurden
            if all(count >= 1 for count in counters.values()):
                all_numbers_drawn = True
                break

        # Beenden, wenn alle Zahlen mindestens einmal gezogen wurden
        if all_numbers_drawn:
            break

    # Rückgabe der Ergebnisse
    counters_str = ','.join([f"[{num}: {count}]" for num, count in counters.items()])
    counts_only_str = ','.join([str(count) for count in counters.values()])
    return draws_count, counters_str, counts_only_str, duo_counts, trio_counts, quatro_counts


# Hauptfunktion, die die Ergebnisse auch in eine CSV-Datei schreibt
def main():
    draws = read_draws(input_file_path)
    results = []

    for index in range(1, len(draws)):  # Überspringe die Kopfzeile
        draws_count, counters_str, counts_only_str, duo_counts, trio_counts, quatro_counts = process_draws_for_target(draws, index)
        results_row = draws[index] + [draws_count, counters_str, counts_only_str, duo_counts, trio_counts, quatro_counts]
        results.append(results_row)

    # Ergebnisse in eine neue CSV-Datei schreiben
    with open(output_file_path, mode='w', newline='') as file:
        csv_writer = csv.writer(file, delimiter=';')
        header = draws[0] + ['Anzahl Ziehungen', 'Zählungen', 'Counts', 'Duo', 'Trio', 'Quatro']
        csv_writer.writerow(header)
        for result_row in results:
            csv_writer.writerow(result_row)

if __name__ == "__main__":
    main()


