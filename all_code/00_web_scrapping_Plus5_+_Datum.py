
# ce programm permet de copier les donne de la Zusatz lotterie Plus 5Kono sur la page de "Lotto-RLP" dans une periode predefinit en donnant la Date et Le Jour
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

def scrape_keno_data_for_type(driver, date_url, date_text):
    driver.get(date_url)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'table_quoten')))
    time.sleep(2)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    data = []

    # Angenommen, die zweite Tabelle folgt direkt nach einem eindeutigen Marker im Dokument, wie einer Überschrift
    table_container = soup.select_one('div.body_font.padding_left_right_0')
    
    if table_container:
        quoten_blocks = table_container.find_all('div', class_='table_quoten')
        
        for block in quoten_blocks:
            gewinnklasse_info = block.find('div', class_='col-md-4', recursive=False)
            gewinnklasse = gewinnklasse_info.select_one('span.success_class').get_text(strip=True) if gewinnklasse_info else 'N/A'
            gewinner = block.select_one('div.text_align > span').get_text(strip=True)
            gewinnquote = block.select('div.text_align > span')[-1].get_text(strip=True)
            
            data_entry = {
                'Datum': date_text,
                'Gewinnklasse': gewinnklasse,
                'Anzahl der Gewinner': gewinner,
                'Gewinnquote': gewinnquote
            }
            print(f"Extrahierte Daten für Datum {date_text}: {data_entry}")
            data.append(data_entry)
    else:
        print("Keine Daten in der zweiten Tabelle gefunden.")
    
    return data

def main(url, output_path):
    chrome_options = Options()
    chromedriver_path = "C:\\Users\\Admin1\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    all_data = []

    try:
        driver.get(url)
        select_year(driver, '2023')
        time.sleep(5)

        date_select = Select(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'gcid'))))
        dates = [(option.get_attribute('value'), option.text.strip()) for option in date_select.options]

        for value, date_text in dates:
            date_url = f"https://www.lotto-rlp.de/keno/quoten?gbn=6&gcid={value}"
            all_data.extend(scrape_keno_data_for_type(driver, date_url, date_text))

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




# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait, Select
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import StaleElementReferenceException
# from bs4 import BeautifulSoup
# import pandas as pd
# import time

# def select_year(driver, year):
#     # Warten, bis das Dropdown-Menü geladen ist
#     WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'year')))
#     year_select = Select(driver.find_element(By.ID, 'year'))
#     year_select.select_by_value(year)  # Wählen Sie das Jahr als Wert


# def retry_operation(driver, operation, attempts=3):
#     """Tries an operation multiple times if a StaleElementReferenceException occurs."""
#     for attempt in range(attempts):
#         try:
#             return operation()
#         except StaleElementReferenceException:
#             print(f"Attempt {attempt + 1} of {attempts} failed. Retrying...")
#             time.sleep(1)  # Short pause before retrying
#             if attempt < attempts - 1:
#                 continue  # Try again
#             else:
#                 raise  # Last attempt: pass on the exception

# def scrape_keno_data_for_type(driver, date_url, date_text):
#     driver.get(date_url)
    
#     # Kurzes Warten, um sicherzustellen, dass die Seite vollständig geladen wurde
#     WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'table_quoten')))
#     time.sleep(2)
    
#     soup = BeautifulSoup(driver.page_source, 'html.parser')
#     data = []
    
#     # Annahme: Die zweite Tabelle ist direkt nach der ersten Tabelle
#     # Hier müsste die Logik angepasst werden, um spezifisch die zweite Tabelle zu selektieren
#     table_containers = soup.select('div.body_font.padding_left_right_0 > div.table_quoten')
    
#     if table_containers:
#         for block in table_containers:
#             gewinnklasse = block.select_one('div.col-md-4.col-sm-4.col-xs-7 > span.success_class').get_text(strip=True)
#             gewinner = block.select_one('div.col-md-4.col-sm-4.col-xs-6.col-sm-offset-0.text_align > span').get_text(strip=True)
#             gewinnquote = block.select_one('div.col-md-4.col-sm-4.col-xs-6.col-sm-offset-0.text_align > span').get_text(strip=True)
            
#             data_entry = {
#                 'Datum': date_text,
#                 'Gewinnklasse': gewinnklasse,
#                 'Anzahl der Gewinner': gewinner,
#                 'Gewinnquote': gewinnquote.replace(u'\xa0', u' ')
#             }
            
#             print(f"Extrahierte Daten für Datum {date_text}: {data_entry}")
#             data.append(data_entry)
#     else:
#         print("Keine Daten in der zweiten Tabelle gefunden.")
    
#     return data


# def main(url, output_path):
#     chrome_options = webdriver.ChromeOptions()
#     chromedriver_path = "C:\\Users\\Admin1\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
#     service = Service(chromedriver_path)

#     driver = webdriver.Chrome(service=service, options=chrome_options)
#     all_data = []
#     start_date = "So, 31.12."  # Festgelegtes Startdatum

#     try:
#         driver.get(url)
#         select_year(driver, '2023')  # Wählen Sie das Jahr 2023 aus dem Dropdown
#         time.sleep(5)  # Warten Sie einen Moment, bis die Seite nach der Auswahl des Jahres neu geladen wurde

#         date_select = Select(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'gcid'))))
#         dates = [(option.get_attribute('value'), option.text.strip()) for option in date_select.options]

#         start_extraction = False
#         for value, date_text in dates:
#             if date_text == start_date:
#                 start_extraction = True  # Starten Sie die Datenextraktion ab dem festgelegten Datum

#             if start_extraction:
#                 date_url = f"https://www.lotto-rlp.de/keno/quoten?gbn=6&gcid={value}"
#                 data = scrape_keno_data_for_type(driver, date_url, date_text)
#                 all_data.extend(data)

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
#     output_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\keno_PLUS5-2023.csv"
#     main(url, output_path)







#url = 'https://www.lotto-rlp.de/keno/quoten'
    # chromedriver_path = "C:\\Users\\Admin1\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
  
    # output_path = "C:\\Users\\Admin1\\Documents\\01_PROJECT\\Keno_GPTs\\keno_data.csv"