#############################################
#                                           #
#      Google Maps Business Extractor       #
#                 by @wiqi                  #
#                                           #
#############################################
import time
import random
import os
import re
import openpyxl
import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

DISTRICTS_FILE = './districts.txt'
PROXIES_FILE = './proxies.txt'

def load_districts():
    with open(DISTRICTS_FILE, 'r') as f:
        districts = [line.strip() for line in f if line.strip()]
    return districts


def load_proxies():
    file_path = PROXIES_FILE
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as file:
        proxies = [line.strip() for line in file if line.strip()]
    return proxies


def create_driver(headless=True, proxy=None):
    options = uc.ChromeOptions()
    if headless:
        options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")

    if proxy:
        options.add_argument(f'--proxy-server={proxy}')
        print(f"[+] Using proxy: {proxy}")

    driver = uc.Chrome(options=options)
    driver.set_page_load_timeout(60)
    return driver


def search_and_scrape(driver, search_term, niche):
    search_url = f"https://www.google.com/maps/search/{search_term.replace(' ', '+')}"
    driver.get(search_url)

    business_list = []

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label,'Results for')]"))
        )
    except TimeoutException:
        print(f"[!] No results found for {search_term}")
        return []

    scrollable_div_xpath = "//div[@role='feed']"
    scrollable_div = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, scrollable_div_xpath))
    )

    last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
    reached_end = False
    retry_scrolls = 0

    while not reached_end and retry_scrolls < 3:
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
        time.sleep(random.uniform(2, 4))

        new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        if new_height == last_height:
            retry_scrolls += 1
        else:
            last_height = new_height
            retry_scrolls = 0

    listings = driver.find_elements(By.XPATH, "//a[contains(@href,'/place/')]")

    for listing in listings:
        driver.execute_script("arguments[0].scrollIntoView();", listing)
        time.sleep(random.uniform(0.5, 1.0))
        try:
            listing.click()
        except:
            continue

        time.sleep(random.uniform(2, 3))

        try:
            name = driver.find_element(By.XPATH, "//h1[contains(@class,'DUwDvf')]").text
        except:
            name = ''

        try:
            address = driver.find_element(By.XPATH, "//button[contains(@data-item-id,'address')]").text
        except:
            address = ''

        try:
            phone = driver.find_element(By.XPATH, "//button[contains(@data-item-id,'phone')]").text
        except:
            phone = ''

        try:
            website = driver.find_element(By.XPATH, "//a[contains(@data-item-id,'authority')]").get_attribute('href')
        except:
            website = ''

        try:
            category = driver.find_element(By.XPATH, "//button[contains(@aria-label,'Category')]").text
        except:
            category = niche  # fallback

        zipcode = ''
        match = re.search(r'[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}', address)
        if match:
            zipcode = match.group(0)

        business_list.append({
            'Name': name,
            'Address': address,
            'Zipcode': zipcode,
            'Phone': phone,
            'Website': website,
            'BusinessType': category
        })

    return business_list


def save_to_xlsx(all_data, output_file='output/businesses.xlsx'):
    if not os.path.exists('output'):
        os.makedirs('output')

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(['Name', 'Address', 'Zipcode', 'Phone', 'Website', 'BusinessType'])

    for item in all_data:
        sheet.append([
            item['Name'],
            item['Address'],
            item['Zipcode'],
            item['Phone'],
            item['Website'],
            item['BusinessType']
        ])

    workbook.save(output_file)
    print(f"[+] Data saved to {output_file}")


def main():
    districts = load_districts()
    niches = [
        # "Restaurant",
        # "Lawyer",
        # "Hospital",
        # "Pharmacy",
    ]

    # Ask if empty
    if not niches:
        user_input = input("Enter business niches separated by commas (e.g., Restaurant, Lawyer, Pharmacy): ").strip()
        if user_input:
            niches = [n.strip() for n in user_input.split(",") if n.strip()]
        else:
            print("[!] No niches entered. Exiting.")
            return

    proxies = load_proxies()

    all_data = []

    for district in districts:
        for niche in niches:
            search_term = f"{niche} in {district}"
            print(f"[+] Searching: {search_term}")

            proxy = random.choice(proxies) if proxies else None

            try:
                driver = create_driver(headless=False, proxy=proxy)
                businesses = search_and_scrape(driver, search_term, niche)
                all_data.extend(businesses)
                driver.quit()
            except Exception as e:
                print(f"[!] Error scraping {search_term}: {e}")
                try:
                    driver.quit()
                except:
                    pass
                continue

            time.sleep(random.uniform(3, 6))  # pause between searches

    save_to_xlsx(all_data)


if __name__ == "__main__":
    main()