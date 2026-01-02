# Adjusting the provided Python code to have different ranges for the noise generation and the tt800 number generation.

import itertools
import numpy as np
class KenoNumberGeneratorUnsorted:
    def __init__(self, noise_low, noise_high, tt800_low, tt800_high, valid_range):
        # Initialize the pseudo-random generator with separate range parameters for noise and tt800
        self.rng = np.random.default_rng()
        self.noise_low = noise_low
        self.noise_high = noise_high
        self.tt800_low = tt800_low
        self.tt800_high = tt800_high
        self.valid_range = valid_range

    def generate_noise(self):
        # Simulates generating noise (random bit) within the custom range for noise
        return self.rng.integers(self.noise_low, self.noise_high)

    def generate_tt800_number(self):
        # Simulates generating a random number with the tt800 within the custom range for tt800
        return self.rng.integers(self.tt800_low, self.tt800_high)

    def xor_numbers(self, number1, number2):
        # XOR operation between two numbers
        return number1 ^ number2

    def draw_numbers(self):
        # Draws 20 unique Keno numbers
        drawn_numbers = []
        while len(drawn_numbers) < 20:
            # Generate a random number with tt800 and noise
            tt800_num = self.generate_tt800_number()
            noise = self.generate_noise()
            number = self.xor_numbers(tt800_num, noise)

            # Check if the number is in the valid range and not already drawn
            if number in self.valid_range or number in [555,777,2000,4000,9111,81] and number not in [34,38,59,68] and number not in drawn_numbers:
                drawn_numbers.append(number)
        return drawn_numbers

# Separate user-defined ranges for noise and tt800 number generation
noise_low = 1
noise_high = 111
tt800_low = 1
tt800_high = 9990
# Valid range of numbers for Keno is assumed to be between 1 and 70
valid_numbers_range = set(range(1, 71))

# Instantiate the Keno generator with separate range parameters for noise and tt800
keno_generator_unsorted = KenoNumberGeneratorUnsorted(
    noise_low, noise_high, tt800_low, tt800_high, valid_numbers_range)

# Draw numbers without sorting
keno_numbers_unsorted = keno_generator_unsorted.draw_numbers()
number_x = print(keno_numbers_unsorted)


#################################################
## Combination_Generator

def is_multiple(num, multiples):
    for multiple in multiples:
        if num % multiple == 0:
            return multiple
    return None

def find_combinations_v2():
    numbers =  keno_numbers_unsorted # Zahlenmenge
    multiples = [1,11,111]  # Liste der Zahlen, von denen wir überprüfen möchten, ob sie Vielfache sind
    targets = [1,11]  # Ziele für die Differenzen

    counter = 0  # Zähler für die gefundenen Kombinationen
    results = []

    # Durchlaufen aller Kombinationen von 6 Zahlen aus der Zahlenmenge
    for combination in itertools.combinations(numbers, 8):
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
