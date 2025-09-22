#!/usr/bin/env python3
"""
Standalone test script for JJ service - simplified version
Run this directly to test if the JJ service is working properly
"""

import requests
import time
import subprocess
import html
import base64

container_name = "lunachef"
host = "localhost"
port = 5000

def check():
    """Main check function that runs all tests - matches JJ.py logic exactly"""
    try:
        # Step 1: Test endpoint accessibility
        endpoints = ["/", "/crypto", "/scripts", "/scripts/encryption", "/scripts/signing", "/scripts/hash"]
        session = requests.Session()
        for endpoint in endpoints:
            url = f'http://{host}:{port}{endpoint}'
            r = session.get(url, timeout=5)
            assert r.status_code == 200, f'Failed to fetch {url}, status {r.status_code}'

        # Step 2: get key from container
        container_key = subprocess.run(
            ["docker", "exec", container_name, "cat", "/app/config/__init__.py"],
            capture_output=True,
            text=True
        ).stdout.strip()
        assert container_key, 'Key not found in container config.py'
        scope = {}
        exec(container_key, {}, scope)
        encryption_key = scope.get('key', None)
        assert encryption_key, 'Key variable not found in container config.py'
        
        # Step 3: Test core functionality of encrypt decrypt crypto service
        endpoint_encrypt = f'http://{host}:{port}/encrypt'
        endpoint_decrypt = f'http://{host}:{port}/decrypt'
        endpoint_script = f'http://{host}:{port}/scripts/encryption'
        test_text = f"TestText-{int(time.time())}"
        r = session.post(endpoint_encrypt, data={'text': test_text}, timeout=5)
        assert r.status_code == 200, f'Encryption request failed, status {r.status_code}'
        resp_json = r.json()
        r = session.post(endpoint_decrypt, data={'encrypted_data': resp_json.get('encrypted_data', '')}, timeout=5)
        assert r.status_code == 200, f'Decryption request failed, status {r.status_code}'
        resp_json = r.json()
        assert resp_json.get('decrypted_text', '') == test_text, 'Decrypted text does not match original'
        r = session.get(endpoint_script, timeout=5)
        assert r.status_code == 200, f'Failed to fetch script page, status {r.status_code}'
        source_code = r.text.split('><code class="language-python">')[1].split('</code></pre>')[0]
        source_code_decoding = html.unescape(source_code)
          # For debugging
        scope = {
            "base64": base64,      # supaya bisa import base64
            "config": {"key": encryption_key} # fake config module
        }
        exec(source_code_decoding, {}, scope)  # Basic check if code runs without error
        print(scope)
        
        # Step 3: Check if the flag still exists and matches the one in the container
        with open('flags/lunachef.txt', 'r') as f:
            host_flag = f.read().strip()

        container_flag = subprocess.run(
            ["docker", "exec", container_name, "cat", "/flag.txt"],
            capture_output=True,
            text=True
        ).stdout.strip()
        
        assert host_flag == container_flag, 'Flag mismatch between host and container'

        print('Check passed for Lunachef')
        return True

    except Exception as e:
        print(f'Could not check JJ: {e}')
        return False


if __name__ == "__main__":
    success = check()
    if success:
        print("SUCCESS")
    else:
        print("FAILED")
    exit(0 if success else 1)