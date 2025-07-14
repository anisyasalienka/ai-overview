# scraper.py

import pickle
import random
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

import csv
import requests
import typing
import tempfile
import shutil
from openpyxl import Workbook  # type: ignore
# --------------------------- Setup & Utilities ---------------------------

def setup_chrome_driver():
    """Setup Chrome driver with options and Jakarta geolocation."""
    chrome_options = Options()
    temp_data = tempfile.mkdtemp()
    chrome_options.add_argument(f"--user-data-dir={temp_data}")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    chrome_options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(options=chrome_options)

    # Set Jakarta geolocation
    driver.execute_cdp_cmd('Emulation.setGeolocationOverride', {
        'latitude': -6.2088,
        'longitude': 106.8456,
        'accuracy': 100
    })

    return driver

def save_cookies_to_pickle(cookies, filename="cookies.pkl"):
    """Save cookies to a pickle file."""
    with open(filename, "wb") as f:
        pickle.dump(cookies, f)
    print(f"Cookies saved to {filename}")

def load_cookies_from_pickle(driver, filename="cookies.pkl"):
    """Load cookies from a pickle file into the driver."""
    try:
        with open(filename, "rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie({"name": cookie["name"], "value": cookie["value"]})
        print("Cookies loaded successfully.")
    except Exception as e:
        print(f"Could not load cookies: {e}")

# --------------------------- Bot Detection ---------------------------

class BotDetector:
    """
    Handles bot detection during scraping.
    """
    BOT_DETECTION_XPATH = "/html/body/div[1]/div/br[2]"  # Example: replace with actual element Google shows on captcha page

    @staticmethod
    def check_bot_detection(driver, timeout=5):
        """
        Check if bot detection is triggered.

        Args:
            driver: Selenium WebDriver instance
            timeout: seconds to wait

        Returns:
            bool: True if detected, False otherwise
        """
        try:
            time.sleep(random.uniform(1, 2))
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, BotDetector.BOT_DETECTION_XPATH))
            )
            print("⚠️ Bot detection triggered!")
            return True
        except TimeoutException:
            return False
        except Exception as e:
            print(f"Error checking bot detection: {str(e)}")
            return True

# --------------------------- Google Login ---------------------------

def google_login(email, password):
    """Login to Google account and return driver & cookies."""
    driver = setup_chrome_driver()
    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://accounts.google.com/ServiceLogin")

        # Enter email
        email_field = wait.until(EC.element_to_be_clickable((By.ID, "identifierId")))
        email_field.clear()
        email_field.send_keys(email)
        email_field.send_keys(Keys.RETURN)

        # Enter password
        password_field = wait.until(EC.element_to_be_clickable((By.NAME, "Passwd")))
        password_field.clear()
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

        # Wait for login completion
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="identifierId"]')))
            print("✅ Login successful!")
            print("Page title:", driver.title)
            cookies = driver.get_cookies()
            print("Cookies:", cookies)
            return driver, cookies
        except TimeoutException:
            print("Login may have failed or verification element not found.")
            print("Page title:", driver.title)
            print("URL:", driver.current_url)
            print(driver.page_source[:1000])  # First 1000 chars for debugging
            return None, None

    except Exception as e:
        print(f"Unexpected error: {e}")
        driver.quit()
        return None, None

# --------------------------- AI Overview Detector ---------------------------

# def ai_overview_detector(keywords):
#     """
#     Search keywords on Google, detect AI overview & bot detection.
#     Returns list of results.
#     """
#     results = []
#     driver = setup_chrome_driver()
#     wait = WebDriverWait(driver, 10)

#     try:
#         driver.get("https://www.google.com")
#         driver.delete_all_cookies()
#         load_cookies_from_pickle(driver)
#         driver.get("https://www.google.com")
#         time.sleep(2 + random.random())

#         for keyword in keywords:
#             try:
#                 search_box = wait.until(EC.element_to_be_clickable((By.NAME, "q")))
#                 search_box.clear()
#                 search_box.send_keys(keyword)
#                 search_box.send_keys(Keys.RETURN)
#                 time.sleep(2 + random.random())

#                 # Bot detection check
#                 if BotDetector.check_bot_detection(driver):
#                     print(f"⚠️ Google flagged as bot when searching '{keyword}'. Skipping.")
#                     results.append({
#                         "keyword": keyword,
#                         "detected": False,
#                         "text": None,
#                         "bot_detected": True
#                     })
#                     continue

#                 # Try find AI overview
#                 try:
#                     element = driver.find_element(By.ID, "m-x-content")
#                     detected_text = element.text
#                     print(f"✅ AI overview detected for '{keyword}': {detected_text[:100]}...")
#                     results.append({
#                         "keyword": keyword,
#                         "detected": True,
#                         "text": detected_text,
#                         "bot_detected": False
#                     })
#                 except Exception:
#                     print(f"❌ No AI overview for '{keyword}'")
#                     results.append({
#                         "keyword": keyword,
#                         "detected": False,
#                         "text": None,
#                         "bot_detected": False
#                     })

#                 # Go back before next search
#                 driver.get("https://www.google.com")
#                 time.sleep(1 + random.random())

#             except Exception as e:
#                 print(f"⚠️ Error searching '{keyword}': {e}")
#                 results.append({
#                     "keyword": keyword,
#                     "detected": False,
#                     "text": None,
#                     "bot_detected": False
#                 })

#     finally:
#         driver.quit()

#     return results

# def ai_overview_detector(all_keywords):
#     """
#     Detect AI Overview for list of keywords, split into random batches.
#     """
#     def split_keywords_random_batches(keywords, min_size=3, max_size=8):
#         batches = []
#         cursor = 0
#         while cursor < len(keywords):
#             batch_size = random.randint(min_size, max_size)
#             batch = keywords[cursor:cursor + batch_size]
#             batches.append(batch)
#             cursor += batch_size
#         return batches

#     batches = split_keywords_random_batches(all_keywords)
#     print(f"🔍 Total keywords: {len(all_keywords)}, running in {len(batches)} batches...")

#     results = []

#     for idx, batch in enumerate(batches):
#         print(f"\n🚀 Batch {idx+1}: {len(batch)} keywords")

#         driver = setup_chrome_driver()
#         wait = WebDriverWait(driver, 10)
#         batch_results = []

#         try:
#             driver.get("https://www.google.com")
#             driver.delete_all_cookies()
#             load_cookies_from_pickle(driver)
#             driver.get("https://www.google.com")
#             time.sleep(2 + random.random())

#             for keyword in batch:
#                 try:
#                     search_box = wait.until(EC.element_to_be_clickable((By.NAME, "q")))
#                     search_box.clear()
#                     search_box.send_keys(keyword)
#                     search_box.send_keys(Keys.RETURN)
#                     time.sleep(2 + random.random())

#                     if BotDetector.check_bot_detection(driver):
#                         print(f"⚠️ Bot detected for '{keyword}'")
#                         batch_results.append({
#                             "keyword": keyword,
#                             "detected": False,
#                             "text": None,
#                             "bot_detected": True
#                         })
#                         continue

#                     try:
#                         element = driver.find_element(By.ID, "m-x-content")
#                         detected_text = element.text
#                         print(f"✅ AI Overview for '{keyword}': {detected_text[:100]}...")
#                         batch_results.append({
#                             "keyword": keyword,
#                             "detected": True,
#                             "text": detected_text,
#                             "bot_detected": False
#                         })
#                     except Exception:
#                         print(f"❌ No AI Overview for '{keyword}'")
#                         batch_results.append({
#                             "keyword": keyword,
#                             "detected": False,
#                             "text": None,
#                             "bot_detected": False
#                         })

#                     driver.get("https://www.google.com")
#                     time.sleep(1 + random.random())

#                 except Exception as e:
#                     print(f"⚠️ Error on '{keyword}': {e}")
#                     batch_results.append({
#                         "keyword": keyword,
#                         "detected": False,
#                         "text": None,
#                         "bot_detected": False
#                     })

#         finally:
#             driver.quit()

#         results.extend(batch_results)

#         if idx < len(batches)-1:
#             wait_time = random.uniform(10, 20)
#             print(f"✅ Finished batch {idx+1}, waiting {wait_time:.1f}s before next batch...")
#             time.sleep(wait_time)

#     return results

def ai_overview_detector(all_keywords):
    """
    Detect AI Overview for list of keywords, split into random batches.
    Save every 100 results immediately.
    """
    def split_keywords_random_batches(keywords, min_size=3, max_size=8):
        batches = []
        cursor = 0
        while cursor < len(keywords):
            batch_size = random.randint(min_size, max_size)
            batch = keywords[cursor:cursor + batch_size]
            batches.append(batch)
            cursor += batch_size
        return batches

    batches = split_keywords_random_batches(all_keywords)
    print(f"🔍 Total keywords: {len(all_keywords)}, running in {len(batches)} batches...")

    results = []

    for idx, batch in enumerate(batches):
        print(f"\n🚀 Batch {idx+1}: {len(batch)} keywords")

        driver = setup_chrome_driver()
        wait = WebDriverWait(driver, 10)
        batch_results = []

        try:
            driver.get("https://www.google.com")
            driver.delete_all_cookies()
            load_cookies_from_pickle(driver)
            driver.get("https://www.google.com")
            time.sleep(2 + random.random())

            for keyword in batch:
                try:
                    search_box = wait.until(EC.element_to_be_clickable((By.NAME, "q")))
                    search_box.clear()
                    search_box.send_keys(keyword)
                    search_box.send_keys(Keys.RETURN)
                    time.sleep(2 + random.random())

                    if BotDetector.check_bot_detection(driver):
                        print(f"⚠️ Bot detected for '{keyword}'")
                        batch_results.append({
                            "keyword": keyword,
                            "detected": False,
                            "text": None,
                            "bot_detected": True
                        })
                        continue

                    try:
                        element = driver.find_element(By.ID, "m-x-content")
                        detected_text = element.text
                        print(f"✅ AI Overview for '{keyword}': {detected_text[:100]}...")
                        batch_results.append({
                            "keyword": keyword,
                            "detected": True,
                            "text": detected_text,
                            "bot_detected": False
                        })
                    except Exception:
                        print(f"❌ No AI Overview for '{keyword}'")
                        batch_results.append({
                            "keyword": keyword,
                            "detected": False,
                            "text": None,
                            "bot_detected": False
                        })

                    driver.get("https://www.google.com")
                    time.sleep(1 + random.random())

                except Exception as e:
                    print(f"⚠️ Error on '{keyword}': {e}")
                    batch_results.append({
                        "keyword": keyword,
                        "detected": False,
                        "text": None,
                        "bot_detected": False
                    })

        finally:
            	driver.quit()
	        shutil.rmtree(temp_data, ignore_errors=True)

        # Merge current batch into results
        results.extend(batch_results)

        # ✅ Save every 100 results collected so far
        if len(results) % 100 == 0 or idx == len(batches) - 1:
            part = len(results) // 100
            filename = f"ai_overview_results_part{part + 1}.xlsx"
            save_results_to_excel(results[-100:], filename)
            print(f"✅ Saved last 100 results to {filename}")

        if idx < len(batches) - 1:
            wait_time = random.uniform(10, 20)
            print(f"✅ Finished batch {idx+1}, waiting {wait_time:.1f}s before next batch...")
            time.sleep(wait_time)

    return results

# --------------------------- Scrap keywords ---------------------------
def scrape_keywords_from_spreadsheet() -> typing.List[str]:
    csv_url = 'https://docs.google.com/spreadsheets/d/1VONI6nuRmR_KRSlBKI8HKzqwFPOgka1CxpaJq1S863U/export?format=csv&gid=0'
    response = requests.get(csv_url)
    response.raise_for_status()

    keywords = []
    reader = csv.reader(response.text.splitlines())
    next(reader, None)  # Skip the header row if there's one

    for row in reader:
        if row and row[0].strip():
            keywords.append(row[0].strip())
    return keywords

# --------------------------- Download Excel ---------------------------
def save_results_to_excel(results, filename="ai_overview_results.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Results"

    # Write header
    # ws.append(["Keyword", "Detected", "Bot Detected", "Text"])
    ws.append(["Keyword"])
    # Write data rows
    for r in results:
        ws.append([
            r["keyword"],
            r["detected"],
            r.get("bot_detected", False),
            r["text"] or ""
        ])

    wb.save(filename)
    print(f"✅ Results saved to '{filename}'")

# --------------------------- Main ---------------------------

def main():
    email = "your_email@gmail.com"   # replace
    password = "your_password"       # replace

    driver, cookies = google_login(email, password)

    if driver:
        try:
            save_cookies_to_pickle(cookies)
        finally:
            driver.quit()
    else:
        print("Login failed.")

    # Example run:
    keywords = ["openai", "machine learning", "deep learning"]
    results = ai_overview_detector(keywords)
    print("\n=== Results ===")
    for r in results:
        print(r)

# --------------------------- Result Excel ---------------------------

def save_results_in_chunks(results, chunk_size=100):
    """
    Save results into separate Excel files every `chunk_size` items.
    """
    for i in range(0, len(results), chunk_size):
        chunk = results[i:i + chunk_size]
        filename = f"ai_overview_results_part{i//chunk_size + 1}.xlsx"
        save_results_to_excel(chunk, filename)
        print(f"✅ Saved {len(chunk)} results to {filename}")
