#!/bin/bash
# Starts the vulnerable binary service accessible via netcat

echo "Starting C2 System Network Service..."

# Start SSH service in background
/usr/sbin/sshd -D &

# Start the vulnerable binary service using socat
# This allows multiple concurrent connections and proper stdin/stdout handling
socat TCP-LISTEN:8000,reuseaddr,fork EXEC:"/opt/tni_c2_system",pty,raw,echo=0

# Alternative using traditional netcat (single connection):
# while true; do nc -l -p 8000 -e /opt/tni_c2_system; done