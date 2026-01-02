import pandas as pd
from itertools import combinations
import os
from tqdm import tqdm

def generiere_oder_lese_kombinationen(datei_pfad):
    if os.path.exists(datei_pfad):
        print("Lese Kombinationen aus Datei...")
        kombinationen_df = pd.read_csv(datei_pfad)
        kombinationen = [tuple(row) for row in kombinationen_df.values]
    else:
        print("Generiere neue Kombinationen...")
        alle_kombinationen = list(combinations(range(1, 51), 6))
        kombinationen = [kombi for kombi in tqdm(alle_kombinationen) if len([z for z in kombi if z <= 12]) >= 2]
        kombinationen_df = pd.DataFrame(kombinationen)
        kombinationen_df.to_csv(datei_pfad, index=False)
    return kombinationen

# def hauptprogramm():
#     kombinationen_datei_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\kombinationen.csv"
#     kombinationen = generiere_oder_lese_kombinationen(kombinationen_datei_pfad)
#     # Weiterer Code hier...

# if __name__ == '__main__':
#     hauptprogramm()

def generiere_kombinationen():
    alle_kombinationen = list(combinations(range(1, 51), 6))
    gefilterte_kombinationen = [kombi for kombi in alle_kombinationen if len([z for z in kombi if z <= 12]) >= 2]
    return gefilterte_kombinationen

def vorpruefung_gegen_archiv(kombinationen, archiv_pfad):
    archiv_df = pd.read_csv(archiv_pfad, sep=';')
    archiv_kombinationen = [set(row.dropna().astype(int)) for index, row in archiv_df.iterrows()]
    
    def hat_max_vier_gemeinsame(kombi):
        for archiv_kombi in archiv_kombinationen:
            if len(set(kombi) & archiv_kombi) > 4:
                return False
        return True
    
    return [kombi for kombi in kombinationen if hat_max_vier_gemeinsame(kombi)]

def check_keno_numbers(csv_path, kombinationen_liste, start_date, end_date):
    keno_data = pd.read_csv(csv_path, sep=';', parse_dates=['Datum'], dayfirst=True)
    keno_data = keno_data[(keno_data['Datum'] >= pd.to_datetime(start_date)) & (keno_data['Datum'] <= pd.to_datetime(end_date))]
    
    results = []
    for kombination in kombinationen_liste:
        numbers_to_check = set(kombination)
        for index, row in keno_data.iterrows():
            drawn_numbers = set(row.loc['z1':'z20'].dropna().astype(int))
            matches = drawn_numbers.intersection(numbers_to_check)
            if len(matches) >= 6:
                results.append({'Datum': row['Datum'], 'Kombination': kombination, 'Treffer': len(matches), 'Getroffene Zahlen': list(matches)})
    return results

def vergleich_der_treffer(treffer):
    # Implementierung ausstehend
    pass

def hauptprogramm():
    kombinationen_datei_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\kombinationen.csv"
    kombinationen = generiere_oder_lese_kombinationen(kombinationen_datei_pfad)
    kombinationen_nach_archiv = vorpruefung_gegen_archiv(kombinationen, "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\EJ_archiv_bereinigt.csv")
    treffer_details = check_keno_numbers("C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\Basis_Tab\\KENO_ab_2018 - Kopie.csv", kombinationen_nach_archiv, '2021-01-01', '2021-12-31')
    
    # Ergebnisse speichern
    pd.DataFrame(treffer_details).to_csv("C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\Basis_Tab\\Zahlen_treffer_Detail.csv", index=False)
    # Weitere Verarbeitung und Speicherung der Ergebnisse nach Bedarf

if __name__ == '__main__':
    hauptprogramm()
