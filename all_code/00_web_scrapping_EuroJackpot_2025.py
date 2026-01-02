#!/usr/bin/env python
"""
EuroJackpot Gewinnquoten Scraper - für 2025
Basiert auf KENO V5 Scraper
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
from pathlib import Path


def select_year(driver, year):
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'year')))
    year_select = Select(driver.find_element(By.ID, 'year'))
    year_select.select_by_value(year)


def scrape_eurojackpot_data(driver, date_text, max_retries=3):
    """Scrape Gewinnquoten für ein Datum."""
    import re
    retries = 0
    data = []

    while retries < max_retries:
        try:
            # Warte auf Tabelle
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table-quoten'))
            )
            time.sleep(2)

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Suche nach Quoten-Tabelle
            tables = soup.find_all('table', class_='table-quoten')

            for table in tables:
                rows = table.find_all('tr')

                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        cell1_text = cells[0].get_text(strip=True)
                        cell2_text = cells[1].get_text(strip=True)
                        cell3_text = cells[2].get_text(strip=True)

                        # Überspringe leere Zeilen
                        if not cell1_text or cell1_text == 'Gewinnklasse':
                            continue

                        # Parse Gewinnklasse (z.B. "Gewinnklasse1(5+2)")
                        gk_match = re.search(r'Gewinnklasse\s*(\d+)\s*\(([^)]+)\)', cell1_text)
                        if gk_match:
                            gk_num = gk_match.group(1)
                            gk_desc = gk_match.group(2)
                            gewinnklasse = f"{gk_num} ({gk_desc})"
                        else:
                            gewinnklasse = cell1_text.replace('Gewinnklasse', '').strip()

                        # Parse Anzahl Gewinner
                        anzahl_match = re.search(r'(\d[\d.,]*)', cell2_text)
                        anzahl = anzahl_match.group(1) if anzahl_match else '0'

                        # Parse Quote
                        quote_match = re.search(r'([\d.,]+)\s*€', cell3_text)
                        quote = quote_match.group(1) + ' €' if quote_match else cell3_text.replace('Gewinnquote', '').strip()

                        # EuroJackpot hat Gewinnklassen 1-12
                        if gewinnklasse:
                            data.append({
                                'Datum': date_text,
                                'Gewinnklasse': gewinnklasse,
                                'Anzahl Gewinner': anzahl,
                                'Quote': quote,
                            })

            if data:
                break

        except TimeoutException:
            pass

        retries += 1
        time.sleep(3)

    return data


def main(url, output_path, year='2025'):
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

    print("[1] Installiere/Lade ChromeDriver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    all_data = []

    try:
        print(f"[2] Lade {url}...")
        driver.get(url)
        time.sleep(5)

        print(f"[3] Wähle Jahr {year}...")
        try:
            select_year(driver, year)
            time.sleep(3)
        except Exception as e:
            print(f"    Jahr-Auswahl fehlgeschlagen: {e}")

        print("[4] Lade Datumsliste...")
        try:
            date_select = Select(WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'gcid'))
            ))
            dates = [(option.get_attribute('value'), option.text.strip()) for option in date_select.options]
            print(f"    Gefunden: {len(dates)} Ziehungstage")
        except Exception as e:
            print(f"    Datumsliste nicht gefunden: {e}")
            dates = []

        print(f"[5] Starte Scraping...")
        for idx, (value, date_text) in enumerate(dates, 1):
            try:
                # Datum auswählen
                date_select = Select(driver.find_element(By.ID, 'gcid'))
                date_select.select_by_value(value)
                time.sleep(2)

                # Daten scrapen
                result = scrape_eurojackpot_data(driver, date_text)

                if result:
                    all_data.extend(result)
                    print(f"  [{idx}/{len(dates)}] {date_text}: {len(result)} Zeilen")
                else:
                    print(f"  [{idx}/{len(dates)}] {date_text}: keine Daten")

                # Zwischenspeichern
                if idx % 20 == 0 and all_data:
                    df = pd.DataFrame(all_data)
                    df.to_csv(output_path, index=False, encoding='utf-8-sig')
                    print(f"    [Zwischenstand: {len(all_data)} Zeilen]")

            except Exception as e:
                print(f"  [{idx}/{len(dates)}] {date_text}: Fehler - {str(e)[:40]}")
                continue

    except KeyboardInterrupt:
        print("\nAbgebrochen!")
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
        if all_data:
            df = pd.DataFrame(all_data)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"\n[6] Gespeichert: {output_path}")
            print(f"    {len(df)} Zeilen, {df['Datum'].nunique()} Tage")
        else:
            print("Keine Daten!")


if __name__ == "__main__":
    url = 'https://www.lotto-rlp.de/eurojackpot/quoten'
    base_path = Path(__file__).parent.parent
    output_path = base_path / "Keno_GPTs" / "EuroJackpot_GQ_2025.csv"

    print("=" * 60)
    print("EuroJackpot Gewinnquoten Scraper - Jahr 2025")
    print("=" * 60)

    main(url, str(output_path), year='2025')
