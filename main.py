import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

load_dotenv()
accounts = []
month = os.getenv('MONTH')
for i in range(1, 13):
    user = os.getenv(f'USERNAME_{i}')
    pw = os.getenv(f'PASSWORD_{i}')
    if user and pw:
        accounts.append({"username": user, "password": pw})

LOGIN_URL = "https://www.zinzino.com/shop/site/DE/de-DE/login/Login"
DOWNLOAD_DIR = "pdf_rechnungen"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

from selenium.webdriver.chrome.options import Options

def date_in_last_month(date_str):
    d = datetime.strptime(date_str, "%d.%m.%Y")
    if month:
        try:
            m = datetime.strptime(month, "%m.%Y")
            lm_start = m.replace(day=1)
            next_month = m.replace(day=28) + timedelta(days=4) # go to next month
            lm_end = next_month - timedelta(days=next_month.day)
            return lm_start <= d <= lm_end
        except ValueError:
            print(f"Ungültiges Datumsformat für Monat: {month}. Bitte MM.YYYY verwenden.")
            return False
    else:
        t = datetime.today()
        lm_end = t.replace(day=1) - timedelta(days=1)
        lm_start = lm_end.replace(day=1)
        return lm_start <= d <= lm_end

def checkForCookies(driver):
    try:
        accept_btn = driver.find_element(By.CSS_SELECTOR, "button[id='CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll']")
        accept_btn.click()
        print("Cookies accepted.")
    except Exception as e:
        print("No cookie prompt found or could not interact.")

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")


from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

driver = webdriver.Chrome(options=chrome_options)
try:
    for acc in accounts:
        try:
            print(f"Logging in for user {acc['username']}")
            driver.get(LOGIN_URL)
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='CustomerID/User ']"))
                )
                user_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='CustomerID/User ']")
                pw_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Passwort ']")
                user_input.clear()
                user_input.send_keys(acc["username"])
                pw_input.clear()
                pw_input.send_keys(acc["password"])
                driver.find_element(By.XPATH, "//a[contains(text(), 'ANMELDEN')]").click()
            except Exception as e:
                print("Login fields not found or could not interact.")
                print(f"Exception: {e}")
                time.sleep(20)
                continue
            checkForCookies(driver)

            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Aufträge"))
            )
            driver.find_element(By.LINK_TEXT, "Aufträge").click()

            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//table/tbody/tr"))
            )

            rows = driver.find_elements(By.XPATH, "//table/tbody/tr")
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) < 9:
                    continue
                auftragsnummer = tds[0].text.strip()
                bestelldatum = tds[1].text.strip()
                bestellstatus = tds[5].text.strip().upper()  # 6. Spalte / Index 5
                if bestellstatus != "BEZAHLT":
                    continue
                if date_in_last_month(bestelldatum):
                    try:
                        # 1. Click the button/link to open new tab
                        link_elem = tds[8].find_element(By.TAG_NAME, "a")
                        driver.execute_script("window.open(arguments[0], '_blank');", link_elem.get_attribute("href"))
                        time.sleep(1)
                        driver.switch_to.window(driver.window_handles[-1])
                        # 3. Wait for page to load (PDF or redirects)
                        # Wait until document.readyState == complete
                        WebDriverWait(driver, 15).until(
                            lambda d: d.execute_script("return document.readyState") == "complete"
                        )
                        time.sleep(1)  # Small delay to ensure all network requests finish
                        pdf_url = driver.current_url
                        # 4. Request with cookies from selenium to get headers & body
                        cookies = {c['name']: c['value'] for c in driver.get_cookies()}
                        resp = requests.get(pdf_url, cookies=cookies)
                        content_type = resp.headers.get('Content-Type', '')
                        # 5. Save if PDF
                        if resp.status_code == 200 and 'application/pdf' in content_type.lower():
                            filename = f"{bestelldatum}_{auftragsnummer}".replace('.', '-') + ".pdf"
                            filepath = os.path.join(DOWNLOAD_DIR, filename)
                            with open(filepath, "wb") as f:
                                f.write(resp.content)
                            print(f"PDF gespeichert: {filepath}")
                        else:
                            print(f"Kein PDF gefunden/Fehler: {resp.status_code}, {content_type}, URL:{pdf_url}")
                        # 6. Close tab and continue
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    except Exception as e:
                        print(f"Fehler bei Auftrag {auftragsnummer}: {e}")
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            print(f"Fehler bei Account {acc['username']}: {e}")
        except Exception as e:
            print(f"Unerwarteter Fehler bei Account {acc['username']}: {e}")
        try:
            # Try to locate and click the "Abmelden" button (logout)
            abmelden_btn = driver.find_element(By.XPATH, "//span[contains(text(), 'Abmelden')]")
            abmelden_btn.click()
            print(f"Logout successful for user {acc['username']}")
            # Wait for the login page or a suitable indicator of being logged out
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.sign-in-link"))
            )
        except Exception as e:
            print(f"Could not log out for user {acc['username']}: {e}")
finally:
    driver.quit()
