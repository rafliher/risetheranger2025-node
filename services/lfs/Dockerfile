# Langkah 1: Pilih base image yang ringan dan fungsional
FROM python:3.11-slim-bullseye

# Langkah 2: Set direktori kerja di dalam kontainer
WORKDIR /app

# Langkah 3: Instal dependensi sistem yang diperlukan
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    util-linux \
    file \
    e2fsprogs \
    libimage-exiftool-perl \
    pngcheck \
    poppler-utils \
    ntfs-3g \
    zip \
    fdisk \
    sleuthkit \
    && rm -rf /var/lib/apt/lists/*

# Langkah 4: Salin file requirements.txt terlebih dahulu
# Path 'src/requirements.txt' relatif terhadap lokasi Dockerfile (root proyek)
COPY src/requirements.txt .

# Langkah 5: Instal dependensi Python
RUN pip install --no-cache-dir -r requirements.txt

# Langkah 6: Salin seluruh kode sumber aplikasi dari direktori 'src'
COPY src/ .

# Langkah 7: Buat direktori yang akan digunakan oleh aplikasi
RUN mkdir -p /app/uploads /mnt



# Langkah 8: Buat user non-root untuk keamanan
RUN useradd --no-create-home appuser
RUN chown -R appuser:appuser /app/uploads /mnt /app/static
USER appuser


# Langkah 9: Expose port yang digunakan oleh Flask
EXPOSE 5000

# Langkah 10: Tentukan perintah untuk menjalankan aplikasi
CMD ["python", "run.py"]