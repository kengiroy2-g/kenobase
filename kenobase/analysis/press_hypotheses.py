# kenobase/analysis/press_hypotheses.py
"""Generate hypotheses from KENO winner press releases."""

import json
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class HypothesisCandidate:
    """A candidate hypothesis generated from press release data."""

    id: str
    name: str
    category: str
    description: str
    evidence: list[str]
    supporting_data: dict
    confidence: float  # 0.0 - 1.0
    priority: str  # HOCH, MITTEL, NIEDRIG
    testable: bool
    acceptance_criteria: list[str]
    data_requirements: list[str]

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "evidence": self.evidence,
            "supporting_data": self.supporting_data,
            "confidence": self.confidence,
            "priority": self.priority,
            "testable": self.testable,
            "acceptance_criteria": self.acceptance_criteria,
            "data_requirements": self.data_requirements,
        }


@dataclass
class PressHypothesesResult:
    """Result of hypothesis generation from press data."""

    hypotheses: list[HypothesisCandidate]
    records_analyzed: int
    sources_analyzed: int
    timestamp: datetime = field(default_factory=datetime.now)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "records_analyzed": self.records_analyzed,
            "sources_analyzed": self.sources_analyzed,
            "hypotheses_generated": len(self.hypotheses),
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "warnings": self.warnings,
        }


class PressHypothesesGenerator:
    """Generate testable hypotheses from KENO winner press release data."""

    def __init__(self, min_records: int = 3):
        """Initialize the generator.

        Args:
            min_records: Minimum records needed for hypothesis generation
        """
        self.min_records = min_records

    def generate_from_file(self, json_path: Path) -> PressHypothesesResult:
        """Generate hypotheses from a JSON file with scraped press data.

        Args:
            json_path: Path to JSON file from scrape_press.py

        Returns:
            PressHypothesesResult with generated hypotheses
        """
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        records = data.get("records", [])
        sources = set()
        for rec in records:
            if rec.get("bundesland"):
                sources.add(rec["bundesland"])

        return self._generate_hypotheses(records, len(sources))

    def generate_from_records(
        self, records: list[dict], sources_count: int = 0
    ) -> PressHypothesesResult:
        """Generate hypotheses from a list of record dictionaries.

        Args:
            records: List of KenoWinnerRecord dicts
            sources_count: Number of unique sources

        Returns:
            PressHypothesesResult with generated hypotheses
        """
        return self._generate_hypotheses(records, sources_count)

    def _generate_hypotheses(
        self, records: list[dict], sources_count: int
    ) -> PressHypothesesResult:
        """Internal method to generate hypotheses from records.

        Generates hypotheses in these categories:
        1. Regional distribution patterns
        2. KENO type preferences
        3. Amount clustering patterns
        4. Temporal patterns
        """
        warnings: list[str] = []
        hypotheses: list[HypothesisCandidate] = []

        if len(records) < self.min_records:
            warnings.append(
                f"Only {len(records)} records found, minimum {self.min_records} needed "
                "for reliable hypothesis generation"
            )

        # Generate hypotheses from different patterns
        regional_hyp = self._analyze_regional_patterns(records)
        if regional_hyp:
            hypotheses.append(regional_hyp)

        keno_type_hyp = self._analyze_keno_type_patterns(records)
        if keno_type_hyp:
            hypotheses.append(keno_type_hyp)

        amount_hyp = self._analyze_amount_patterns(records)
        if amount_hyp:
            hypotheses.append(amount_hyp)

        temporal_hyp = self._analyze_temporal_patterns(records)
        if temporal_hyp:
            hypotheses.append(temporal_hyp)

        number_hyp = self._analyze_number_patterns(records)
        if number_hyp:
            hypotheses.append(number_hyp)

        return PressHypothesesResult(
            hypotheses=hypotheses,
            records_analyzed=len(records),
            sources_analyzed=sources_count,
            warnings=warnings,
        )

    def _analyze_regional_patterns(
        self, records: list[dict]
    ) -> Optional[HypothesisCandidate]:
        """Analyze regional distribution of KENO winners."""
        bundesland_counts: Counter = Counter()
        city_counts: Counter = Counter()

        for rec in records:
            if rec.get("bundesland"):
                bundesland_counts[rec["bundesland"]] += 1
            if rec.get("city"):
                city_counts[rec["city"]] += 1
            if rec.get("region"):
                city_counts[rec["region"]] += 1

        if len(bundesland_counts) < 2:
            return None

        total = sum(bundesland_counts.values())
        top_bundesland, top_count = bundesland_counts.most_common(1)[0]
        top_pct = (top_count / total) * 100 if total > 0 else 0

        evidence = [
            f"Top Bundesland: {top_bundesland} ({top_count}/{total}, {top_pct:.1f}%)",
        ]
        for bl, count in bundesland_counts.most_common(5):
            pct = (count / total) * 100
            evidence.append(f"  - {bl}: {count} ({pct:.1f}%)")

        if city_counts:
            top_cities = city_counts.most_common(3)
            evidence.append(f"Top Orte: {', '.join([c[0] for c in top_cities])}")

        return HypothesisCandidate(
            id="HYP-PRESS-001",
            name="Regionale KENO-Gewinner-Verteilung",
            category="Regional",
            description=(
                "KENO-Hochgewinne sind regional ungleich verteilt. "
                f"{top_bundesland} zeigt ueberdurchschnittlich viele Gewinne ({top_pct:.1f}%). "
                "Dies koennte auf Spielerverhalten, Bevoelkerungsdichte oder Zufall zurueckzufuehren sein."
            ),
            evidence=evidence,
            supporting_data={
                "bundesland_distribution": dict(bundesland_counts),
                "city_distribution": dict(city_counts.most_common(10)),
                "total_records": total,
            },
            confidence=min(0.4 + (len(records) / 100), 0.8),
            priority="HOCH" if len(records) >= 10 else "MITTEL",
            testable=True,
            acceptance_criteria=[
                "Chi-Quadrat-Test auf Bevoelkerungs-Proportionalitaet",
                "Vergleich mit DLTB-Statistiken (20% NRW Anteil)",
                "Korrektur fuer unterschiedliche Spielerzahlen pro Bundesland",
            ],
            data_requirements=[
                "Bevoelkerungszahlen pro Bundesland",
                "KENO-Spielerzahlen pro Bundesland (falls verfuegbar)",
                "Mehr Pressemitteilungen fuer statistische Signifikanz",
            ],
        )

    def _analyze_keno_type_patterns(
        self, records: list[dict]
    ) -> Optional[HypothesisCandidate]:
        """Analyze KENO type distribution among winners."""
        type_counts: Counter = Counter()
        type_amounts: defaultdict = defaultdict(list)

        for rec in records:
            keno_type = rec.get("keno_type")
            if keno_type:
                type_counts[keno_type] += 1
                if rec.get("amount_eur"):
                    type_amounts[keno_type].append(rec["amount_eur"])

        if not type_counts:
            return None

        evidence = ["KENO-Typ Verteilung der Hochgewinne:"]
        total = sum(type_counts.values())
        for ktype, count in sorted(type_counts.items()):
            pct = (count / total) * 100
            avg_amount = (
                sum(type_amounts[ktype]) / len(type_amounts[ktype])
                if type_amounts[ktype]
                else 0
            )
            evidence.append(
                f"  - Typ {ktype}: {count} ({pct:.1f}%), "
                f"Avg: {avg_amount:,.0f} EUR"
            )

        # Check if Typ 10 dominates (expected for jackpot news)
        typ10_count = type_counts.get(10, 0)
        typ10_pct = (typ10_count / total) * 100 if total > 0 else 0

        return HypothesisCandidate(
            id="HYP-PRESS-002",
            name="KENO-Typ Praeferenz bei Hochgewinnen",
            category="Strategie",
            description=(
                f"KENO Typ 10 dominiert die Pressemitteilungen ({typ10_pct:.1f}%). "
                "Dies ist bedingt durch hohe Quoten (100.000x) und Nachrichtenwert. "
                "Typ 8/9 erscheinen seltener trotz hoeherer Gewinnwahrscheinlichkeit."
            ),
            evidence=evidence,
            supporting_data={
                "type_distribution": dict(type_counts),
                "type_avg_amounts": {
                    k: sum(v) / len(v) if v else 0
                    for k, v in type_amounts.items()
                },
            },
            confidence=0.7 if len(records) >= 5 else 0.5,
            priority="MITTEL",
            testable=True,
            acceptance_criteria=[
                "Vergleich mit tatsaechlicher GK1-Verteilung nach Typ",
                "ROI-Berechnung: Typ 10 vs Typ 8 vs Typ 6",
                "Erwartungswert-Analyse pro KENO-Typ",
            ],
            data_requirements=[
                "Offizielle KENO-Quoten und Wahrscheinlichkeiten",
                "Historische GK1-Events nach Typ aus Keno_GPTs Daten",
            ],
        )

    def _analyze_amount_patterns(
        self, records: list[dict]
    ) -> Optional[HypothesisCandidate]:
        """Analyze amount distribution patterns."""
        amounts: list[float] = []
        for rec in records:
            if rec.get("amount_eur"):
                amounts.append(rec["amount_eur"])

        if len(amounts) < 3:
            return None

        amounts.sort()
        min_amt = min(amounts)
        max_amt = max(amounts)
        avg_amt = sum(amounts) / len(amounts)
        median_amt = amounts[len(amounts) // 2]

        # Cluster amounts by magnitude
        clusters: dict[str, int] = {
            "10k-50k": 0,
            "50k-100k": 0,
            "100k-500k": 0,
            "500k+": 0,
        }
        for amt in amounts:
            if amt < 50000:
                clusters["10k-50k"] += 1
            elif amt < 100000:
                clusters["50k-100k"] += 1
            elif amt < 500000:
                clusters["100k-500k"] += 1
            else:
                clusters["500k+"] += 1

        evidence = [
            f"Gewinnspanne: {min_amt:,.0f} - {max_amt:,.0f} EUR",
            f"Durchschnitt: {avg_amt:,.0f} EUR",
            f"Median: {median_amt:,.0f} EUR",
            "Verteilung nach Groesse:",
        ]
        for cluster, count in clusters.items():
            if count > 0:
                evidence.append(f"  - {cluster}: {count}")

        return HypothesisCandidate(
            id="HYP-PRESS-003",
            name="Gewinnhoehen-Clustering bei KENO",
            category="Oekonomie",
            description=(
                "KENO-Hochgewinne clustern um bestimmte Betraege (100k, 500k). "
                "Dies entspricht den festen Quoten und typischen Einsatzhoehen. "
                "Multi-Einsatz-Strategien fuehren zu aggregierten Gewinnen."
            ),
            evidence=evidence,
            supporting_data={
                "min_amount": min_amt,
                "max_amount": max_amt,
                "avg_amount": avg_amt,
                "median_amount": median_amt,
                "clusters": clusters,
                "sample_size": len(amounts),
            },
            confidence=0.6,
            priority="NIEDRIG",
            testable=True,
            acceptance_criteria=[
                "Vergleich mit festen KENO-Quoten (10k, 100k, 1M)",
                "Analyse typischer Einsatzhoehen (1, 2, 5, 10 EUR)",
                "Identifikation von Multi-Einsatz-Faellen",
            ],
            data_requirements=[
                "KENO Quoten-Tabelle pro Typ und Einsatz",
                "Detaillierte Gewinnaufschluesselung aus Pressemitteilungen",
            ],
        )

    def _analyze_temporal_patterns(
        self, records: list[dict]
    ) -> Optional[HypothesisCandidate]:
        """Analyze temporal patterns in KENO wins."""
        dates: list[datetime] = []
        months: Counter = Counter()
        weekdays: Counter = Counter()

        for rec in records:
            date_str = rec.get("draw_date") or rec.get("publish_date")
            if date_str:
                try:
                    if isinstance(date_str, str):
                        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    else:
                        dt = date_str
                    dates.append(dt)
                    months[dt.month] += 1
                    weekdays[dt.weekday()] += 1
                except (ValueError, AttributeError):
                    continue

        if len(dates) < 3:
            return None

        weekday_names = [
            "Montag", "Dienstag", "Mittwoch", "Donnerstag",
            "Freitag", "Samstag", "Sonntag"
        ]
        month_names = [
            "", "Januar", "Februar", "Maerz", "April", "Mai", "Juni",
            "Juli", "August", "September", "Oktober", "November", "Dezember"
        ]

        evidence = ["Zeitliche Verteilung der Hochgewinne:"]
        if months:
            top_month = months.most_common(1)[0]
            evidence.append(
                f"  - Top Monat: {month_names[top_month[0]]} ({top_month[1]}x)"
            )
        if weekdays:
            top_weekday = weekdays.most_common(1)[0]
            evidence.append(
                f"  - Top Wochentag: {weekday_names[top_weekday[0]]} ({top_weekday[1]}x)"
            )

        return HypothesisCandidate(
            id="HYP-PRESS-004",
            name="Zeitliche Muster bei KENO-Hochgewinnen",
            category="Zeitlich",
            description=(
                "KENO-Hochgewinne zeigen moegliche zeitliche Muster. "
                "Bestimmte Monate oder Wochentage koennten haeufiger vorkommen. "
                "Korrelation mit Spielerverhalten und Jackpot-Zyklen moeglich."
            ),
            evidence=evidence,
            supporting_data={
                "month_distribution": dict(months),
                "weekday_distribution": dict(weekdays),
                "date_range": {
                    "earliest": min(dates).isoformat() if dates else None,
                    "latest": max(dates).isoformat() if dates else None,
                },
            },
            confidence=0.4 if len(dates) < 10 else 0.6,
            priority="NIEDRIG",
            testable=True,
            acceptance_criteria=[
                "Chi-Quadrat-Test auf Gleichverteilung",
                "Vergleich mit HYP-011 (Feiertags-Effekt)",
                "Kontrolle fuer Pressemitteilungs-Timing vs. Ziehungs-Timing",
            ],
            data_requirements=[
                "Vollstaendige KENO-Ziehungsdaten mit Datum",
                "Feiertags-Kalender (bereits in HYP-011 genutzt)",
            ],
        )

    def _analyze_number_patterns(
        self, records: list[dict]
    ) -> Optional[HypothesisCandidate]:
        """Analyze number patterns from extracted winning numbers."""
        all_numbers: list[int] = []
        number_counts: Counter = Counter()
        birthday_count = 0
        total_numbers = 0

        for rec in records:
            numbers = rec.get("numbers")
            if numbers and isinstance(numbers, list):
                all_numbers.extend(numbers)
                for n in numbers:
                    number_counts[n] += 1
                    total_numbers += 1
                    if 1 <= n <= 31:
                        birthday_count += 1

        if total_numbers < 20:
            return None

        birthday_pct = (birthday_count / total_numbers) * 100 if total_numbers > 0 else 0
        expected_birthday_pct = (31 / 70) * 100  # 44.3%

        evidence = [
            f"Analysierte Zahlen: {total_numbers}",
            f"Birthday-Zahlen (1-31): {birthday_count} ({birthday_pct:.1f}%)",
            f"Erwarteter Anteil: {expected_birthday_pct:.1f}%",
        ]

        top_numbers = number_counts.most_common(5)
        if top_numbers:
            evidence.append("Haeufigste Zahlen:")
            for num, count in top_numbers:
                evidence.append(f"  - {num}: {count}x")

        return HypothesisCandidate(
            id="HYP-PRESS-005",
            name="Gewinnzahlen-Muster in Pressemitteilungen",
            category="Pattern",
            description=(
                f"Birthday-Zahlen (1-31) machen {birthday_pct:.1f}% der Gewinnzahlen aus "
                f"(erwartet: {expected_birthday_pct:.1f}%). "
                "Abweichungen koennten auf Spielerverhalten oder Selection Bias hindeuten."
            ),
            evidence=evidence,
            supporting_data={
                "total_numbers": total_numbers,
                "birthday_count": birthday_count,
                "birthday_percentage": birthday_pct,
                "expected_birthday_pct": expected_birthday_pct,
                "top_numbers": dict(number_counts.most_common(10)),
            },
            confidence=0.5,
            priority="MITTEL",
            testable=True,
            acceptance_criteria=[
                "Vergleich mit HYP-004 (Birthday-Korrelation r=0.39)",
                "Binomial-Test auf Birthday-Abweichung",
                "Kontrolle fuer Selection Bias (nur Hochgewinne publiziert)",
            ],
            data_requirements=[
                "Mehr extrahierte Gewinnzahlen aus Pressemitteilungen",
                "Vollstaendige KENO-Ziehungsdaten zum Vergleich",
            ],
        )


def generate_hypotheses_markdown(result: PressHypothesesResult) -> str:
    """Generate markdown documentation for hypotheses.

    Args:
        result: PressHypothesesResult from generator

    Returns:
        Markdown-formatted string
    """
    lines = [
        "## Hypothesen aus Pressemitteilungen",
        "",
        f"**Generiert:** {result.timestamp.strftime('%Y-%m-%d %H:%M')}",
        f"**Records analysiert:** {result.records_analyzed}",
        f"**Quellen:** {result.sources_analyzed}",
        "",
    ]

    if result.warnings:
        lines.append("### Warnungen")
        for warning in result.warnings:
            lines.append(f"- {warning}")
        lines.append("")

    if not result.hypotheses:
        lines.append("*Keine Hypothesen generiert - zu wenig Daten.*")
        return "\n".join(lines)

    for hyp in result.hypotheses:
        lines.extend([
            f"### {hyp.id}: {hyp.name}",
            f"**Kategorie:** {hyp.category}",
            f"**Prioritaet:** {hyp.priority}",
            f"**Konfidenz:** {hyp.confidence:.0%}",
            f"**Testbar:** {'Ja' if hyp.testable else 'Nein'}",
            "",
            f"**Beschreibung:**",
            hyp.description,
            "",
            "**Evidenz:**",
        ])
        for ev in hyp.evidence:
            lines.append(f"- {ev}")

        lines.extend([
            "",
            "**Acceptance Criteria:**",
        ])
        for ac in hyp.acceptance_criteria:
            lines.append(f"- [ ] {ac}")

        lines.extend([
            "",
            "**Datenbedarf:**",
        ])
        for dr in hyp.data_requirements:
            lines.append(f"- {dr}")

        lines.extend(["", "---", ""])

    return "\n".join(lines)
