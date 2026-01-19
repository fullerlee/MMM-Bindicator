import json
import time
import argparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_bin_dates(is_pi):
    chrome_options = Options()
    
    # --- Driver Configuration ---
    if is_pi:
        print("Mode: Raspberry Pi (ARM/Headless) - Default")
        # Required flags for Raspberry Pi / MagicMirror environment
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # Point to the system-installed Chromium on the Pi
        chrome_options.binary_location = "/usr/bin/chromium-browser"
        service = Service(executable_path="/usr/bin/chromedriver")
    else:
        print("Mode: PC / Development (Manual Toggle)")
        # PC configuration using webdriver-manager
        from webdriver_manager.chrome import ChromeDriverManager
        chrome_options.add_argument("--headless") 
        service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)
    results_json = []

    try:
        print("Navigating to St Helens Council website...")
        driver.get("https://www.sthelens.gov.uk/article/3473/Check-your-collection-dates")

        # 1. Handle Cookie Banner
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept all')]")))
            driver.execute_script("arguments[0].click();", cookie_btn)
        except:
            pass

        # 2. Input Postcode
        postcode_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[id*='POSTCODE']")))
        postcode_field.send_keys("WA12 8BE")
        time.sleep(1)
        postcode_field.send_keys(Keys.ENTER)

        # 3. Handle Dropdown
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "select")))
        for _ in range(15):
            dropdown = driver.find_element(By.TAG_NAME, "select")
            if len(dropdown.find_elements(By.TAG_NAME, "option")) > 1:
                driver.execute_script("arguments[0].selectedIndex = 1; arguments[0].dispatchEvent(new Event('change'));", dropdown)
                break
            time.sleep(1)

        # 4. Navigate to final page
        next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Next')] | //input[contains(@value, 'Next')]")))
        driver.execute_script("arguments[0].click();", next_btn)

        # 5. Parse Table into Machine-Parsable JSON
        print("Parsing table and converting dates...")
        time.sleep(5) 
        
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        current_month_year = ""

        for row in rows:
            # Check for Month/Year header (e.g., "January 2026")
            headers = row.find_elements(By.TAG_NAME, "th")
            if headers:
                current_month_year = headers[0].text.strip()
                continue
            
            # Parse data rows
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 4:
                day_num = cells[0].text.strip().zfill(2)
                collection_type = cells[3].text.strip()
                
                try:
                    # Construct standardized YYYY-MM-DD format
                    raw_date_str = f"{day_num} {current_month_year}"
                    date_obj = datetime.strptime(raw_date_str, "%d %B %Y")

                    # Keep only current or future dates
                    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
                    if date_obj >= today:
                        machine_date = date_obj.strftime("%Y-%m-%d")
                        results_json.append({
                            "date": machine_date,
                            "collectionType": collection_type
                        })
                    
                except ValueError:
                    continue

        # 6. Final Output
        if results_json:
            # Full path for MagicMirror if in default Pi mode
            output_path = 'bin_schedule.json'
            if is_pi:
                output_path = '/home/fullerlee/MagicMirror/modules/MMM-Bindicator/scripts/bin_schedule.json'

            print("\n--- MACHINE-PARSABLE JSON ---")
            print(json.dumps(results_json, indent=4))
            
            with open(output_path, 'w') as f:
                json.dump(results_json, f, indent=4)
            print(f"\nSuccessfully saved to {output_path}")

    except Exception as e:
        print(f"\nError: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    # Setup command line argument to toggle PC mode
    parser = argparse.ArgumentParser(description='Fetch St Helens bin dates.')
    parser.add_argument('--pc', action='store_true', help='Use PC / Development configuration (Intel/AMD)')
    args = parser.parse_args()
    
    # Defaults to Pi mode unless --pc flag is provided
    get_bin_dates(is_pi=not args.pc)