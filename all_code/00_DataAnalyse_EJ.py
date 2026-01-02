##### Tage count bis jackpot
# Zählungen = wie oft kam eine Zahl bis jackpot 
#Counts = index von Zahlungen
#Dieses Skript analysiert Lottoziehungsdaten, speziell für den Eurojackpot, aus einer CSV-Datei und berechnet, 
# wie oft jede Zahl nach einer bestimmten Ziehung bis zu ihrem erneuten Erscheinen gezogen wurde. 
# Dann speichert es die Analyseergebnisse in einer neuen CSV-Datei.
# Hier ist eine detaillierte Erläuterung der einzelnen Komponenten des Skripts:

import csv

# Dateipfad der CSV-Datei
input_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\eurojackpo_bereinigt_for_GPT.csv"
output_file_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\DataAnalyse_EJ\\analyse_EJ_ziehungen_0.csv"

# Ziehungsdaten einlesen
def read_draws(file_path):
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file, delimiter=';')
        draws = [row for row in csv_reader]
    return draws

# Ziehungen für eine bestimmte Zielreihe verarbeiten
def process_draws_for_target(draws, target_index):
    target_numbers = set(map(int, draws[target_index][1:]))  # Zielzahlen der aktuellen Ziehung
    counters = {number: 0 for number in target_numbers}
    draws_count = 0

    for draw in draws[target_index + 1:]:
        if draw[0] == 'Datum':  # Überspringe die Kopfzeile
            continue
        numbers = list(map(int, draw[1:]))
        draws_count += 1
        for number in numbers:
            if number in target_numbers:
                counters[number] += 1
        if all(count >= 1 for count in counters.values()):
            break
    else:
        draws_count = 0  # Alle Zahlen wurden nicht mindestens einmal gezogen

    # Zähler in der gewünschten String-Form erstellen
    counters_str = ','.join([f"[{num}: {count}]" for num, count in counters.items()])
    counts_only_str = ','.join([str(count) for count in counters.values()])
    return draws_count, counters_str, counts_only_str

# Hauptfunktion, die die Ergebnisse auch in eine CSV-Datei schreibt
def main():
    draws = read_draws(input_file_path)
    results = []

    for index in range(1, len(draws)):  # Überspringe die Kopfzeile
        draws_count, counters_str, counts_only_str = process_draws_for_target(draws, index)
        results_row = draws[index] + [draws_count, counters_str, counts_only_str]
        results.append(results_row)

    # Ergebnisse in eine neue CSV-Datei schreiben
    with open(output_file_path, mode='w', newline='') as file:
        csv_writer = csv.writer(file, delimiter=';')
        header = draws[0] + ['Anzahl Ziehungen', 'Zählungen', 'Counts']
        csv_writer.writerow(header)
        for result_row in results:
            csv_writer.writerow(result_row)

if __name__ == "__main__":
    main()
