import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime
import re
import requests

def send_data_to_backend(products):
    url = "http://localhost:5000/insert-products"
    payload = {"table_name": "produse_flanco", "products": products}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 201:
            print(f"Data was successfully sent and saved in produse_flanco!")
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
    print(f"Running scraping on Flanco for keyword: {keyword}")

    base_url = "https://www.flanco.ro/catalogsearch/result/?q="
    search_url = f"{base_url}{urllib.parse.quote(keyword)}"

    next_page_url = search_url
    current_date = datetime.now().strftime("%Y-%m-%d")
    all_products = []
    page = 1

    while next_page_url and len(all_products) < 150:
        driver.get(next_page_url)

        try:
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".product-item"))
            )
        except:
            print(f"Page {page}: products did not load.")
            break

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        page_products = []
        for product in soup.select('.product-item-info'):
            name_tag = product.find('a', class_='product-item-link')
            name = name_tag.get_text(strip=True) if name_tag else "Name unavailable"

            if keyword_exact in name.lower():
                link = name_tag['href'] if name_tag and 'href' in name_tag.attrs else "Link unavailable"
                price_tag = product.select_one(".special-price") or product.select_one(".price")
                price_text = price_tag.get_text(strip=True) if price_tag else "Price unavailable"
                price = re.sub(r"[^\d,.]", "", price_text)

                already_in_list = any(p['name'] == name and p['link'] == link for p in all_products)
                if not already_in_list:
                    if len(all_products) >= 150:
                        next_page_url = None
                        break
                    page_products.append({
                        'name': name,
                        'link': link,
                        'price': clean_price(price),
                        'data_adaugarii': current_date
                    })

        if page == 1 and len(page_products) == 0:
            print("No relevant products on the first page. Stopping.")
            break

        max_remaining = 150 - len(all_products)
        all_products.extend(page_products[:max_remaining])

        next_page_tag = soup.select_one("li.pages-item-next a")
        if next_page_tag and "href" in next_page_tag.attrs:
            next_page_url = next_page_tag["href"]
            page += 1
        else:
            print("No more next pages.")
            break

    if all_products:
        send_data_to_backend(all_products)
    else:
        print("\nNo relevant products found.")

    try:
        requests.post("http://localhost:5000/scrape-done", json={"query": keyword, "source": "flanco"})
        print(f"[INFO] Notified backend that scraping for '{keyword}' is done.")
    except Exception as e:
        print(f"[WARNING] Could not notify backend that scraping for {keyword} is done: {e}")

    print("Flanco scraping completed.")
    end = datetime.now()
    print(f"Flanco scraping took {(end - start).total_seconds()} seconds.", flush=True)

finally:
    driver.quit()
