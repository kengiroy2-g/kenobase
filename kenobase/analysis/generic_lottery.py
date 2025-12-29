#!/usr/bin/env python3
"""
Generisches Lotterie-Analyse-Framework

Dieses Modul definiert abstrakte Basisklassen, die fuer jede deutsche Lotterie
(KENO, Lotto 6aus49, EuroJackpot, Gluecksspirale) implementiert werden koennen.

Verwendung:
    1. Subclass von LotteryGame erstellen
    2. Abstrakte Methoden implementieren
    3. Analyse mit LotteryAnalyzer durchfuehren

Autor: Kenobase Team
Datum: 2025-12-29
"""

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd


# ============================================================================
# DATENKLASSEN
# ============================================================================

@dataclass
class Draw:
    """Repraesentiert eine einzelne Ziehung."""
    date: datetime
    numbers: List[int]
    bonus_numbers: Optional[List[int]] = None
    jackpot: Optional[int] = None
    total_stake: Optional[float] = None
    metadata: Optional[Dict] = None

    @property
    def numbers_set(self) -> Set[int]:
        return set(self.numbers)

    @property
    def all_numbers(self) -> List[int]:
        if self.bonus_numbers:
            return self.numbers + self.bonus_numbers
        return self.numbers


@dataclass
class Ticket:
    """Repraesentiert ein gespieltes Ticket."""
    numbers: List[int]
    bonus_numbers: Optional[List[int]] = None
    stake: float = 1.0
    game_type: Optional[int] = None  # z.B. KENO Typ 2-10

    @property
    def numbers_set(self) -> Set[int]:
        return set(self.numbers)


@dataclass
class BacktestResult:
    """Ergebnis eines Backtests."""
    period: str
    total_days: int
    played: int
    skipped: int
    invested: float
    won: float
    profit: float
    roi: float
    hits_distribution: Dict[int, int]
    big_wins: List[Dict]
    daily_results: Optional[List[Dict]] = None


# ============================================================================
# ABSTRAKTE BASISKLASSEN
# ============================================================================

class LotteryGame(ABC):
    """
    Abstrakte Basisklasse fuer ein Lotteriespiel.

    Jede Lotterie muss diese Klasse erweitern und die abstrakten
    Methoden implementieren.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Name des Spiels (z.B. 'KENO', 'Lotto 6aus49')."""
        pass

    @property
    @abstractmethod
    def number_range(self) -> Tuple[int, int]:
        """Zahlenbereich als (min, max) Tuple."""
        pass

    @property
    @abstractmethod
    def numbers_drawn(self) -> int:
        """Anzahl der gezogenen Zahlen pro Ziehung."""
        pass

    @property
    @abstractmethod
    def numbers_to_pick(self) -> int:
        """Anzahl der vom Spieler gewaehlten Zahlen."""
        pass

    @abstractmethod
    def load_data(self, path: Path) -> List[Draw]:
        """
        Laedt Ziehungsdaten aus einer Datei.

        Args:
            path: Pfad zur CSV-Datei

        Returns:
            Liste von Draw-Objekten
        """
        pass

    @abstractmethod
    def calculate_win(self, ticket: Ticket, draw: Draw) -> Tuple[float, int]:
        """
        Berechnet den Gewinn eines Tickets fuer eine Ziehung.

        Args:
            ticket: Das gespielte Ticket
            draw: Die Ziehung

        Returns:
            (gewinn, treffer)
        """
        pass

    @abstractmethod
    def get_quotes(self, game_type: Optional[int] = None) -> Dict[int, float]:
        """
        Gibt die Gewinnquoten zurueck.

        Args:
            game_type: Optional - z.B. KENO Typ (2-10)

        Returns:
            Dict mit {treffer: quote}
        """
        pass


class LotteryAnalyzer:
    """
    Generischer Lotterie-Analyzer.

    Fuehrt standardisierte Analysen auf beliebigen Lotteriespielen durch.
    """

    def __init__(self, game: LotteryGame, draws: List[Draw]):
        self.game = game
        self.draws = draws
        self._df = self._to_dataframe()

    def _to_dataframe(self) -> pd.DataFrame:
        """Konvertiert Draws zu DataFrame."""
        records = []
        for draw in self.draws:
            record = {
                "date": draw.date,
                "numbers": draw.numbers,
                "numbers_set": draw.numbers_set,
                "jackpot": draw.jackpot,
            }
            records.append(record)
        return pd.DataFrame(records).sort_values("date").reset_index(drop=True)

    # ========================================================================
    # HYPOTHESEN-TESTS
    # ========================================================================

    def analyze_recurrence(self, window: int = 1) -> Dict:
        """
        Analysiert wiederkehrende Zahlen (Hypothese HYP-006).

        Args:
            window: Anzahl vorheriger Ziehungen zu vergleichen

        Returns:
            Dict mit Recurrence-Statistiken
        """
        recurrence_counts = []

        for i in range(window, len(self.draws)):
            current = self.draws[i].numbers_set
            previous = set()
            for j in range(1, window + 1):
                previous.update(self.draws[i - j].numbers_set)

            overlap = len(current & previous)
            recurrence_counts.append(overlap)

        return {
            "mean_recurrence": np.mean(recurrence_counts),
            "std_recurrence": np.std(recurrence_counts),
            "min_recurrence": np.min(recurrence_counts),
            "max_recurrence": np.max(recurrence_counts),
            "recurrence_rate": np.mean([c > 0 for c in recurrence_counts]),
        }

    def analyze_pairs(self, min_support: int = 50) -> Dict:
        """
        Analysiert Zahlenpaare (Hypothese WL-001, WL-007).

        Args:
            min_support: Mindestanzahl gemeinsamer Vorkommen

        Returns:
            Dict mit Paar-Statistiken
        """
        from itertools import combinations

        pair_counts = defaultdict(int)

        for draw in self.draws:
            for pair in combinations(sorted(draw.numbers), 2):
                pair_counts[pair] += 1

        # Erwartete Haeufigkeit
        n = self.game.numbers_drawn
        total = self.game.number_range[1] - self.game.number_range[0] + 1
        expected = len(self.draws) * (n * (n - 1)) / (total * (total - 1))

        strong_pairs = []
        for pair, count in pair_counts.items():
            if count >= min_support:
                lift = count / expected
                strong_pairs.append({
                    "pair": pair,
                    "count": count,
                    "lift": lift,
                })

        return {
            "total_pairs": len(pair_counts),
            "strong_pairs": len(strong_pairs),
            "top_pairs": sorted(strong_pairs, key=lambda x: -x["lift"])[:20],
            "expected_count": expected,
        }

    def analyze_birthday_bias(self, birthday_threshold: int = 31) -> Dict:
        """
        Analysiert Birthday-Bias (Hypothese HYP-004).

        Args:
            birthday_threshold: Grenze fuer Birthday-Zahlen (Standard: 31)

        Returns:
            Dict mit Birthday-Statistiken
        """
        birthday_scores = []

        for draw in self.draws:
            birthday_count = sum(1 for n in draw.numbers if n <= birthday_threshold)
            birthday_score = birthday_count / len(draw.numbers)
            birthday_scores.append(birthday_score)

        return {
            "mean_birthday_score": np.mean(birthday_scores),
            "std_birthday_score": np.std(birthday_scores),
            "high_birthday_draws": sum(1 for s in birthday_scores if s > 0.5),
            "low_birthday_draws": sum(1 for s in birthday_scores if s < 0.35),
        }

    def analyze_jackpot_cooldown(
        self,
        jackpot_draws: List[datetime],
        cooldown_days: int = 30
    ) -> Dict:
        """
        Analysiert Post-Jackpot Performance (Hypothese WL-003).

        Args:
            jackpot_draws: Liste der Jackpot-Daten
            cooldown_days: Cooldown-Periode in Tagen

        Returns:
            Dict mit Cooldown-Statistiken
        """
        post_jackpot_draws = []
        normal_draws = []

        for draw in self.draws:
            is_post_jackpot = any(
                0 < (draw.date - jp).days <= cooldown_days
                for jp in jackpot_draws
                if jp < draw.date
            )

            if is_post_jackpot:
                post_jackpot_draws.append(draw)
            else:
                normal_draws.append(draw)

        return {
            "post_jackpot_count": len(post_jackpot_draws),
            "normal_count": len(normal_draws),
            "post_jackpot_ratio": len(post_jackpot_draws) / len(self.draws),
        }

    # ========================================================================
    # BACKTEST
    # ========================================================================

    def backtest(
        self,
        ticket_generator: Callable[[Draw, int], Ticket],
        game_type: Optional[int] = None,
        skip_condition: Optional[Callable[[Draw, List[datetime]], bool]] = None,
        jackpot_dates: Optional[List[datetime]] = None,
        start_idx: int = 1
    ) -> BacktestResult:
        """
        Fuehrt einen Backtest durch.

        Args:
            ticket_generator: Funktion die Ticket basierend auf vorheriger Ziehung generiert
            game_type: Spieltyp (z.B. KENO Typ 2-10)
            skip_condition: Optional - Funktion die True zurueckgibt wenn Skip
            jackpot_dates: Optional - Liste der Jackpot-Daten
            start_idx: Start-Index (fuer Look-Back)

        Returns:
            BacktestResult
        """
        invested = 0.0
        won = 0.0
        played = 0
        skipped = 0
        hits_distribution = defaultdict(int)
        big_wins = []
        daily_results = []

        for i in range(start_idx, len(self.draws)):
            prev_draw = self.draws[i - 1]
            curr_draw = self.draws[i]

            # Skip-Bedingung pruefen
            if skip_condition and skip_condition(curr_draw, jackpot_dates or []):
                skipped += 1
                continue

            # Ticket generieren
            ticket = ticket_generator(prev_draw, game_type or self.game.numbers_to_pick)

            # Gewinn berechnen
            win, hits = self.game.calculate_win(ticket, curr_draw)

            invested += ticket.stake
            won += win
            played += 1
            hits_distribution[hits] += 1

            result = {
                "date": str(curr_draw.date.date()),
                "ticket": ticket.numbers,
                "hits": hits,
                "win": win,
            }
            daily_results.append(result)

            if win >= 50:
                big_wins.append(result)

        profit = won - invested
        roi = (profit / invested * 100) if invested > 0 else 0

        return BacktestResult(
            period=f"{self.draws[start_idx].date.date()} - {self.draws[-1].date.date()}",
            total_days=len(self.draws) - start_idx,
            played=played,
            skipped=skipped,
            invested=invested,
            won=won,
            profit=profit,
            roi=roi,
            hits_distribution=dict(hits_distribution),
            big_wins=big_wins,
            daily_results=daily_results,
        )


# ============================================================================
# KENO IMPLEMENTIERUNG
# ============================================================================

class KenoGame(LotteryGame):
    """KENO Implementierung."""

    QUOTES = {
        2: {2: 6, 1: 0, 0: 0},
        3: {3: 16, 2: 1, 1: 0, 0: 0},
        4: {4: 22, 3: 2, 2: 1, 1: 0, 0: 0},
        5: {5: 100, 4: 7, 3: 2, 2: 0, 1: 0, 0: 0},
        6: {6: 500, 5: 15, 4: 5, 3: 1, 2: 0, 1: 0, 0: 0},
        7: {7: 1000, 6: 100, 5: 12, 4: 4, 3: 1, 2: 0, 1: 0, 0: 0},
        8: {8: 10000, 7: 1000, 6: 100, 5: 10, 4: 2, 3: 0, 2: 0, 1: 0, 0: 0},
        9: {9: 50000, 8: 5000, 7: 500, 6: 50, 5: 10, 4: 2, 3: 0, 2: 0, 1: 0, 0: 0},
        10: {10: 100000, 9: 10000, 8: 1000, 7: 100, 6: 15, 5: 5, 4: 0, 3: 0, 2: 0, 1: 0, 0: 2},
    }

    @property
    def name(self) -> str:
        return "KENO"

    @property
    def number_range(self) -> Tuple[int, int]:
        return (1, 70)

    @property
    def numbers_drawn(self) -> int:
        return 20

    @property
    def numbers_to_pick(self) -> int:
        return 10  # Standard-Typ

    def load_data(self, path: Path) -> List[Draw]:
        df = pd.read_csv(path, sep=";", encoding="utf-8")
        df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")

        draws = []
        pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]

        for _, row in df.iterrows():
            numbers = [int(row[col]) for col in pos_cols]
            draw = Draw(
                date=row["Datum"],
                numbers=numbers,
                total_stake=row.get("Keno_Spieleinsatz"),
            )
            draws.append(draw)

        return sorted(draws, key=lambda d: d.date)

    def calculate_win(self, ticket: Ticket, draw: Draw) -> Tuple[float, int]:
        hits = len(ticket.numbers_set & draw.numbers_set)
        keno_type = ticket.game_type or len(ticket.numbers)
        win = self.QUOTES.get(keno_type, {}).get(hits, 0)
        return float(win), hits

    def get_quotes(self, game_type: Optional[int] = None) -> Dict[int, float]:
        if game_type:
            return self.QUOTES.get(game_type, {})
        return self.QUOTES


class Lotto6aus49Game(LotteryGame):
    """Lotto 6aus49 Implementierung (Platzhalter)."""

    # Durchschnittliche Quoten (Parimutuel)
    AVG_QUOTES = {
        (6, True): 10000000,
        (6, False): 1000000,
        (5, True): 50000,
        (5, False): 3000,
        (4, True): 200,
        (4, False): 50,
        (3, True): 20,
        (3, False): 10,
        (2, True): 5,
    }

    @property
    def name(self) -> str:
        return "Lotto 6aus49"

    @property
    def number_range(self) -> Tuple[int, int]:
        return (1, 49)

    @property
    def numbers_drawn(self) -> int:
        return 6

    @property
    def numbers_to_pick(self) -> int:
        return 6

    def load_data(self, path: Path) -> List[Draw]:
        # TODO: Implementieren wenn Daten vorhanden
        raise NotImplementedError("Lotto 6aus49 Datenlader noch nicht implementiert")

    def calculate_win(self, ticket: Ticket, draw: Draw) -> Tuple[float, int]:
        hits = len(ticket.numbers_set & draw.numbers_set)
        # Superzahl-Logik hier
        superzahl_match = False  # TODO
        win = self.AVG_QUOTES.get((hits, superzahl_match), 0)
        return float(win), hits

    def get_quotes(self, game_type: Optional[int] = None) -> Dict[int, float]:
        return {k[0]: v for k, v in self.AVG_QUOTES.items()}


# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def create_skip_condition(jackpot_cooldown_days: int = 30):
    """
    Erstellt eine Skip-Condition fuer Jackpot-Cooldown.

    Args:
        jackpot_cooldown_days: Cooldown in Tagen

    Returns:
        Callable fuer skip_condition
    """
    def skip_condition(draw: Draw, jackpot_dates: List[datetime]) -> bool:
        for jp in jackpot_dates:
            if jp < draw.date:
                days_since = (draw.date - jp).days
                if days_since <= jackpot_cooldown_days:
                    return True
        return False

    return skip_condition


def create_optimal_ticket_generator(optimal_numbers: List[int]):
    """
    Erstellt einen Ticket-Generator mit festen optimalen Zahlen.

    Args:
        optimal_numbers: Liste der optimalen Zahlen

    Returns:
        Callable fuer ticket_generator
    """
    def ticket_generator(prev_draw: Draw, game_type: int) -> Ticket:
        numbers = optimal_numbers[:game_type]
        return Ticket(numbers=numbers, game_type=game_type)

    return ticket_generator


# ============================================================================
# BEISPIEL-VERWENDUNG
# ============================================================================

if __name__ == "__main__":
    from pathlib import Path

    # KENO Beispiel
    base_path = Path(__file__).parent.parent.parent

    keno = KenoGame()
    data_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"

    if data_path.exists():
        draws = keno.load_data(data_path)
        analyzer = LotteryAnalyzer(keno, draws)

        print(f"Geladene Ziehungen: {len(draws)}")
        print(f"Zeitraum: {draws[0].date.date()} - {draws[-1].date.date()}")

        # Analysen
        recurrence = analyzer.analyze_recurrence()
        print(f"\nRecurrence: {recurrence['mean_recurrence']:.2f} Zahlen/Ziehung")

        pairs = analyzer.analyze_pairs()
        print(f"Starke Paare: {pairs['strong_pairs']}")

        birthday = analyzer.analyze_birthday_bias()
        print(f"Birthday-Score: {birthday['mean_birthday_score']:.2%}")

        # Backtest
        optimal_ticket = create_optimal_ticket_generator([3, 9, 10, 20, 24, 36, 49, 51, 64])
        skip = create_skip_condition(30)

        result = analyzer.backtest(
            ticket_generator=optimal_ticket,
            game_type=9,
            skip_condition=skip,
            jackpot_dates=[],
        )

        print(f"\nBacktest Typ 9:")
        print(f"  ROI: {result.roi:+.1f}%")
        print(f"  Gespielt: {result.played}")
        print(f"  Big-Wins: {len(result.big_wins)}")
