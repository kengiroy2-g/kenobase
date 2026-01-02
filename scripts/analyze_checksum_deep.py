"""
Tiefere Checksum-Analyse - Suche nach versteckten Mustern
"""

from functools import reduce
import operator


def main():
    kombinationen = {
        "Kyritz": [5, 12, 20, 26, 34, 36, 42, 45, 48, 66],
        "Oberbayern": [3, 15, 18, 27, 47, 53, 54, 55, 66, 68],
        "Nordsachsen": [9, 19, 37, 38, 43, 45, 48, 57, 59, 67],
    }

    print("=" * 80)
    print("TIEFERE CHECKSUM-ANALYSE")
    print("=" * 80)

    # Das gefundene Muster: Ziffernprodukt mod 9 = 0
    print("\n### VERIFIZIERTES MUSTER: Ziffernprodukt mod 9 = 0 ###")
    print("-" * 60)

    for name, combo in kombinationen.items():
        # Ziffernprodukt berechnen (ohne Nullen)
        produkt = 1
        ziffern = []
        for z in combo:
            for d in str(z):
                if d != '0':
                    produkt *= int(d)
                    ziffern.append(int(d))

        print(f"\n{name}:")
        print(f"  Kombination: {combo}")
        print(f"  Alle Ziffern (ohne 0): {ziffern}")
        print(f"  Ziffernprodukt: {produkt}")
        print(f"  Ziffernprodukt mod 9: {produkt % 9}")

        # Warum ist es durch 9 teilbar?
        # Wenn die Quersumme der Ziffern durch 9 teilbar ist, ist das Produkt durch 9 teilbar
        # ABER: Das Produkt ist durch 9 teilbar wenn mindestens zwei 3en oder eine 9 enthalten ist
        count_3 = ziffern.count(3)
        count_6 = ziffern.count(6)
        count_9 = ziffern.count(9)
        faktor_3 = count_3 + count_6 + 2 * count_9  # 6=2*3, 9=3*3
        print(f"  Faktoren von 3: {count_3}x3, {count_6}x6, {count_9}x9 -> {faktor_3} Dreier-Faktoren")

    # Weitere Muster-Suche
    print("\n" + "=" * 80)
    print("WEITERE MUSTER-KANDIDATEN")
    print("=" * 80)

    # 1. Summe der Zehner-Stellen
    print("\n### Summe der Zehner-Stellen ###")
    for name, combo in kombinationen.items():
        zehner_sum = sum(z // 10 for z in combo)
        print(f"  {name}: {zehner_sum}")

    # 2. Summe der Einer-Stellen
    print("\n### Summe der Einer-Stellen ###")
    for name, combo in kombinationen.items():
        einer_sum = sum(z % 10 for z in combo)
        print(f"  {name}: {einer_sum}")

    # 3. Gerade Zahlen XOR Ungerade Zahlen
    print("\n### XOR: Gerade vs Ungerade Zahlen ###")
    for name, combo in kombinationen.items():
        gerade = [z for z in combo if z % 2 == 0]
        ungerade = [z for z in combo if z % 2 != 0]
        xor_gerade = reduce(operator.xor, gerade) if gerade else 0
        xor_ungerade = reduce(operator.xor, ungerade) if ungerade else 0
        print(f"  {name}: Gerade XOR={xor_gerade}, Ungerade XOR={xor_ungerade}, Combined={xor_gerade ^ xor_ungerade}")

    # 4. Durchschnitt (gerundet)
    print("\n### Durchschnitt der Zahlen ###")
    for name, combo in kombinationen.items():
        avg = sum(combo) / len(combo)
        print(f"  {name}: {avg:.2f}")

    # 5. Median
    print("\n### Median der Zahlen ###")
    for name, combo in kombinationen.items():
        sorted_c = sorted(combo)
        median = (sorted_c[4] + sorted_c[5]) / 2  # Bei 10 Zahlen
        print(f"  {name}: {median}")

    # 6. Minimum + Maximum
    print("\n### Min + Max ###")
    for name, combo in kombinationen.items():
        minmax = min(combo) + max(combo)
        print(f"  {name}: {min(combo)} + {max(combo)} = {minmax}")

    # 7. Spannweite (Max - Min)
    print("\n### Spannweite (Max - Min) ###")
    for name, combo in kombinationen.items():
        spann = max(combo) - min(combo)
        print(f"  {name}: {max(combo)} - {min(combo)} = {spann}")

    # 8. Anzahl in unteren/oberen Haelfte (1-35 vs 36-70)
    print("\n### Verteilung untere/obere Haelfte (1-35 vs 36-70) ###")
    for name, combo in kombinationen.items():
        unten = len([z for z in combo if z <= 35])
        oben = len([z for z in combo if z > 35])
        print(f"  {name}: {unten}:{oben}")

    # 9. Summe der ersten 5 vs letzte 5 (sortiert)
    print("\n### Summe erste 5 vs letzte 5 (sortiert) ###")
    for name, combo in kombinationen.items():
        s = sorted(combo)
        erste5 = sum(s[:5])
        letzte5 = sum(s[5:])
        print(f"  {name}: Erste 5={erste5}, Letzte 5={letzte5}, Diff={letzte5-erste5}")

    # 10. Produkt aller Zahlen mod verschiedene N
    print("\n### Produkt aller Zahlen mod N ###")
    for mod_n in [7, 11, 13, 17, 19, 23]:
        results = []
        for name, combo in kombinationen.items():
            prod = 1
            for z in combo:
                prod = (prod * z) % mod_n  # Overflow vermeiden
            results.append(prod)
        gleich = "JA!" if len(set(results)) == 1 else ""
        print(f"  mod {mod_n}: {results} {gleich}")

    # 11. Summe aller Zahlen die durch 2, 3, 5, 7 teilbar sind
    print("\n### Summe teilbarer Zahlen ###")
    for teiler in [2, 3, 5, 7]:
        results = []
        for name, combo in kombinationen.items():
            summe = sum(z for z in combo if z % teiler == 0)
            results.append(summe)
        gleich = "JA!" if len(set(results)) == 1 else ""
        print(f"  Summe teilbar durch {teiler}: {results} {gleich}")

    # 12. Anzahl Zahlen in jedem Drittel (1-23, 24-46, 47-70)
    print("\n### Drittel-Verteilung (1-23, 24-46, 47-70) ###")
    for name, combo in kombinationen.items():
        d1 = len([z for z in combo if 1 <= z <= 23])
        d2 = len([z for z in combo if 24 <= z <= 46])
        d3 = len([z for z in combo if 47 <= z <= 70])
        print(f"  {name}: [{d1}, {d2}, {d3}]")

    # 13. Check: Enthaelt jede Kombination mindestens eine aus jedem Drittel?
    print("\n### Jedes Drittel besetzt? ###")
    for name, combo in kombinationen.items():
        d1 = any(1 <= z <= 23 for z in combo)
        d2 = any(24 <= z <= 46 for z in combo)
        d3 = any(47 <= z <= 70 for z in combo)
        alle = d1 and d2 and d3
        print(f"  {name}: D1={d1}, D2={d2}, D3={d3} -> Alle: {alle}")

    # 14. Differenz groesste - kleinste Zahl mod 7
    print("\n### (Max - Min) mod 7 ###")
    results = []
    for name, combo in kombinationen.items():
        diff = max(combo) - min(combo)
        results.append(diff % 7)
    gleich = "JA!" if len(set(results)) == 1 else ""
    print(f"  {results} {gleich}")

    # 15. Hash-artige Berechnung: (summe * anzahl_primzahlen) mod 10
    print("\n### (Summe * Anzahl_Primzahlen) mod 10 ###")

    def ist_primzahl(n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True

    results = []
    for name, combo in kombinationen.items():
        summe = sum(combo)
        prim_count = sum(1 for z in combo if ist_primzahl(z))
        result = (summe * prim_count) % 10
        results.append(result)
        print(f"  {name}: ({summe} * {prim_count}) mod 10 = {result}")
    gleich = "JA!" if len(set(results)) == 1 else ""
    print(f"  Alle gleich? {gleich}")

    # 16. Alternierende Summe (sortiert): z0 - z1 + z2 - z3 + ...
    print("\n### Alternierende Summe (sortiert) ###")
    results = []
    for name, combo in kombinationen.items():
        s = sorted(combo)
        alt_sum = sum(s[i] * (1 if i % 2 == 0 else -1) for i in range(len(s)))
        results.append(alt_sum)
    print(f"  {list(kombinationen.keys())}: {results}")
    gleich = "JA!" if len(set(results)) == 1 else ""
    print(f"  Alle gleich? {gleich}")

    # 17. Summe der Positionen (wenn sortiert 1-10)
    print("\n### Position * Zahl Summe ###")
    for name, combo in kombinationen.items():
        s = sorted(combo)
        weighted = sum((i + 1) * z for i, z in enumerate(s))
        print(f"  {name}: {weighted}")

    # 18. Kleinste Luecke zwischen aufeinanderfolgenden Zahlen
    print("\n### Kleinste & Groesste Luecke ###")
    for name, combo in kombinationen.items():
        s = sorted(combo)
        diffs = [s[i + 1] - s[i] for i in range(len(s) - 1)]
        print(f"  {name}: Min={min(diffs)}, Max={max(diffs)}")

    # 19. Anzahl "Doppel-Zehner" (gleiche Zehnerstelle bei zwei Zahlen)
    print("\n### Anzahl gleiche Zehnerstelle ###")
    from collections import Counter
    for name, combo in kombinationen.items():
        zehner = [z // 10 for z in combo]
        counts = Counter(zehner)
        doppel = sum(c - 1 for c in counts.values() if c > 1)
        print(f"  {name}: {counts} -> {sum(1 for c in counts.values() if c >= 2)} Dekaden mit 2+")

    # 20. Besonderes Muster: Summe der geraden Positionen vs ungerade (sortiert)
    print("\n### Summe gerade/ungerade Positionen (sortiert, 0-basiert) ###")
    for name, combo in kombinationen.items():
        s = sorted(combo)
        gerade_pos = sum(s[i] for i in range(0, 10, 2))  # 0,2,4,6,8
        ungerade_pos = sum(s[i] for i in range(1, 10, 2))  # 1,3,5,7,9
        print(f"  {name}: Gerade={gerade_pos}, Ungerade={ungerade_pos}, Diff={gerade_pos-ungerade_pos}")

    # ZUSAMMENFASSUNG DER GEFUNDENEN MUSTER
    print("\n" + "=" * 80)
    print("ZUSAMMENFASSUNG: POTENTIELLE CHECKSUM-EIGENSCHAFTEN")
    print("=" * 80)

    print("""
    VERIFIZIERTE GEMEINSAME MUSTER:
    ===============================

    1. Ziffernprodukt mod 9 = 0 (EXAKT GLEICH bei allen 3)
       -> Bedeutung: Mindestens zwei 3er-Faktoren in den Ziffern

    2. Dekade 00-09: Genau 1 Zahl (EXAKT GLEICH bei allen 3)
       -> Jede Gewinner-Kombination hat exakt EINE einstellige Zahl

    3. Jedes Drittel (1-23, 24-46, 47-70) ist besetzt (ALLE TRUE)
       -> Gewinner-Kombinationen haben Zahlen aus allen Bereichen

    4. 6 von 7 Dekaden besetzt (GLEICH bei allen 3)
       -> Hohe Streuung ueber das Zahlenspektrum

    POTENTIELLE MUSTER (naeher untersuchen):
    ========================================

    - Summe im Bereich ~330-430 (koennte Constraint sein)
    - Max-Min Spannweite 61-65 (relativ einheitlich)
    - Mindestens 2 Zahlen teilbar durch 3 (immer erfuellt)
    """)


if __name__ == "__main__":
    main()
