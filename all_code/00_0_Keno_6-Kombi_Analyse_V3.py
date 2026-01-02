#v1 optimiert 

import pandas as pd
from itertools import combinations
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

def filter_archiv_nach_datum_optimiert(archiv_df, start_datum, end_datum):
    gefiltertes_archiv_df = archiv_df[(archiv_df['Datum'] >= start_datum) & (archiv_df['Datum'] <= end_datum)]
    return gefiltertes_archiv_df

def generiere_zahlenpool_optimiert(archiv_df, start_datum, end_datum):
    gefilterte_df = archiv_df[(archiv_df['Datum'] >= start_datum) & (archiv_df['Datum'] <= end_datum)]
    einzigartige_zahlen = set(gefilterte_df.iloc[:, 1:21].stack().astype(int))
    print("Einzigartige Zahlen:", sorted(einzigartige_zahlen))
    return sorted(einzigartige_zahlen)

def generiere_kombinationen(zahlenpool, ziel_summe):
    return [kombi for kombi in combinations(zahlenpool, 6) if sum(kombi) >= ziel_summe]

def pruefe_kombination_batch(kombinationen, archiv_df):
    ergebnisse = []
    for kombi in kombinationen:
        vorkommen = archiv_df.iloc[:, 1:21].apply(lambda row: set(kombi) <= set(row.dropna().astype(int)), axis=1).sum()
        if vorkommen <= 1:
            ergebnisse.append(kombi)
    return ergebnisse

def pruefe_kombinationen(kombinationen, archiv_df):
    ergebnisse = []
    batch_size = 100  # Oder ein anderer Wert, der für deine Hardware geeignet ist

    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(pruefe_kombination_batch, kombinationen[i:i + batch_size], archiv_df) for i in range(0, len(kombinationen), batch_size)]
        for future in tqdm(as_completed(futures), total=len(futures), desc='Batch-Verarbeitung'):
            ergebnisse.extend(future.result())

    return ergebnisse

def zaehle_kombination_batch(kombinationen, archiv_df):
    ergebnisse = []
    for kombi in kombinationen:
        zählung = {zahl: 0 for zahl in kombi}
        durchgelaufene_ziehungen = 0
        for index, row in archiv_df.iterrows():
            gezogene_zahlen = set(row[1:21].dropna().astype(int))
            durchgelaufene_ziehungen += 1
            for zahl in kombi:
                if zahl in gezogene_zahlen:
                    zählung[zahl] += 1
            if all(zahl > 0 for zahl in zählung.values()):
                break
        counter_string = ','.join(str(zählung[zahl]) for zahl in kombi)
        ergebnisse.append((kombi, durchgelaufene_ziehungen, zählung, counter_string))
    return ergebnisse

# Stellen Sie sicher, dass Sie diese Funktion entsprechend den obigen Änderungen aufrufen.


# def zaehle_kombination_batch(kombinationen, archiv_df):
#     ergebnisse = []
#     for kombi in kombinationen:
#         zählung = {zahl: 0 for zahl in kombi}
#         durchgelaufene_ziehungen = 0
#         for index, row in archiv_df.iterrows():
#             gezogene_zahlen = set(row[1:21].dropna().astype(int))
#             durchgelaufene_ziehungen += 1
#             for zahl in kombi:
#                 if zahl in gezogene_zahlen:
#                     zählung[zahl] += 1
#             if all(zahl > 0 for zahl in zählung.values()):
#                 break
#         ergebnisse.append((kombi, durchgelaufene_ziehungen, zählung))
#     return ergebnisse

def zaehle_kombinationen(kombinationen, archiv_df):
    ergebnisse = []
    batch_size = 100  # Anpassbar basierend auf der Leistung

    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(zaehle_kombination_batch, kombinationen[i:i + batch_size], archiv_df) for i in range(0, len(kombinationen), batch_size)]
        for future in tqdm(as_completed(futures), total=len(futures), desc='Zähl-Verarbeitung'):
            try:
                result = future.result()
                if result and len(result[0]) != 4:  # Überprüft das erste Tupel auf die erwartete Länge
                    raise ValueError("Expected tuples with 4 elements. Got: {}".format(result[0]))
                ergebnisse.extend(result)
            except Exception as e:
                 print(f"Ein Fehler ist in einem parallelen Prozess aufgetreten: {e}")

        # for future in tqdm(as_completed(futures), total=len(futures), desc='Zähl-Verarbeitung'):
        #     try:
        #         ergebnisse.extend(future.result())
        #     except Exception as e:
        #         print(f"Ein Fehler ist in einem parallelen Prozess aufgetreten: {e}")

    # Erstellen eines DataFrames mit einer zusätzlichen Spalte für den Counter
    ergebnisse_df = pd.DataFrame(ergebnisse, columns=['Kombination', 'Anzahl der durchgelaufenen Ziehungen', 'Zählungen', 'Counter'])
    ergebnisse_df.to_csv("C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\00_Keno_6-Kombi_Analyse\\ergebnisse_v3.csv", index=False)
    return ergebnisse_df

# def zaehle_kombinationen(kombinationen, archiv_df):
#     ergebnisse = []
#     batch_size = 100  # Anpassbar basierend auf der Leistung

#     with ProcessPoolExecutor(max_workers=4) as executor:
#         futures = [executor.submit(zaehle_kombination_batch, kombinationen[i:i + batch_size], archiv_df) for i in range(0, len(kombinationen), batch_size)]
#         for future in tqdm(as_completed(futures), total=len(futures), desc='Zähl-Verarbeitung'):
#             try:
#                 ergebnisse.extend(future.result())
#             except Exception as e:
#                 print(f"Ein Fehler ist in einem parallelen Prozess aufgetreten: {e}")

#     ergebnisse_df = pd.DataFrame(ergebnisse, columns=['Kombination', 'Anzahl der durchgelaufenen Ziehungen', 'Zählungen'])
#     ergebnisse_df.to_csv("C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\00_Keno_6-Kombi_Analyse\\ergebnisse.csv", index=False)
#     return ergebnisse_df

# Hauptfunktion, die alle Schritte integriert
def hauptfunktion_optimiert(archiv_pfad, ziel_summe, start_datum, end_datum, start_datum_pool, end_datum_pool):
    archiv_df = pd.read_csv(archiv_pfad, sep=';', dayfirst=True)
    archiv_df['Datum'] = pd.to_datetime(archiv_df['Datum'], format='%d.%m.%Y')

    gefiltertes_archiv_df = filter_archiv_nach_datum_optimiert(archiv_df, start_datum, end_datum)
    zahlenpool = generiere_zahlenpool_optimiert(gefiltertes_archiv_df, start_datum_pool, end_datum_pool) # {3, 6, 9, 10, 14, 17, 21, 24, 26, 29, 30, 36, 46, 48}
    kombinationen = generiere_kombinationen(zahlenpool, ziel_summe)
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

    hauptfunktion_optimiert(archiv_pfad, ziel_summe, start_datum, end_datum, start_datum_pool, end_datum_pool)


#{1, 4, 5, 7, 12, 15, 18, 19, 20, 25, 33, 34, 37, 38, 39, 40, 42, 43, 44, 45, 47} #nicht gemeinsamen zahlen 
    #{3, 6, 9, 10, 14, 17, 21, 24, 26, 29, 30, 36, 46, 48} gemeinsamen Zahlen  ##############################################################################################
    
    #{1, 3, 6, 9, 10, 12, 14, 17, 18, 20, 21, 24, 25, 26, 29, 30, 33, 34, 36, 38, 39, 40, 42, 44, 45, 48, 46} # Zahlen aus keno analyse
    #{3,4,5,6,7,9,10,14,15,17,19,21,24,26,29,30,36,37,43,46,47,48} Zahlen aus EJ anylyse
    