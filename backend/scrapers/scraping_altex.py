import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.parse
import sys
import requests

def send_data_to_backend(products):
    url = "http://localhost:5000/insert-products"
    payload = {"table_name": "produse_altex", "products": products}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 201:
            print(f"Data was successfully sent and saved in produse_altex!")
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

    print(f"Running scraping on Altex for keyword: {keyword}")

    keyword_exact = keyword.lower()
    base_url = "https://altex.ro/"
    search_url = f"{base_url}cauta/?q=" + urllib.parse.quote(keyword)

    page = 1
    products = []

    while len(products) < 150:
        url = search_url if page == 1 else f"{base_url}cauta/filtru/p/{page}/?q=" + urllib.parse.quote(keyword)
        driver.get(url)

        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, "Product-photoWrapper"))
            )
        except:
            print(f"Page {page} did not load products. Stopping search.")
            break

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        current_date = datetime.now().strftime("%Y-%m-%d")

        page_products = []
        for product in soup.select('.Product-photoWrapper'):
            img_tag = product.find('img')
            name = img_tag.get("alt", "Name unavailable") if img_tag else "Name unavailable"

            if keyword_exact in name.lower():
                link_tag = product.find_parent('a')
                link = "https://altex.ro" + link_tag['href'] if link_tag and 'href' in link_tag.attrs else "Link unavailable"

                price_container = product.find_next('div', class_='leading-none text-red-brand -tracking-0.48 lg:-tracking-0.56')
                price = "Price unavailable"

                if price_container:
                    price_tag = price_container.find('span', class_='Price-int leading-none')
                    decimal_tag = price_container.find('sup', class_='inline-block -tracking-0.33')

                    if price_tag:
                        price = price_tag.get_text(strip=True)
                        if decimal_tag:
                            decimal_value = decimal_tag.get_text(strip=True).replace(",", "").strip()
                            price += "," + decimal_value

                page_products.append({
                    'name': name,
                    'link': link,
                    'price': clean_price(price),
                    'data adaugarii': current_date
                })

                if len(products) + len(page_products) >= 150:
                    break

        products.extend(page_products)

        if len(page_products) == 0:
            print("No relevant products found on this page. Stopping.")
            break

        next_div = soup.find("div", class_="hidden md:inline-block", string="Pagina urmatoare")
        if not next_div or not next_div.find_parent("a"):
            print("No next page. Stopping.")
            break

        page += 1

    if products:
        send_data_to_backend(products)
    else:
        print("\nNo relevant products found.")

    print("Altex scraping completed.")
    end = datetime.now()
    print(f"Altex scraping took {(end - start).total_seconds()} seconds.", flush=True)

    try:
        requests.post("http://localhost:5000/scrape-done", json={"query": keyword, "source": "altex"})
        print(f"[INFO] Notified backend that scraping for '{keyword}' is done.")
    except Exception as e:
        print(f"[WARNING] Could not notify backend that scraping for {keyword} is done: {e}")

finally:
    driver.quit()


