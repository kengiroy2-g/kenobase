import itertools

def is_multiple(num, multiples):
    for multiple in multiples:
        if num % multiple == 0:
            return multiple
    return None

def find_combinations_v2():
    numbers = [3, 8, 10, 12, 13, 18, 26, 31, 32, 41, 43, 44, 45, 48, 60, 61, 63, 65, 68, 69]  # Zahlenmenge
    multiples = [3, 11, 37, 111]  # Liste der Zahlen, von denen wir überprüfen möchten, ob sie Vielfache sind
    targets = [1, 3, 11, 37, 111]  # Ziele für die Differenzen

    counter = 0  # Zähler für die gefundenen Kombinationen
    results = []

    # Durchlaufen aller Kombinationen von 6 Zahlen aus der Zahlenmenge
    for combination in itertools.combinations(numbers, 9):
        sum_comb = sum(combination)
        sum_comb_rev = int(str(sum_comb)[::-1])
        conditions = []

        # Prüfen, ob die Summe ein Vielfaches ist und der Quotient ist 1 oder 11
        multiple = is_multiple(sum_comb, multiples)
        if multiple is not None and (sum_comb / multiple in {1, 11}):
            conditions.append(f"Summe Vielfaches von {multiple}: {sum_comb / multiple}")

        multiple = is_multiple(sum_comb_rev, multiples)
        if multiple is not None and (sum_comb_rev / multiple in {1, 11}):
            conditions.append(f"Umgekehrte Summe Vielfaches von {multiple}: {sum_comb_rev / multiple}")

        # Prüfen, ob die Differenzen Vielfache sind und der Quotient ist 1 oder 11
        for target in targets:
            diff = abs(sum_comb - target)
            diff_rev = int(str(diff)[::-1])

            multiple = is_multiple(diff, multiples)
            if multiple is not None and (diff / multiple in {1, 11}):
                conditions.append(f"Differenz mit {target} Vielfaches von {multiple}: {diff / multiple}")

            multiple = is_multiple(diff_rev, multiples)
            if multiple is not None and (diff_rev / multiple in {1, 11}):
                conditions.append(f"Umgekehrte Differenz mit {target} Vielfaches von {multiple}: {diff_rev / multiple}")

        # Wenn es erfüllte Bedingungen gibt, geben wir die Kombination und die Bedingungen zurück
        if conditions:
            results.append((combination, conditions))
            counter += 1  # Erhöht den Zähler

    print(f"Anzahl der gefundenen Kombinationen: {counter}")
    return results

# Aufruf der Funktion und Speichern der passenden Kombinationen und Bedingungen
results_v2 = find_combinations_v2()


for combination, conditions in results_v2:
    print(f"Kombination: {combination}")
    print("Erfüllte Bedingungen:")
    for condition in conditions:
        print(condition)
    print()

results_v2 = find_combinations_v2()