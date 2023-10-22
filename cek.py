import threading
import requests
from termcolor import colored

API_KEY = "806927d4d3fc3953efebc576"
API_URL = f"https://api.lolhuman.xyz/api/ipaddress/{{}}?apikey={API_KEY}"

def check_proxy(proxy, live_proxies):
    url = "https://www.google.com"
    proxies = {
        "http": proxy,
        "https": proxy
    }

    try:
        response = requests.get(url, proxies=proxies, timeout=5)
        if response.status_code == 200:
            if proxy not in live_proxies:
                ip_address = proxy.split(":")[0]
                location_info = get_location_info(ip_address)
                with open("live.txt", "a") as file:
                    file.write(f"{proxy} | {location_info}\n")
                live_proxies.add(proxy)
                print(colored(f"Proxy {proxy} is 200OK {location_info}. Saved.", "green"))
            else:
                print(colored(f"Proxy {proxy} is already in the live proxies list.", "yellow"))
        else:
            print(colored(f"Proxy {proxy} provided an invalid response.", "yellow"))
    except requests.RequestException:
        print(colored(f"Proxy {proxy} is not functioning.", "red"))

def get_location_info(ip_address):
    try:
        response = requests.get(API_URL.format(ip_address), timeout=5)
        if response.status_code == 200:
            data = response.json().get("result", {})
            country = data.get("country", "N/A")
            city = data.get("city", "N/A")
            isp = data.get("isp", "N/A")
            if country == "" and city == "" and isp == "":
                return "Location information not available"
            return f"Country: {country} ||| ISP: {isp}"
        else:
            return "Location information not available"
    except requests.RequestException:
        return "Location request failed"

def main():
    proxy_list_file = "proxy.txt"
    live_proxies = set()

    with open(proxy_list_file, "r") as file:
        proxies = file.readlines()

    threads = []
    for proxy in proxies:
        proxy = proxy.strip()
        thread = threading.Thread(target=check_proxy, args=(proxy, live_proxies))
        threads.append(thread)
        thread.start()

        # Pause every 3 threads started to reduce the load
        if len(threads) % 10 == 0:
            for t in threads:
                t.join()
            threads = []

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
