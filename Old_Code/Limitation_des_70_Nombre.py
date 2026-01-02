def process_numbers(XX, value1, value2, value3):
    # Addition und Subtraktion separat durchführen
    XX_add1 = [x + value1 for x in XX]
    XX_sub1 = [x - value1 for x in XX]
    XX_add2 = [x + value2 for x in XX]
    XX_sub2 = [x - value2 for x in XX]
    if value3 > 0:
        XX_add3 = [x + value3 for x in XX]
        XX_sub3 = [x - value3 for x in XX]
    # Kombinieren und Filtern der Listen
        XX_combined = list(set(XX_add1 + XX_sub1 + XX_add2 + XX_sub2 + XX_add3 + XX_sub3))
    else:
        XX_combined = list(set(XX_add1 + XX_sub1 + XX_add2 + XX_sub2))
    XX_filtered = [x for x in XX_combined if 0 < x <= 70]

    # Sortieren der Liste
    return sorted(XX_filtered)

# Anwenden der Funktion
XX = [2, 3, 4, 5, 6, 7, 11, 15, 25, 31, 33, 34, 35, 37, 38, 44, 59, 62, 65, 68]
XX_3 = process_numbers(XX, 5, 7,0)

# Finden von Zahlen, die nicht in XX_3 enthalten sind
numbers_not_in_XX_3 = [x for x in range(1, 71) if x not in XX_3]

print("XX_3:", XX_3)
print("Nicht in XX_3:", numbers_not_in_XX_3)

    