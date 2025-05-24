import time
import re
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def get_text_safe(driver, by, value):
    try:
        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((by, value)))
        return element.text
    except:
        return ''

def get_attribute_safe(driver, by, value, attribute):
    try:
        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((by, value)))
        return element.get_attribute(attribute)
    except:
        return ''

def scrape_businesses(driver, search_term, fallback_category):
    url = f"https://www.google.com/maps/search/{search_term.replace(' ', '+')}"
    driver.get(url)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label,'Results for')]"))
        )
    except TimeoutException:
        print(f"[!] No results found for {search_term}")
        return []

    business_data = []

    scrollable_div = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//div[@role='feed']"))
    )

    last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
    for _ in range(3):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        time.sleep(random.uniform(2, 4))
        new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        if new_height == last_height:
            break
        last_height = new_height

    listings = driver.find_elements(By.XPATH, "//a[contains(@href,'/place/')]")
    visited = set()
    for listing in listings:
        href = listing.get_attribute("href")
        if href in visited:
            continue
        visited.add(href)
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", listing)
            time.sleep(random.uniform(0.5, 1.0))
            listing.click()
            time.sleep(random.uniform(2, 3))
        except:
            continue

        name = get_text_safe(driver, By.XPATH, "//h1[contains(@class,'DUwDvf')]")
        address = get_text_safe(driver, By.XPATH, "//button[contains(@data-item-id,'address')]")
        phone = get_text_safe(driver, By.XPATH, "//button[contains(@data-item-id,'phone')]")
        website = get_attribute_safe(driver, By.XPATH, "//a[contains(@data-item-id,'authority')]", 'href')
        category = get_text_safe(driver, By.XPATH, "//button[contains(@aria-label,'Category')]") or fallback_category

        zipcode = ''
        match = re.search(r'[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}', address)
        if match:
            zipcode = match.group(0)

        business_data.append({
            'Name': name,
            'Address': address,
            'Zipcode': zipcode,
            'Phone': phone,
            'Website': website,
            'BusinessType': category
        })

    return business_data