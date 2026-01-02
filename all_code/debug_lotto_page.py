#!/usr/bin/env python
"""Debug script to analyze Lotto 6aus49 page structure."""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

chrome_options = Options()
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    url = 'https://www.lotto-rlp.de/lotto6aus49/quoten'
    print(f"Loading {url}...")
    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Save raw HTML for analysis
    with open('lotto_page_debug.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("Saved lotto_page_debug.html")

    # Find all tables
    tables = soup.find_all('table')
    print(f"\nFound {len(tables)} tables:")
    for i, t in enumerate(tables):
        classes = t.get('class', [])
        print(f"  Table {i+1}: classes={classes}")
        rows = t.find_all('tr')[:3]  # First 3 rows
        for row in rows:
            cells = row.find_all(['td', 'th'])
            print(f"    Row: {[c.get_text(strip=True)[:30] for c in cells]}")

    # Find divs with 'quoten' in class
    quoten_divs = soup.find_all('div', class_=lambda x: x and 'quoten' in str(x).lower() if x else False)
    print(f"\nFound {len(quoten_divs)} divs with 'quoten' class:")
    for div in quoten_divs[:5]:
        print(f"  Class: {div.get('class')}")
        text = div.get_text(strip=True)[:100]
        print(f"  Text: {text}...")

    # Find elements containing "Gewinnklasse"
    gk_elements = soup.find_all(string=lambda t: t and 'Gewinnklasse' in t)
    print(f"\nFound {len(gk_elements)} elements with 'Gewinnklasse':")
    for el in gk_elements[:5]:
        parent = el.parent
        print(f"  Parent tag: {parent.name}, class: {parent.get('class')}")
        print(f"  Text: {el.strip()[:60]}")

finally:
    driver.quit()
