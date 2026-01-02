import pandas as pd
from itertools import combinations

def generiere_kombinationen():
    # Generiert alle möglichen Kombinationen von 6 Zahlen im Bereich von 1 bis 50
    # Jede Kombination muss mindestens zwei Zahlen zwischen 1 und 12 enthalten
    alle_kombinationen = list(combinations(range(1, 51), 6))
    gefilterte_kombinationen = [kombi for kombi in alle_kombinationen if len([z for z in kombi if z <= 12]) >= 2]
    return gefilterte_kombinationen

def vorpruefung_gegen_archiv(kombinationen, archiv_pfad):
    # Liest das Archiv und filtert Kombinationen basierend auf dem Archiv
    archiv_df = pd.read_csv(archiv_pfad, sep=';')
    archiv_kombinationen = [set(row.dropna().astype(int)) for index, row in archiv_df.iterrows()]
    
    def hat_max_vier_gemeinsame(kombi):
        for archiv_kombi in archiv_kombinationen:
            if len(set(kombi) & archiv_kombi) > 4:
                return False
        return True
    
    return [kombi for kombi in kombinationen if hat_max_vier_gemeinsame(kombi)]

def ueberpruefung_gegen_keno(kombinationen, keno_pfad, start_date, end_date):
    # Liest die KENO-Datei und führt die Überprüfung durch
    keno_df = pd.read_csv(keno_pfad, sep=';', parse_dates=['Datum'], dayfirst=True)
    keno_df = keno_df[(keno_df['Datum'] >= start_date) & (keno_df['Datum'] <= end_date)]
    
    treffer_details = []
    for kombi in kombinationen:
        kombi_set = set(kombi)
        for index, row in keno_df.iterrows():
            gezogene_nummern = set(row[['z1', 'z2', 'z3', 'z4', 'z5', 'z6', 'z7', 'z8', 'z9', 'z10',
                                        'z11', 'z12', 'z13', 'z14', 'z15', 'z16', 'z17', 'z18', 'z19', 'z20']].dropna().astype(int))
            gemeinsame = kombi_set & gezogene_nummern
            if len(gemeinsame) >= 6:
                treffer_details.append({'Datum': row['Datum'], 'Kombination': kombi, 'Treffer': len(gemeinsame), 'Getroffene Zahlen': list(gemeinsame)})
    
    return treffer_details

def vergleich_der_treffer(treffer):
    # Vergleicht die Treffer untereinander, um Kombinationen mit 5 gemeinsamen Elementen zu finden
    # Hinweis: Dieser Teil könnte je nach Datenstruktur der Trefferliste angepasst werden müssen
    pass

# Hauptfunktion, die alles zusammenführt
def hauptprogramm():
    kombinationen = generiere_kombinationen()
    kombinationen_nach_archiv = vorpruefung_gegen_archiv(kombinationen, 'EJ_archiv_bereinigt.csv')
    treffer_details = ueberpruefung_gegen_keno(kombinationen_nach_archiv, 'KENO_ab_2018 - Kopie.csv', '2018-01-01', '2022-12-31')
    
    # Hier können Sie die Funktion `vergleich_der_treffer` mit den erforderlichen Daten aufrufen
    
    # Ergebnisse speichern
    pd.DataFrame(treffer_details).to_csv('Zahlen_treffer_Detail.csv', index=False)
    # Weitere Schritte für das Speichern der finalen Kombinationen und Trefferlisten

if __name__ == '__main__':
    hauptprogramm()
