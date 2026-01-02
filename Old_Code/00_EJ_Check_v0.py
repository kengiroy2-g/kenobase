import pandas as pd
from itertools import combinations
from tqdm import tqdm

def generiere_kombinationen():
    alle_kombinationen = list(combinations(range(1, 51), 6))
    # Integration von tqdm für die Fortschrittsanzeige
    gefilterte_kombinationen = [kombi for kombi in tqdm(alle_kombinationen, desc="Generiere Kombinationen") if len([z for z in kombi if z <= 12]) >= 2]
    return gefilterte_kombinationen

def vorpruefung_gegen_archiv(kombinationen, archiv_pfad):
    archiv_df = pd.read_csv(archiv_pfad, sep=';')
    archiv_kombinationen = [set(row.dropna().astype(int)) for index, row in archiv_df.iterrows()]
    
    def hat_max_vier_gemeinsame(kombi):
        for archiv_kombi in archiv_kombinationen:
            if len(set(kombi) & archiv_kombi) > 4:
                return False
        return True
    
    # Integration von tqdm
    return [kombi for kombi in tqdm(kombinationen, desc="Vorprüfung gegen Archiv") if hat_max_vier_gemeinsame(kombi)]

def ueberpruefung_gegen_keno(kombinationen, keno_pfad, start_date, end_date):
    keno_df = pd.read_csv(keno_pfad, sep=';', parse_dates=['Datum'], dayfirst=True)
    keno_df = keno_df[(keno_df['Datum'] >= start_date) & (keno_df['Datum'] <= end_date)]
    
    treffer_details = []
    # Integration von tqdm
    for kombi in tqdm(kombinationen, desc="Überprüfung gegen KENO"):
        kombi_set = set(kombi)
        for index, row in keno_df.iterrows():
            gezogene_nummern = set(row[['z1', 'z2', 'z3', 'z4', 'z5', 'z6', 'z7', 'z8', 'z9', 'z10',
                                        'z11', 'z12', 'z13', 'z14', 'z15', 'z16', 'z17', 'z18', 'z19', 'z20']].dropna().astype(int))
            gemeinsame = kombi_set & gezogene_nummern
            if len(gemeinsame) >= 6:
                treffer_details.append({'Datum': row['Datum'], 'Kombination': kombi, 'Treffer': len(gemeinsame), 'Getroffene Zahlen': list(gemeinsame)})
    
    return treffer_details

def vergleich_der_treffer(treffer):
    # Vergleich der Treffer
    pass

def hauptprogramm():
    kombinationen = generiere_kombinationen()
    kombinationen_nach_archiv = vorpruefung_gegen_archiv(kombinationen,  "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\EJ_archiv_bereinigt.csv")
    treffer_details = ueberpruefung_gegen_keno(kombinationen_nach_archiv, "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\KENO_2021.csv", '2021-01-01', '2021-12-31')
    
    pd.DataFrame(treffer_details).to_csv("C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\Basis_Tab\\Zahlen_treffer_Detail.csv", index=False)

if __name__ == '__main__':
    hauptprogramm()


# kombinationen_datei_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\kombinationen.csv"
#     archiv_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\EJ_archiv_bereinigt.csv"
#     keno_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\Basis_Tab\\KENO_ab_2018 - Kopie.csv"
#     vorpruefung_datei_pfad = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\Kenogpts_2\\EJ_Datei\\vorpruefung_ergebnisse.csv"
    