import requests
import threading

# Fungsi untuk memeriksa proxy
def check_proxy(proxy, working_proxies):
    try:
        response = requests.get('http://www.google.com', proxies={'http': proxy}, timeout=5)
        if response.status_code == 200:
            print(f'{proxy} is working')
            working_proxies.append(proxy)
            # Menyimpan proxy yang berfungsi kembali ke file 'live.txt'
            with open('live.txt', 'a') as file:
                file.write(f'{proxy}\n')
        else:
            print(f'{proxy} is not working')
    except requests.RequestException as e:
        print(f'{proxy} is not working')

# Membaca daftar proxy dari file 'proxy.txt'
with open('proxy.txt', 'r') as file:
    proxy_list = file.read().splitlines()

# Maksimum jumlah thread yang akan digunakan
max_threads = 1000
working_proxies = []

# Memeriksa proxy menggunakan multithreading
threads = []
for proxy in proxy_list:
    if len(threads) >= max_threads:
        for thread in threads:
            thread.join()
        threads = []

    thread = threading.Thread(target=check_proxy, args=(proxy, working_proxies))
    thread.start()
    threads.append(thread)

# Menunggu semua thread selesai
for thread in threads:
    thread.join()

print("Proxy yang tidak berfungsi telah dihapus dari 'live.txt'")
