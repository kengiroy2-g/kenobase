import csv

# Pfad zur CSV-Datei
dateipfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\10-9_CheckNumbers_z120.csv"

# Ein Set, um alle einzigartigen Zahlen zu speichern
einzigartige_zahlen = set()

# Öffnen und Einlesen der CSV-Datei
einzigartige_zahlen = set()  # Initialisieren des Sets, um einzigartige Zahlen zu speichern
gespeicherte_zahlen_anzahl = 0  # Initialisieren des Zählers für die gespeicherten Zahlen

with open(dateipfad, mode='r', encoding='utf-8') as datei:
    csv_reader = csv.reader(datei)
    next(csv_reader)  # Überspringen der Kopfzeile

    for zeile in csv_reader:
        zahlen = []
        for wert in zeile[1:21]:  # Annahme, dass die relevanten Daten in den Spalten 1 bis 20 stehen
            if wert:  # Überprüfen, ob der Wert nicht leer ist
                try:
                    zahlen.append(int(wert))  # Versuchen, den Wert in Integer umzuwandeln
                except ValueError:
                    # Hier können Sie entscheiden, was zu tun ist, wenn der Wert nicht in einen Integer umgewandelt werden kann.
                    pass
        
        vorherige_anzahl = len(einzigartige_zahlen)  # Anzahl der einzigartigen Zahlen vor dem Update
        einzigartige_zahlen.update(zahlen)
        nachherige_anzahl = len(einzigartige_zahlen)  # Anzahl der einzigartigen Zahlen nach dem Update
        gespeicherte_zahlen_anzahl += nachherige_anzahl - vorherige_anzahl  # Aktualisieren der Gesamtzahl der gespeicherten Zahlen

# Ausgabe der Gesamtzahl der gespeicherten Zahlen
print(f"Gesamtzahl der gespeicherten einzigartigen Zahlen: {gespeicherte_zahlen_anzahl}")

        # Hinzufügen der Zahlen zum Set, um Duplikate zu entfernen
        # Stellen Sie sicher, dass 'einzigartige_zahlen' vor dieser Schleife initialisiert wurde



# Umwandlung des Sets in eine Liste und Sortierung
sortierte_einzigartige_zahlen = sorted(einzigartige_zahlen)

# Ausgabe der sortierten Liste einzigartiger Zahlen
print(sortierte_einzigartige_zahlen)
