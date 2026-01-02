#v1 optimiert 

import pandas as pd
from itertools import combinations
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

# Funktion zum Filtern des Keno-Archivs nach Datum
def filter_archiv_nach_datum(archiv_pfad, start_datum, end_datum):
    try:
        archiv_df = pd.read_csv(archiv_pfad, sep=';', dayfirst=True)
        archiv_df['Datum'] = pd.to_datetime(archiv_df['Datum'], format='%d.%m.%Y')
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        return pd.DataFrame()

    gefiltertes_archiv_df = archiv_df[(archiv_df['Datum'] >= start_datum) & (archiv_df['Datum'] <= end_datum)]
    return gefiltertes_archiv_df

# Funktion zur Generierung eines Zahlenpools aus der CSV-Datei
def generiere_zahlenpool(datei_pfad, start_datum, end_datum):
    try:
        df = pd.read_csv(datei_pfad, sep=';', dayfirst=True)
        df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y')
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        return []

    gefilterte_df = df[(df['Datum'] >= start_datum) & (df['Datum'] <= end_datum)]
    einzigartige_zahlen = set()
    for zeile in gefilterte_df.itertuples(index=False):
        einzigartige_zahlen.update(int(wert) for wert in zeile[1:21] if pd.notnull(wert))

    return sorted(einzigartige_zahlen)

# Funktion zur Generierung aller möglichen 6-Zahlen-Kombinationen aus dem Zahlenpool
def generiere_kombinationen(zahlenpool, ziel_summe):
    return [kombi for kombi in combinations(zahlenpool, 6) if sum(kombi) >= ziel_summe]


# Funktion zur Überprüfung der Kombinationen gegen das gefilterte Keno-Archiv in Batches
def pruefe_kombination_batch(kombinationen, archiv_df):
    ergebnisse = []
    for kombi in kombinationen:
        vorkommen = sum(1 for index, zeile in archiv_df.iterrows() if set(kombi) <= set(map(int, zeile[1:21])))
        if vorkommen <= 1:
            ergebnisse.append(kombi)
    return ergebnisse

def pruefe_kombinationen(kombinationen, archiv_df):
    ergebnisse = []
    batch_size = 100  # Oder ein anderer Wert, der für deine Hardware geeignet ist

    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = []
        for i in range(0, len(kombinationen), batch_size):
            batch = kombinationen[i:i + batch_size]
            futures.append(executor.submit(pruefe_kombination_batch, batch, archiv_df))

        for future in tqdm(as_completed(futures), total=len(futures), desc='Batch-Verarbeitung'):
            ergebnisse.extend(future.result())

    return ergebnisse
# Funktion zur parallelen Zählung, wie oft jede Zahl in jeder Kombination vorkommt
def zaehle_kombination_batch(kombinationen, archiv_df):
    ergebnisse = []
    for kombi in kombinationen:
        zählung = {zahl: 0 for zahl in kombi}
        durchgelaufene_ziehungen = 0
        for zeile in archiv_df.itertuples(index=False):
            gezogene_zahlen = set(map(int, zeile[1:21]))
            durchgelaufene_ziehungen += 1
            for zahl in kombi:
                if zahl in gezogene_zahlen:
                    zählung[zahl] += 1
            if all(zahl > 0 for zahl in zählung.values()):
                break
        ergebnisse.append((kombi, durchgelaufene_ziehungen, zählung))
    return ergebnisse

def zaehle_kombinationen(kombinationen, archiv_df):
    ergebnisse = []
    batch_size = 100  # Anpassbar basierend auf der Leistung

    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = []
        for i in range(0, len(kombinationen), batch_size):
            batch = kombinationen[i:i + batch_size]
            futures.append(executor.submit(zaehle_kombination_batch, batch, archiv_df))

        for future in tqdm(as_completed(futures), total=len(futures), desc='Zähl-Verarbeitung'):
            try:
                ergebnisse.extend(future.result())
            except Exception as e:
                print(f"Ein Fehler ist in einem parallelen Prozess aufgetreten: {e}")

    # Speichern der Ergebnisse in einer CSV-Datei
    ergebnisse_df = pd.DataFrame(ergebnisse, columns=['Kombination', 'Anzahl der durchgelaufenen Ziehungen', 'Zählungen'])
    ergebnisse_df.to_csv("C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\00_Keno_6-Kombi_Analyse\\Final_CSV.csv", index=False)
    return ergebnisse_df

# Hauptfunktion, die alle Schritte integriert
def hauptfunktion(archiv_pfad, ziel_summe, start_datum, end_datum, start_datum_pool, end_datum_pool):
    zahlenpool = generiere_zahlenpool(archiv_pfad, start_datum_pool, end_datum_pool)
    kombinationen = generiere_kombinationen(zahlenpool, ziel_summe)
    gefiltertes_archiv_df = filter_archiv_nach_datum(archiv_pfad, start_datum, end_datum)
    gepruefte_kombinationen = pruefe_kombinationen(kombinationen, gefiltertes_archiv_df)
    zaehl_ergebnisse = zaehle_kombinationen(gepruefte_kombinationen, gefiltertes_archiv_df)
    return zaehl_ergebnisse

if __name__ == '__main__':
    archiv_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\00_Keno_6-Kombi_Analyse\\KENO_ab_2018 - Kopie.csv"
    ziel_summe = 1  # Beispielzielsumme
    start_datum = pd.to_datetime('2004-02-02')
    end_datum = pd.to_datetime('2024-03-06')
    start_datum_pool = pd.to_datetime('2024-03-01')
    end_datum_pool= pd.to_datetime('2024-03-06')

    hauptfunktion(archiv_pfad, ziel_summe, start_datum, end_datum, start_datum_pool, end_datum_pool)
