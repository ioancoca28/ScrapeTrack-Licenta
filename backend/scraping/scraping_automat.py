import subprocess
import time
import requests
from datetime import datetime

products = ["iphone 13"]

flask_server = "D:\\Downloads\\Licenta\\.venv\\Scripts\\python.exe"
flask_app = "D:\\Downloads\\Licenta\\backend\\app.py"

scraping_url = "http://localhost:5000/scrape-all"
log_path = r"D:\Downloads\Licenta\backend\scraping\scraping_log.txt"

def log(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def is_flask_running():
    try:
        response = requests.get("http://localhost:5000/login")
        return response.status_code == 200
    except:
        return False

def start_flask_server():
    return subprocess.Popen([flask_server, flask_app])

def stop_flask_server(flask_process):
    flask_process.terminate()


def wait_for_scraping(query, max_attempts=30, delay=10):
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:5000/scrape-status", params={"query": query})
            if response.status_code == 200:
                data = response.json()
                if not data.get("scraping", True):
                    return True
        except Exception as e:
            log(f"[E] Error checking scraping status for '{query}': {e}")
        time.sleep(delay)
    return False

def start_scraping():
    if is_flask_running():
        log("[i] Flask server already running. Script skipped.")
        print("[!] Flask server is already running. Exiting.")
        return

    flask_process = start_flask_server()
    time.sleep(5)

    for query in products:
        log(f"Starting scraping for: {query}")
        try:
            response = requests.post(scraping_url, json={"query": query})
            if response.status_code == 200:
                log(f"Scraping started for '{query}'")
            else:
                log(f"[E] Error starting scraping for '{query}': {response.json()}")
                continue
        except Exception as e:
            log(f"[E] Error sending POST request for '{query}': {e}")
            continue

        if wait_for_scraping(query):
            log(f"Scraping completed for '{query}'")
        else:
            log(f"[!] Timeout: scraping for '{query}' did not finish in time")

    stop_flask_server(flask_process)

if __name__ == "__main__":
    start_scraping()
