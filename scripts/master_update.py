#!/usr/bin/env python3
"""
Master Update Script - Konsolidierte Datenaktualisierung fuer Kenobase V2.0

Dieses Script fuehrt alle notwendigen Schritte aus um die Daten zu aktualisieren:
1. Neue Ziehungsdaten scrapen (optional, erfordert Selenium)
2. Pattern-Analyse ausfuehren
3. Daten konsolidieren und deduplizieren
4. Hauptdateien aktualisieren

Verwendung:
    python scripts/master_update.py --game keno --mode full
    python scripts/master_update.py --game all --mode patterns-only
    python scripts/master_update.py --game eurojackpot --mode scrape

Autor: Claude Code (Kenobase V2.0)
Erstellt: 2025-12-27
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import pandas as pd
import yaml
import time

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/master_update.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Laedt Konfiguration aus YAML-Datei."""
    if config_path is None:
        config_path = Path(__file__).parent.parent / 'config' / 'default.yaml'

    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


class DataSourceConfig:
    """Konfiguration fuer Datenquellen."""

    GAMES = {
        'keno': {
            'url': 'https://www.lotto-rlp.de/keno/quoten',
            'raw_dir': 'Keno_GPTs/',
            'output_file': 'data/raw/keno/KENO_ab_2018.csv',
            'pattern_files': ['KENO_10K.csv', '10-9_CheckNumbers_z120.csv'],
            'update_freq': 'daily'
        },
        'eurojackpot': {
            'url': 'https://www.eurojackpot.de/zahlen-quoten/',
            'raw_dir': 'Keno_GPTs/',
            'output_file': 'data/raw/eurojackpot/eurojackpot_archiv_bereinigt.csv',
            'pattern_files': [],
            'update_freq': 'tue_fri'
        },
        'lotto': {
            'url': 'https://www.lotto.de/lotto-6aus49/lottozahlen',
            'raw_dir': 'Keno_GPTs/',
            'output_file': 'data/raw/lotto/Lotto_archiv_bereinigt.csv',
            'pattern_files': [],
            'update_freq': 'wed_sat'
        }
    }


class KenoScraper:
    """Web Scraper fuer KENO-Daten von lotto-rlp.de.

    Basiert auf all_code/00_web_scrapping_V4_+_Datum.py mit konfigurierbarem
    ChromeDriver-Pfad und Headless-Modus.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config.get('scraper', {})
        self.logger = logging.getLogger(self.__class__.__name__)

        # Scraper settings from config
        self.chromedriver_path = self.config.get('chromedriver_path')
        self.headless = self.config.get('headless', True)
        self.page_load_timeout = self.config.get('page_load_timeout', 30)
        self.element_wait_timeout = self.config.get('element_wait_timeout', 10)
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 5)
        self.request_delay = self.config.get('request_delay', 2)

    def _get_driver(self):
        """Erstellt und konfiguriert Chrome WebDriver."""
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options

        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        if self.chromedriver_path:
            service = Service(self.chromedriver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)

        driver.set_page_load_timeout(self.page_load_timeout)
        return driver

    def _select_year(self, driver, year: str):
        """Waehlt ein Jahr im Dropdown aus."""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait, Select
        from selenium.webdriver.support import expected_conditions as EC

        WebDriverWait(driver, self.element_wait_timeout).until(
            EC.visibility_of_element_located((By.ID, 'year'))
        )
        year_select = Select(driver.find_element(By.ID, 'year'))
        year_select.select_by_value(year)

    def _scrape_keno_for_date(
        self,
        driver,
        date_url: str,
        keno_type: int,
        date_text: str
    ) -> List[Dict[str, Any]]:
        """Scrapt KENO-Daten fuer ein spezifisches Datum und Keno-Typ."""
        from bs4 import BeautifulSoup
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait, Select
        from selenium.webdriver.support import expected_conditions as EC

        data = []
        retries = 0

        while retries < self.max_retries:
            try:
                driver.get(date_url)
                select = Select(WebDriverWait(driver, self.element_wait_timeout).until(
                    EC.visibility_of_element_located((By.ID, 'kenotyp'))
                ))
                select.select_by_value(str(keno_type))

                WebDriverWait(driver, self.element_wait_timeout).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, 'table_quoten'))
                )
                time.sleep(self.request_delay)

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                table_container = soup.select_one(
                    'body > main > div.quoten > section.row.row_outer.margin_elements > div:nth-child(2)'
                )

                if table_container:
                    quoten_blocks = table_container.find_all('div', class_='table_quoten')
                    for block in quoten_blocks:
                        numbers = block.find('span').get_text(strip=True) if block.find('span') else 'N/A'
                        winners = block.find('div', class_='text_align').get_text(strip=True) if block.find('div', class_='text_align') else 'N/A'
                        euro_values = [div.get_text(strip=True) for div in block.find_all('div', class_='text_align')[1:]]

                        data_entry = {
                            'Datum': date_text,
                            'Keno-Typ': keno_type,
                            'Anzahl richtiger Zahlen': numbers,
                            'Anzahl der Gewinner': winners,
                            '1 Euro Gewinn': euro_values[0] if euro_values else 'N/A',
                        }
                        data.append(data_entry)
                    break
                else:
                    retries += 1
                    self.logger.warning(
                        f"Keine Daten fuer {date_text}, Typ {keno_type}. Retry {retries}/{self.max_retries}"
                    )
                    time.sleep(self.retry_delay)

            except Exception as e:
                retries += 1
                self.logger.warning(f"Fehler beim Scrapen: {e}. Retry {retries}/{self.max_retries}")
                time.sleep(self.retry_delay)

        return data

    def scrape_year(self, year: int, url: str, output_path: Path) -> bool:
        """Scrapt alle KENO-Daten fuer ein Jahr.

        Args:
            year: Jahr zum Scrapen (z.B. 2024)
            url: Basis-URL fuer KENO-Quoten
            output_path: Pfad fuer Output-CSV

        Returns:
            True wenn erfolgreich, False sonst
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait, Select
        from selenium.webdriver.support import expected_conditions as EC

        self.logger.info(f"Starte Scraping fuer Jahr {year}")
        all_data = []
        driver = None

        try:
            driver = self._get_driver()
            driver.get(url)
            self._select_year(driver, str(year))
            time.sleep(self.retry_delay)

            date_select = Select(WebDriverWait(driver, self.element_wait_timeout).until(
                EC.presence_of_element_located((By.ID, 'gcid'))
            ))
            dates = [(option.get_attribute('value'), option.text) for option in date_select.options]

            self.logger.info(f"Gefunden: {len(dates)} Ziehungstermine fuer {year}")

            for idx, (value, date_text) in enumerate(dates):
                self.logger.info(f"Scrape Datum {idx + 1}/{len(dates)}: {date_text}")

                for keno_type in range(2, 11):
                    date_url = f"{url}?gbn=6&gcid={value}"
                    data = self._scrape_keno_for_date(driver, date_url, keno_type, date_text)
                    all_data.extend(data)

            if all_data:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                df = pd.DataFrame(all_data)
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
                self.logger.info(f"Gespeichert: {len(all_data)} Eintraege in {output_path}")
                return True
            else:
                self.logger.warning("Keine Daten gefunden")
                return False

        except Exception as e:
            self.logger.error(f"Fehler beim Scraping: {e}")
            if all_data:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                df = pd.DataFrame(all_data)
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
                self.logger.info(f"Teilweise gespeichert: {len(all_data)} Eintraege")
            return False

        finally:
            if driver:
                driver.quit()


class PatternAnalyzer:
    """Fuehrt Pattern-Analyse auf Ziehungsdaten aus."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.logger = logging.getLogger(self.__class__.__name__)

    def analyze_repeating_numbers(self, draws_df: pd.DataFrame) -> pd.DataFrame:
        """Analysiert wiederholte Zahlen zwischen aufeinanderfolgenden Ziehungen."""
        self.logger.info("Analysiere wiederholte Zahlen...")

        results = []
        number_cols = [col for col in draws_df.columns if col.startswith('z')]

        prev_numbers = set()
        for idx, row in draws_df.iterrows():
            current_numbers = set(row[number_cols].dropna().astype(int))

            if prev_numbers:
                repeated = current_numbers.intersection(prev_numbers)
                results.append({
                    'Datum': row['Datum'],
                    'Anzahl_wiederholte': len(repeated),
                    'Wiederholte_Zahlen': ','.join(map(str, sorted(repeated)))
                })

            prev_numbers = current_numbers

        return pd.DataFrame(results)

    def analyze_frequency(self, draws_df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """Berechnet Haeufigkeitsstatistiken fuer Zahlen."""
        self.logger.info(f"Berechne Haeufigkeit (Window={window})...")

        number_cols = [col for col in draws_df.columns if col.startswith('z')]
        all_numbers = draws_df[number_cols].values.flatten()
        all_numbers = [int(n) for n in all_numbers if pd.notna(n)]

        from collections import Counter
        freq = Counter(all_numbers)

        df = pd.DataFrame([
            {'Zahl': num, 'Haeufigkeit': count}
            for num, count in freq.most_common()
        ])

        return df

    def run_full_analysis(self, game: str) -> dict:
        """Fuehrt vollstaendige Pattern-Analyse durch."""
        self.logger.info(f"Starte vollstaendige Analyse fuer {game}...")

        config = DataSourceConfig.GAMES.get(game)
        if not config:
            raise ValueError(f"Unbekanntes Spiel: {game}")

        # Lade Daten
        output_file = Path(config['output_file'])
        if not output_file.exists():
            self.logger.warning(f"Datendatei nicht gefunden: {output_file}")
            return {}

        draws_df = pd.read_csv(output_file, sep=';', encoding='utf-8')

        results = {
            'game': game,
            'total_draws': len(draws_df),
            'date_range': f"{draws_df['Datum'].iloc[-1]} - {draws_df['Datum'].iloc[0]}",
            'repeating': self.analyze_repeating_numbers(draws_df),
            'frequency': self.analyze_frequency(draws_df)
        }

        return results


class DataConsolidator:
    """Konsolidiert und dedupliziert Daten."""

    def __init__(self, game: str):
        self.game = game
        self.config = DataSourceConfig.GAMES.get(game)
        self.logger = logging.getLogger(self.__class__.__name__)

    def deduplicate(self, df: pd.DataFrame, key_column: str = 'Datum') -> pd.DataFrame:
        """Entfernt Duplikate basierend auf Schluesselsspalte."""
        original_count = len(df)
        df = df.drop_duplicates(subset=[key_column], keep='last')
        removed = original_count - len(df)

        if removed > 0:
            self.logger.info(f"Entfernt: {removed} Duplikate")

        return df

    def merge_new_data(self, existing_file: Path, new_data: pd.DataFrame) -> pd.DataFrame:
        """Fuegt neue Daten zu bestehender Datei hinzu."""
        if existing_file.exists():
            existing_df = pd.read_csv(existing_file, sep=';', encoding='utf-8')
            merged = pd.concat([existing_df, new_data], ignore_index=True)
        else:
            merged = new_data

        return self.deduplicate(merged)

    def validate_data(self, df: pd.DataFrame) -> bool:
        """Validiert Datenintegritaet."""
        self.logger.info("Validiere Daten...")

        # Pruefe auf erforderliche Spalten
        required_cols = ['Datum']
        if self.game == 'keno':
            required_cols.extend([f'z{i}' for i in range(1, 21)])

        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            self.logger.error(f"Fehlende Spalten: {missing}")
            return False

        # Pruefe auf leere Daten
        if len(df) == 0:
            self.logger.error("DataFrame ist leer")
            return False

        return True


class MasterUpdater:
    """Hauptklasse fuer konsolidierte Updates."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).parent.parent
        self.logger = logging.getLogger(self.__class__.__name__)

        # Stelle sicher, dass Log-Verzeichnis existiert
        (self.base_dir / 'logs').mkdir(exist_ok=True)

    def run_scrape(self, game: str, year: Optional[int] = None) -> bool:
        """Fuehrt Web-Scraping fuer ein Spiel aus.

        Args:
            game: Spieltyp ('keno', 'eurojackpot', 'lotto')
            year: Jahr zum Scrapen (default: aktuelles Jahr)

        Returns:
            True wenn erfolgreich, False sonst
        """
        self.logger.info(f"Starte Scraping fuer {game}...")

        # Pruefe ob Selenium verfuegbar ist
        try:
            from selenium import webdriver
            from bs4 import BeautifulSoup
        except ImportError as e:
            self.logger.error(
                f"Fehlende Abhaengigkeit: {e}. "
                "Bitte 'pip install selenium beautifulsoup4' ausfuehren."
            )
            return False

        # Lade Konfiguration
        config = load_config()
        game_config = DataSourceConfig.GAMES.get(game)

        if not game_config:
            self.logger.error(f"Unbekanntes Spiel: {game}")
            return False

        # Aktuell nur KENO unterstuetzt
        if game != 'keno':
            self.logger.warning(
                f"Scraping fuer {game} noch nicht implementiert. "
                "Nur 'keno' wird aktuell unterstuetzt."
            )
            return False

        # Jahr festlegen
        if year is None:
            year = datetime.now().year

        # Output-Pfad bestimmen
        output_dir = self.base_dir / 'data' / 'scraped'
        output_path = output_dir / f'{game}_scraped_{year}.csv'

        # Scraper initialisieren und ausfuehren
        scraper = KenoScraper(config)
        url = game_config['url']

        success = scraper.scrape_year(year, url, output_path)

        if success:
            self.logger.info(f"Scraping abgeschlossen: {output_path}")

            # Merge mit Hauptdatei wenn gewuenscht
            main_file = self.base_dir / game_config['output_file']
            if main_file.exists():
                consolidator = DataConsolidator(game)
                try:
                    scraped_df = pd.read_csv(output_path, encoding='utf-8-sig')
                    merged_df = consolidator.merge_new_data(main_file, scraped_df)
                    merged_df.to_csv(main_file, sep=';', index=False, encoding='utf-8')
                    self.logger.info(f"Daten gemerged in {main_file}")
                except Exception as e:
                    self.logger.warning(f"Merge fehlgeschlagen: {e}")

        return success

    def run_patterns(self, game: str) -> bool:
        """Fuehrt Pattern-Analyse aus."""
        self.logger.info(f"Starte Pattern-Analyse fuer {game}...")

        analyzer = PatternAnalyzer(self.base_dir)

        try:
            results = analyzer.run_full_analysis(game)

            if results:
                # Speichere Ergebnisse
                output_dir = self.base_dir / 'analysis'
                output_dir.mkdir(exist_ok=True)

                if 'frequency' in results:
                    freq_file = output_dir / f'{game}_frequency.csv'
                    results['frequency'].to_csv(freq_file, index=False)
                    self.logger.info(f"Haeufigkeit gespeichert: {freq_file}")

                if 'repeating' in results:
                    rep_file = output_dir / f'{game}_repeating.csv'
                    results['repeating'].to_csv(rep_file, index=False)
                    self.logger.info(f"Wiederholungen gespeichert: {rep_file}")

                return True

        except Exception as e:
            self.logger.error(f"Fehler bei Pattern-Analyse: {e}")

        return False

    def run_consolidate(self, game: str) -> bool:
        """Konsolidiert Daten fuer ein Spiel."""
        self.logger.info(f"Konsolidiere Daten fuer {game}...")

        consolidator = DataConsolidator(game)
        config = DataSourceConfig.GAMES.get(game)

        if not config:
            self.logger.error(f"Unbekanntes Spiel: {game}")
            return False

        output_file = self.base_dir / config['output_file']

        if not output_file.exists():
            self.logger.warning(f"Keine Daten zum Konsolidieren: {output_file}")
            return False

        try:
            df = pd.read_csv(output_file, sep=';', encoding='utf-8')

            if consolidator.validate_data(df):
                df = consolidator.deduplicate(df)
                df.to_csv(output_file, sep=';', index=False, encoding='utf-8')
                self.logger.info(f"Konsolidiert: {len(df)} Eintraege in {output_file}")
                return True

        except Exception as e:
            self.logger.error(f"Fehler beim Konsolidieren: {e}")

        return False

    def run_full(self, game: str) -> bool:
        """Fuehrt vollstaendiges Update durch."""
        self.logger.info(f"=== Vollstaendiges Update fuer {game} ===")

        steps = [
            ('Scraping', lambda: self.run_scrape(game)),
            ('Konsolidierung', lambda: self.run_consolidate(game)),
            ('Pattern-Analyse', lambda: self.run_patterns(game))
        ]

        results = {}
        for name, step_fn in steps:
            self.logger.info(f"Schritt: {name}")
            results[name] = step_fn()

        # Zusammenfassung
        success = sum(results.values())
        total = len(results)
        self.logger.info(f"=== Abgeschlossen: {success}/{total} Schritte erfolgreich ===")

        return success == total

    def run(self, games: List[str], mode: str) -> dict:
        """Haupteinstiegspunkt."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.logger.info(f"Master Update gestartet: {timestamp}")
        self.logger.info(f"Spiele: {games}, Modus: {mode}")

        results = {}

        for game in games:
            if mode == 'full':
                results[game] = self.run_full(game)
            elif mode == 'scrape':
                results[game] = self.run_scrape(game)
            elif mode == 'patterns-only':
                results[game] = self.run_patterns(game)
            elif mode == 'consolidate':
                results[game] = self.run_consolidate(game)
            else:
                self.logger.error(f"Unbekannter Modus: {mode}")
                results[game] = False

        return results


def main():
    parser = argparse.ArgumentParser(
        description='Master Update Script fuer Kenobase V2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python scripts/master_update.py --game keno --mode full
  python scripts/master_update.py --game all --mode patterns-only
  python scripts/master_update.py --game eurojackpot --mode consolidate
        """
    )

    parser.add_argument(
        '--game', '-g',
        choices=['keno', 'eurojackpot', 'lotto', 'all'],
        default='keno',
        help='Spiel zum Aktualisieren (default: keno)'
    )

    parser.add_argument(
        '--mode', '-m',
        choices=['full', 'scrape', 'patterns-only', 'consolidate'],
        default='full',
        help='Update-Modus (default: full)'
    )

    parser.add_argument(
        '--year', '-y',
        type=int,
        default=None,
        help='Jahr fuer Scraping (optional)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Zeigt was getan wuerde, ohne tatsaechlich auszufuehren'
    )

    args = parser.parse_args()

    # Bestimme welche Spiele
    if args.game == 'all':
        games = list(DataSourceConfig.GAMES.keys())
    else:
        games = [args.game]

    if args.dry_run:
        logger.info("=== DRY RUN ===")
        logger.info(f"Wuerde ausfuehren: Spiele={games}, Modus={args.mode}")
        return

    # Fuehre Update aus
    updater = MasterUpdater()
    results = updater.run(games, args.mode)

    # Zeige Zusammenfassung
    print("\n" + "="*50)
    print("ZUSAMMENFASSUNG")
    print("="*50)
    for game, success in results.items():
        status = "OK" if success else "FEHLER"
        print(f"  {game.upper():15} [{status}]")
    print("="*50)


if __name__ == '__main__':
    main()
