"""
Analyse der mathematischen Checksum-Eigenschaften von KENO-Gewinner-Kombinationen.
Sucht nach gemeinsamen Mustern die ein Algorithmus als Validierung nutzen koennte.
"""

from typing import Any
from functools import reduce
import operator


def quersumme(n: int) -> int:
    """Berechnet die Quersumme einer Zahl."""
    return sum(int(d) for d in str(abs(n)))


def iterierte_quersumme(n: int) -> int:
    """Berechnet die iterierte Quersumme bis einstellig."""
    while n >= 10:
        n = quersumme(n)
    return n


def ist_primzahl(n: int) -> bool:
    """Prueft ob n eine Primzahl ist."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


def ziffernprodukt(zahlen: list[int]) -> int:
    """Berechnet das Produkt aller Ziffern aller Zahlen."""
    produkt = 1
    for z in zahlen:
        for d in str(z):
            if d != '0':  # 0 wuerde alles nullen
                produkt *= int(d)
    return produkt


def xor_alle(zahlen: list[int]) -> int:
    """XOR aller Zahlen."""
    return reduce(operator.xor, zahlen, 0)


def analyze_combination(name: str, combo: list[int]) -> dict[str, Any]:
    """Analysiert eine Kombination auf alle Checksum-Eigenschaften."""

    result = {
        "name": name,
        "kombination": combo,
        "anzahl": len(combo),
    }

    # 1. Summe und Summen-Muster
    summe = sum(combo)
    result["summe"] = summe
    result["summe_mod_7"] = summe % 7
    result["summe_mod_9"] = summe % 9
    result["summe_mod_10"] = summe % 10
    result["summe_mod_11"] = summe % 11
    result["summe_mod_13"] = summe % 13
    result["summe_mod_70"] = summe % 70  # KENO-Range

    # 2. Quersumme
    quersumme_gesamt = sum(quersumme(z) for z in combo)
    result["quersumme_gesamt"] = quersumme_gesamt
    result["quersumme_mod_9"] = quersumme_gesamt % 9
    result["iterierte_quersumme"] = iterierte_quersumme(summe)

    # 3. Ziffernprodukt
    zp = ziffernprodukt(combo)
    result["ziffernprodukt"] = zp
    result["ziffernprodukt_mod_9"] = zp % 9
    result["ziffernprodukt_mod_7"] = zp % 7

    # 4. Primzahlen-Analyse
    primzahlen = [z for z in combo if ist_primzahl(z)]
    result["primzahlen"] = primzahlen
    result["anzahl_primzahlen"] = len(primzahlen)
    result["summe_primzahlen"] = sum(primzahlen)

    # 5. Gerade/Ungerade
    gerade = [z for z in combo if z % 2 == 0]
    ungerade = [z for z in combo if z % 2 != 0]
    result["anzahl_gerade"] = len(gerade)
    result["anzahl_ungerade"] = len(ungerade)
    result["parity_ratio"] = f"{len(gerade)}:{len(ungerade)}"

    # 6. XOR
    xor_result = xor_alle(combo)
    result["xor_alle"] = xor_result
    result["xor_bin"] = bin(xor_result)
    result["xor_mod_7"] = xor_result % 7

    # 7. Teilbarkeits-Analyse
    teilbar_3 = [z for z in combo if z % 3 == 0]
    teilbar_5 = [z for z in combo if z % 5 == 0]
    teilbar_7 = [z for z in combo if z % 7 == 0]
    result["anzahl_teilbar_3"] = len(teilbar_3)
    result["anzahl_teilbar_5"] = len(teilbar_5)
    result["anzahl_teilbar_7"] = len(teilbar_7)
    result["teilbar_3"] = teilbar_3
    result["teilbar_5"] = teilbar_5
    result["teilbar_7"] = teilbar_7

    # 8. Dekaden-Verteilung (0-9, 10-19, ...)
    dekaden = {}
    for d in range(0, 8):
        start = d * 10
        end = start + 9
        count = len([z for z in combo if start <= z <= end])
        dekaden[f"{start:02d}-{end:02d}"] = count
    result["dekaden"] = dekaden

    # 9. Differenzen-Analyse
    sorted_combo = sorted(combo)
    differenzen = [sorted_combo[i+1] - sorted_combo[i] for i in range(len(sorted_combo)-1)]
    result["differenzen"] = differenzen
    result["summe_differenzen"] = sum(differenzen)  # = max - min
    result["max_diff"] = max(differenzen)
    result["min_diff"] = min(differenzen)

    # 10. Spezielle Checksummen
    # Luhn-aehnlich: Summe mit alternierenden Gewichten
    luhn_like = sum(z * (2 if i % 2 == 0 else 1) for i, z in enumerate(sorted_combo))
    result["luhn_like"] = luhn_like
    result["luhn_like_mod_10"] = luhn_like % 10

    # Fletcher-aehnlich: Kumulative Summe
    fletcher = sum(sum(sorted_combo[:i+1]) for i in range(len(sorted_combo)))
    result["fletcher_like"] = fletcher
    result["fletcher_like_mod_255"] = fletcher % 255

    # 11. Bitanalyse
    bit_sum = sum(bin(z).count('1') for z in combo)
    result["gesetzte_bits_gesamt"] = bit_sum

    # 12. Spezielle Modulo-Kombinationen
    result["summe_mod_69"] = summe % 69  # KENO max-1
    result["summe_mod_71"] = summe % 71  # KENO max+1

    return result


def find_common_patterns(results: list[dict]) -> dict[str, Any]:
    """Findet gemeinsame Muster ueber alle Kombinationen."""

    patterns = {}

    # Eigenschaften die exakt gleich sein koennten
    exact_match_keys = [
        "summe_mod_7", "summe_mod_9", "summe_mod_10", "summe_mod_11", "summe_mod_13",
        "quersumme_mod_9", "iterierte_quersumme",
        "anzahl_primzahlen", "anzahl_gerade", "anzahl_ungerade",
        "xor_mod_7", "luhn_like_mod_10",
        "anzahl_teilbar_3", "anzahl_teilbar_5", "anzahl_teilbar_7",
        "gesetzte_bits_gesamt"
    ]

    for key in exact_match_keys:
        values = [r[key] for r in results]
        if len(set(values)) == 1:
            patterns[key] = {"status": "EXAKT GLEICH", "wert": values[0]}
        else:
            patterns[key] = {"status": "unterschiedlich", "werte": values}

    # Summen-Bereich pruefen
    summen = [r["summe"] for r in results]
    patterns["summen_bereich"] = {
        "min": min(summen),
        "max": max(summen),
        "durchschnitt": sum(summen) / len(summen),
        "spannweite": max(summen) - min(summen)
    }

    return patterns


def main():
    # Die 3 verifizierten Gewinner-Kombinationen
    kombinationen = [
        ("Kyritz", [5, 12, 20, 26, 34, 36, 42, 45, 48, 66]),
        ("Oberbayern", [3, 15, 18, 27, 47, 53, 54, 55, 66, 68]),
        ("Nordsachsen", [9, 19, 37, 38, 43, 45, 48, 57, 59, 67]),
    ]

    print("=" * 80)
    print("MATHEMATISCHE CHECKSUM-ANALYSE DER KENO-GEWINNER-KOMBINATIONEN")
    print("=" * 80)
    print()

    results = []

    for name, combo in kombinationen:
        result = analyze_combination(name, combo)
        results.append(result)

    # Haupt-Tabelle
    print("KOMBINATION DETAILS:")
    print("-" * 80)
    for r in results:
        print(f"\n{r['name']}: {r['kombination']}")
    print()

    # Strukturierte Ergebnis-Tabelle
    print("=" * 80)
    print("CHECKSUM-EIGENSCHAFTEN IM VERGLEICH")
    print("=" * 80)

    # Tabellen-Format
    headers = ["Eigenschaft", "Kyritz", "Oberbayern", "Nordsachsen", "Gleich?"]

    def print_row(prop_name: str, values: list, format_str: str = "{}"):
        gleich = "JA" if len(set(values)) == 1 else ""
        v1, v2, v3 = [format_str.format(v) for v in values]
        print(f"{prop_name:<30} {v1:>12} {v2:>12} {v3:>12} {gleich:>8}")

    print(f"{'Eigenschaft':<30} {'Kyritz':>12} {'Oberbayern':>12} {'Nordsachsen':>12} {'Gleich?':>8}")
    print("-" * 80)

    # Summen
    print("\n--- SUMMEN ---")
    print_row("Summe", [r["summe"] for r in results])
    print_row("Summe mod 7", [r["summe_mod_7"] for r in results])
    print_row("Summe mod 9", [r["summe_mod_9"] for r in results])
    print_row("Summe mod 10", [r["summe_mod_10"] for r in results])
    print_row("Summe mod 11", [r["summe_mod_11"] for r in results])
    print_row("Summe mod 13", [r["summe_mod_13"] for r in results])
    print_row("Summe mod 69", [r["summe_mod_69"] for r in results])
    print_row("Summe mod 70", [r["summe_mod_70"] for r in results])
    print_row("Summe mod 71", [r["summe_mod_71"] for r in results])

    # Quersummen
    print("\n--- QUERSUMMEN ---")
    print_row("Quersumme gesamt", [r["quersumme_gesamt"] for r in results])
    print_row("Quersumme mod 9", [r["quersumme_mod_9"] for r in results])
    print_row("Iterierte Quersumme", [r["iterierte_quersumme"] for r in results])

    # Ziffernprodukt
    print("\n--- ZIFFERNPRODUKT ---")
    print_row("Ziffernprodukt", [r["ziffernprodukt"] for r in results])
    print_row("Ziffernprodukt mod 7", [r["ziffernprodukt_mod_7"] for r in results])
    print_row("Ziffernprodukt mod 9", [r["ziffernprodukt_mod_9"] for r in results])

    # Primzahlen
    print("\n--- PRIMZAHLEN ---")
    print_row("Anzahl Primzahlen", [r["anzahl_primzahlen"] for r in results])
    print_row("Summe Primzahlen", [r["summe_primzahlen"] for r in results])
    for r in results:
        print(f"  {r['name']}: {r['primzahlen']}")

    # Paritaet
    print("\n--- GERADE/UNGERADE ---")
    print_row("Anzahl gerade", [r["anzahl_gerade"] for r in results])
    print_row("Anzahl ungerade", [r["anzahl_ungerade"] for r in results])
    print_row("Parity Ratio", [r["parity_ratio"] for r in results])

    # XOR
    print("\n--- XOR-ANALYSE ---")
    print_row("XOR alle Zahlen", [r["xor_alle"] for r in results])
    print_row("XOR mod 7", [r["xor_mod_7"] for r in results])
    for r in results:
        print(f"  {r['name']} XOR binaer: {r['xor_bin']}")

    # Teilbarkeit
    print("\n--- TEILBARKEIT ---")
    print_row("Anzahl teilbar durch 3", [r["anzahl_teilbar_3"] for r in results])
    print_row("Anzahl teilbar durch 5", [r["anzahl_teilbar_5"] for r in results])
    print_row("Anzahl teilbar durch 7", [r["anzahl_teilbar_7"] for r in results])

    # Dekaden
    print("\n--- DEKADEN-VERTEILUNG ---")
    for d in ["00-09", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69"]:
        print_row(f"Dekade {d}", [r["dekaden"][d] for r in results])

    # Differenzen
    print("\n--- DIFFERENZEN (sortiert) ---")
    print_row("Max Differenz", [r["max_diff"] for r in results])
    print_row("Min Differenz", [r["min_diff"] for r in results])
    for r in results:
        print(f"  {r['name']}: {r['differenzen']}")

    # Spezielle Checksummen
    print("\n--- SPEZIELLE CHECKSUMMEN ---")
    print_row("Luhn-like", [r["luhn_like"] for r in results])
    print_row("Luhn-like mod 10", [r["luhn_like_mod_10"] for r in results])
    print_row("Fletcher-like", [r["fletcher_like"] for r in results])
    print_row("Fletcher mod 255", [r["fletcher_like_mod_255"] for r in results])

    # Bit-Analyse
    print("\n--- BIT-ANALYSE ---")
    print_row("Gesetzte Bits gesamt", [r["gesetzte_bits_gesamt"] for r in results])

    # Zusammenfassung: Gemeinsame Muster
    print("\n" + "=" * 80)
    print("ZUSAMMENFASSUNG: GEMEINSAME MUSTER")
    print("=" * 80)

    patterns = find_common_patterns(results)

    print("\n--- EXAKT GLEICHE WERTE ---")
    found_exact = False
    for key, val in patterns.items():
        if isinstance(val, dict) and val.get("status") == "EXAKT GLEICH":
            print(f"  {key}: {val['wert']}")
            found_exact = True

    if not found_exact:
        print("  (Keine exakt gleichen Werte gefunden)")

    print("\n--- AUFFAELLIGE MUSTER ---")

    # Manuelle Muster-Checks
    summen = [r["summe"] for r in results]
    print(f"\n  Summen: {summen}")
    print(f"    -> Bereich: {min(summen)} bis {max(summen)}")
    print(f"    -> Durchschnitt: {sum(summen)/3:.1f}")
    print(f"    -> Alle im Bereich 330-420? {all(330 <= s <= 420 for s in summen)}")

    # Quersummen-Muster
    qs = [r["quersumme_gesamt"] for r in results]
    print(f"\n  Quersummen: {qs}")
    print(f"    -> Durchschnitt: {sum(qs)/3:.1f}")

    # Primzahl-Muster
    pz = [r["anzahl_primzahlen"] for r in results]
    print(f"\n  Anzahl Primzahlen: {pz}")
    print(f"    -> Bereich: {min(pz)} bis {max(pz)}")

    # XOR-Muster
    xors = [r["xor_alle"] for r in results]
    print(f"\n  XOR-Werte: {xors}")
    print(f"    -> XOR mod 8: {[x % 8 for x in xors]}")
    print(f"    -> XOR mod 16: {[x % 16 for x in xors]}")

    # Dekaden-Balance
    print("\n  Dekaden-Balance:")
    for r in results:
        dek = r["dekaden"]
        non_zero = [k for k, v in dek.items() if v > 0]
        print(f"    {r['name']}: {len(non_zero)} Dekaden besetzt, Verteilung: {list(dek.values())[:7]}")

    # Tiefere Muster-Suche
    print("\n--- TIEFERE MUSTER-SUCHE ---")

    # Summe der Ziffern pro Position
    print("\n  Ziffernanalyse:")
    for r in results:
        einer = sum(z % 10 for z in r["kombination"])
        zehner = sum(z // 10 for z in r["kombination"])
        print(f"    {r['name']}: Summe Einer={einer}, Summe Zehner={zehner}, Verhaeltnis={einer/max(zehner,1):.2f}")

    # Abstand zum theoretischen Durchschnitt
    # Bei 10 aus 70: Erwarteter Durchschnitt = 35.5, Erwartete Summe = 355
    print("\n  Abweichung vom Erwartungswert (355):")
    for r in results:
        abw = r["summe"] - 355
        print(f"    {r['name']}: {abw:+d} ({abw/355*100:+.1f}%)")


if __name__ == "__main__":
    main()
