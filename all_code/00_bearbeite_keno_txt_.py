import pandas as pd
import re

def daten_von_txt_zu_csv(txt_dateipfad, csv_dateipfad):
    bearbeitete_daten = []
    vorherige_zahlen = set()

    with open(txt_dateipfad, 'r') as file:
        for line in file:
            # Daten extrahieren mit Regex
            match = re.match(r"Datum: ([\d\.]+), Anzahl Treffer: (\d+), Treffer-Zahlen: {(.+)}", line.strip())
            if match:
                datum, anzahl_treffer, treffer_zahlen_str = match.groups()
                treffer_zahlen = sorted([int(zahl) for zahl in treffer_zahlen_str.split(", ")])
                
                # Wiederholte Zahlen identifizieren
                wiederholte_zahlen = vorherige_zahlen.intersection(treffer_zahlen)
                anzahl_wiederholte_zahlen = len(wiederholte_zahlen)
                vorherige_zahlen = set(treffer_zahlen)
                
                # Daten für den DataFrame vorbereiten
                zeile = {
                    "Datum": datum,
                    "Anzahl Treffer": anzahl_treffer,
                    **{f"z{i+1}": treffer_zahlen[i] if i < len(treffer_zahlen) else '' for i in range(12)},
                    "Anzahl-wiederholte-zahlen": anzahl_wiederholte_zahlen,
                    "Wiederholte Zahlen": ', '.join(map(str, sorted(wiederholte_zahlen))) if wiederholte_zahlen else ''
                }
                
                bearbeitete_daten.append(zeile)

    # DataFrame erstellen
    df = pd.DataFrame(bearbeitete_daten)

    # CSV-Datei speichern
    df.to_csv(csv_dateipfad, index=False, encoding='utf-8')

# Pfade für die TXT- und CSV-Dateien festlegen


# Pfade für die TXT- und CSV-Dateien festlegen
txt_dateipfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\keno_10k.txt"
csv_dateipfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\KENO_10K.csv"


# Funktion ausführen
daten_von_txt_zu_csv(txt_dateipfad, csv_dateipfad)

print(f"Die bearbeiteten Daten wurden erfolgreich von '{txt_dateipfad}' nach '{csv_dateipfad}' konvertiert.")



