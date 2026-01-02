# funktion check_keno_numbers optimiert
# Funktion Vorprüfung_gegen_archiv optimiert 
#Parallel arbeit und workeranzahl fest gelegt
##Batch verarbeitung
## Checkspoint
#New Logik und optimiert 
#Break mit Strg + C und Zustand speichern hinzugefügt
#geänderte Logik bei Zahlengeneration und vorpruefung 
#############################

# Importieren der notwendigen Bibliotheken

import pandas as pd
from itertools import combinations
import os
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import signal
import sys


import pandas as pd
from itertools import combinations
import os
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import signal
import sys

# Globale Variablen für den Executor und Fortschritt
global_executor = None
global_checkpoint_pfad = ''
global_aktueller_fortschritt = 0
global_ergebnisse = []  # Für das Sammeln von Zwischenergebnissen

def speichere_checkpoint(datei_pfad, zustand):
    zustand_df = pd.DataFrame([zustand])
    zustand_df.to_csv(datei_pfad, index=False)

def speichere_ergebnisse(datei_pfad, ergebnisse, modus='a'):
    if not ergebnisse:
        return
    header = not os.path.exists(datei_pfad)
    ergebnisse_df = pd.DataFrame(ergebnisse)
    ergebnisse_df.to_csv(datei_pfad, mode=modus, index=False, header=header)

def lese_checkpoint(datei_pfad):
    if os.path.exists(datei_pfad):
        zustand_df = pd.read_csv(datei_pfad)
        return zustand_df.iloc[0].to_dict()
    return None

def generiere_oder_lese_kombinationen(datei_pfad):
    ziel_summen = {109, 119, 129, 139, 149, 159, 169, 179, 189, 199}
    if os.path.exists(datei_pfad):
        print("Lese Kombinationen aus Datei...")
        kombinationen_df = pd.read_csv(datei_pfad)
    else:
        print("Generiere neue Kombinationen...")
        alle_kombinationen = list(combinations(range(13, 51), 5))
        kombinationen_df = pd.DataFrame([kombi for kombi in tqdm(alle_kombinationen, desc="Generiere Kombinationen") if sum(kombi) in ziel_summen])
        kombinationen_df.to_csv(datei_pfad, index=False)
    return kombinationen_df

def batch_vorpruefung(kombinationen_batch, archiv_kombinationen):
    ergebnisse = []
    for kombi in kombinationen_batch:
        if all(len(set(kombi) & archiv_kombi) <= 5 for archiv_kombi in archiv_kombinationen):
            ergebnisse.append(kombi)
    return ergebnisse

def check_keno_parallel(kombinationen, keno_data):
    results = []
    for kombination in kombinationen:
        numbers_to_check = set(kombination)
        for index, row in keno_data.iterrows():
            drawn_numbers = set(row.loc['z1':'z20'].dropna().astype(int))
            matches = drawn_numbers.intersection(numbers_to_check)
            if len(matches) >= 5:                                       ################################### Werte Anpassen
                results.append({'Datum': row['Datum'], 'Kombination': kombination, 'Treffer': len(matches), 'Getroffene Zahlen': list(matches)})
    return results



def shutdown_executor():
    global global_executor
    if global_executor:
        global_executor.shutdown(wait=True)
        print("Alle Prozesse wurden sauber beendet.")
    speichere_ergebnisse(global_checkpoint_pfad.replace('checkpoint', 'ergebnisse'), global_ergebnisse, modus='a')

def signal_handler(sig, frame):
    global global_aktueller_fortschritt
    print('\nManueller Abbruch erkannt. Speichere aktuellen Fortschritt bei Batch Index:', global_aktueller_fortschritt)
    speichere_checkpoint(global_checkpoint_pfad, {'letzter_index': global_aktueller_fortschritt})
    shutdown_executor()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def vorpruefung_gegen_archiv_parallel(kombinationen_df, archiv_pfad, ergebnis_datei_pfad, checkpoint_pfad, batch_size=100):
    global global_checkpoint_pfad
    global global_aktueller_fortschritt
    global_checkpoint_pfad = checkpoint_pfad

    checkpoint = lese_checkpoint(checkpoint_pfad)
    start_index = checkpoint['letzter_index'] + 1 if checkpoint is not None else 0
    
    archiv_df = pd.read_csv(archiv_pfad, sep=';')
    archiv_kombinationen = [set(row.dropna().astype(int)) for index, row in archiv_df.iterrows()]
    
    kombinationen = kombinationen_df.to_numpy().tolist()
    kombinationen_batches = [kombinationen[i:i+batch_size] for i in range(start_index, len(kombinationen), batch_size)]
    
    ergebnisse = []
    with ProcessPoolExecutor(max_workers=4) as executor:   #############
        futures = {executor.submit(batch_vorpruefung, batch, archiv_kombinationen): i for i, batch in enumerate(kombinationen_batches, start=start_index)}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Vorprüfung gegen Archiv"):
            batch_index = futures[future]
            global_aktueller_fortschritt = batch_index
            ergebnisse.extend(future.result())
            speichere_checkpoint(checkpoint_pfad, {'letzter_index': batch_index})
    
    ergebnisse_df = pd.DataFrame(ergebnisse, columns=kombinationen_df.columns)
    ergebnisse_df.to_csv(ergebnis_datei_pfad, index=False)
    
    if os.path.exists(checkpoint_pfad):
        os.remove(checkpoint_pfad)
        
    return ergebnisse_df


def check_keno_numbers_parallel(csv_path, kombinationen_df, start_date, end_date, checkpoint_pfad, batch_size=10):########################
    global global_checkpoint_pfad
    global global_aktueller_fortschritt
    global_checkpoint_pfad = checkpoint_pfad

    keno_data = pd.read_csv(csv_path, sep=';', parse_dates=['Datum'], dayfirst=True)
    keno_data = keno_data[(keno_data['Datum'] >= pd.to_datetime(start_date)) & (keno_data['Datum'] <= pd.to_datetime(end_date))]

    checkpoint = lese_checkpoint(checkpoint_pfad)
    start_index = checkpoint['letzter_index'] + 1 if checkpoint is not None else 0
    
    kombinationen = kombinationen_df.to_numpy().tolist()
    kombinationen_batches = [kombinationen[i:i+batch_size] for i in range(start_index, len(kombinationen), batch_size)]

    results = []
    ergebnis_datei_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\ergebnisdatei.csv"  # Pfad zur Ergebnisdatei aktualisieren
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(check_keno_parallel, batch, keno_data): i for i, batch in enumerate(kombinationen_batches, start=start_index)}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Überprüfung gegen Keno"):
            batch_index = futures[future]
            global_aktueller_fortschritt = batch_index
            batch_results = future.result()
            results.extend(batch_results)
            # Speichert Zwischenergebnisse nach jedem Batch
            speichere_ergebnisse(ergebnis_datei_pfad, batch_results)
            speichere_checkpoint(checkpoint_pfad, {'letzter_index': batch_index})
    
    if os.path.exists(checkpoint_pfad):
        os.remove(checkpoint_pfad)
        
    return results
# def check_keno_numbers_parallel(csv_path, kombinationen_df, start_date, end_date, checkpoint_pfad, batch_size=10):  ##################
#     global global_checkpoint_pfad
#     global global_aktueller_fortschritt
#     global_checkpoint_pfad = checkpoint_pfad

#     keno_data = pd.read_csv(csv_path, sep=';', parse_dates=['Datum'], dayfirst=True)
#     keno_data = keno_data[(keno_data['Datum'] >= pd.to_datetime(start_date)) & (keno_data['Datum'] <= pd.to_datetime(end_date))]

#     checkpoint = lese_checkpoint(checkpoint_pfad)
#     start_index = checkpoint['letzter_index'] + 1 if checkpoint is not None else 0
    
#     kombinationen = kombinationen_df.to_numpy().tolist()
#     kombinationen_batches = [kombinationen[i:i+batch_size] for i in range(start_index, len(kombinationen), batch_size)]

#     results = []
#     with ProcessPoolExecutor(max_workers=6) as executor:   ############################
#         futures = {executor.submit(check_keno_parallel, batch, keno_data): i for i, batch in enumerate(kombinationen_batches, start=start_index)}
#         for future in tqdm(as_completed(futures), total=len(futures), desc="Überprüfung gegen Keno"):
#             batch_index = futures[future]
#             global_aktueller_fortschritt = batch_index
#             results.extend(future.result())
#             speichere_checkpoint(checkpoint_pfad, {'letzter_index': batch_index})
    
#     if os.path.exists(checkpoint_pfad):
#         os.remove(checkpoint_pfad)
        
#     return results

def hauptprogramm():
    global global_executor
    # Setup für global_executor
    global_executor = ProcessPoolExecutor(max_workers=5)

    kombinationen_datei_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\kombinationen.csv"
    archiv_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\EJ_archiv_bereinigt.csv"
    keno_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\KENO_2021.csv"
    vorpruefung_datei_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\vorpruefung_ergebnisse.csv"
    vorpruefung_checkpoint_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\vorpruefung_checkpoint.csv"
    keno_checkpoint_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\keno_checkpoint.csv"
    
    kombinationen_df = generiere_oder_lese_kombinationen(kombinationen_datei_pfad)
    kombinationen_nach_archiv_df = vorpruefung_gegen_archiv_parallel(kombinationen_df, archiv_pfad, vorpruefung_datei_pfad, vorpruefung_checkpoint_pfad)
    treffer_details = check_keno_numbers_parallel(keno_pfad, kombinationen_nach_archiv_df, '2021-01-01', '2021-12-31', keno_checkpoint_pfad)
    
    pd.DataFrame(treffer_details).to_csv("C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\Zahlen_treffer_Detail.csv", index=False)

if __name__ == '__main__':
    hauptprogramm()

































# Globale Variablen für den Executor und Fortschritt
global_executor = None
global_checkpoint_pfad = ''
global_aktueller_fortschritt = 0





def speichere_checkpoint(datei_pfad, zustand):
    zustand_df = pd.DataFrame([zustand])
    zustand_df.to_csv(datei_pfad, index=False)

def lese_checkpoint(datei_pfad):
    if os.path.exists(datei_pfad):
        zustand_df = pd.read_csv(datei_pfad)
        return zustand_df.iloc[0].to_dict()
    return None











def shutdown_executor():
    global global_executor
    if global_executor:
        global_executor.shutdown(wait=True)
        print("Alle Prozesse wurden sauber beendet.")

def signal_handler(sig, frame):
    global global_aktueller_fortschritt
    print('\nManueller Abbruch erkannt. Speichere aktuellen Fortschritt bei Batch Index:', global_aktueller_fortschritt)
    speichere_checkpoint(global_checkpoint_pfad, {'letzter_index': global_aktueller_fortschritt})
    shutdown_executor()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)













def hauptprogramm():
    global global_executor
    # Setup für global_executor
    global_executor = ProcessPoolExecutor(max_workers=4)

    kombinationen_datei_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\kombinationen.csv"
    archiv_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\EJ_archiv_bereinigt.csv"
    keno_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\KENO_2021.csv"
    vorpruefung_datei_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\vorpruefung_ergebnisse.csv"
    vorpruefung_checkpoint_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\vorpruefung_checkpoint.csv"
    keno_checkpoint_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\keno_checkpoint.csv"
    
    kombinationen_df = generiere_oder_lese_kombinationen(kombinationen_datei_pfad)
    kombinationen_nach_archiv_df = vorpruefung_gegen_archiv_parallel(kombinationen_df, archiv_pfad, vorpruefung_datei_pfad, vorpruefung_checkpoint_pfad)
    treffer_details = check_keno_numbers_parallel(keno_pfad, kombinationen_nach_archiv_df, '2021-01-01', '2021-12-31', keno_checkpoint_pfad)
    
    pd.DataFrame(treffer_details).to_csv("C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\Zahlen_treffer_Detail.csv", index=False)

if __name__ == '__main__':
    hauptprogramm()








































