from proxy_handler import fetch_free_proxies, get_valid_proxy
from driver_factory import create_driver
from scraper import scrape_businesses
from storage import save_to_excel
import time
import random

def load_districts():
    with open('./districts.txt', 'r') as f:
        return [line.strip() for line in f if line.strip()]

def main():
    districts = load_districts()
    user_input = input("Enter business niches separated by commas (e.g., Restaurant, Lawyer, Pharmacy): ").strip()
    if not user_input:
        print("[!] No niches entered. Exiting.")
        return
    niches = [n.strip() for n in user_input.split(",") if n.strip()]

    proxies = fetch_free_proxies()
    all_data = []

    for district in districts:
        for niche in niches:
            term = f"{niche} in {district}"
            print(f"[+] Searching for: {term}")
            proxy = get_valid_proxy(proxies)
            driver = create_driver(headless=True, proxy=proxy)
            if not driver:
                continue
            try:
                results = scrape_businesses(driver, term, niche)
                all_data.extend(results)
            except Exception as e:
                print(f"[!] Error during scraping {term}: {e}")
            finally:
                driver.quit()
            time.sleep(random.uniform(3, 5))

    if all_data:
        save_to_excel(all_data)

if __name__ == "__main__":
    main()