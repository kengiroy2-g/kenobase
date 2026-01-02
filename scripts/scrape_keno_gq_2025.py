#!/usr/bin/env python
"""Scrape KENO Gewinnquoten from lotto-rlp.de for 2025."""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from pathlib import Path


def extract_number(text):
    """Extract number from text like 'Anzahl richtiger Zahlen10' -> '10'."""
    if not text:
        return ''
    # Remove common prefixes
    text = text.replace('Anzahl richtiger Zahlen', '')
    text = text.replace('Anzahl der Gewinner', '')
    text = text.replace('1 Euro *', '')
    text = text.replace('2 Euro *', '')
    return text.strip()


def parse_date(date_text, year="2025"):
    """
    Parse date from 'So, 28.12.' or 'Sa, 27.12.' to '28.12.2025'.

    Args:
        date_text: Raw date string like "So, 28.12."
        year: Year to append (default: 2025)

    Returns:
        Formatted date string like "28.12.2025"
    """
    if not date_text:
        return ''

    # Remove weekday prefix (Mo, Di, Mi, Do, Fr, Sa, So)
    # Pattern: "So, 28.12." -> "28.12."
    match = re.search(r'(\d{1,2})\.(\d{1,2})\.?', date_text)
    if match:
        day = match.group(1).zfill(2)
        month = match.group(2).zfill(2)
        return f"{day}.{month}.{year}"

    return date_text.strip()


def is_plus5_row(richtige_text):
    """
    Check if this row is a PLUS5 row (not KENO).

    PLUS5 rows contain 'Gewinnklasse' in the first column.
    """
    if not richtige_text:
        return False
    return 'Gewinnklasse' in richtige_text or 'Endziffer' in richtige_text


def scrape_keno_type(driver, keno_type, date_text, year="2025"):
    """Scrape data for a specific Keno type."""
    data = []

    try:
        # Select Keno type
        kenotyp_select = Select(WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, 'kenotyp'))
        ))
        kenotyp_select.select_by_value(str(keno_type))
        time.sleep(1.5)  # Wait for table to update
    except Exception:
        return data

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find the quoten table
    tables = soup.find_all('table', class_='table-quoten')

    # Parse date once (convert "So, 28.12." to "28.12.2025")
    parsed_date = parse_date(date_text, year)

    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 4:
                try:
                    # Extract and clean values
                    richtige_raw = cells[0].get_text(strip=True)

                    # Skip PLUS5 rows (contain "Gewinnklasse" or "Endziffer")
                    if is_plus5_row(richtige_raw):
                        continue

                    gewinner_raw = cells[1].get_text(strip=True)
                    quote_raw = cells[2].get_text(strip=True)

                    # Clean values
                    richtige = extract_number(richtige_raw)
                    gewinner = extract_number(gewinner_raw)
                    quote = extract_number(quote_raw)

                    # Skip if no valid data
                    if not richtige:
                        continue

                    data.append({
                        'Datum': parsed_date,
                        'Keno-Typ': keno_type,
                        'Anzahl richtiger Zahlen': richtige,
                        'Anzahl der Gewinner': gewinner,
                        '1 Euro Gewinn': quote,
                    })
                except Exception:
                    continue

    return data


def main():
    """Main scraping function for 2025."""
    url = 'https://www.lotto-rlp.de/keno/quoten'
    year = "2025"
    output_path = Path(__file__).parent.parent / "Keno_GPTs" / f"Keno_GQ_{year}.csv"

    print("=" * 60)
    print(f"KENO Gewinnquoten Scraper {year} (Alle Typen)")
    print("=" * 60)
    print("FIXES: Date parsing (DD.MM.YYYY), PLUS5 filtering")
    print("=" * 60)
    print(f"Quelle: {url}")
    print(f"Output: {output_path}")
    print()

    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    print("[1] Installiere/Lade ChromeDriver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    all_data = []

    try:
        print("[2] Lade lotto-rlp.de...")
        driver.get(url)
        time.sleep(5)

        print(f"[3] Wähle Jahr {year}...")
        year_select = Select(WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'year'))
        ))
        year_select.select_by_value(year)
        time.sleep(3)

        print("[4] Lade Datumsliste...")
        date_select = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'gcid'))
        ))
        dates = [(option.get_attribute('value'), option.text.strip()) for option in date_select.options]

        print(f"    Gefunden: {len(dates)} Ziehungstage")
        print()

        print("[5] Starte Scraping (alle Keno-Typen 2-10)...")
        total = len(dates)
        keno_types = list(range(2, 11))  # Types 2-10

        for idx, (value, date_text) in enumerate(dates, 1):
            date_rows = 0
            try:
                # Select date first
                date_select = Select(driver.find_element(By.ID, 'gcid'))
                date_select.select_by_value(value)
                time.sleep(1.5)

                # Scrape each Keno type
                for keno_type in keno_types:
                    result = scrape_keno_type(driver, keno_type, date_text, year)
                    if result:
                        all_data.extend(result)
                        date_rows += len(result)

                print(f"\r    [{idx}/{total}] {date_text} - {date_rows} rows", end="", flush=True)

                # Progress save every 20 dates
                if idx % 20 == 0 and all_data:
                    df_temp = pd.DataFrame(all_data)
                    df_temp.to_csv(output_path, index=False, encoding='utf-8-sig')
                    print(f" [saved {len(all_data)} rows]")

            except Exception as e:
                print(f"\r    [{idx}/{total}] {date_text} - Error: {str(e)[:30]}")
                continue

        print()

    except KeyboardInterrupt:
        print("\n\nAbgebrochen! Speichere bisherige Daten...")
    except Exception as e:
        print(f"\n\nFehler: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

        if all_data:
            print(f"\n[6] Speichere {len(all_data)} Datensätze...")
            df = pd.DataFrame(all_data)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"    Gespeichert: {output_path}")

            # Show summary
            print("\n" + "=" * 60)
            print("ZUSAMMENFASSUNG")
            print("=" * 60)
            print(f"Zeilen gesamt: {len(df)}")
            print(f"Tage: {df['Datum'].nunique()}")
            print(f"Keno-Typen: {sorted(df['Keno-Typ'].unique())}")
            print("\nErste 10 Zeilen:")
            print(df.head(10).to_string(index=False))
        else:
            print("\nKeine Daten gefunden!")


if __name__ == "__main__":
    main()
