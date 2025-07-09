# scraper.py

import pickle
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException

def setup_chrome_driver():
    options = uc.ChromeOptions()
    # if headless:
    #     
    #options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--disable-notifications')
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    )

    driver = uc.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    try:
        driver.execute_cdp_cmd('Emulation.setGeolocationOverride', {
            'latitude': -6.2088,
            'longitude': 106.8456,
            'accuracy': 100
        })
    except Exception as e:
        print(f"Could not set geolocation: {e}")
    return driver

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

        # Wait until redirected or login complete
        time.sleep(3)
        print("Login successful! Current URL:", driver.current_url)

        cookies = driver.get_cookies()
        print(f"Collected {len(cookies)} cookies.")
        return driver, cookies

    except Exception as e:
        print(f"Unexpected login error: {e}")
        driver.quit()
        return None, None

def save_cookies_to_pickle(cookies, filename="cookies.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(cookies, f)
    print(f"Cookies saved to {filename}")

def load_cookies_from_pickle(driver, filename="cookies.pkl"):
    try:
        with open(filename, "rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie({"name": cookie["name"], "value": cookie["value"]})
        print("Cookies loaded successfully.")
    except Exception as e:
        print(f"Could not load cookies: {e}")

def ai_overview_detector(keywords):
    results = []
    driver = setup_chrome_driver()
    wait = WebDriverWait(driver, 10)

    try:
        driver.get("https://www.google.com")
        driver.delete_all_cookies()
        load_cookies_from_pickle(driver)
        driver.get("https://www.google.com")
        time.sleep(2 + random.random())

        for keyword in keywords:
            try:
                search_box = wait.until(EC.element_to_be_clickable((By.NAME, "q")))
                search_box.clear()
                search_box.send_keys(keyword)
                search_box.send_keys(Keys.RETURN)

                time.sleep(2 + random.random())

                try:
                    element = driver.find_element(By.ID, "m-x-content")
                    detected_text = element.text
                    print(f"✅ AI overview detected for '{keyword}': {detected_text[:100]}...")
                    results.append({"keyword": keyword, "detected": True, "text": detected_text})
                except Exception:
                    print(f"❌ No AI overview found for '{keyword}'")
                    results.append({"keyword": keyword, "detected": False, "text": None})

                driver.get("https://www.google.com")
                time.sleep(1 + random.random())

            except Exception as e:
                print(f"Error searching '{keyword}': {e}")
                results.append({"keyword": keyword, "detected": False, "text": None})

    finally:
        driver.quit()
    
    return results  # ✅ This is safe and works with FastAPI

# def ai_overview_detector(keyword):
#     driver = setup_chrome_driver()
#     wait = WebDriverWait(driver, 10)

#     try:
#         driver.get("https://www.google.com")  # visit so domain matches
#         driver.delete_all_cookies()           # clear existing
#         load_cookies_from_pickle(driver)      # add saved cookies
#         driver.get("https://www.google.com")  # refresh with new cookies
#         time.sleep(2 + random.random())

#         search_box = wait.until(EC.element_to_be_clickable((By.NAME, "q")))
#         search_box.clear()
#         search_box.send_keys(keyword)
#         search_box.send_keys(Keys.RETURN)

#         time.sleep(2 + random.random())

#         try:
#             element = driver.find_element(By.ID, "m-x-content")
#             detected_text = element.text
#             print(f"✅ AI overview detected for '{keyword}': {detected_text[:100]}...")
#             return {"detected": True, "text": detected_text}
#         except Exception:
#             print(f"❌ No AI overview found for '{keyword}'")
#             return {"detected": False, "text": None}

#     except Exception as e:
#         print(f"Error during detection for '{keyword}': {e}")
#         return {"detected": False, "text": None}
#     finally:
#         driver.quit()

def main():
    email = "boxyummie@gmail.com"
    password = "yummie123"

    driver, cookies = google_login(email, password)
    if driver and cookies:
        save_cookies_to_pickle(cookies)
        driver.quit()

    else:
        print("Login failed. Please check credentials or see log above.")
