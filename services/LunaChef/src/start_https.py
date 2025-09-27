#!/usr/bin/env python3
"""
Easy startup script for LunaChef HTTPS server
"""

import os
import sys
import subprocess

def main():
    # Change to the src directory
    src_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(src_dir)
    
    print("🌙 LunaChef HTTPS Server Setup")
    print("=" * 40)
    
    # Check if certificates exist
    cert_dir = os.path.join(src_dir, 'certs')
    cert_file = os.path.join(cert_dir, 'server.crt')
    key_file = os.path.join(cert_dir, 'server.key')
    
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        print("🔒 Generating self-signed SSL certificates...")
        try:
            subprocess.run([sys.executable, 'generate_cert.py'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to generate certificates: {e}")
            return 1
    else:
        print("✅ SSL certificates found")
    
    # Set environment variables for HTTPS
    os.environ['USE_HTTPS'] = 'true'
    os.environ['FLASK_DEBUG'] = 'false'
    
    print("🚀 Starting LunaChef server with HTTPS...")
    print("🌐 Server will be available at: https://localhost:5000")
    print("⚠️  Your browser will show a security warning (self-signed certificate)")
    print("   Click 'Advanced' and 'Proceed to localhost' to continue")
    print("")
    print("Press Ctrl+C to stop the server")
    print("=" * 40)
    
    try:
        # Start the server
        subprocess.run([sys.executable, 'main.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 LunaChef server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())