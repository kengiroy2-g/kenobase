#!/usr/bin/env python3
"""
Geometrische/Raeumliche Analyse von KENO-Gewinner-Kombinationen.

Analysiert:
1. Zeilen-Verteilung
2. Spalten-Verteilung
3. Diagonalen
4. Cluster
5. Symmetrie
6. Manhattan-Distanz
7. Konvexe Huelle
8. Zentroid
"""

import json
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class GridPosition:
    """Position auf dem KENO-Spielschein (7x10 Grid)."""
    number: int
    row: int  # 0-6
    col: int  # 0-9

    @classmethod
    def from_number(cls, n: int) -> "GridPosition":
        """Konvertiere KENO-Zahl (1-70) zu Grid-Position."""
        row = (n - 1) // 10
        col = (n - 1) % 10
        return cls(number=n, row=row, col=col)


def number_to_position(n: int) -> tuple[int, int]:
    """Konvertiere KENO-Zahl zu (row, col) Position."""
    row = (n - 1) // 10
    col = (n - 1) % 10
    return (row, col)


def analyze_row_distribution(numbers: list[int]) -> dict[str, Any]:
    """Analysiere Zeilen-Verteilung."""
    rows = [number_to_position(n)[0] for n in numbers]
    row_counts = Counter(rows)

    # Zeilen-Namen
    row_names = {
        0: "Zeile 1 (1-10)",
        1: "Zeile 2 (11-20)",
        2: "Zeile 3 (21-30)",
        3: "Zeile 4 (31-40)",
        4: "Zeile 5 (41-50)",
        5: "Zeile 6 (51-60)",
        6: "Zeile 7 (61-70)"
    }

    distribution = {row_names[i]: row_counts.get(i, 0) for i in range(7)}

    # Statistiken
    counts = list(row_counts.values())
    max_per_row = max(counts) if counts else 0
    min_per_row = min(counts) if counts else 0
    empty_rows = 7 - len(row_counts)

    return {
        "distribution": distribution,
        "max_per_row": max_per_row,
        "min_per_row": min_per_row,
        "empty_rows": empty_rows,
        "rows_used": len(row_counts),
        "spread_ratio": len(row_counts) / 7  # 1.0 = alle Zeilen belegt
    }


def analyze_column_distribution(numbers: list[int]) -> dict[str, Any]:
    """Analysiere Spalten-Verteilung."""
    cols = [number_to_position(n)[1] for n in numbers]
    col_counts = Counter(cols)

    distribution = {f"Spalte {i+1}": col_counts.get(i, 0) for i in range(10)}

    counts = list(col_counts.values())
    max_per_col = max(counts) if counts else 0
    min_per_col = min(counts) if counts else 0
    empty_cols = 10 - len(col_counts)

    return {
        "distribution": distribution,
        "max_per_col": max_per_col,
        "min_per_col": min_per_col,
        "empty_cols": empty_cols,
        "cols_used": len(col_counts),
        "spread_ratio": len(col_counts) / 10
    }


def analyze_diagonals(numbers: list[int]) -> dict[str, Any]:
    """Analysiere Diagonalen-Muster."""
    positions = [number_to_position(n) for n in numbers]

    # Hauptdiagonalen (links-oben nach rechts-unten): row - col = konstant
    main_diags = Counter([pos[0] - pos[1] for pos in positions])

    # Nebendiagonalen (rechts-oben nach links-unten): row + col = konstant
    anti_diags = Counter([pos[0] + pos[1] for pos in positions])

    # Finde Diagonalen mit mehreren Zahlen
    main_diag_clusters = {k: v for k, v in main_diags.items() if v >= 2}
    anti_diag_clusters = {k: v for k, v in anti_diags.items() if v >= 2}

    # Zahlen auf gleicher Diagonale finden
    main_diag_numbers = {}
    for diag_id, count in main_diag_clusters.items():
        nums = [n for n in numbers if number_to_position(n)[0] - number_to_position(n)[1] == diag_id]
        main_diag_numbers[f"diag_{diag_id}"] = nums

    anti_diag_numbers = {}
    for diag_id, count in anti_diag_clusters.items():
        nums = [n for n in numbers if number_to_position(n)[0] + number_to_position(n)[1] == diag_id]
        anti_diag_numbers[f"anti_diag_{diag_id}"] = nums

    return {
        "main_diagonal_clusters": main_diag_numbers,
        "anti_diagonal_clusters": anti_diag_numbers,
        "total_main_diagonal_pairs": sum(v for v in main_diags.values() if v >= 2),
        "total_anti_diagonal_pairs": sum(v for v in anti_diags.values() if v >= 2),
        "diagonal_score": len(main_diag_clusters) + len(anti_diag_clusters)
    }


def analyze_clusters(numbers: list[int]) -> dict[str, Any]:
    """Analysiere raeumliche Haeufungen (Cluster)."""
    positions = [number_to_position(n) for n in numbers]

    # Finde direkte Nachbarn (Manhattan-Distanz = 1)
    neighbors = []
    for i, (r1, c1) in enumerate(positions):
        for j, (r2, c2) in enumerate(positions):
            if i < j:
                dist = abs(r1 - r2) + abs(c1 - c2)
                if dist == 1:
                    neighbors.append((numbers[i], numbers[j]))

    # Finde 2x2 Bloecke
    blocks_2x2 = []
    for n in numbers:
        r, c = number_to_position(n)
        # Pruefe ob 2x2 Block existiert
        block = [n]
        for dr, dc in [(0, 1), (1, 0), (1, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 7 and 0 <= nc < 10:
                candidate = nr * 10 + nc + 1
                if candidate in numbers:
                    block.append(candidate)
        if len(block) >= 3:
            blocks_2x2.append(sorted(block))

    # Entferne Duplikate
    blocks_2x2 = list(set(tuple(b) for b in blocks_2x2))

    # Finde horizontale/vertikale Sequenzen
    horizontal_sequences = []
    vertical_sequences = []

    for n in numbers:
        r, c = number_to_position(n)
        # Horizontal
        h_seq = [n]
        for dc in [1, 2, 3]:
            if c + dc < 10 and (r * 10 + (c + dc) + 1) in numbers:
                h_seq.append(r * 10 + (c + dc) + 1)
        if len(h_seq) >= 2:
            horizontal_sequences.append(h_seq)

        # Vertikal
        v_seq = [n]
        for dr in [1, 2, 3]:
            if r + dr < 7 and ((r + dr) * 10 + c + 1) in numbers:
                v_seq.append((r + dr) * 10 + c + 1)
        if len(v_seq) >= 2:
            vertical_sequences.append(v_seq)

    return {
        "direct_neighbors": neighbors,
        "neighbor_count": len(neighbors),
        "blocks_2x2": [list(b) for b in blocks_2x2],
        "horizontal_sequences": horizontal_sequences,
        "vertical_sequences": vertical_sequences,
        "cluster_density": len(neighbors) / max(len(numbers), 1)
    }


def analyze_symmetry(numbers: list[int]) -> dict[str, Any]:
    """Analysiere Symmetrie-Eigenschaften."""
    positions = set(number_to_position(n) for n in numbers)

    # Horizontale Spiegelung (um Zeile 3.5)
    h_mirror_matches = 0
    for r, c in positions:
        mirror_r = 6 - r
        if (mirror_r, c) in positions:
            h_mirror_matches += 1

    # Vertikale Spiegelung (um Spalte 4.5)
    v_mirror_matches = 0
    for r, c in positions:
        mirror_c = 9 - c
        if (r, mirror_c) in positions:
            v_mirror_matches += 1

    # Punkt-Symmetrie (um Zentrum 3.5, 4.5)
    point_mirror_matches = 0
    for r, c in positions:
        mirror_r, mirror_c = 6 - r, 9 - c
        if (mirror_r, mirror_c) in positions:
            point_mirror_matches += 1

    n = len(numbers)
    return {
        "horizontal_symmetry_score": h_mirror_matches / n if n > 0 else 0,
        "vertical_symmetry_score": v_mirror_matches / n if n > 0 else 0,
        "point_symmetry_score": point_mirror_matches / n if n > 0 else 0,
        "horizontal_mirror_pairs": h_mirror_matches // 2,
        "vertical_mirror_pairs": v_mirror_matches // 2,
        "point_mirror_pairs": point_mirror_matches // 2
    }


def analyze_manhattan_distances(numbers: list[int]) -> dict[str, Any]:
    """Berechne Manhattan-Distanzen zwischen allen Paaren."""
    positions = [number_to_position(n) for n in numbers]

    distances = []
    pair_distances = []
    for i, (r1, c1) in enumerate(positions):
        for j, (r2, c2) in enumerate(positions):
            if i < j:
                dist = abs(r1 - r2) + abs(c1 - c2)
                distances.append(dist)
                pair_distances.append({
                    "pair": (numbers[i], numbers[j]),
                    "distance": dist
                })

    if not distances:
        return {"error": "Keine Paare zum Analysieren"}

    # Sortiere nach Distanz
    pair_distances.sort(key=lambda x: x["distance"])

    return {
        "min_distance": min(distances),
        "max_distance": max(distances),
        "mean_distance": sum(distances) / len(distances),
        "median_distance": sorted(distances)[len(distances) // 2],
        "std_distance": (sum((d - sum(distances)/len(distances))**2 for d in distances) / len(distances)) ** 0.5,
        "closest_pairs": pair_distances[:5],
        "farthest_pairs": pair_distances[-5:],
        "distance_distribution": dict(Counter(distances))
    }


def analyze_convex_hull(numbers: list[int]) -> dict[str, Any]:
    """Berechne konvexe Huelle und deren Flaeche."""
    positions = [number_to_position(n) for n in numbers]

    def cross(O, A, B):
        return (A[0] - O[0]) * (B[1] - O[1]) - (A[1] - O[1]) * (B[0] - O[0])

    # Andrew's monotone chain algorithm
    points = sorted(set(positions))
    if len(points) <= 2:
        return {"area": 0, "perimeter": 0, "hull_points": len(points)}

    # Build lower hull
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    # Build upper hull
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    hull = lower[:-1] + upper[:-1]

    # Flaeche (Shoelace formula)
    n = len(hull)
    area = 0
    for i in range(n):
        j = (i + 1) % n
        area += hull[i][0] * hull[j][1]
        area -= hull[j][0] * hull[i][1]
    area = abs(area) / 2

    # Umfang
    perimeter = 0
    for i in range(n):
        j = (i + 1) % n
        perimeter += math.sqrt((hull[j][0] - hull[i][0])**2 + (hull[j][1] - hull[i][1])**2)

    # Konvertiere Hull-Punkte zu Zahlen
    hull_numbers = []
    for r, c in hull:
        num = r * 10 + c + 1
        if num in numbers:
            hull_numbers.append(num)

    return {
        "area": area,
        "perimeter": round(perimeter, 2),
        "hull_points_count": len(hull),
        "hull_numbers": hull_numbers,
        "bounding_box": {
            "min_row": min(p[0] for p in positions),
            "max_row": max(p[0] for p in positions),
            "min_col": min(p[1] for p in positions),
            "max_col": max(p[1] for p in positions)
        },
        "fill_ratio": len(numbers) / max(area, 1)  # Wie dicht sind Punkte in der Huelle?
    }


def analyze_centroid(numbers: list[int]) -> dict[str, Any]:
    """Berechne Schwerpunkt (Zentroid) der Zahlen."""
    positions = [number_to_position(n) for n in numbers]

    if not positions:
        return {"error": "Keine Zahlen"}

    centroid_row = sum(p[0] for p in positions) / len(positions)
    centroid_col = sum(p[1] for p in positions) / len(positions)

    # Grid-Zentrum ist (3, 4.5)
    grid_center = (3, 4.5)

    # Distanz zum Grid-Zentrum
    dist_to_center = math.sqrt((centroid_row - grid_center[0])**2 + (centroid_col - grid_center[1])**2)

    # Quadrant-Analyse
    quadrant_counts = {
        "oben_links": 0,
        "oben_rechts": 0,
        "unten_links": 0,
        "unten_rechts": 0
    }
    for r, c in positions:
        if r < 3.5:
            if c < 5:
                quadrant_counts["oben_links"] += 1
            else:
                quadrant_counts["oben_rechts"] += 1
        else:
            if c < 5:
                quadrant_counts["unten_links"] += 1
            else:
                quadrant_counts["unten_rechts"] += 1

    return {
        "centroid": {
            "row": round(centroid_row, 2),
            "col": round(centroid_col, 2),
            "approx_number": int(round(centroid_row) * 10 + round(centroid_col) + 1)
        },
        "grid_center": {"row": 3, "col": 4.5},
        "distance_to_grid_center": round(dist_to_center, 2),
        "quadrant_distribution": quadrant_counts,
        "balance_score": 1 - (dist_to_center / 5)  # 1 = perfekt zentriert
    }


def visualize_grid(numbers: list[int], name: str) -> str:
    """Erstelle ASCII-Visualisierung des Spielscheins."""
    lines = [f"\n=== {name} ==="]
    lines.append("    " + "  ".join(f"{i:2d}" for i in range(1, 11)))
    lines.append("   " + "-" * 33)

    for row in range(7):
        row_nums = []
        for col in range(10):
            num = row * 10 + col + 1
            if num in numbers:
                row_nums.append(f"[{num:2d}]")
            else:
                row_nums.append(f" {num:2d} ")
        lines.append(f"R{row+1} |" + "".join(row_nums))

    return "\n".join(lines)


def analyze_combination(numbers: list[int], name: str) -> dict[str, Any]:
    """Fuehre vollstaendige geometrische Analyse durch."""
    return {
        "name": name,
        "numbers": numbers,
        "count": len(numbers),
        "visualization": visualize_grid(numbers, name),
        "row_distribution": analyze_row_distribution(numbers),
        "column_distribution": analyze_column_distribution(numbers),
        "diagonals": analyze_diagonals(numbers),
        "clusters": analyze_clusters(numbers),
        "symmetry": analyze_symmetry(numbers),
        "manhattan_distances": analyze_manhattan_distances(numbers),
        "convex_hull": analyze_convex_hull(numbers),
        "centroid": analyze_centroid(numbers)
    }


def find_invariants(analyses: list[dict]) -> dict[str, Any]:
    """Suche nach geometrischen Invarianten ueber alle Kombinationen."""
    invariants = {
        "potential_anti_patterns": [],
        "common_properties": [],
        "statistical_summary": {}
    }

    # Extrahiere Metriken
    row_spreads = [a["row_distribution"]["spread_ratio"] for a in analyses]
    col_spreads = [a["column_distribution"]["spread_ratio"] for a in analyses]
    neighbor_counts = [a["clusters"]["neighbor_count"] for a in analyses]
    mean_distances = [a["manhattan_distances"]["mean_distance"] for a in analyses]
    hull_areas = [a["convex_hull"]["area"] for a in analyses]
    centroids_dist = [a["centroid"]["distance_to_grid_center"] for a in analyses]

    invariants["statistical_summary"] = {
        "row_spread": {
            "mean": sum(row_spreads) / len(row_spreads),
            "min": min(row_spreads),
            "max": max(row_spreads),
            "all_values": row_spreads
        },
        "col_spread": {
            "mean": sum(col_spreads) / len(col_spreads),
            "min": min(col_spreads),
            "max": max(col_spreads),
            "all_values": col_spreads
        },
        "neighbor_count": {
            "mean": sum(neighbor_counts) / len(neighbor_counts),
            "min": min(neighbor_counts),
            "max": max(neighbor_counts),
            "all_values": neighbor_counts
        },
        "mean_manhattan_distance": {
            "mean": sum(mean_distances) / len(mean_distances),
            "min": min(mean_distances),
            "max": max(mean_distances),
            "all_values": mean_distances
        },
        "convex_hull_area": {
            "mean": sum(hull_areas) / len(hull_areas),
            "min": min(hull_areas),
            "max": max(hull_areas),
            "all_values": hull_areas
        },
        "centroid_distance": {
            "mean": sum(centroids_dist) / len(centroids_dist),
            "min": min(centroids_dist),
            "max": max(centroids_dist),
            "all_values": centroids_dist
        }
    }

    # Identifiziere potenzielle Anti-Patterns

    # 1. Hohe Zeilen-Streuung (alle Gewinner nutzen viele Zeilen)
    if all(s >= 0.7 for s in row_spreads):
        invariants["potential_anti_patterns"].append({
            "name": "HOHE_ZEILEN_STREUUNG",
            "description": "Alle Gewinner nutzen mindestens 70% der Zeilen",
            "threshold": 0.7,
            "values": row_spreads,
            "engineering_note": "Ein Ingenieur koennte Kombinationen mit zu wenig Zeilen-Streuung als 'unnatuerlich' markieren"
        })

    # 2. Hohe Spalten-Streuung
    if all(s >= 0.6 for s in col_spreads):
        invariants["potential_anti_patterns"].append({
            "name": "HOHE_SPALTEN_STREUUNG",
            "description": "Alle Gewinner nutzen mindestens 60% der Spalten",
            "threshold": 0.6,
            "values": col_spreads,
            "engineering_note": "Vermeidung von 'Spalten-Clustern' koennte als Anti-Pattern dienen"
        })

    # 3. Niedrige Nachbar-Dichte
    if all(n <= 3 for n in neighbor_counts):
        invariants["potential_anti_patterns"].append({
            "name": "GERINGE_NACHBAR_DICHTE",
            "description": "Maximal 3 direkte Nachbar-Paare",
            "threshold": 3,
            "values": neighbor_counts,
            "engineering_note": "Zu viele Nachbarn wirken 'kuenstlich' - Gewinner meiden Cluster"
        })

    # 4. Mindest-Manhattan-Distanz
    if all(d >= 4.5 for d in mean_distances):
        invariants["potential_anti_patterns"].append({
            "name": "MINDEST_DISTANZ",
            "description": "Mittlere Manhattan-Distanz >= 4.5",
            "threshold": 4.5,
            "values": mean_distances,
            "engineering_note": "Zahlen muessen 'verstreut' sein fuer natuerliche Optik"
        })

    # 5. Konvexe-Huelle-Mindestflaeche
    if all(a >= 20 for a in hull_areas):
        invariants["potential_anti_patterns"].append({
            "name": "MINDEST_HUELLE_FLAECHE",
            "description": "Konvexe Huelle >= 20 Flaechen-Einheiten",
            "threshold": 20,
            "values": hull_areas,
            "engineering_note": "Kombination muss das Grid 'aufspannen'"
        })

    # 6. Zentroid nahe Mitte
    if all(d <= 2.0 for d in centroids_dist):
        invariants["potential_anti_patterns"].append({
            "name": "ZENTROID_NAHE_MITTE",
            "description": "Schwerpunkt maximal 2 Einheiten vom Grid-Zentrum",
            "threshold": 2.0,
            "values": centroids_dist,
            "engineering_note": "Ausgewogene Kombinationen haben Schwerpunkt nahe der Mitte"
        })

    # Gemeinsame Eigenschaften
    for a in analyses:
        # Pruefe auf Muster in Diagonalen
        if a["diagonals"]["diagonal_score"] >= 2:
            invariants["common_properties"].append({
                "name": a["name"],
                "property": "DIAGONAL_MUSTER",
                "detail": f"Diagonal-Score: {a['diagonals']['diagonal_score']}"
            })

        # Pruefe Quadranten-Balance
        quads = a["centroid"]["quadrant_distribution"]
        quad_values = list(quads.values())
        if max(quad_values) - min(quad_values) <= 4:
            invariants["common_properties"].append({
                "name": a["name"],
                "property": "QUADRANTEN_BALANCE",
                "detail": f"Differenz max-min: {max(quad_values) - min(quad_values)}"
            })

    return invariants


def main():
    """Hauptfunktion."""
    # Die 3 verifizierten Gewinner-Kombinationen
    winners = [
        {"name": "Kyritz", "numbers": [5, 12, 20, 26, 34, 36, 42, 45, 48, 66]},
        {"name": "Oberbayern", "numbers": [3, 15, 18, 27, 47, 53, 54, 55, 66, 68]},
        {"name": "Nordsachsen", "numbers": [9, 19, 37, 38, 43, 45, 48, 57, 59, 67]}
    ]

    # Analysiere jede Kombination
    analyses = []
    for winner in winners:
        analysis = analyze_combination(winner["numbers"], winner["name"])
        analyses.append(analysis)
        print(analysis["visualization"])

    # Finde Invarianten
    invariants = find_invariants(analyses)

    # Erstelle Gesamtbericht
    result = {
        "metadata": {
            "analysis_type": "Geometrische/Raeumliche Muster-Analyse",
            "grid_dimensions": "7 Zeilen x 10 Spalten",
            "total_combinations_analyzed": len(winners),
            "keno_layout": {
                "rows": 7,
                "cols": 10,
                "total_numbers": 70
            }
        },
        "individual_analyses": analyses,
        "cross_combination_invariants": invariants,
        "engineering_hypothesis": {
            "summary": "Potenzielle Anti-Pattern-Kriterien die ein Ingenieur nutzen koennte",
            "criteria": [
                {
                    "criterion": "Zeilen-Streuung",
                    "min_threshold": 0.7,
                    "rationale": "Natuerliche Kombinationen nutzen viele Zeilen"
                },
                {
                    "criterion": "Spalten-Streuung",
                    "min_threshold": 0.6,
                    "rationale": "Vermeidung von vertikalen Clustern"
                },
                {
                    "criterion": "Nachbar-Limit",
                    "max_threshold": 3,
                    "rationale": "Zu viele Nachbarn wirken kuenstlich"
                },
                {
                    "criterion": "Mittlere Distanz",
                    "min_threshold": 4.5,
                    "rationale": "Zahlen muessen verstreut sein"
                },
                {
                    "criterion": "Huelle-Flaeche",
                    "min_threshold": 20,
                    "rationale": "Kombination muss Grid aufspannen"
                },
                {
                    "criterion": "Zentroid-Distanz",
                    "max_threshold": 2.0,
                    "rationale": "Schwerpunkt nahe der Mitte"
                }
            ]
        }
    }

    # Speichern
    output_path = Path("C:/Users/kenfu/Documents/keno_base/results/geometric_analysis.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Entferne nicht-serialisierbare Teile fuer JSON
    for analysis in result["individual_analyses"]:
        # Konvertiere Tuple-Keys zu Strings
        if "closest_pairs" in analysis["manhattan_distances"]:
            for pair in analysis["manhattan_distances"]["closest_pairs"]:
                pair["pair"] = list(pair["pair"])
        if "farthest_pairs" in analysis["manhattan_distances"]:
            for pair in analysis["manhattan_distances"]["farthest_pairs"]:
                pair["pair"] = list(pair["pair"])

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    # Zusammenfassung ausgeben
    print("\n" + "=" * 60)
    print("ZUSAMMENFASSUNG: Potenzielle geometrische Anti-Patterns")
    print("=" * 60)

    for ap in invariants["potential_anti_patterns"]:
        print(f"\n{ap['name']}:")
        print(f"  Beschreibung: {ap['description']}")
        print(f"  Schwellwert: {ap['threshold']}")
        print(f"  Engineering-Note: {ap['engineering_note']}")

    return result


if __name__ == "__main__":
    main()
