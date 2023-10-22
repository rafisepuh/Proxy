import requests
from faker import Faker
import re

# Ganti dengan nilai yang sesuai
channel = "csindosat"
post = "36"

# Inisialisasi objek Faker
fake = Faker()

# Membuat User-Agent palsu
user_agent = fake.user_agent()

url = f'https://t.me/{channel}/{post}'
params = {'embed': '1', 'mode': 'tme'}
headers = {'referer': f'https://t.me/{channel}/{post}?embed=1&mode=tme', 'user-agent': user_agent}

try:
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        # Mencari data-view menggunakan regex
        data_view_match = re.search('data-view="([^"]+)', response.text)
        
        if data_view_match:
            data_view_value = data_view_match.group(1)
            # Anda dapat melakukan sesuatu dengan data-view_value di sini
            print("Data-view value:", data_view_value)
        else:
            print("Data-view tidak ditemukan dalam respons.")

        # Menggunakan session untuk permintaan berikutnya
        cookies_dict = response.cookies.get_dict()
        session = requests.Session()
        response2 = session.get(
            'https://t.me/v/', params={'views': data_view_value}, cookies={
                'stel_dt': '-240', 'stel_web_auth': 'https%3A%2F%2Fweb.telegram.org%2Fz%2F',
                'stel_ssid': cookies_dict.get('stel_ssid', None), 'stel_on': cookies_dict.get('stel_on', None)
            },
            headers={
                'referer': f'https://t.me/{channel}/{post}?embed=1&mode=tme',
                'user-agent': user_agent, 'x-requested-with': 'XMLHttpRequest'
            },
        )

        if response2.status_code == 200:
            # Lakukan sesuatu dengan respons kedua jika perlu
            print(response2.text)
        else:
            # Gagal mendapatkan respons kedua
            print("Gagal mendapatkan respons kedua. Kode status:", response2.status_code)

    else:
        # Gagal mendapatkan konten pertama
        print("Gagal mengambil konten pertama. Kode status:", response.status_code)

except requests.exceptions.RequestException as e:
    print("Terjadi kesalahan saat melakukan permintaan:", e)
