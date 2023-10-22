import requests
from termcolor import colored
from configparser import ConfigParser
from re import compile
from time import sleep, time as current_time
import os
import time

PROXIES_TYPES = ('http', 'socks4', 'socks5')

REGEX = compile(r"(?:^|\D)?((" + r"(?:[1-9]|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
                + r"\." + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
                + r"\." + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
                + r"\." + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
                + r"):" + (r"(?:\d|[1-9]\d{1,3}|[1-5]\d{4}|6[0-4]\d{3}"
                + r"|65[0-4]\d{2}|655[0-2]\d|6553[0-5])")
                + r")(?:\D|$)")

errors = open('errors.txt', 'a+')
http_proxies, socks4_proxies, socks5_proxies = [], [], []
proxy_error = 0

cfg = ConfigParser(interpolation=None) 
cfg.read("config.ini", encoding="utf-8")

try:
    http, socks4, socks5 = cfg["HTTP"], cfg["SOCKS4"], cfg["SOCKS5"]
except KeyError:
    print(' [ OUTPUT ] Error | config.ini not found!')
    sleep(3)
    exit()

def scrap(sources, _proxy_type):
    global proxy_error
    for source in sources:
        if source:
            try:
                response = requests.get(source, timeout=15)
                if tuple(REGEX.finditer(response.text)):
                    for proxy in tuple(REGEX.finditer(response.text)):
                        if _proxy_type == 'http':
                            http_proxies.append(proxy.group(1))
                        elif _proxy_type == 'socks4':
                            socks4_proxies.append(proxy.group(1))
                        elif _proxy_type == 'socks5':
                            socks5_proxies.append(proxy.group(1))
            except Exception as e:
                errors.write(f'{e}\n')
                proxy_error += 1

def send_proxy_to_telegram(proxy, region, country):
    TOKEN = '6486689995:AAG2NTK30Dwki5S80F1vrv7cNbZ80mRm7Y0'
    chat_id = '-1001831115192'

    api_url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

    location_url = f"https://api.findip.net/{proxy.split(':')[0]}/?token=72f03ec3c2ba4cc18b782c9820e2bc22"
    location_data = requests.get(location_url).json()
    country = location_data.get("country", {}).get("names", {}).get("en", "Unknown")
    region = location_data.get("subdivisions", [{}])[0].get("names", {}).get("en", "Unknown")
    isp = location_data.get("traits", {}).get("isp", "Unknown")

    message = (
        f"PROXY: {proxy}\n\n"
        f"PROXY STATUS: LIVE! ✅\n"
        f"Lokasi: {region}, {country}\n"
        f"Isp: {isp}\n"
        f"Bot By: @ilham_maulana1"
    )

    data = {
        'chat_id': chat_id,
        'text': message,
        'disable_web_page_preview': True
    }

    try:
        response = requests.post(api_url, data=data)
        if response.status_code == 200:
            print(f"Proxy {proxy} dikirim ke Telegram.")
        else:
            print(f"Error mengirim pesan: {response.text}")
    except Exception as e:
        print(f"Error mengirim pesan: {e}")

def check_proxy_ip_match(proxy):
    url = "https://httpbin.org/ip"
    proxies = {
        "http": proxy,
        "https": proxy
    }

    try:
        response = requests.get(url, proxies=proxies, timeout=15)
        if response.status_code == 200:
            origin_ip = response.json().get("origin")
            if origin_ip == proxy.split(':')[0]:
                return True
    except requests.RequestException:
        pass

    return False

def check_proxy(proxy, live_proxies):
    if check_proxy_ip_match(proxy):
        if proxy not in live_proxies:
            with open("live.txt", "a") as file:
                file.write(proxy + "\n")
            live_proxies.add(proxy)
            print(colored(f"Proxy {proxy} bekerja dengan baik. Disimpan.", "green"))

            location_url = f"https://api.findip.net/{proxy.split(':')[0]}/?token=YOUR_FINDIP_TOKEN"
            location_data = requests.get(location_url).json()
            country = location_data.get("country", {}).get("names", {}).get("en", "Unknown")
            region = location_data.get("subdivisions", [{}])[0].get("names", {}).get("en", "Unknown")

            send_proxy_to_telegram(proxy, region, country)
        else:
            print(colored(f"Proxy {proxy} sudah ada dalam daftar live proxies.", "yellow"))
    else:
        print(colored(f"Proxy {proxy} tidak berfungsi atau IP tidak cocok.", "red"))

def start_scrap():
    for i in (http_proxies, socks4_proxies, socks5_proxies):
        i.clear()
    for source_list, proxy_type in ((http.get("Sources").splitlines(), 'http'),
                                    (socks4.get("Sources").splitlines(), 'socks4'),
                                    (socks5.get("Sources").splitlines(), 'socks5')):
        scrap(source_list, proxy_type)

def main():
    while True:
        proxy_list_file = "proxy.txt"
        live_proxies = set()

        if os.path.exists(proxy_list_file):
            os.remove(proxy_list_file)

        start_scrap()
        with open(proxy_list_file, "w") as file:
            for proxy in http_proxies + socks4_proxies + socks5_proxies:
                file.write(proxy + "\n")

        with open(proxy_list_file, "r") as file:
            proxies = file.readlines()

        for proxy in proxies:
            proxy = proxy.strip()
            check_proxy(proxy, live_proxies)

        time.sleep(1200)

if __name__ == "__main__":
    main()
