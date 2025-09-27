# Import a base class from your CTF framework, e.g., from .Challenge import Challenge
# If you don't have one, this class can stand alone, but you'll need to supply logger and port.
from .Challenge import Challenge
import requests
import os
import subprocess

class LFS(Challenge):
    flag_location = 'flags/lfs.txt'
    history_location = 'history/lfs.txt'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payload_base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'payloads', 'lfs')
        )

    def distribute(self, flag):
        try:
            with open(self.flag_location, 'w') as f:
                f.write(flag)
            with open(self.history_location, 'a') as f:
                f.write(flag + '\n')
            self.logger.info(f"Flag '{flag}' distributed to {self.flag_location}")
            return True
        except Exception as e:
            self.logger.error(f"Could not write flag: {e}")
            return False

    def _test_endpoint_accessibility(self, base_url):
        endpoints = ['/', '/disk', '/pdf', '/png']
        self.logger.info("Checking web page accessibility...")
        for endpoint in endpoints:
            url = base_url + endpoint
            response = requests.get(url, timeout=5)
            assert response.status_code == 200, f"{endpoint} returned {response.status_code}"
            assert "</html>" in response.text.lower(), f"{endpoint} not valid HTML"
            self.logger.info(f"  - Endpoint {endpoint}: OK")
        return True

    def _test_feature_functionality(self, base_url):
        self.logger.info("Checking feature functionality...")

        # Disk analyzer
        disk_url = base_url + '/analyze/disk'
        disk_payload_dir = os.path.join(self.payload_base_dir, 'disk')
        for filename in os.listdir(disk_payload_dir):
            path = os.path.join(disk_payload_dir, filename)
            if not os.path.isfile(path): continue
            with open(path, 'rb') as f:
                files = {'disk_image': (filename, f, 'application/octet-stream')}
                response = requests.post(disk_url, files=files, timeout=25)
            assert response.status_code == 200
            assert "</html>" in response.text.lower()
            assert "blacklisted" not in response.text.lower()
        self.logger.info("  - Disk analyzer functionality: OK")

        # PDF analyzer
        pdf_url = base_url + '/analyze/pdf'
        pdf_payload_dir = os.path.join(self.payload_base_dir, 'pdf')
        for filename in os.listdir(pdf_payload_dir):
            path = os.path.join(pdf_payload_dir, filename)
            if not os.path.isfile(path): continue
            with open(path, 'rb') as f:
                files = {'pdf_file': (filename, f, 'application/pdf')}
                response = requests.post(pdf_url, files=files, timeout=15)
            assert response.status_code == 200
            assert "</html>" in response.text.lower()
        self.logger.info("  - PDF analyzer functionality: OK")

        # PNG analyzer
        png_url = base_url + '/analyze/png'
        png_payload_dir = os.path.join(self.payload_base_dir, 'png')
        for filename in os.listdir(png_payload_dir):
            path = os.path.join(png_payload_dir, filename)
            if not os.path.isfile(path): continue
            with open(path, 'rb') as f:
                files = {'png_file': (filename, f, 'image/png')}
                response = requests.post(png_url, files=files, timeout=15)
            assert response.status_code == 200
            assert "</html>" in response.text.lower()
        self.logger.info("  - PNG analyzer functionality: OK")

        return True

    def check(self):
        try:
            base_url = f"http://localhost:{self.port}"

            # Step 1
            self.logger.info(f"Pinging {base_url}...")
            response = requests.get(base_url, timeout=5)
            assert response.status_code == 200
            self.logger.info("Website is online.")

            # Step 2
            assert self._test_endpoint_accessibility(base_url)

            # Step 3
            assert self._test_feature_functionality(base_url)

            # Step 4: flag check
            with open(self.flag_location, 'r') as f:
                host_flag = f.read().strip()
            container_flag = subprocess.run(
                ["docker", "exec", "lfs_container", "cat", "/flag.txt"],
                capture_output=True, text=True
            ).stdout.strip()
            assert host_flag == container_flag, "Flag mismatch"

            self.logger.info("LFS check passed successfully!")
            return True
        except Exception as e:
            self.logger.error(f"LFS check failed: {e}")
            return False
