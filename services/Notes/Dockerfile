FROM python:3.11-slim-bullseye

ARG PASSWORD

WORKDIR /app

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install basic development tools and SSH
RUN apt-get update && \
    apt-get install -y \
    openssh-server nano \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Create user needed for SSH access
RUN useradd -m -d /home/ctfuser ctfuser && echo ctfuser:${PASSWORD} | chpasswd

# Copy the application source
COPY src/ .

# Create directories needed by the application
RUN mkdir -p notes
RUN chmod 755 /app
RUN chmod 777 notes

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Configure SSH for basic access
RUN echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config && \
    echo "PermitRootLogin no" >> /etc/ssh/sshd_config && \
    echo "AllowUsers ctfuser" >> /etc/ssh/sshd_config && \
    echo "PermitEmptyPasswords no" >> /etc/ssh/sshd_config

# Start SSH service setup
RUN ssh-keygen -A
RUN mkdir -p /run/sshd && chmod 755 /run/sshd

# Create the main flag file
RUN touch /flag.txt && chown root:root /flag.txt && chmod 644 /flag.txt

# Create a startup script that starts SSH as root then switches to ctfuser
RUN echo '#!/bin/bash\n\
service ssh start\n\
if [ ! -z "$FLAG" ]; then\n\
    echo "$FLAG" > /flag.txt\n\
fi\n\
su - ctfuser -c "cd /app && python3 -m gunicorn --bind 0.0.0.0:8000 main:app"' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 8000
EXPOSE 22

# Switch back to root for SSH service management, then run startup script
USER root
CMD ["/app/start.sh"]