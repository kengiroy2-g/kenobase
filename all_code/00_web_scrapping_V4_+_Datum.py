
# ce programm permet de copier les donne de Kono sur la page de "Lotto-RLP" dans une periode predefinit en donnant la Date et Le Jour


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup
import pandas as pd
import time


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
    retries = 0
    data = []
    while retries < max_retries:
        driver.get(date_url)
        select = Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'kenotyp'))))
        select.select_by_value(str(keno_type))
        
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'table_quoten')))
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
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
                print(f"Extrahierte Daten für Datum {date_text} und Keno-Typ {keno_type}: {data_entry}")
                data.append(data_entry)
            break
        else:
            retries += 1
            print(f"Keine Daten für {date_text} gefunden, Seite wird neu geladen...")
            time.sleep(5)
            if retries >= max_retries:
                print("Maximale Neuladeversuche erreicht. Daten für diesen Tag und Typ könnten fehlen.")
    
    return data

def main(url, output_path):
    chrome_options = Options()
    chromedriver_path = "C:\\Users\\Admin1\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
    service = Service(chromedriver_path)

    driver = webdriver.Chrome(service=service, options=chrome_options)
    all_data = []
    start_date = "Sa, 31.12."

    try:
        driver.get(url)
        select_year(driver, '2022')
        time.sleep(5)

        date_select = Select(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'gcid'))))
        dates = [(option.get_attribute('value'), option.text) for option in date_select.options]

        start_extraction = False
        for value, date_text in dates:
            if date_text == start_date:
                start_extraction = True

            if start_extraction:
                for keno_type in range(2, 11):
                    date_url = f"https://www.lotto-rlp.de/keno/quoten?gbn=6&gcid={value}"
                    data = scrape_keno_data_for_type(driver, date_url, keno_type, date_text)
                    all_data.extend(data)

    except KeyboardInterrupt:
        print("Skript durch Benutzer unterbrochen. Gesammelte Daten werden gespeichert.")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
    finally:
        driver.quit()
        if all_data:
            df = pd.DataFrame(all_data)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"Daten erfolgreich in {output_path} gespeichert.")
        else:
            print("Keine Daten gefunden zum Speichern.")

if __name__ == "__main__":
    url = 'https://www.lotto-rlp.de/keno/quoten'
    output_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\keno_RohData2022.csv"
    main(url, output_path)



# def main(url, output_path):
#     chrome_options = Options()
#     chromedriver_path = "C:\\Users\\Admin1\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
#     service = Service(chromedriver_path)

#     driver = webdriver.Chrome(service=service, options=chrome_options)
#     all_data = []

#     try:
#         driver.get(url)
#         keno_types = [str(i) for i in range(2, 11)]

#         date_select = Select(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'gcid'))))
#         dates = [(option.get_attribute('value'), option.text.strip()) for option in date_select.options]

#         for value, date_text in dates:
#             for keno_type in keno_types:
#                 def operation():
#                     date_select = Select(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'gcid'))))
#                     date_select.select_by_value(value)

#                     date_url = f"https://www.lotto-rlp.de/keno/quoten?gbn=6&gcid={value}"
#                     return scrape_keno_data_for_type(driver, date_url, keno_type, date_text)
                
#                 all_data.extend(retry_operation(driver, operation))
#     except KeyboardInterrupt:
#         print("Script was interrupted by the user. Saving collected data.")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#     finally:
#         driver.quit()
#         if all_data:
#             df = pd.DataFrame(all_data)
#             df.to_csv(output_path, index=False, encoding='utf-8-sig')
#             print(f"Data successfully saved to {output_path}.")
#         else:
#             print("No data found to save.")

# if __name__ == "__main__":
#     url = 'https://www.lotto-rlp.de/keno/quoten'
#     output_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\keno_data.csv"
#     main(url, output_path)




#url = 'https://www.lotto-rlp.de/keno/quoten'
    # chromedriver_path = "C:\\Users\\Admin1\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
  
    # output_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\keno_data.csv"