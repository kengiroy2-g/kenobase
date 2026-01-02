#!/usr/bin/env python3
"""
VALIDIERUNG: Pool-Hits gegen echte GK-Gewinner (Keno_GQ)

Prueft ob an Tagen mit 8/9/10 Pool-Treffern tatsaechlich
GK8/9/10 Gewinner existierten.
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

def load_gq_data(filepath: Path) -> dict:
    """Laedt Keno_GQ Gewinnklassen-Daten."""
    data = defaultdict(lambda: defaultdict(dict))

    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                datum = row.get("Datum", "").strip()
                keno_typ = int(row.get("Keno-Typ", 0))
                richtige = int(row.get("Anzahl richtiger Zahlen", 0))
                gewinner_str = row.get("Anzahl der Gewinner", "0").replace(".", "")
                gewinner = int(gewinner_str) if gewinner_str else 0

                # Speichere: data[datum][typ][richtige] = gewinner
                data[datum][keno_typ][richtige] = gewinner
            except Exception as e:
                continue

    return dict(data)


def main():
    base_path = Path(__file__).parent.parent

    # Lade GQ-Daten fuer 2025
    gq_path = base_path / "Keno_GPTs/Keno_GQ_2025.csv"
    gq_data = load_gq_data(gq_path)

    print("=" * 80)
    print("VALIDIERUNG: Pool-Hits vs. Echte GK-Gewinner")
    print("=" * 80)
    print()
    print(f"GQ-Daten geladen: {len(gq_data)} Tage")
    print()

    # Unsere Big Hits aus der Pool-Analyse
    big_hits = [
        {"datum": "05.01.2025", "pool_hits": 8, "zahlen": [24, 30, 33, 34, 36, 54, 62, 64]},
        {"datum": "15.01.2025", "pool_hits": 8, "zahlen": [4, 12, 24, 33, 34, 36, 61, 62]},
        {"datum": "09.02.2025", "pool_hits": 8, "zahlen": [7, 10, 12, 19, 32, 44, 56, 57]},
        {"datum": "23.02.2025", "pool_hits": 8, "zahlen": [16, 17, 20, 32, 34, 38, 45, 51]},
        {"datum": "26.02.2025", "pool_hits": 8, "zahlen": [16, 17, 19, 44, 47, 51, 56, 57]},
        {"datum": "09.04.2025", "pool_hits": 8, "zahlen": [1, 6, 7, 11, 24, 35, 45, 61]},
        {"datum": "15.04.2025", "pool_hits": 9, "zahlen": [1, 5, 8, 11, 24, 45, 50, 60, 61]},
        {"datum": "04.05.2025", "pool_hits": 8, "zahlen": [3, 9, 14, 19, 26, 65, 66, 70]},
        {"datum": "06.07.2025", "pool_hits": 8, "zahlen": [1, 8, 26, 29, 35, 56, 63, 67]},
        {"datum": "17.07.2025", "pool_hits": 8, "zahlen": [1, 8, 9, 10, 35, 36, 44, 63]},
        {"datum": "19.07.2025", "pool_hits": 8, "zahlen": [6, 10, 29, 36, 53, 63, 67, 68]},
        {"datum": "30.07.2025", "pool_hits": 8, "zahlen": [6, 9, 10, 26, 29, 35, 36, 68]},
        {"datum": "21.10.2025", "pool_hits": 10, "zahlen": [8, 15, 20, 26, 29, 35, 42, 45, 47, 57]},
        {"datum": "27.10.2025", "pool_hits": 9, "zahlen": [15, 16, 26, 35, 42, 45, 57, 67, 68]},
        {"datum": "16.11.2025", "pool_hits": 8, "zahlen": [6, 13, 17, 46, 49, 57, 63, 66]},
        {"datum": "19.11.2025", "pool_hits": 10, "zahlen": [1, 6, 15, 17, 21, 39, 45, 46, 49, 66]},
        {"datum": "22.11.2025", "pool_hits": 8, "zahlen": [6, 17, 41, 45, 46, 57, 63, 66]},
        {"datum": "18.12.2025", "pool_hits": 8, "zahlen": [3, 7, 43, 44, 48, 49, 55, 63]},
        {"datum": "27.12.2025", "pool_hits": 9, "zahlen": [2, 3, 6, 7, 40, 43, 46, 48, 63]},
    ]

    # Analyse
    results = []
    validated_gk10 = []
    validated_gk9 = []
    validated_gk8 = []

    print("DETAILLIERTE ANALYSE:")
    print("=" * 80)

    for hit in big_hits:
        datum = hit["datum"]
        pool_hits = hit["pool_hits"]

        print(f"\n{datum} - Pool-Treffer: {pool_hits}")
        print(f"  Gezogene Pool-Zahlen: {hit['zahlen']}")
        print()

        if datum not in gq_data:
            print(f"  ⚠️  KEINE GQ-DATEN fuer diesen Tag!")
            results.append({
                "datum": datum,
                "pool_hits": pool_hits,
                "gq_available": False,
                "validated": None
            })
            continue

        day_data = gq_data[datum]

        # Zeige relevante GK-Gewinner
        print(f"  GK-GEWINNER an diesem Tag:")

        # Pruefe Typ 8
        if 8 in day_data:
            gk8_8 = day_data[8].get(8, 0)
            print(f"    Typ 8 - 8/8: {gk8_8} Gewinner {'✅' if gk8_8 > 0 else ''}")

        # Pruefe Typ 9
        if 9 in day_data:
            gk9_9 = day_data[9].get(9, 0)
            gk9_8 = day_data[9].get(8, 0)
            print(f"    Typ 9 - 9/9: {gk9_9} Gewinner {'✅ JACKPOT!' if gk9_9 > 0 else ''}")
            print(f"    Typ 9 - 8/9: {gk9_8} Gewinner")

        # Pruefe Typ 10
        if 10 in day_data:
            gk10_10 = day_data[10].get(10, 0)
            gk10_9 = day_data[10].get(9, 0)
            gk10_8 = day_data[10].get(8, 0)
            print(f"    Typ 10 - 10/10: {gk10_10} Gewinner {'✅ JACKPOT!' if gk10_10 > 0 else ''}")
            print(f"    Typ 10 - 9/10: {gk10_9} Gewinner")
            print(f"    Typ 10 - 8/10: {gk10_8} Gewinner")

        # Validierung
        validated = False
        validation_type = None

        if pool_hits >= 10 and 10 in day_data:
            if day_data[10].get(10, 0) > 0:
                validated = True
                validation_type = "GK10 (10/10)"
                validated_gk10.append(datum)

        if pool_hits >= 9 and 9 in day_data:
            if day_data[9].get(9, 0) > 0:
                validated = True
                validation_type = "GK9 (9/9)"
                validated_gk9.append(datum)

        if pool_hits >= 8 and 8 in day_data:
            if day_data[8].get(8, 0) > 0:
                validated = True
                validation_type = "GK8 (8/8)"
                validated_gk8.append(datum)

        if validated:
            print(f"\n  ✅ VALIDIERT: {validation_type} Gewinner existierte!")
        else:
            print(f"\n  ❌ Kein direkter GK{pool_hits} Gewinner an diesem Tag")

        results.append({
            "datum": datum,
            "pool_hits": pool_hits,
            "gq_available": True,
            "validated": validated,
            "validation_type": validation_type,
            "gk8_winners": day_data.get(8, {}).get(8, 0) if 8 in day_data else None,
            "gk9_winners": day_data.get(9, {}).get(9, 0) if 9 in day_data else None,
            "gk10_winners": day_data.get(10, {}).get(10, 0) if 10 in day_data else None,
        })

    # Zusammenfassung
    print()
    print("=" * 80)
    print("ZUSAMMENFASSUNG")
    print("=" * 80)
    print()

    total_hits = len(big_hits)
    with_data = len([r for r in results if r.get("gq_available")])
    validated = len([r for r in results if r.get("validated")])

    print(f"Big Hits (8+ Pool-Treffer):     {total_hits}")
    print(f"Mit GQ-Daten verfuegbar:        {with_data}")
    print(f"Validiert (echte GK-Gewinner):  {validated}")
    print()

    if validated_gk10:
        print(f"GK10 (10/10) validiert: {validated_gk10}")
    if validated_gk9:
        print(f"GK9 (9/9) validiert:    {validated_gk9}")
    if validated_gk8:
        print(f"GK8 (8/8) validiert:    {validated_gk8}")

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print()
    print("Ein 'validierter' Tag bedeutet:")
    print("- Unser Pool hatte 8/9/10 Treffer in der Ziehung")
    print("- UND tatsaechlich gab es GK8/9/10 Gewinner an diesem Tag")
    print()
    print("Dies bestaetigt, dass unser Pool an diesen Tagen")
    print("die richtigen Zahlen fuer hohe Gewinnklassen enthielt!")

    # Speichern
    output = {
        "analysis_date": datetime.now().isoformat(),
        "total_big_hits": total_hits,
        "with_gq_data": with_data,
        "validated_count": validated,
        "validated_gk10": validated_gk10,
        "validated_gk9": validated_gk9,
        "validated_gk8": validated_gk8,
        "detailed_results": results,
    }

    output_path = base_path / "results/pool_hits_gq_validation.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
