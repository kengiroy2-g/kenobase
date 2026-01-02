import itertools

#In diesem Code wird nun für jede Kombination ein Dictionary mit den Ergebnissen jeder Bedingung zurückgegeben. 
# Wenn mindestens eine der Bedingungen erfüllt ist (das heißt, wenn mindestens ein Wert im Dictionary True ist), 
# wird die Kombination zusammen mit den Bedingungsergebnissen zurückgegeben und der Zähler wird erhöht. 
# Die Ergebnisse jeder Bedingung werden dann für jede gültige Kombination ausgegeben.

def check_conditions(sum_combination):
    factors = [3, 11, 37, 111]
    check_numbers = [111, 37, 11, 3, 1]
    
    results = {}

    # Überprüfe ob die Summe gleich 111 ist
    results["Summe gleich 111"] = sum_combination == 111

    # Überprüfe ob die Summe ein Vielfaches der Faktoren ist
    results["Summe Vielfaches der Faktoren"] = any(sum_combination % factor == 0 for factor in factors)

    # Überprüfe ob die Differenzen Vielfache der Faktoren sind
    for check_number in check_numbers:
        diff = abs(sum_combination - check_number)
        results[f"Differenz mit {check_number} Vielfaches der Faktoren"] = any(diff % factor == 0 for factor in factors)

    # Überprüfe ob die umgedrehten Summen oder Differenzen Vielfache der Faktoren sind
    reversed_sum_combination = int(str(sum_combination)[::-1])
    results["Umgekehrte Summe Vielfaches der Faktoren"] = any(reversed_sum_combination % factor == 0 for factor in factors)

    for check_number in check_numbers:
        reversed_diff = int(str(abs(sum_combination - check_number))[::-1])
        results[f"Umgekehrte Differenz mit {check_number} Vielfaches der Faktoren"] = any(reversed_diff % factor == 0 for factor in factors)

    return results

def find_combinations():
    numbers = [1, 2, 5, 11, 12, 40,60,65,34]  # Spezifische Zahlenmenge
    counter = 0  # Zähler für die gefundenen Kombinationen
    
    # Durchlaufen aller Kombinationen von 6 Zahlen aus der Zahlenmenge
    for combination in itertools.combinations(numbers, 8):
        sum_combination = sum(combination)
        condition_results = check_conditions(sum_combination)
        if any(condition_results.values()):
            yield combination, condition_results  # Gibt die passende Kombination und die Bedingungen zurück
            counter += 1  # Erhöht den Zähler

    print(f"Anzahl der gefundenen Kombinationen: {counter}")

# Aufruf der Funktion und Ausgabe der passenden Kombinationen
for combination, condition_results in find_combinations():
    print("Kombination:", combination)
    print("Bedingungen:")
    for condition, result in condition_results.items():
        print(f"{condition}: {result}")
    print("\n")
