#!/usr/bin/env python3
"""
JJ challenge checker that inherits from Challenge base class.
"""

from .Challenge import Challenge

import requests
import time
import subprocess


class JJ(Challenge):
    flag_location = 'flags/jj.txt'
    history_location = 'history/jj.txt'

    def distribute(self, flag):
        try:
            with open(self.flag_location, 'w') as f:
                f.write(flag)
            
            with open(self.history_location, 'a') as f:
                f.write(flag + '\n')

            self.logger.info(f'Flag {flag} written to {self.flag_location}')
            return True

        except Exception as e:
            self.logger.error(f'Could not write flag to {self.flag_location}: {e}')
            return False

    def check(self):
        try:
            # Step 1: Test endpoint accessibility
            endpoints = ["/", "/marine", "/image.jpg"]
            self.logger.info("Checking endpoint accessibility...")
            
            for ep in endpoints:
                url = f'http://localhost:{self.port}{ep}'
                r = requests.get(url, timeout=5)
                assert r.status_code == 200, f'Endpoint {ep} returned status {r.status_code}'
                self.logger.info(f"  - {ep} OK (200)")

            # Step 2: Test core functionality
            self.logger.info("Testing core functionality...")
            
            # Initialize cookie via GET /
            session = requests.Session()
            url_idx = f'http://localhost:{self.port}/'
            r = session.get(url_idx, timeout=5)
            assert r.status_code == 200, 'Failed to fetch index page for cookie init'

            # POST some data to /airforce
            post_url = f'http://localhost:{self.port}/airforce'
            key = f"TestKey-{int(time.time())}"
            value = "TestValue"
            payload = {"Jalesveva": key, "Jayamahe": value}
            r = session.post(post_url, data=payload, allow_redirects=True, timeout=5)
            assert r.status_code in (200, 302), f'POST to /airforce returned bad status {r.status_code}'

            # GET /marine and check for stored data
            show_url = f'http://localhost:{self.port}/marine'
            r = session.get(show_url, timeout=5)
            assert r.status_code == 200, 'Failed to fetch /marine'
            assert key in r.text and value in r.text, 'Posted key-value not found on /marine'

            # GET /image.jpg
            img_url = f'http://localhost:{self.port}/image.jpg'
            r = session.get(img_url, timeout=5)
            assert r.status_code == 200, 'Failed to fetch /image.jpg'
            assert len(r.content) > 0, '/image.jpg returned empty content'

            # Step 3: Check if the flag still exists and matches the one in the container
            with open(self.flag_location, 'r') as f:
                host_flag = f.read().strip()

            container_flag = subprocess.run(
                ["docker", "exec", "jj_container", "cat", "/flag.txt"],
                capture_output=True,
                text=True
            ).stdout.strip()
            
            assert host_flag == container_flag, 'Flag mismatch between host and container'

            self.logger.info('Check passed for JJ')
            return True

        except Exception as e:
            self.logger.error(f'Could not check JJ: {e}')
            return False
