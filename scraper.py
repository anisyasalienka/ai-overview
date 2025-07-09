# def ai_overview_detector(keywords):
#     print(keywords)
#     return keywords

# scraper.py

import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from selenium.webdriver.chrome.options import Options

def google_login(email, password):
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

        # ✅ Improved: wait for Google account avatar or account icon instead of hardcoded ID
        try:
            wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="identifierId"]')) 
            )
            print("Login successful!")

            # Print current page title
            print("Current page title:", driver.title)

            # Get cookies
            cookies = driver.get_cookies()
            print("Cookies:", cookies)

            return driver, cookies

        except TimeoutException:
            print("Login may have failed or verification element not found.")
            print("Page title:", driver.title)
            print("Current URL:", driver.current_url)
            # Optional: print HTML for debugging
            print(driver.page_source[:1000])  # print first 1000 chars
            return None, None

    except Exception as e:
        print(f"Unexpected error: {e}")
        driver.quit()
        return None, None

def save_cookies_to_pickle(cookies, filename="cookies.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(cookies, f)
    print(f"Cookies saved to {filename}")

def main():
    email = "boxyummie@gmail.com"
    password = "yummie123"

    driver, cookies = google_login(email, password)

    if driver:
        try:
            save_cookies_to_pickle(cookies)
        finally:
            driver.quit()
    else:
        print("Login failed. Please check credentials or check browser output above.")

import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import random

def setup_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(options=chrome_options)

    # Set Jakarta geolocation
    driver.execute_cdp_cmd('Emulation.setGeolocationOverride', {
        'latitude': -6.2088,
        'longitude': 106.8456,
        'accuracy': 100
    })

    return driver

def load_cookies_from_pickle(driver, filename="cookies.pkl"):
    try:
        with open(filename, "rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie({"name": cookie["name"], "value": cookie["value"]})
        print("Cookies loaded successfully.")
    except Exception as e:
        print(f"Could not load cookies: {e}")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

def ai_overview_detector(keywords):
    results = []
    driver = setup_chrome_driver()
    wait = WebDriverWait(driver, 10)

    try:
        # Start by loading Google and cookies
        driver.get("https://www.google.com")
        driver.delete_all_cookies()
        load_cookies_from_pickle(driver)
        driver.get("https://www.google.com")
        time.sleep(2 + random.random())

        for keyword in keywords:
            try:
                # Wait for and fill the search box
                search_box = wait.until(EC.element_to_be_clickable((By.NAME, "q")))
                search_box.clear()
                search_box.send_keys(keyword)
                search_box.send_keys(Keys.RETURN)
                time.sleep(2 + random.random())

                try:
                    # Try to find AI Overview
                    element = driver.find_element(By.ID, "m-x-content")
                    detected_text = element.text
                    print(f"✅ AI overview detected for '{keyword}': {detected_text[:100]}...")
                    results.append({
                        "keyword": keyword,
                        "detected": True,
                        "text": detected_text
                    })
                except Exception:
                    print(f"❌ No AI overview found for '{keyword}'")
                    results.append({
                        "keyword": keyword,
                        "detected": False,
                        "text": None
                    })
                    print(driver.page_source)

                # Go back to Google home page before next search
                driver.get("https://www.google.com")
                time.sleep(1 + random.random())

            except Exception as e:
                print(f"⚠️ Error searching '{keyword}': {e}")
                results.append({
                    "keyword": keyword,
                    "detected": False,
                    "text": None
                })

    finally:
        driver.quit()

    return results
