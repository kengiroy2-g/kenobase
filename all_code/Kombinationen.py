import math

def berechne_kombinationen(n, k):
    return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))

def eingabe_mit_validierung(prompt):
    while True:
        try:
            wert = int(input(prompt))
            if wert < 0:
                raise ValueError("Der Wert darf nicht negativ sein.")
            return wert
        except ValueError as e:
            print("Ungültige Eingabe. Bitte geben Sie eine positive ganze Zahl ein.", e)

# Benutzer um Eingabe bitten
n = eingabe_mit_validierung("Bitte geben Sie n ein (Gesamtzahl der Objekte): ")
k = eingabe_mit_validierung("Bitte geben Sie k ein (Anzahl der auszuwählenden Objekte): ")

# Sicherstellen, dass k nicht größer als n ist
if k > n:
    print("Fehler: k darf nicht größer als n sein.")
else:
    ergebnis = berechne_kombinationen(n, k)
    print(f"Anzahl der Kombinationen C({n}, {k}) = {ergebnis}")
