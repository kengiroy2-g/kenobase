from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_keno_data_for_type(driver, date_url, keno_type):
    driver.get(date_url)
    time.sleep(3)  # Warten auf das Laden der Seite

    # Wähle den Keno-Typ
    select = Select(driver.find_element(By.ID, 'kenotyp'))
    select.select_by_value(str(keno_type))
    time.sleep(3)  # Warten auf das Laden der Daten

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    data = []

    quoten_blocks = soup.find_all('div', class_='table_quoten')
    for block in quoten_blocks:
        correct_numbers_element = block.find('div', class_='col-md-2 col-sm-2 col-xs-6')
        correct_numbers = correct_numbers_element.span.text.strip() if correct_numbers_element and correct_numbers_element.span else 'Nicht gefunden'

        winners_element = block.find('div', class_='col-md-2 col-sm-2 col-xs-6 col-sm-offset-0 text_align')
        winners = winners_element.text.strip() if winners_element else 'Nicht gefunden'
        
        data.append({
            'Keno-Typ': keno_type,
            'Anzahl Richtiger': correct_numbers,
            'Anzahl Gewinner': winners
        })
    
    return data

def main(url, output_path):
    chrome_options = Options()
    #chrome_options.add_argument("--headless")

    chromedriver_path = "C:\\Users\\Admin1\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
    service = Service(chromedriver_path)

    driver = webdriver.Chrome(service=service, options=chrome_options)
    all_data = []
    try:
        driver.get(url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        dates = [option['value'] for option in soup.find('select', {'id': 'gcid'}).find_all('option')]
        keno_types = [str(i) for i in range(2, 11)]  # Keno-Typen 2 bis 10

        for date in dates:
            date_url = f"https://www.lotto-rlp.de/keno/quoten?gbn=6&gcid={date}"
            for keno_type in keno_types:
                all_data.extend(scrape_keno_data_for_type(driver, date_url, keno_type))
    except KeyboardInterrupt:
        print("Ausführung wurde frühzeitig abgebrochen.")
    finally:
        driver.quit()
        if all_data:
            df = pd.DataFrame(all_data)
            df.to_csv(output_path, index=False)
            print(f"Daten erfolgreich in {output_path} gespeichert.")
        else:
            print("Keine Daten zum Speichern gefunden.")

url = 'https://www.lotto-rlp.de/keno/quoten'
output_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\keno_data.csv"
main(url, output_path)
