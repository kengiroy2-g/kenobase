import itertools

def check_conditions(sum_combination):
    factors = [3, 11, 37, 111]
    check_numbers = [111, 37, 11, 3, 1]
    
    # Überprüfe ob die Summe gleich 111 ist
    if sum_combination == 111:
        return True

    # Überprüfe ob die Summe ein Vielfaches der Faktoren ist
    if any(sum_combination % factor == 0 for factor in factors):
        return True

    # Überprüfe ob die Differenzen Vielfache der Faktoren sind
    for check_number in check_numbers:
        diff = abs(sum_combination - check_number)
        if any(diff % factor == 0 for factor in factors):
            return True

    # Überprüfe ob die umgedrehten Summen oder Differenzen Vielfache der Faktoren sind
    reversed_sum_combination = int(str(sum_combination)[::-1])
    if any(reversed_sum_combination % factor == 0 for factor in factors):
        return True

    for check_number in check_numbers:
        reversed_diff = int(str(abs(sum_combination - check_number))[::-1])
        if any(reversed_diff % factor == 0 for factor in factors):
            return True

    return False

def find_combinations():
    numbers = [1, 2, 60, 11, 50, 40,18,33,45]  # Spezifische Zahlenmenge
    counter = 0  # Zähler für die gefundenen Kombinationen
    
    # Durchlaufen aller Kombinationen von 7 Zahlen aus der Zahlenmenge
    for combination in itertools.combinations(numbers, 7):
        sum_combination = sum(combination)
        if check_conditions(sum_combination):
            yield combination  # Gibt die passende Kombination zurück
            counter += 1  # Erhöht den Zähler

    print(f"Anzahl der gefundenen Kombinationen: {counter}")

# Aufruf der Funktion und Ausgabe der passenden Kombinationen
for combination in find_combinations():
    print(combination)
