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

def retry_operation(driver, operation, attempts=3):
    """Tries an operation multiple times if a StaleElementReferenceException occurs."""
    for attempt in range(attempts):
        try:
            return operation()
        except StaleElementReferenceException:
            print(f"Attempt {attempt + 1} of {attempts} failed. Retrying...")
            time.sleep(1)  # Short pause before retrying
            if attempt < attempts - 1:
                continue  # Try again
            else:
                raise  # Last attempt: pass on the exception

def scrape_keno_data_for_type(driver, date_url, keno_type, date_text):
    driver.get(date_url)
    
    # Warten auf das Dropdown und Auswahl des Keno-Typs
    select = Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'kenotyp'))))
    select.select_by_value(str(keno_type))
    
    # Sicherstellen, dass die Seite geladen wurde
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'table_quoten')))
    time.sleep(2)  # Kurze Pause, um sicherzustellen, dass die Seite vollständig geladen wurde
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    data = []
    
    # Selektiere den spezifischen Container, der die erste Tabelle umschließt
    table_container = soup.select_one('body > main > div.quoten > section.row.row_outer.margin_elements > div:nth-child(2)')
    
    if table_container:
        # Extrahiere Daten nur aus diesem Container
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
                '1 Euro Gewinn': euro_values[0] if len(euro_values) > 0 else 'N/A',
                # Ergänzen Sie weitere Euro-Werte, falls benötigt
            }
            
            print(f"Extrahierte Daten für Datum {date_text} und Keno-Typ {keno_type}: {data_entry}")
            data.append(data_entry)
    else:
        print("Der spezifizierte Container für die erste Tabelle wurde nicht gefunden. Überprüfen Sie den CSS-Selektor.")
    
    return data





def main(url, output_path):
    chrome_options = Options()
    chromedriver_path = "C:\\Users\\Admin1\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
    service = Service(chromedriver_path)

    driver = webdriver.Chrome(service=service, options=chrome_options)
    all_data = []

    try:
        driver.get(url)
        keno_types = [str(i) for i in range(2, 11)]

        date_select = Select(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'gcid'))))
        dates = [(option.get_attribute('value'), option.text.strip()) for option in date_select.options]

        for value, date_text in dates:
            for keno_type in keno_types:
                def operation():
                    date_select = Select(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'gcid'))))
                    date_select.select_by_value(value)

                    date_url = f"https://www.lotto-rlp.de/keno/quoten?gbn=6&gcid={value}"
                    return scrape_keno_data_for_type(driver, date_url, keno_type, date_text)
                
                all_data.extend(retry_operation(driver, operation))
    except KeyboardInterrupt:
        print("Script was interrupted by the user. Saving collected data.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        driver.quit()
        if all_data:
            df = pd.DataFrame(all_data)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"Data successfully saved to {output_path}.")
        else:
            print("No data found to save.")

if __name__ == "__main__":
    url = 'https://www.lotto-rlp.de/keno/quoten'
    output_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\keno_data.csv"
    main(url, output_path)






#url = 'https://www.lotto-rlp.de/keno/quoten'
    # chromedriver_path = "C:\\Users\\Admin1\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
  
    # output_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\keno_data.csv"

