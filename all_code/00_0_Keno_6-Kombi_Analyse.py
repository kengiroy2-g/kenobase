

# Pfade zu den CSV-Dateien als Variablen, sodass sie leicht angepasst werden können
# ARCHIV_CSV_PFAD = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\00_Keno_6-Kombi_Analyse\\KENO_ab_2018 - Kopie.csv"
# ERGEBNISSE_CSV_PFAD = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\00_Keno_6-Kombi_Analyse\\final_ergebnisse.csv"

#'2024-02-27', '2024-02-27', '2024-02-27', '2023-03-03')

import pandas as pd
from itertools import combinations
import csv
from tqdm import tqdm

# Funktion zum Filtern des Keno-Archivs nach Datum
def filter_archiv_nach_datum(archiv_pfad, start_datum, end_datum):
    archiv_df = pd.read_csv(archiv_pfad, sep=';', dayfirst=True)
    archiv_df['Datum'] = pd.to_datetime(archiv_df['Datum'], format='%d.%m.%Y')
    gefiltertes_archiv_df = archiv_df[(archiv_df['Datum'] >= start_datum) & (archiv_df['Datum'] <= end_datum)]
    return gefiltertes_archiv_df

# Funktion zur Generierung eines Zahlenpools aus der CSV-Datei
# def generiere_zahlenpool(datei_pfad):
#     einzigartige_zahlen = set()
#     with open(datei_pfad, mode='r') as datei:
#         csv_reader = csv.reader(datei)
#         next(csv_reader)  # Überspringen der Kopfzeile
#         for zeile in csv_reader:
#             for wert in zeile[1:21]:  # Annahme, dass relevante Daten in Spalten 1 bis 20 stehen
#                 if wert:
#                     einzigartige_zahlen.add(int(wert))
#     return sorted(einzigartige_zahlen)
def generiere_zahlenpool(datei_pfad, start_datum, end_datum):
    # Einlesen der CSV-Datei
    df = pd.read_csv(datei_pfad, sep=';', dayfirst=True)
    
    # Umwandlung der Datumsspalte in datetime Format
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y')
    
    
    # Filterung der Daten nach dem angegebenen Datum
    gefilterte_df = df[(df['Datum'] >= start_datum) & (df['Datum'] <= end_datum)]

    # Initialisierung eines Sets, um einzigartige Zahlen zu speichern
    einzigartige_zahlen = set()

    # Durchlauf durch jede Zeile der gefilterten Daten, um die Zahlen zu extrahieren
    for index, zeile in gefilterte_df.iterrows():
        for wert in zeile[1:21]:  # Annahme, dass relevante Daten in Spalten 1 bis 20 stehen
            if pd.notnull(wert):  # Überprüfung, ob der Wert nicht NaN ist
                einzigartige_zahlen.add(int(wert))

    # Rückgabe der sortierten Liste der einzigartigen Zahlen
    return sorted(einzigartige_zahlen)


# Funktion zur Generierung aller möglichen 6-Zahlen-Kombinationen aus dem Zahlenpool
def generiere_kombinationen(zahlenpool, ziel_summe):
    return [kombi for kombi in combinations(zahlenpool, 6) if sum(kombi) >= ziel_summe]

# Funktion zur Überprüfung der Kombinationen gegen das gefilterte Keno-Archiv
def pruefe_kombinationen(kombinationen, archiv_df):
    ergebnisse = []
    for kombi in tqdm(kombinationen, desc='Überprüfe Kombinationen'):
        vorkommen = sum(1 for index, zeile in archiv_df.iterrows() if set(kombi) <= set(map(int, zeile[1:21])))
        if vorkommen <= 1:  # Behalten von Kombinationen, die höchstens einmal vorkommen
            ergebnisse.append(kombi)
    return ergebnisse

# Funktion zur Zählung, wie oft jede Zahl in jeder Kombination vorkommt
def zaehle_kombinationen(kombinationen, archiv_df):
    ergebnisse = []
    for kombi in tqdm(kombinationen, desc='Zähle Kombinationen'):
        zählung = {zahl: 0 for zahl in kombi}
        durchgelaufene_ziehungen = 0
        for index, zeile in archiv_df.iterrows():
            gezogene_zahlen = set(map(int, zeile[1:21]))
            durchgelaufene_ziehungen += 1
            for zahl in kombi:
                if zahl in gezogene_zahlen:
                    zählung[zahl] += 1
            if all(zahl > 0 for zahl in zählung.values()):
                break
        ergebnisse.append((kombi, durchgelaufene_ziehungen, zählung))
    
    # Speichern der Ergebnisse in einer CSV-Datei
    ergebnisse_df = pd.DataFrame(ergebnisse, columns=['Kombination', 'Anzahl der durchgelaufenen Ziehungen', 'Zählungen'])
    ergebnisse_df.to_csv("C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\00_Keno_6-Kombi_Analyse\\Final_CSV.csv", index=False)
    return ergebnisse_df

# Hauptfunktion, die alle Schritte integriert
def hauptfunktion(archiv_pfad, ziel_summe, start_datum, end_datum, start_datum_pool, end_datum_pool):
    # Zahlenpool generieren
    zahlenpool = generiere_zahlenpool(archiv_pfad, start_datum_pool, end_datum_pool)
    
    # Kombinationen generieren
    kombinationen = generiere_kombinationen(zahlenpool, ziel_summe)
    
    # Archiv nach Datum filtern
    gefiltertes_archiv_df = filter_archiv_nach_datum(archiv_pfad, start_datum, end_datum)
    
    # Kombinationen überprüfen
    gepruefte_kombinationen = pruefe_kombinationen(kombinationen, gefiltertes_archiv_df)
    
    # Kombinationen zählen
    zaehl_ergebnisse = zaehle_kombinationen(gepruefte_kombinationen, gefiltertes_archiv_df)
    
    return zaehl_ergebnisse

# Beispielhafte Ausführung der Hauptfunktion
archiv_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\00_Keno_6-Kombi_Analyse\\KENO_ab_2018 - Kopie.csv"
ziel_summe = 1  # Beispielzielsumme
start_datum = pd.to_datetime('2020-01-01')
end_datum = pd.to_datetime('2024-03-03')
start_datum_pool = pd.to_datetime('2024-02-27')
end_datum_pool= pd.to_datetime('2024-02-27')

hauptfunktion(archiv_pfad, ziel_summe, start_datum, end_datum, start_datum_pool, end_datum_pool)
