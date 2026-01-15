import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def get_bin_dates():
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
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
            print(current_month_year)
            # Parse data rows
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 4:
                day_num = cells[0].text.strip().zfill(2) # Ensures "5" becomes "05"
                collection_type = cells[3].text.strip()
                
                try:
                    # Convert "05 January 2026" to "2026-01-05"
                    raw_date_str = f"{day_num} {current_month_year}"
                    date_obj = datetime.strptime(raw_date_str, "%d %B %Y")

                    # Compare with today's date - only bother keeping future dates
                    print("we compare: ", date_obj, " with ", datetime.today().replace(hour=0, minute=0, second=0, microsecond=0))
                    if date_obj >= datetime.today().replace(hour=0, minute=0, second=0, microsecond=0):
                        machine_date = date_obj.strftime("%Y-%m-%d")
                        results_json.append({
                            "date": machine_date,
                            "collectionType": collection_type
                        })
                    
                except ValueError:
                    continue

        # 6. Final Output
        if results_json:
            print("\n--- MACHINE-PARSABLE JSON ---")
            print(json.dumps(results_json, indent=4))
            
            with open('bin_schedule.json', 'w') as f:
                json.dump(results_json, f, indent=4)
            print("\nSuccessfully saved to bin_schedule.json")

    except Exception as e:
        print(f"\nError: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    get_bin_dates()

