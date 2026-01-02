import itertools

def find_combinations():
    numbers = range(1, 51)  # Zahlenmenge von 1 bis 50
    target_sum = 111  # Zielsumme

    counter = 0  # Zähler für die gefundenen Kombinationen
    # Durchlaufen aller Kombinationen von 6 Zahlen aus der Zahlenmenge
    for combination in itertools.combinations(numbers, 5):
        if sum(combination) == target_sum and 1 in combination and 11 in combination and 3 in combination and 37 in combination:
            yield combination  # Gibt die passende Kombination zurück
            counter += 1  # Erhöht den Zähler

    print(f"Anzahl der gefundenen Kombinationen: {counter}")

# Aufruf der Funktion und Ausgabe der passenden Kombinationen
for combination in find_combinations():
    print(combination)
