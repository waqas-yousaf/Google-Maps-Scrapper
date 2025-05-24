import undetected_chromedriver as uc
from selenium.common.exceptions import WebDriverException

def create_driver(headless=True, proxy=None):
    options = uc.ChromeOptions()
    if headless:
        options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--window-size=1920,1080")
    if proxy:
        options.add_argument(f'--proxy-server=http://{proxy}')
        print(f"[+] Using proxy: {proxy}")
    try:
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(60)
        return driver
    except WebDriverException as e:
        print(f"[!] Failed to create driver: {e}")
        return None