import csv
from datetime import datetime

input_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Lotto_archiv_bereinigt.csv"
output_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Lotto_archiv_umformatiert.csv"

def format_row(row):
    # Teilt die Zeile an der Stelle des zweiten Kommas
    date_str, numbers_str = row.split(',', 1)

    # Umwandeln des ISO 8601 Datumformats in ein DD.MM.YYYY Format
    date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    formatted_date = date_obj.strftime("%d.%m.%Y")

    # Ersetzen der Bindestriche durch Kommas in der Zahlenliste
    formatted_numbers = numbers_str.replace('-', ',')

    # Zusammenführen des umformatierten Datums und der Zahlenliste und Hinzufügen von zwei Kommas am Ende
    return f"{formatted_date},{formatted_numbers},,"

with open(input_path, mode='r', newline='', encoding='utf-8') as infile, \
     open(output_path, mode='w', newline='', encoding='utf-8') as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    for row in reader:
        # Formatieren der Zeile, bevor sie geschrieben wird
        formatted_data = format_row(row[0])
        writer.writerow([formatted_data])

print("Datenbereinigung, Umformatierung und Ergänzung abgeschlossen. Umformatierte Datei gespeichert unter:", output_path)
