import csv

input_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\lottozahlen_archiv.csv"
output_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Lotto_archiv_bereinigt.csv"

def keep_until_second_comma(row):
    # Findet das zweite Komma im zusammengesetzten String aus beiden Zellen
    combined_string = ','.join(row[:2])  # Verbindet die ersten beiden Zellen
    comma_index = combined_string.find(',', combined_string.find(',') + 1)
    return combined_string[:comma_index] if comma_index != -1 else combined_string

with open(input_path, mode='r', newline='', encoding='utf-8') as infile, \
     open(output_path, mode='w', newline='', encoding='utf-8') as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    for row in reader:
        cleaned_data = keep_until_second_comma(row)
        writer.writerow([cleaned_data])

print("Datenbereinigung abgeschlossen. Bereinigte Datei gespeichert unter:", output_path)
