# Use Python 3.11 slim image as base
FROM python:3.11-slim

ARG PASSWORD

# Create ctfuser and set password
RUN useradd -m -d /var/www/html ctfuser && echo ctfuser:${PASSWORD} | chpasswd

# Install necessary packages
RUN apt-get update && apt-get install -y openssh-server curl

# Configure SSH for ctfuser
RUN echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config && \
    echo "PermitRootLogin no" >> /etc/ssh/sshd_config && \
    echo "AllowUsers ctfuser" >> /etc/ssh/sshd_config

# Generate SSH host keys
RUN ssh-keygen -A

# Ensure /run/sshd directory exists with correct permissions
RUN mkdir -p /run/sshd && chmod 755 /run/sshd

# Copy requirements first for better caching
COPY src/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=main.py
ENV FLASK_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nano \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY src/ .

RUN chown -R ctfuser:ctfuser /app

# Expose port
EXPOSE 5000
EXPOSE 22

USER ctfuser
# Run the application
CMD ["python", "main.py"]