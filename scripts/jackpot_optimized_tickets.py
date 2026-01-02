"""
Jackpot-Optimierte Ticket-Generierung.

Nutzt die Erkenntnisse aus der Jackpot-Analyse:
1. Universelle Constraints der Gewinner
2. Ueberrepraesentierte Zahlen an Jackpot-Tagen
3. Vermeidung von unterrepraesentierten Zahlen
4. Birthday-Vermeidung
"""

from itertools import combinations
import random
from collections import Counter
import json
from pathlib import Path
from datetime import datetime


# Aus der Analyse: Ueberrepraesentiert an Jackpot-Tagen
JACKPOT_FAVORITES = [43, 51, 52, 36, 40, 19, 38, 4, 61, 69, 62, 13, 8, 35, 45, 17, 46, 58, 64, 30]

# Aus der Analyse: Unterrepraesentiert an Jackpot-Tagen (VERMEIDEN!)
JACKPOT_AVOID = [1, 16, 21, 27, 29, 37, 67, 25, 68, 28]

# Birthday-Zahlen (1-31) - bei Gewinnern unterrepraesentiert
BIRTHDAY_NUMBERS = set(range(1, 32))

# Hohe Zahlen (>50) - bei Gewinnern ueberrepraesentiert
HIGH_NUMBERS = set(range(51, 71))


def ziffernprodukt_mod9(combo: list[int]) -> int:
    """Berechnet Ziffernprodukt mod 9."""
    produkt = 1
    for z in combo:
        for d in str(z):
            if d != '0':
                produkt *= int(d)
    return produkt % 9


def check_constraints(combo: list[int]) -> dict:
    """Prueft alle Constraints und gibt Details zurueck."""
    results = {}

    # 1. Ziffernprodukt mod 9 = 0
    zp = ziffernprodukt_mod9(combo)
    results['ziffernprodukt_mod9'] = zp == 0
    results['ziffernprodukt_value'] = zp

    # 2. Genau 1 einstellige Zahl
    einstellig = sum(1 for z in combo if z <= 9)
    results['einstellig_ok'] = einstellig == 1
    results['einstellig_count'] = einstellig

    # 3. Dekaden-Verteilung (6 von 7 besetzt bei 10er Ticket)
    dekaden = len(set(z // 10 for z in combo))
    results['dekaden'] = dekaden
    results['dekaden_ok'] = dekaden >= 5  # Flexibler fuer kleinere Tickets

    # 4. Alle 3 Drittel besetzt
    drittel_1 = any(1 <= z <= 23 for z in combo)
    drittel_2 = any(24 <= z <= 46 for z in combo)
    drittel_3 = any(47 <= z <= 70 for z in combo)
    results['alle_drittel'] = drittel_1 and drittel_2 and drittel_3

    # 5. Keine Endziffer 1
    endziffer_1 = sum(1 for z in combo if z % 10 == 1)
    results['keine_endziffer_1'] = endziffer_1 == 0
    results['endziffer_1_count'] = endziffer_1

    # 6. Birthday-Anteil (weniger = besser)
    birthday = sum(1 for z in combo if z <= 31)
    results['birthday_count'] = birthday
    results['birthday_ratio'] = birthday / len(combo)

    # 7. Jackpot-Favorites
    favorites = sum(1 for z in combo if z in JACKPOT_FAVORITES)
    results['favorites_count'] = favorites

    # 8. Jackpot-Avoid
    avoid = sum(1 for z in combo if z in JACKPOT_AVOID)
    results['avoid_count'] = avoid

    return results


def generate_optimized_ticket(size: int = 10, strategy: str = "balanced") -> list[int]:
    """
    Generiert ein optimiertes Ticket basierend auf Jackpot-Mustern.

    Strategien:
    - "balanced": Ausgewogene Mischung aller Faktoren
    - "anti_birthday": Maximale Birthday-Vermeidung
    - "favorites": Maximale Jackpot-Favorites
    - "constraints": Fokus auf universelle Constraints
    """

    best_ticket = None
    best_score = -1

    # Generiere viele Kandidaten und waehle den besten
    for _ in range(10000):
        # Basis-Pool: Alle Zahlen ausser Avoid-Zahlen
        pool = [z for z in range(1, 71) if z not in JACKPOT_AVOID]

        if strategy == "anti_birthday":
            # Stark gewichtet gegen Birthday
            weights = [0.3 if z <= 31 else 1.0 for z in pool]
        elif strategy == "favorites":
            # Stark gewichtet fuer Favorites
            weights = [3.0 if z in JACKPOT_FAVORITES else 1.0 for z in pool]
        elif strategy == "constraints":
            # Gleichmaessig, aber keine Endziffer 1
            pool = [z for z in pool if z % 10 != 1]
            weights = [1.0] * len(pool)
        else:  # balanced
            weights = []
            for z in pool:
                w = 1.0
                if z in JACKPOT_FAVORITES:
                    w *= 2.0
                if z <= 31:
                    w *= 0.5
                if z > 50:
                    w *= 1.5
                if z % 10 == 1:
                    w *= 0.3
                weights.append(w)

        # Normalisiere Gewichte
        total = sum(weights)
        weights = [w/total for w in weights]

        # Ziehe Ticket
        try:
            ticket = list(random.choices(pool, weights=weights, k=size))
            ticket = list(set(ticket))  # Entferne Duplikate

            while len(ticket) < size:
                extra = random.choices(pool, weights=weights, k=1)[0]
                if extra not in ticket:
                    ticket.append(extra)

            ticket = sorted(ticket[:size])
        except:
            continue

        # Bewerte Ticket
        checks = check_constraints(ticket)

        score = 0

        # Universelle Constraints (WICHTIG)
        if checks['ziffernprodukt_mod9']:
            score += 3
        if checks['einstellig_ok']:
            score += 2
        if checks['alle_drittel']:
            score += 2
        if checks['keine_endziffer_1']:
            score += 2

        # Jackpot-Muster
        score += checks['favorites_count'] * 0.5
        score -= checks['avoid_count'] * 1.0
        score -= checks['birthday_count'] * 0.3

        # Hohe Zahlen Bonus
        high = sum(1 for z in ticket if z > 50)
        score += high * 0.3

        if score > best_score:
            best_score = score
            best_ticket = ticket

    return best_ticket


def generate_ticket_portfolio(num_tickets: int = 5, ticket_size: int = 10) -> list[dict]:
    """Generiert ein Portfolio von optimierten Tickets."""

    portfolio = []
    strategies = ["balanced", "anti_birthday", "favorites", "constraints", "balanced"]

    for i in range(num_tickets):
        strategy = strategies[i % len(strategies)]
        ticket = generate_optimized_ticket(ticket_size, strategy)
        checks = check_constraints(ticket)

        portfolio.append({
            "ticket": ticket,
            "strategy": strategy,
            "constraints": checks,
        })

    return portfolio


def main():
    print("=" * 70)
    print("JACKPOT-OPTIMIERTE TICKET-GENERIERUNG")
    print("=" * 70)
    print(f"\nDatum: {datetime.now().strftime('%d.%m.%Y')}")

    print("""
BASIEREND AUF ANALYSE-ERKENNTNISSEN:

1. BEVORZUGTE ZAHLEN (Jackpot-Favorites):
   43, 51, 52, 36, 40, 19, 38, 4, 61, 69, 62, 13, 8, 35, 45

2. VERMIEDENE ZAHLEN (Jackpot-Avoid):
   1, 16, 21, 27, 29, 37, 67, 25, 68, 28

3. UNIVERSELLE CONSTRAINTS:
   - Ziffernprodukt mod 9 = 0
   - Genau 1 einstellige Zahl
   - Alle 3 Drittel besetzt (1-23, 24-46, 47-70)
   - Keine Endziffer 1

4. JACKPOT-MUSTER:
   - Wenig Birthday-Zahlen (1-31)
   - Mehr hohe Zahlen (>50)
""")

    # Generiere Tickets fuer verschiedene Typen
    for ticket_type in [6, 7, 8, 9, 10]:
        print(f"\n{'='*70}")
        print(f"TYP {ticket_type} - EMPFOHLENE TICKETS")
        print(f"{'='*70}")

        portfolio = generate_ticket_portfolio(3, ticket_type)

        for i, p in enumerate(portfolio):
            ticket = p['ticket']
            checks = p['constraints']

            # Status-Icons
            zp_ok = "✓" if checks['ziffernprodukt_mod9'] else "✗"
            ein_ok = "✓" if checks['einstellig_ok'] else "✗"
            drit_ok = "✓" if checks['alle_drittel'] else "✗"
            end_ok = "✓" if checks['keine_endziffer_1'] else "✗"

            print(f"\nTicket #{i+1} ({p['strategy']}): {ticket}")
            print(f"  Ziffernprod mod9={checks['ziffernprodukt_value']} {zp_ok} | "
                  f"Einstellig={checks['einstellig_count']} {ein_ok} | "
                  f"Drittel {drit_ok} | Endz1={checks['endziffer_1_count']} {end_ok}")
            print(f"  Birthday: {checks['birthday_count']}/{ticket_type} | "
                  f"Favorites: {checks['favorites_count']}/{ticket_type} | "
                  f"Avoid: {checks['avoid_count']}/{ticket_type}")

    # Beste Empfehlung
    print(f"\n\n{'='*70}")
    print("BESTE EMPFEHLUNG (Typ 10 - Maximale Jackpot-Chance)")
    print(f"{'='*70}")

    best_tickets = []
    for _ in range(100):
        ticket = generate_optimized_ticket(10, "balanced")
        checks = check_constraints(ticket)

        # Nur Tickets die ALLE Constraints erfuellen
        if (checks['ziffernprodukt_mod9'] and
            checks['einstellig_ok'] and
            checks['alle_drittel'] and
            checks['keine_endziffer_1']):

            score = (checks['favorites_count'] -
                    checks['avoid_count'] -
                    checks['birthday_count'] * 0.5)
            best_tickets.append((ticket, checks, score))

    if best_tickets:
        best_tickets.sort(key=lambda x: x[2], reverse=True)

        print("\nTop-3 Tickets die ALLE Constraints erfuellen:\n")
        for i, (ticket, checks, score) in enumerate(best_tickets[:3]):
            print(f"#{i+1}: {ticket}")
            print(f"    Score: {score:.1f} | Birthday: {checks['birthday_count']} | "
                  f"Favorites: {checks['favorites_count']} | Avoid: {checks['avoid_count']}")
    else:
        print("\nKeine perfekten Tickets gefunden. Generiere beste Alternative...")
        ticket = generate_optimized_ticket(10, "balanced")
        print(f"Empfehlung: {ticket}")

    # Speichern
    output = {
        "datum": datetime.now().isoformat(),
        "methode": "Jackpot-Optimierte Ticket-Generierung",
        "erkenntnisse": {
            "jackpot_favorites": JACKPOT_FAVORITES,
            "jackpot_avoid": JACKPOT_AVOID,
            "constraints": [
                "Ziffernprodukt mod 9 = 0",
                "Genau 1 einstellige Zahl",
                "Alle 3 Drittel besetzt",
                "Keine Endziffer 1",
            ],
        },
        "empfehlungen": {
            "typ_10": [t[0] for t in best_tickets[:3]] if best_tickets else [],
        }
    }

    output_path = Path("C:/Users/kenfu/Documents/keno_base/results/jackpot_optimized_tickets.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    return best_tickets


if __name__ == "__main__":
    main()
