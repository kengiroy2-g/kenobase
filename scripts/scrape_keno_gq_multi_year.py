#!/usr/bin/env python
"""
KENO Gewinnquoten Scraper - Multi-Year (2022, 2023, 2024)
Basiert auf 00_web_scrapping_V5_2025.py
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


def scrape_keno_data_for_type(driver, date_url, keno_type, date_text, max_retries=3):
    """Scrape Gewinnquoten für einen Keno-Typ."""
    retries = 0
    data = []

    while retries < max_retries:
        try:
            driver.get(date_url)
            select = Select(WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'kenotyp'))
            ))
            select.select_by_value(str(keno_type))

            # Warte auf Tabelle
            try:
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'table.table-quoten'))
                )
            except TimeoutException:
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, 'table_quoten'))
                )
            time.sleep(2)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            tables = soup.find_all('table', class_='table-quoten')

            if tables:
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            numbers = cells[0].get_text(strip=True)
                            winners = cells[1].get_text(strip=True)
                            quote = cells[2].get_text(strip=True) if len(cells) > 2 else 'N/A'

                            numbers = numbers.replace('Anzahl richtiger Zahlen', '').strip()
                            winners = winners.replace('Anzahl der Gewinner', '').strip()
                            quote = quote.replace('1 Euro *', '').replace('2 Euro *', '').strip()

                            if numbers:
                                data.append({
                                    'Datum': date_text,
                                    'Keno-Typ': keno_type,
                                    'Anzahl richtiger Zahlen': numbers,
                                    'Anzahl der Gewinner': winners,
                                    '1 Euro Gewinn': quote,
                                })

                if data:
                    break
            else:
                # Fallback: alte Struktur
                table_container = soup.select_one('body > main > div.quoten > section.row.row_outer.margin_elements > div:nth-child(2)')
                if table_container:
                    quoten_blocks = table_container.find_all('div', class_='table_quoten')
                    for block in quoten_blocks:
                        numbers = block.find('span').get_text(strip=True) if block.find('span') else 'N/A'
                        winners = block.find('div', class_='text_align').get_text(strip=True) if block.find('div', class_='text_align') else 'N/A'
                        euro_values = [div.get_text(strip=True) for div in block.find_all('div', class_='text_align')[1:]]

                        data.append({
                            'Datum': date_text,
                            'Keno-Typ': keno_type,
                            'Anzahl richtiger Zahlen': numbers,
                            'Anzahl der Gewinner': winners,
                            '1 Euro Gewinn': euro_values[0] if euro_values else 'N/A',
                        })
                    if data:
                        break

        except Exception as e:
            pass

        retries += 1
        time.sleep(3)

    return data


def scrape_year(driver, url, year, output_path):
    """Scrape alle Daten für ein Jahr."""
    all_data = []

    try:
        print(f"\n{'='*60}")
        print(f"STARTE SCRAPING FÜR JAHR {year}")
        print(f"{'='*60}")

        driver.get(url)
        time.sleep(3)

        print(f"[1] Wähle Jahr {year}...")
        select_year(driver, year)
        time.sleep(5)

        print("[2] Lade Datumsliste...")
        date_select = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'gcid'))
        ))
        dates = [(option.get_attribute('value'), option.text) for option in date_select.options]
        print(f"    Gefunden: {len(dates)} Ziehungstage für {year}")

        print(f"[3] Starte Scraping für {year}...")
        for idx, (value, date_text) in enumerate(dates, 1):
            print(f"\n[{idx}/{len(dates)}] {date_text}")

            for keno_type in range(2, 11):
                date_url = f"https://www.lotto-rlp.de/keno/quoten?gbn=6&gcid={value}"
                data = scrape_keno_data_for_type(driver, date_url, keno_type, date_text)
                all_data.extend(data)

                if data:
                    print(f"  Typ {keno_type}: {len(data)} Zeilen")

            # Zwischenspeichern alle 30 Tage
            if idx % 30 == 0 and all_data:
                df = pd.DataFrame(all_data)
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
                print(f"    [Zwischenstand: {len(all_data)} Zeilen gespeichert]")

    except Exception as e:
        print(f"Fehler bei Jahr {year}: {e}")
        import traceback
        traceback.print_exc()

    # Speichern am Ende des Jahres
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n[4] Jahr {year} gespeichert: {output_path}")
        print(f"    Zeilen: {len(df)}, Tage: {df['Datum'].nunique()}")

    return all_data


def main():
    url = 'https://www.lotto-rlp.de/keno/quoten'
    base_path = Path(__file__).parent.parent
    output_dir = base_path / "Keno_GPTs"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Jahre zum Scrapen (älteste zuerst)
    years = ['2022', '2023', '2024']

    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

    print("=" * 60)
    print("KENO Gewinnquoten Scraper - Multi-Year")
    print(f"Jahre: {', '.join(years)}")
    print("=" * 60)

    print("\n[0] Installiere/Lade ChromeDriver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        for year in years:
            output_path = output_dir / f"Keno_GQ_{year}.csv"
            scrape_year(driver, url, year, str(output_path))

    except KeyboardInterrupt:
        print("\n\nAbgebrochen durch Benutzer!")
    finally:
        driver.quit()
        print("\n" + "=" * 60)
        print("SCRAPING ABGESCHLOSSEN")
        print("=" * 60)


if __name__ == "__main__":
    main()
