FROM golang:1.20 AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main main.go

FROM ubuntu:20.04

ARG PASSWORD

WORKDIR /app

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install basic development tools and SSH
RUN apt-get update && \
    apt-get install -y \
    openssh-server \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Create user needed for SSH access
RUN useradd -m -d /home/ctfuser ctfuser && echo ctfuser:${PASSWORD} | chpasswd

# Copy the built Go application from builder stage
COPY --from=builder /app/main .
COPY --from=builder /app/tmpl ./tmpl
COPY --from=builder /app/image.png .

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

# Make the application executable
RUN chmod +x ./main

# Create a startup script to handle flag initialization
RUN echo '#!/bin/bash\n\
service ssh start\n\
if [ ! -z "$FLAG" ]; then\n\
    echo "$FLAG" > /flag.txt\n\
fi\n\
./main' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 8080
EXPOSE 22

# Start SSH service and then run the application
CMD ["/app/start.sh"]