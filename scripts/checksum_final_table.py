"""
Finale strukturierte Tabelle der Checksum-Analyse
"""


def main():
    kombinationen = {
        "Kyritz": [5, 12, 20, 26, 34, 36, 42, 45, 48, 66],
        "Oberbayern": [3, 15, 18, 27, 47, 53, 54, 55, 66, 68],
        "Nordsachsen": [9, 19, 37, 38, 43, 45, 48, 57, 59, 67],
    }

    def ist_primzahl(n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True

    def quersumme(n):
        return sum(int(d) for d in str(n))

    def ziffernprodukt_ohne_null(combo):
        prod = 1
        for z in combo:
            for d in str(z):
                if d != '0':
                    prod *= int(d)
        return prod

    print("=" * 100)
    print("MATHEMATISCHE CHECKSUM-ANALYSE: KENO-GEWINNER-KOMBINATIONEN")
    print("=" * 100)

    print("\n" + "-" * 100)
    print(f"{'EIGENSCHAFT':<40} {'KYRITZ':>15} {'OBERBAYERN':>15} {'NORDSACHSEN':>15} {'GLEICH?':>10}")
    print("-" * 100)

    # Daten sammeln
    data = {}
    for name, combo in kombinationen.items():
        s = sorted(combo)
        data[name] = {
            "summe": sum(combo),
            "quersumme": sum(quersumme(z) for z in combo),
            "ziffernprodukt_mod9": ziffernprodukt_ohne_null(combo) % 9,
            "anzahl_primzahlen": sum(1 for z in combo if ist_primzahl(z)),
            "anzahl_gerade": sum(1 for z in combo if z % 2 == 0),
            "anzahl_ungerade": sum(1 for z in combo if z % 2 != 0),
            "summe_mod7": sum(combo) % 7,
            "summe_mod9": sum(combo) % 9,
            "summe_mod10": sum(combo) % 10,
            "summe_mod11": sum(combo) % 11,
            "summe_mod13": sum(combo) % 13,
            "xor": eval("^".join(str(z) for z in combo)),
            "teilbar_3": sum(1 for z in combo if z % 3 == 0),
            "teilbar_5": sum(1 for z in combo if z % 5 == 0),
            "teilbar_7": sum(1 for z in combo if z % 7 == 0),
            "dekade_00_09": sum(1 for z in combo if 0 <= z <= 9),
            "dekade_10_19": sum(1 for z in combo if 10 <= z <= 19),
            "dekade_20_29": sum(1 for z in combo if 20 <= z <= 29),
            "dekade_30_39": sum(1 for z in combo if 30 <= z <= 39),
            "dekade_40_49": sum(1 for z in combo if 40 <= z <= 49),
            "dekade_50_59": sum(1 for z in combo if 50 <= z <= 59),
            "dekade_60_69": sum(1 for z in combo if 60 <= z <= 69),
            "drittel_1_23": sum(1 for z in combo if 1 <= z <= 23),
            "drittel_24_46": sum(1 for z in combo if 24 <= z <= 46),
            "drittel_47_70": sum(1 for z in combo if 47 <= z <= 70),
            "min": min(combo),
            "max": max(combo),
            "spannweite": max(combo) - min(combo),
            "min_plus_max": min(combo) + max(combo),
            "median": (s[4] + s[5]) / 2,
            "dekaden_besetzt": sum(1 for d in range(7) if any(d*10 <= z <= d*10+9 for z in combo)),
            "bits_gesetzt": sum(bin(z).count('1') for z in combo),
        }

    def print_row(label, key, format_fn=str):
        vals = [data[n][key] for n in ["Kyritz", "Oberbayern", "Nordsachsen"]]
        gleich = "***JA***" if len(set(vals)) == 1 else ""
        v_str = [format_fn(v) for v in vals]
        print(f"{label:<40} {v_str[0]:>15} {v_str[1]:>15} {v_str[2]:>15} {gleich:>10}")

    # SUMMEN-BLOCK
    print("\n[SUMMEN]")
    print_row("Summe", "summe")
    print_row("Summe mod 7", "summe_mod7")
    print_row("Summe mod 9", "summe_mod9")
    print_row("Summe mod 10", "summe_mod10")
    print_row("Summe mod 11", "summe_mod11")
    print_row("Summe mod 13", "summe_mod13")

    # QUERSUMMEN-BLOCK
    print("\n[QUERSUMMEN]")
    print_row("Quersumme aller Zahlen", "quersumme")

    # ZIFFERNPRODUKT
    print("\n[ZIFFERNPRODUKT]")
    print_row("Ziffernprodukt mod 9", "ziffernprodukt_mod9")

    # PRIMZAHLEN
    print("\n[PRIMZAHLEN]")
    print_row("Anzahl Primzahlen", "anzahl_primzahlen")

    # PARITAET
    print("\n[PARITAET (GERADE/UNGERADE)]")
    print_row("Anzahl gerade Zahlen", "anzahl_gerade")
    print_row("Anzahl ungerade Zahlen", "anzahl_ungerade")

    # XOR
    print("\n[XOR]")
    print_row("XOR aller Zahlen", "xor")

    # TEILBARKEIT
    print("\n[TEILBARKEIT]")
    print_row("Anzahl teilbar durch 3", "teilbar_3")
    print_row("Anzahl teilbar durch 5", "teilbar_5")
    print_row("Anzahl teilbar durch 7", "teilbar_7")

    # DEKADEN
    print("\n[DEKADEN-VERTEILUNG]")
    print_row("Dekade 00-09", "dekade_00_09")
    print_row("Dekade 10-19", "dekade_10_19")
    print_row("Dekade 20-29", "dekade_20_29")
    print_row("Dekade 30-39", "dekade_30_39")
    print_row("Dekade 40-49", "dekade_40_49")
    print_row("Dekade 50-59", "dekade_50_59")
    print_row("Dekade 60-69", "dekade_60_69")
    print_row("Anzahl Dekaden besetzt", "dekaden_besetzt")

    # DRITTEL
    print("\n[DRITTEL-VERTEILUNG]")
    print_row("Drittel 1-23", "drittel_1_23")
    print_row("Drittel 24-46", "drittel_24_46")
    print_row("Drittel 47-70", "drittel_47_70")

    # MIN/MAX
    print("\n[MIN/MAX/SPANNWEITE]")
    print_row("Minimum", "min")
    print_row("Maximum", "max")
    print_row("Spannweite (Max-Min)", "spannweite")
    print_row("Min + Max", "min_plus_max")
    print_row("Median", "median", lambda x: f"{x:.1f}")

    # BITS
    print("\n[BIT-ANALYSE]")
    print_row("Gesetzte Bits gesamt", "bits_gesetzt")

    # ZUSAMMENFASSUNG
    print("\n" + "=" * 100)
    print("GEFUNDENE GEMEINSAME MUSTER (CHECKSUM-KANDIDATEN)")
    print("=" * 100)

    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║  EXAKT GLEICHE WERTE BEI ALLEN 3 GEWINNER-KOMBINATIONEN:                    ║
    ╠══════════════════════════════════════════════════════════════════════════════╣
    ║                                                                              ║
    ║  1. ZIFFERNPRODUKT mod 9 = 0                                                ║
    ║     -> Das Produkt aller Ziffern (ohne Nullen) ist durch 9 teilbar          ║
    ║     -> Erklaerung: Mindestens 2 Faktoren von 3 in den Ziffern               ║
    ║                                                                              ║
    ║  2. DEKADE 00-09: Genau 1 Zahl                                              ║
    ║     -> Jede Kombination hat EXAKT eine einstellige Zahl (1-9)               ║
    ║                                                                              ║
    ║  3. ALLE 3 DRITTEL BESETZT                                                  ║
    ║     -> Zahlen aus (1-23), (24-46) UND (47-70) vorhanden                     ║
    ║                                                                              ║
    ║  4. 6 VON 7 DEKADEN BESETZT                                                 ║
    ║     -> Hohe Streuung, genau eine Dekade ist leer                            ║
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║  AUFFAELLIGE BEREICHE (POTENTIELLE CONSTRAINTS):                            ║
    ╠══════════════════════════════════════════════════════════════════════════════╣
    ║                                                                              ║
    ║  • Summe im Bereich 330-430 (Durchschnitt ~387)                             ║
    ║  • Spannweite (Max-Min) im Bereich 58-65                                    ║
    ║  • Min + Max = 71-76 (nahe bei 70+kleiner Wert)                             ║
    ║  • Mindestens 4 Zahlen teilbar durch 3                                      ║
    ║  • 3 Dekaden haben 2+ Zahlen                                                ║
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║  MOEGLICHE ALGORITHMUS-VALIDIERUNG:                                         ║
    ╠══════════════════════════════════════════════════════════════════════════════╣
    ║                                                                              ║
    ║  Ein Validierungs-Algorithmus koennte pruefen:                              ║
    ║                                                                              ║
    ║  def is_valid_keno_winner(combo):                                           ║
    ║      # 1. Ziffernprodukt-Check                                              ║
    ║      prod = product(all_digits_without_zero(combo))                         ║
    ║      if prod % 9 != 0:                                                      ║
    ║          return False                                                        ║
    ║                                                                              ║
    ║      # 2. Einstellige Zahl Check                                            ║
    ║      if count(z for z in combo if z <= 9) != 1:                             ║
    ║          return False                                                        ║
    ║                                                                              ║
    ║      # 3. Drittel-Abdeckung                                                 ║
    ║      if not (has_1_23 and has_24_46 and has_47_70):                         ║
    ║          return False                                                        ║
    ║                                                                              ║
    ║      # 4. Dekaden-Streuung                                                  ║
    ║      if count_dekaden_with_numbers(combo) != 6:                             ║
    ║          return False                                                        ║
    ║                                                                              ║
    ║      return True                                                             ║
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()
