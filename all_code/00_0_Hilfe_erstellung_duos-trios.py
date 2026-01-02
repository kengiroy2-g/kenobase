from collections import Counter
from itertools import combinations

# Definieren der Ziehungsdaten
ziehungsdaten = [
    {"datum": "02.07.2022", "zahlen": {20, 56, 46, 10, 9, 53, 70, 36, 3, 12, 52, 43, 69, 14, 48, 59, 19, 51, 17, 45}},
    {"datum": "01.07.2022", "zahlen": {68, 15, 2, 59, 4, 27, 49, 20, 45, 29, 61, 51, 43, 5, 32, 56, 34, 12, 17, 47}},
    {"datum": "30.06.2022", "zahlen": {44, 52, 21, 8, 17, 5, 64, 55, 34, 7, 14, 56, 57, 61, 16, 48, 62, 1, 67, 25}},
    {"datum": "29.06.2022", "zahlen": {61, 47, 48, 20, 28, 54, 7, 2, 39, 31, 23, 55, 42, 45, 37, 66, 29, 10, 21, 65}},
    {"datum": "28.06.2022", "zahlen": {64, 51, 52, 23, 50, 3, 39, 36, 28, 16, 46, 13, 62, 42, 66, 53, 56, 6, 58, 25}},
    {"datum": "27.06.2022", "zahlen": {50, 38, 6, 69, 10, 20, 27, 49, 60, 59, 9, 44, 41, 23, 7, 57, 63, 55, 36, 12}},
    {"datum": "26.06.2022", "zahlen": {48, 63, 59, 70, 2, 24, 11, 5, 56, 26, 68, 34, 14, 29, 19, 38, 22, 52, 20, 4}},
    {"datum": "25.06.2022", "zahlen": {3, 69, 63, 6, 52, 66, 50, 28, 41, 32, 17, 39, 60, 22, 64, 56, 9, 40, 18, 5}},
]

# Definieren der Kombinationen
kombinationen = [{3, 9, 10, 46, 48, 17}, {6, 13, 2, 55, 66, 70}]

# Ergebnisse initialisieren
ergebnisse = {}

# Funktion zur Berechnung der Variablen für eine Kombination
def berechne_kombinationswerte(kombi, ziehungsdaten):
    zaehlung = Counter()
    duos = set()
    trios = set()
    quartos = set()
    alle_gefunden = False
    erscheinungsdatum_gefunden = False

    for ziehung in ziehungsdaten:
        if alle_gefunden:
            break

        zahlen_set = ziehung["zahlen"]
        vorkommen = zahlen_set.intersection(kombi)

        if not erscheinungsdatum_gefunden:
            if vorkommen == kombi:
                erscheinungsdatum_gefunden = True
                continue

        if vorkommen:
            zaehlung.update(vorkommen)

            if all(zaehlung[zahl] > 0 for zahl in kombi):
                alle_gefunden = True

        # Duos, Trios und Quartos
        for size in [2, 3, 4]:
            for combo in combinations(vorkommen, size):
                if size == 2:
                    duos.add(combo)
                elif size == 3:
                    trios.add(combo)
                elif size == 4:
                    quartos.add(combo)

    counter_string = ','.join(str(zaehlung[zahl]) for zahl in kombi)
    duos_string = ';'.join(map(str, duos))
    trios_string = ';'.join(map(str, trios))
    quatro_string = ';'.join(map(str, quartos))

    return zaehlung, counter_string, duos_string, trios_string, quatro_string

# Berechne
