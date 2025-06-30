import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.parse
import requests

def send_data_to_backend(products):
    url = "http://localhost:5000/insert-products"
    payload = {"table_name": "produse_emag", "products": products}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 201:
            print(f"Data was successfully sent and saved in produse_emag!")
        else:
            print(f"Error while sending data: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Connection error with the backend: {e}")

def clean_price(price):
    price = price.replace(".", "").replace(",", ".")
    try:
        return float(price)
    except ValueError:
        return None

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

driver_path = os.path.abspath("D:/Downloads/Licenta/frontend/drivers/chromedriver.exe")
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service, options=options)

try:
    start = datetime.now()
    if len(sys.argv) > 1:
        keyword = sys.argv[1].strip().lower()
    else:
        print("Error: No search term provided.")
        sys.exit(1)

    keyword_exact = keyword.lower()
    print(f"Running scraping on eMAG for keyword: {keyword}")

    base_url = "https://www.emag.ro/"
    search_url = f"{base_url}search/{urllib.parse.quote(keyword)}"

    next_page_url = search_url
    products = []
    current_date = datetime.now().strftime("%Y-%m-%d")

    while next_page_url and len(products) < 150:
        driver.get(next_page_url)

        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, "card-v2-info"))
            )
        except:
            print("No products found on this page. Stopping.")
            break

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        found_products_on_page = False

        for product in soup.select('.card-v2-info'):
            if len(products) >= 150:
                break

            name_tag = product.find('h2', class_='card-v2-title-wrapper')
            name = name_tag.get_text(strip=True) if name_tag else "Name unavailable"

            if keyword_exact in name.lower():
                found_products_on_page = True

                link_tag = product.find('a', class_='js-product-url')
                link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else "Link unavailable"

                price_container = product.find_next('p', class_='product-new-price')
                if price_container:
                    span_de_la = price_container.find('span', class_='fs-12')
                    if span_de_la:
                        span_de_la.extract()
                    price_int = price_container.get_text(strip=True).replace("Lei", "").strip()
                else:
                    price_int = "Price unavailable"

                decimal_container = product.find_next('small', class_='mf-decimal')
                decimal_part = decimal_container.get_text(strip=True) if decimal_container else ""

                price = f"{price_int}{decimal_part}".rstrip(',') if price_int != "Price unavailable" else "Price unavailable"

                already_in_list = any(p['name'] == name and p['link'] == link for p in products)
                if not already_in_list:
                    if len(products) >= 150:
                        break
                    products.append({
                        'name': name,
                        'link': link,
                        'price': clean_price(price),
                        'data adaugarii': current_date
                    })

        next_page_tag = soup.find('a', class_='js-change-page', attrs={'aria-label': 'Next'})
        if next_page_tag and 'href' in next_page_tag.attrs:
            next_page_url = base_url.rstrip('/') + next_page_tag['href']
        else:
            break

        if len(products) >= 150:
            products = products[:150]
            break

    if products:
        send_data_to_backend(products)
    else:
        print("\nNo relevant products found.")

    print("eMAG scraping completed.")
    end = datetime.now()
    print(f"eMAG scraping took {(end - start).total_seconds()} seconds.", flush=True)

    try:
        requests.post("http://localhost:5000/scrape-done", json={"query": keyword, "source": "emag"})
        print(f"[INFO] Notified backend that scraping for '{keyword}' is done.")
    except Exception as e:
        print(f"[WARNING] Could not notify backend that scraping for {keyword} is done: {e}")

finally:
    driver.quit()
