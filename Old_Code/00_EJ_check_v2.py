import pandas as pd
from itertools import combinations
import os
from tqdm import tqdm

def generiere_oder_lese_kombinationen(datei_pfad):
    if os.path.exists(datei_pfad):
        print("Lese Kombinationen aus Datei...")
        kombinationen_df = pd.read_csv(datei_pfad)
        kombinationen = [tuple(row) for row in kombinationen_df.to_numpy()]
    else:
        print("Generiere neue Kombinationen...")
        alle_kombinationen = list(combinations(range(1, 51), 6))
        kombinationen = [kombi for kombi in tqdm(alle_kombinationen, desc="Generiere Kombinationen") if len([z for z in kombi if z <= 12]) >= 2]
        kombinationen_df = pd.DataFrame(kombinationen)
        kombinationen_df.to_csv(datei_pfad, index=False)
    return kombinationen

def vorpruefung_gegen_archiv(kombinationen, archiv_pfad, ergebnis_datei_pfad):
    if os.path.exists(ergebnis_datei_pfad):
        print("Lese Vorprüfungsergebnisse aus Datei...")
        ergebnisse_df = pd.read_csv(ergebnis_datei_pfad)
        ergebnisse = [tuple(row) for row in ergebnisse_df.to_numpy()]
    else:
        print("Führe Vorprüfung gegen das Archiv durch...")
        archiv_df = pd.read_csv(archiv_pfad, sep=';')
        archiv_kombinationen = [set(row.dropna().astype(int)) for index, row in archiv_df.iterrows()]

        def hat_max_vier_gemeinsame(kombi):
            for archiv_kombi in archiv_kombinationen:
                if len(set(kombi) & archiv_kombi) > 4:
                    return False
            return True

        ergebnisse = [kombi for kombi in tqdm(kombinationen, desc="Vorprüfung gegen Archiv") if hat_max_vier_gemeinsame(kombi)]
        ergebnisse_df = pd.DataFrame(ergebnisse)
        ergebnisse_df.to_csv(ergebnis_datei_pfad, index=False)
    return ergebnisse


def check_keno_numbers(csv_path, kombinationen_liste, start_date, end_date):
    keno_data = pd.read_csv(csv_path, sep=';', parse_dates=['Datum'], dayfirst=True)
    keno_data = keno_data[(keno_data['Datum'] >= pd.to_datetime(start_date)) & (keno_data['Datum'] <= pd.to_datetime(end_date))]
    
    results = []
    for kombination in tqdm(kombinationen_liste, desc="Überprüfung gegen Keno"):
        numbers_to_check = set(kombination)
        for index, row in keno_data.iterrows():
            drawn_numbers = set(row.loc['z1':'z20'].dropna().astype(int))
            matches = drawn_numbers.intersection(numbers_to_check)
            if len(matches) >= 6:
                results.append({'Datum': row['Datum'], 'Kombination': kombination, 'Treffer': len(matches), 'Getroffene Zahlen': list(matches)})
    return results

def hauptprogramm():
    kombinationen_datei_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\kombinationen.csv"
    archiv_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\EJ_archiv_bereinigt.csv"
    keno_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\Basis_Tab\\KENO_ab_2018 - Kopie.csv"
    vorpruefung_datei_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\vorpruefung_ergebnisse.csv"
    
    kombinationen = generiere_oder_lese_kombinationen(kombinationen_datei_pfad)
    kombinationen_nach_archiv = vorpruefung_gegen_archiv(kombinationen, archiv_pfad, vorpruefung_datei_pfad)
    treffer_details = check_keno_numbers(keno_pfad, kombinationen_nach_archiv, '2021-01-01', '2021-12-31')
    
    # Ergebnisse speichern
    pd.DataFrame(treffer_details).to_csv("C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\Basis_Tab\\Zahlen_treffer_Detail.csv", index=False)

if __name__ == '__main__':
    hauptprogramm()
