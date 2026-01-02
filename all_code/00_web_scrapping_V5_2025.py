#!/usr/bin/env python
"""
KENO Gewinnquoten Scraper V5 - für 2025
Basiert auf 00_web_scrapping_V4_+_Datum.py
Aktualisiert: ChromeDriver via webdriver-manager, Jahr 2025
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
from pathlib import Path


def select_year(driver, year):
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'year')))
    year_select = Select(driver.find_element(By.ID, 'year'))
    year_select.select_by_value(year)


def retry_operation(driver, operation, attempts=3):
    for attempt in range(attempts):
        try:
            return operation()
        except StaleElementReferenceException:
            print(f"Attempt {attempt + 1} of {attempts} failed. Retrying...")
            time.sleep(1)
            if attempt < attempts - 1:
                continue
            else:
                raise


def scrape_keno_data_for_type(driver, date_url, keno_type, date_text, max_retries=3):
    """Scrape Gewinnquoten für einen Keno-Typ.
    AKTUALISIERT: Neue CSS-Selektoren für 2025 (table-quoten statt table_quoten)
    """
    retries = 0
    data = []
    while retries < max_retries:
        driver.get(date_url)
        select = Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'kenotyp'))))
        select.select_by_value(str(keno_type))

        # AKTUALISIERT: Warte auf table-quoten (mit Bindestrich, nicht Unterstrich)
        try:
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'table.table-quoten')))
        except:
            # Fallback: versuche alte Klasse
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'table_quoten')))
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # AKTUALISIERT: Suche nach neuer Tabellenstruktur
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

                        # Bereinige Werte (entferne Präfixe wie "Anzahl richtiger Zahlen")
                        numbers = numbers.replace('Anzahl richtiger Zahlen', '').strip()
                        winners = winners.replace('Anzahl der Gewinner', '').strip()
                        quote = quote.replace('1 Euro *', '').replace('2 Euro *', '').strip()

                        if numbers:  # Nur wenn gültige Daten
                            data_entry = {
                                'Datum': date_text,
                                'Keno-Typ': keno_type,
                                'Anzahl richtiger Zahlen': numbers,
                                'Anzahl der Gewinner': winners,
                                '1 Euro Gewinn': quote,
                            }
                            data.append(data_entry)

            if data:
                print(f"  Typ {keno_type}: {len(data)} Zeilen")
            break
        else:
            # Fallback: alte Struktur (div.table_quoten)
            table_container = soup.select_one('body > main > div.quoten > section.row.row_outer.margin_elements > div:nth-child(2)')
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
                if data:
                    print(f"  Typ {keno_type}: {len(data)} Zeilen (alte Struktur)")
                break

            retries += 1
            print(f"Keine Daten für {date_text} gefunden, Seite wird neu geladen...")
            time.sleep(5)
            if retries >= max_retries:
                print("Maximale Neuladeversuche erreicht. Daten für diesen Tag und Typ könnten fehlen.")

    return data


def main(url, output_path, year='2025', start_date=None):
    """
    Args:
        url: lotto-rlp.de quoten URL
        output_path: CSV output path
        year: Jahr zum Scrapen (default: 2025)
        start_date: Optional - Startdatum (z.B. "So, 01.01.") oder None für alle
    """
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

    # ChromeDriver via webdriver-manager (automatisch)
    print("[1] Installiere/Lade ChromeDriver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    all_data = []

    try:
        print(f"[2] Lade {url}...")
        driver.get(url)

        print(f"[3] Wähle Jahr {year}...")
        select_year(driver, year)
        time.sleep(5)

        print("[4] Lade Datumsliste...")
        date_select = Select(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'gcid'))))
        dates = [(option.get_attribute('value'), option.text) for option in date_select.options]
        print(f"    Gefunden: {len(dates)} Ziehungstage")

        start_extraction = (start_date is None)  # Wenn kein start_date, sofort starten

        print(f"[5] Starte Scraping...")
        for idx, (value, date_text) in enumerate(dates, 1):
            if start_date and date_text.strip() == start_date:
                start_extraction = True

            if start_extraction:
                print(f"\n[{idx}/{len(dates)}] {date_text}")
                for keno_type in range(2, 11):
                    date_url = f"https://www.lotto-rlp.de/keno/quoten?gbn=6&gcid={value}"
                    data = scrape_keno_data_for_type(driver, date_url, keno_type, date_text)
                    all_data.extend(data)

                # Zwischenspeichern alle 20 Tage
                if idx % 20 == 0 and all_data:
                    df = pd.DataFrame(all_data)
                    df.to_csv(output_path, index=False, encoding='utf-8-sig')
                    print(f"    [Zwischenstand: {len(all_data)} Zeilen gespeichert]")

    except KeyboardInterrupt:
        print("\nSkript durch Benutzer unterbrochen. Gesammelte Daten werden gespeichert.")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
        if all_data:
            df = pd.DataFrame(all_data)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"\n[6] Daten erfolgreich in {output_path} gespeichert.")
            print(f"    Zeilen: {len(df)}, Tage: {df['Datum'].nunique()}")
        else:
            print("Keine Daten gefunden zum Speichern.")


if __name__ == "__main__":
    url = 'https://www.lotto-rlp.de/keno/quoten'

    # Output Pfad anpassen
    base_path = Path(__file__).parent.parent
    output_path = base_path / "Keno_GPTs" / "Keno_GQ_2025.csv"

    print("=" * 60)
    print("KENO Gewinnquoten Scraper V5 - Jahr 2025")
    print("=" * 60)

    main(url, str(output_path), year='2025', start_date=None)
