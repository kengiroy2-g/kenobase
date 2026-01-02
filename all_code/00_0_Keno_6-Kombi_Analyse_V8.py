#v1 optimiert 
#Feld Datum hinzugefügt
# Den Zahlenpool aus der CSV-Datei generieren, indem sie die eindeutigen Zahlen extrahiert.
# Alle möglichen 6-Zahlen-Kombinationen aus dem Zahlenpool generieren, die eine bestimmte Zielsumme erfüllen.
# Das Keno-Archiv nach einem bestimmten Datum filtern, um nur relevante Datensätze zu betrachten.
# Die generierten Kombinationen gegen das gefilterte Archiv überprüfen, um zu sehen, welche Kombinationen höchstens einmal vorkommen.
# Die Zählung für jede Kombination durchführen, um zu ermitteln, wie oft jede Zahl in der Kombination erscheint.#
# 
# Lafunktion zaehle_kombination_batch a ete modifie de telle sorte que elle calcule les index a partir de le la date ou la combinaison est survenu pour la premiere fois
# Duos,trios,quatros werden falsch berechnet ,korrektur in v7-1

#####################
#v8
 


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

def generiere_zahlenpool_optimiert(archiv_pfad, start_datum, end_datum):
    # Daten aus der CSV-Datei laden
    df = pd.read_csv(archiv_pfad, delimiter=';', usecols=[i for i in range(21)], parse_dates=["Datum"])
    
    # Einteilung der Daten in drei Zeiträume mit jeweils 10 Ziehungen
    periods = {
        'Zeitraum_1': df.iloc[0:10],
        'Zeitraum_2': df.iloc[10:20],
        'Zeitraum_3': df.iloc[20:30]
    }

    # Häufigkeitsanalyse pro Zeitraum
    frequency_analysis = {}
    for period, data in periods.items():
        counts = data.iloc[:, 1:].apply(pd.Series.value_counts, axis=1).sum(axis=0).sort_values(ascending=False)
        frequency_analysis[period] = counts

    # Gesamthäufigkeitsanalyse
    all_periods_data = pd.concat(periods.values())
    total_counts = all_periods_data.iloc[:, 1:].apply(pd.Series.value_counts, axis=1).sum(axis=0).sort_values(ascending=False)

    # Ermittlung der Top 11 Zahlen pro Zeitraum
    top_11_each_period = {period: freq.head(11) for period, freq in frequency_analysis.items()}

    # Schnittmengen zwischen den Top 11 Listen jedes Zeitraums und den Top 20 der Gesamtanalyse
    top_11_20_intersections = {
        period: freq.index.intersection(total_counts.head(20).index) 
        for period, freq in top_11_each_period.items()
    }

    # Kombinieren der Schnittmengen ohne Duplikate
    combined_top_11_20_intersection = set().union(*top_11_20_intersections.values())

    # Kombinierte Schnittmenge aller paarweisen Top-11 der Zeiträume
    pairwise_top_11_intersection = set().union(
        set(top_11_each_period['Zeitraum_1'].index).intersection(top_11_each_period['Zeitraum_2'].index),
        set(top_11_each_period['Zeitraum_1'].index).intersection(top_11_each_period['Zeitraum_3'].index),
        set(top_11_each_period['Zeitraum_2'].index).intersection(top_11_each_period['Zeitraum_3'].index)
    )
    print("Einzigartige Zahlen:", sorted(combined_top_11_20_intersection))
    return combined_top_11_20_intersection


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



def zaehle_kombination_batch(kombinationen, archiv_liste):
    ergebnisse = []
    standard_datum = datetime(2004, 1, 1)

    for kombi in kombinationen:
        erscheinungsdaten = [datum for datum, gezogene_zahlen in archiv_liste if set(kombi) <= gezogene_zahlen]
        
        if not erscheinungsdaten:  # Wenn die Kombination nie vollständig erschienen ist
            erscheinungsdaten = [standard_datum]  # Verwende das Standarddatum für die Zählung

        for kombi_datum in erscheinungsdaten:
            durchgelaufene_ziehungen = 0
            zählung = Counter({zahl: 0 for zahl in kombi})
            duos, trios, quatro = set(), set(), set()
            

            for datum, gezogene_zahlen in archiv_liste:
                if kombi_datum != standard_datum and pd.to_datetime(datum) >= kombi_datum:
                    continue
                # if pd.to_datetime(datum) >= kombi_datum:
                #     continue  # Ziehungen nach dem Erscheinungsdatum überspringen
                
                durchgelaufene_ziehungen += 1
                aktuelle_uebereinstimmung = set(kombi).intersection(gezogene_zahlen)
                zählung.update(aktuelle_uebereinstimmung)

                # Duos, Trios und Quatros ermitteln
                if len(aktuelle_uebereinstimmung) == 4:
                    quatro.update(combinations(aktuelle_uebereinstimmung, 4))
                elif len(aktuelle_uebereinstimmung) == 3:
                    trios.update(combinations(aktuelle_uebereinstimmung, 3))
                elif len(aktuelle_uebereinstimmung) == 2:
                    duos.update(combinations(aktuelle_uebereinstimmung, 2))

                if all(zahl > 0 for zahl in zählung.values()):
                    break  # Stoppen, wenn alle Zahlen mindestens einmal gezählt wurden

            counter_string = ','.join(str(zählung[zahl]) for zahl in kombi)
            duos_string = ';'.join(map(str, duos)) if duos else '(0,0)'
            trios_string = ';'.join(map(str, trios)) if trios else '(0,0,0)'
            quatro_string = ';'.join(map(str, quatro)) if quatro else '(0,0,0,0)'


            ergebnisse.append((kombi, kombi_datum.strftime('%d.%m.%Y'), durchgelaufene_ziehungen, zählung, counter_string, duos_string, trios_string, quatro_string))

    return ergebnisse


    

def zaehle_kombinationen(kombinationen, archiv_df):
    ergebnisse = []
    batch_size = 100  # Anpassbar basierend auf der Leistung

    archiv_liste = [(row['Datum'], set(row.iloc[1:21].dropna().astype(int))) for index, row in archiv_df.iterrows()]

    with ProcessPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(zaehle_kombination_batch, kombinationen[i:i + batch_size], archiv_liste) for i in range(0, len(kombinationen), batch_size)]
        for future in tqdm(as_completed(futures), total=len(futures), desc='Zähl-Verarbeitung'):
            try:
                ergebnisse.extend(future.result())
            except Exception as e:
                print(f"Ein Fehler ist aufgetreten: {e}")

    ergebnisse_df = pd.DataFrame(ergebnisse, columns=['Kombination', 'Datum','Anzahl Ziehungen', 'Counter_Index','Index', 'Duos', 'Trios', 'Quatros'])
    ergebnisse_df.to_csv("C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\00_Keno_6-Kombi_Analyse\\ergebnisse_v6-22.csv", sep=';', encoding='utf-8', index=False)
    return ergebnisse_df


# Hauptfunktion, die alle Schritte integriert
def hauptfunktion_optimiert(archiv_pfad, ziel_summe, start_datum, end_datum, start_datum_pool, end_datum_pool):
    archiv_df = pd.read_csv(archiv_pfad, sep=';', dayfirst=True)
    archiv_df['Datum'] = pd.to_datetime(archiv_df['Datum'], format='%d.%m.%Y')

    gefiltertes_archiv_df = filter_archiv_nach_datum_optimiert(archiv_df, start_datum, end_datum)
    zahlenpool = generiere_zahlenpool_optimiert(archiv_pfad , start_datum_pool, end_datum_pool)
    kombinationen = generiere_kombinationen(zahlenpool, ziel_summe)
    gepruefte_kombinationen = kombinationen
    zaehl_ergebnisse = zaehle_kombinationen(gepruefte_kombinationen, gefiltertes_archiv_df)

    return zaehl_ergebnisse

if __name__ == '__main__':
    archiv_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\00_Keno_6-Kombi_Analyse\\KENO_ab_2018 - Kopie.csv"
    ziel_summe = 1  # Beispielzielsumme
    start_datum = pd.to_datetime('2004-02-02')
    end_datum = pd.to_datetime('2024-04-01')
    start_datum_pool = pd.to_datetime('2024-03-01')
    end_datum_pool= pd.to_datetime('2024-04-01')

    # Pfad- und Datumseinstellungen bleiben unverändert.
    hauptfunktion_optimiert(archiv_pfad, ziel_summe, start_datum, end_datum, start_datum_pool, end_datum_pool)




#{1, 4, 5, 7, 12, 15, 18, 19, 20, 25, 33, 34, 37, 38, 39, 40, 42, 43, 44, 45, 47} #nicht gemeinsamen zahlen 
    #{3, 6, 9, 10, 14, 17, 21, 24, 26, 29, 30, 36, 46, 48} gemeinsamen Zahlen  ##############################################################################################
    
    #{1, 3, 6, 9, 10, 12, 14, 17, 18, 20, 21, 24, 25, 26, 29, 30, 33, 34, 36, 38, 39, 40, 42, 44, 45, 48, 46} # Zahlen aus keno analyse
    #{3,4,5,6,7,9,10,14,15,17,19,21,24,26,29,30,36,37,43,46,47,48} Zahlen aus EJ anylyse
    