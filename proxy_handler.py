import requests

def fetch_free_proxies():
    print("[*] Fetching free proxies...")
    url = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all'
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            proxies = [line.strip() for line in response.text.splitlines() if line.strip()]
            print(f"[+] {len(proxies)} proxies fetched.")
            return proxies
    except requests.RequestException as e:
        print(f"[!] Failed to fetch proxies: {e}")
    return []

def validate_proxy(proxy):
    try:
        requests.get('https://www.google.com', proxies={'http': f'http://{proxy}', 'https': f'http://{proxy}'}, timeout=3)
        return True
    except:
        return False

def get_valid_proxy(proxies):
    for proxy in proxies:
        if validate_proxy(proxy):
            return proxy
    return None