# Menggunakan base image dari Python
FROM python:3.8-slim

# Menambahkan direktori kerja
WORKDIR /app

# Menyalin requirements.txt ke dalam image
COPY requirements.txt .

# Menginstall dependensi yang diperlukan
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh kode aplikasi ke dalam image
COPY . .

# Menjalankan bot Telegram saat container dijalankan
CMD ["python3", "bot.py"]
