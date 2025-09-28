#!/bin/sh
set -e

# Start SSHD in background (as root)
/usr/sbin/sshd -D &

# Switch to app directory and run the app as ctfuser
cd /app
exec su -s /bin/sh -c "python main.py" ctfuser