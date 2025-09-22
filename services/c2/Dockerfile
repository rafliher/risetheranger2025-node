FROM public.ecr.aws/docker/library/ubuntu:20.04

ARG PASSWORD

WORKDIR /opt

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install basic development tools needed for building the challenge
RUN apt-get update && \
    apt-get install -y \
    nano openssh-server \
    gcc gcc-multilib \
    make \
    libc6-dev-i386 \
    socat \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Create users needed for the challenge
RUN useradd -m -d /home/ctfuser ctfuser && echo ctfuser:${PASSWORD} | chpasswd

COPY src/ .

# Compile the vulnerable TNI C2 binary with maximum vulnerability
RUN cd /opt && make max_vuln

# Copy binary to standard location for easier access
RUN cp /opt/tni_c2_system /usr/local/bin/tni_c2_system

# Generate clearance token for the challenge
RUN cd /opt && make token

# Copy clearance token to ctfuser home directory (for checker)
RUN cp /opt/clearance_token /home/ctfuser/clearance_token && chown ctfuser:ctfuser /home/ctfuser/clearance_token

# Set basic permissions for the challenge
RUN chmod 755 /opt && \
    chmod 644 /opt/clearance_token

# Make the vulnerable binary have basic executable permissions
RUN chmod 755 /opt/tni_c2_system

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

# Set up the network service startup script
RUN chmod +x ./start_service.sh
RUN chmod +x ./tni_c2_system

CMD ./start_service.sh

EXPOSE 8000
EXPOSE 22