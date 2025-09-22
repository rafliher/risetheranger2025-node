# Langkah 1: Pilih base image yang ringan dan fungsional
FROM python:3.11-slim-bullseye

ARG PASSWORD

# Langkah 2: Set direktori kerja di dalam kontainer
WORKDIR /app

# Langkah 3: Instal dependensi sistem yang diperlukan
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    nano openssh-server \
    util-linux \
    file \
    e2fsprogs \
    libimage-exiftool-perl \
    nano openssh-server \
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
RUN useradd -m -d /home/ctfuser ctfuser && echo ctfuser:${PASSWORD} | chpasswd
RUN chown -R ctfuser:ctfuser /app/uploads /mnt /app/static

# Configure SSH for basic access
RUN echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config && \
    echo "PermitRootLogin no" >> /etc/ssh/sshd_config && \
    echo "AllowUsers ctfuser" >> /etc/ssh/sshd_config && \
    echo "PermitEmptyPasswords no" >> /etc/ssh/sshd_config

# Start SSH service
RUN ssh-keygen -A
RUN mkdir -p /run/sshd && chmod 755 /run/sshd

# Create the main flag file
RUN touch /flag.txt && chown root:root /flag.txt && chmod 644 /flag.txt

USER ctfuser

# Langkah 9: Expose port yang digunakan oleh Flask
EXPOSE 5000
EXPOSE 22

# Copy start script and set execute permissions
COPY start.sh .
RUN chmod +x start.sh

# Switch back to root to start SSH service and then run the application
USER root
CMD service ssh start && su - ctfuser -c "cd /app && ./start.sh"

