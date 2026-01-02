#v1 optimiert 
#Feld Datum hinzugefügt
# Den Zahlenpool aus der CSV-Datei generieren, indem sie die eindeutigen Zahlen extrahiert.
# Alle möglichen 6-Zahlen-Kombinationen aus dem Zahlenpool generieren, die eine bestimmte Zielsumme erfüllen.
# Das Keno-Archiv nach einem bestimmten Datum filtern, um nur relevante Datensätze zu betrachten.
# Die generierten Kombinationen gegen das gefilterte Archiv überprüfen, um zu sehen, welche Kombinationen höchstens einmal vorkommen.
# Die Zählung für jede Kombination durchführen, um zu ermitteln, wie oft jede Zahl in der Kombination erscheint.#

from collections import Counter
from datetime import datetime
import pandas as pd
from itertools import combinations
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed



# Hilfsfunktion zur Überprüfung der Zehnergruppen-Bedingung
def max_zwei_pro_zehnergruppe(kombi):
    # Erstelle ein Wörterbuch, das die Zehnergruppe als Schlüssel hat
    zehnergruppen = {}
    for zahl in kombi:
        zehner = zahl // 10  # Zehnergruppe finden
        if zehner not in zehnergruppen:
            zehnergruppen[zehner] = 0
        zehnergruppen[zehner] += 1
        
        # Wenn irgendeine Gruppe mehr als 2 Zahlen enthält, ist die Kombination nicht gültig
        if zehnergruppen[zehner] > 2:
            return False
    return True


def filter_archiv_nach_datum_optimiert(archiv_df, start_datum, end_datum):
    gefiltertes_archiv_df = archiv_df[(archiv_df['Datum'] >= start_datum) & (archiv_df['Datum'] <= end_datum)]
    return gefiltertes_archiv_df

def generiere_zahlenpool_optimiert(archiv_df, start_datum, end_datum):
    gefilterte_df = archiv_df[(archiv_df['Datum'] >= start_datum) & (archiv_df['Datum'] <= end_datum)]
    einzigartige_zahlen = set(gefilterte_df.iloc[:, 1:21].stack().astype(int))
    print("Einzigartige Zahlen:", sorted(einzigartige_zahlen))
    return sorted(einzigartige_zahlen)

# Erweiterte Funktion generiere_kombinationen
def generiere_kombinationen(zahlenpool, ziel_summe):
    # Erstellen einer leeren Liste für die gültigen Kombinationen
    gültige_kombinationen = []

    # Erstellen aller möglichen 6er-Kombinationen und Anzeigen des Fortschritts mit tqdm
    alle_kombinationen = list(combinations(zahlenpool, 6))
    for kombi in tqdm(alle_kombinationen, desc="Generiere Kombinationen"):
        if sum(kombi) >= ziel_summe and max_zwei_pro_zehnergruppe(kombi):
            gültige_kombinationen.append(kombi)

    return gültige_kombinationen

def pruefe_kombination_batch(kombinationen, archiv_df):
    ergebnisse = []
    for kombi in kombinationen:
        vorkommen = archiv_df.iloc[:, 1:21].apply(lambda row: set(kombi) <= set(row.dropna().astype(int)), axis=1).sum()
        if vorkommen == 1:##############################################################################################
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


# Die Funktionen max_zwei_pro_zehnergruppe, filter_archiv_nach_datum_optimiert, generiere_zahlenpool_optimiert, generiere_kombinationen, pruefe_kombination_batch und pruefe_kombinationen bleiben unverändert.
def zaehle_kombination_batch(kombinationen, archiv_df):
    ergebnisse = []
    standard_datum = datetime(2004, 1, 1)
    for kombi in kombinationen:
        zählung = {zahl: 0 for zahl in kombi}
        durchgelaufene_ziehungen = 0
        kombi_datum = standard_datum
        duos, trios, quatro = set(), set(), set()

        for index, row in archiv_df.iterrows():
            gezogene_zahlen = set(row[1:21].dropna().astype(int))
            durchgelaufene_ziehungen += 1
            kombi_set = set(kombi)
            aktuelle_uebereinstimmung = kombi_set.intersection(gezogene_zahlen)

            # Update der Zählung für jede Zahl in der Kombination
            for zahl in aktuelle_uebereinstimmung:
                zählung[zahl] += 1

            # Update von Duos, Trios und Quatros nur, wenn nicht alle Zahlen schon mindestens einmal erschienen sind
            if not all(zahl > 0 for zahl in zählung.values()):
                if len(aktuelle_uebereinstimmung) == 2:
                    duos.update(combinations(aktuelle_uebereinstimmung, 2))
                if len(aktuelle_uebereinstimmung) == 3:
                    trios.update(combinations(aktuelle_uebereinstimmung, 3))
                if len(aktuelle_uebereinstimmung) == 4:
                    quatro.update(aktuelle_uebereinstimmung)

            # Sobald alle Zahlen mindestens einmal erschienen sind, stoppe die Durchläufe
            if all(zahl > 0 for zahl in zählung.values()):
                break

        counter_string = ','.join(str(zählung[zahl]) for zahl in kombi)
        duos_string = ';'.join(map(str, duos))
        trios_string = ';'.join(map(str, trios))
        quatro_string = ';'.join(map(str, quatro))
        ergebnisse.append((kombi, durchgelaufene_ziehungen, zählung, counter_string, kombi_datum.strftime('%d.%m.%Y'), duos_string, trios_string, quatro_string))
    return ergebnisse


def zaehle_kombinationen(kombinationen, archiv_df):
    ergebnisse = []
    batch_size = 100  # Anpassbar basierend auf der Leistung

    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(zaehle_kombination_batch, kombinationen[i:i + batch_size], archiv_df) for i in range(0, len(kombinationen), batch_size)]
        for future in tqdm(as_completed(futures), total=len(futures), desc='Zähl-Verarbeitung'):
            try:
                ergebnisse.extend(future.result())
            except Exception as e:
                print(f"Ein Fehler ist in einem parallelen Prozess aufgetreten: {e}")

    # Aktualisiere die Spaltennamen, um alle 8 Spalten zu berücksichtigen
    ergebnisse_df = pd.DataFrame(ergebnisse, columns=['Kombination', 'Anzahl der durchgelaufenen Ziehungen', 'Zählungen', 'Counter', 'Datum', 'Duos', 'Trios', 'Quatros'])
    ergebnisse_df.to_csv("C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\00_Keno_6-Kombi_Analyse\\ergebnisse_v5_copy.csv", index=False)
    return ergebnisse_df

# Die Funktion hauptfunktion_optimiert bleibt unverändert.



# Hauptfunktion, die alle Schritte integriert
def hauptfunktion_optimiert(archiv_pfad, ziel_summe, start_datum, end_datum, start_datum_pool, end_datum_pool):
    archiv_df = pd.read_csv(archiv_pfad, sep=';', dayfirst=True)
    archiv_df['Datum'] = pd.to_datetime(archiv_df['Datum'], format='%d.%m.%Y')

    gefiltertes_archiv_df = filter_archiv_nach_datum_optimiert(archiv_df, start_datum, end_datum)
    zahlenpool = {1, 3, 6, 9, 10, 12, 14, 17, 18, 20, 21, 24, 25, 26, 29, 30, 33, 34, 36, 38, 39, 40, 42, 44, 45, 48, 46} #generiere_zahlenpool_optimiert(gefiltertes_archiv_df, start_datum_pool, end_datum_pool)
    kombinationen = generiere_kombinationen(zahlenpool, ziel_summe)
    gepruefte_kombinationen = pruefe_kombinationen(kombinationen, gefiltertes_archiv_df)
    zaehl_ergebnisse = zaehle_kombinationen(gepruefte_kombinationen, gefiltertes_archiv_df)

    return zaehl_ergebnisse

if __name__ == '__main__':
    archiv_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\00_Keno_6-Kombi_Analyse\\KENO_ab_2018 - Kopie.csv"
    ziel_summe = 1  # Beispielzielsumme
    start_datum = pd.to_datetime('2004-02-02')
    end_datum = pd.to_datetime('2024-03-09')
    start_datum_pool = pd.to_datetime('2024-03-01')
    end_datum_pool= pd.to_datetime('2024-03-09')

    # Pfad- und Datumseinstellungen bleiben unverändert.
    hauptfunktion_optimiert(archiv_pfad, ziel_summe, start_datum, end_datum, start_datum_pool, end_datum_pool)




#{1, 4, 5, 7, 12, 15, 18, 19, 20, 25, 33, 34, 37, 38, 39, 40, 42, 43, 44, 45, 47} #nicht gemeinsamen zahlen 
    #{3, 6, 9, 10, 14, 17, 21, 24, 26, 29, 30, 36, 46, 48} gemeinsamen Zahlen  ##############################################################################################
    
    #{1, 3, 6, 9, 10, 12, 14, 17, 18, 20, 21, 24, 25, 26, 29, 30, 33, 34, 36, 38, 39, 40, 42, 44, 45, 48, 46} # Zahlen aus keno analyse
    #{3,4,5,6,7,9,10,14,15,17,19,21,24,26,29,30,36,37,43,46,47,48} Zahlen aus EJ anylyse
    