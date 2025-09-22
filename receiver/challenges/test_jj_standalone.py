#!/usr/bin/env python3
"""
Standalone test script for JJ service - simplified version
Run this directly to test if the JJ service is working properly
"""

import requests
import time
import subprocess


def check():
    """Main check function that runs all tests - matches JJ.py logic exactly"""
    try:
        # Step 1: Test endpoint accessibility
        endpoints = ["/", "/marine", "/image.jpg"]
        print("Checking endpoint accessibility...")
        
        for ep in endpoints:
            url = f'http://localhost:12000{ep}'
            r = requests.get(url, timeout=5)
            assert r.status_code == 200, f'Endpoint {ep} returned status {r.status_code}'
            print(f"  - {ep} OK (200)")

        # Step 2: Test core functionality
        print("Testing core functionality...")
        
        # Initialize cookie via GET /
        session = requests.Session()
        url_idx = f'http://localhost:12000/'
        r = session.get(url_idx, timeout=5)
        assert r.status_code == 200, 'Failed to fetch index page for cookie init'

        # POST some data to /airforce
        post_url = f'http://localhost:12000/airforce'
        key = f"TestKey-{int(time.time())}"
        value = "TestValue"
        payload = {"Jalesveva": key, "Jayamahe": value}
        r = session.post(post_url, data=payload, allow_redirects=True, timeout=5)
        assert r.status_code in (200, 302), f'POST to /airforce returned bad status {r.status_code}'

        # GET /marine and check for stored data
        show_url = f'http://localhost:12000/marine'
        r = session.get(show_url, timeout=5)
        assert r.status_code == 200, 'Failed to fetch /marine'
        assert key in r.text and value in r.text, 'Posted key-value not found on /marine'

        # GET /image.jpg
        img_url = f'http://localhost:12000/image.jpg'
        r = session.get(img_url, timeout=5)
        assert r.status_code == 200, 'Failed to fetch /image.jpg'
        assert len(r.content) > 0, '/image.jpg returned empty content'

        # Step 3: Check if the flag still exists and matches the one in the container
        with open('flags/jj.txt', 'r') as f:
            host_flag = f.read().strip()

        container_flag = subprocess.run(
            ["docker", "exec", "jj_container", "cat", "/flag.txt"],
            capture_output=True,
            text=True
        ).stdout.strip()
        
        assert host_flag == container_flag, 'Flag mismatch between host and container'

        print('Check passed for JJ')
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