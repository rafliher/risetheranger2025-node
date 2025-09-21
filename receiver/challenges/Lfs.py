# Import a base class from your CTF framework, e.g., from .Challenge import Challenge
# If you don't have one, this class can stand alone, but you'll need to supply logger and port.
from .Challenge import Challenge 

import requests
import os

class LFS(Challenge):
    """
    SLA Checker for the 'Lovely Forensic Suite' (LFS) challenge.
    This checker verifies:
    1. The web service is online and pages are accessible.
    2. The core functionality of each analysis tool (disk, pdf, png) remains intact
       by uploading benign files and checking for a valid response. This prevents
       teams from overly hardening or breaking the service.
    """
    flag_location = 'flags/lfs.txt'
    history_location = 'history/lftd.txt'
    payload_base_dir = 'payloads/lfs' # Base directory for test payloads

    def distribute(self, flag):
        """Writes the current flag to the specified location for the service to use."""
        try:
            with open(self.flag_location, 'w') as f:
                f.write(flag)
            
            with open(self.history_location, 'a') as f:
                f.write(flag + '\n')

            self.logger.info(f"Flag '{flag}' distributed successfully to {self.flag_location}")
            return True

        except Exception as e:
            self.logger.error(f"Could not write flag to {self.flag_location}: {e}")
            return False

    def _test_endpoint_accessibility(self, base_url):
        """Checks if all required web pages are accessible via GET requests."""
        endpoints = ['/', '/disk', '/pdf', '/png']
        self.logger.info("Checking web page accessibility...")
        for endpoint in endpoints:
            url = base_url + endpoint
            try:
                response = requests.get(url, timeout=5)
                assert response.status_code == 200, f"Endpoint {endpoint} returned status {response.status_code}"
                assert "</html>" in response.text.lower(), f"Endpoint {endpoint} did not return valid HTML"
                self.logger.info(f"  - Endpoint {endpoint}: OK")
            except Exception as e:
                self.logger.error(f"Failed to access endpoint {endpoint}: {e}")
                return False
        self.logger.info("All web pages are accessible.")
        return True

    def _test_feature_functionality(self, base_url):
        """
        Tests the core functionality of each analyzer by POSTing a benign file.
        This ensures that teams cannot simply disable the file upload features.
        """
        self.logger.info("Checking feature functionality...")
        
        # --- Test 1: Disk Analyzer ---
        try:
            # UPDATED: Changed endpoint to /analyze/disk
            disk_url = base_url + '/analyze/disk'
            disk_payload_path = os.path.join(self.payload_base_dir, 'disk', 'benign.dd')
            
            with open(disk_payload_path, 'rb') as f:
                files = {'disk_image': (os.path.basename(disk_payload_path), f, 'application/octet-stream')}
                response = requests.post(disk_url, files=files, timeout=25)

            assert response.status_code == 200, f"Disk analyzer returned status {response.status_code}"
            # Assertion is still valid as it checks for content in the returned HTML
            assert "Partition Information" in response.text, "Disk analyzer response missing key text"
            self.logger.info("  - Disk analyzer functionality: OK")
        except Exception as e:
            self.logger.error(f"Disk analyzer functionality test failed: {e}")
            return False

        # --- Test 2: PDF Analyzer ---
        try:
            # UPDATED: Changed endpoint to /analyze/pdf
            pdf_url = base_url + '/analyze/pdf'
            pdf_payload_path = os.path.join(self.payload_base_dir, 'pdf', 'benign.pdf')

            with open(pdf_payload_path, 'rb') as f:
                files = {'pdf_file': (os.path.basename(pdf_payload_path), f, 'application/pdf')}
                response = requests.post(pdf_url, files=files, timeout=15)
            
            assert response.status_code == 200, f"PDF analyzer returned status {response.status_code}"
            # UPDATED: Check for key text in the rendered HTML, not for a JSON response
            assert "exif_data" in response.text, "PDF analyzer HTML response missing 'exif_data' key"
            self.logger.info("  - PDF analyzer functionality: OK")
        except Exception as e:
            self.logger.error(f"PDF analyzer functionality test failed: {e}")
            return False

        # --- Test 3: PNG Analyzer ---
        try:
            # UPDATED: Changed endpoint to /analyze/png
            png_url = base_url + '/analyze/png'
            png_payload_path = os.path.join(self.payload_base_dir, 'png', 'benign.png')

            with open(png_payload_path, 'rb') as f:
                files = {'png_file': (os.path.basename(png_payload_path), f, 'image/png')}
                response = requests.post(png_url, files=files, timeout=15)

            assert response.status_code == 200, f"PNG analyzer returned status {response.status_code}"
            # UPDATED: Check for key text in the rendered HTML, not for a JSON response
            assert "pngcheck_data" in response.text, "PNG analyzer HTML response missing 'pngcheck_data' key"
            self.logger.info("  - PNG analyzer functionality: OK")
        except Exception as e:
            self.logger.error(f"PNG analyzer functionality test failed: {e}")
            return False
            
        self.logger.info("All feature functionality checks passed.")
        return True

    def check(self):
        """
        Main SLA check function. Called periodically by the game engine.
        """
        try:
            base_url = f'http://localhost:{self.port}'
            
            # Step 1: Check if the website is up at all
            self.logger.info(f"Pinging service at {base_url}...")
            response = requests.get(base_url, timeout=5)
            assert response.status_code == 200, f"Website is down or not responding. Status code: {response.status_code}"
            self.logger.info("Website is online.")
            
            # Step 2: Check if all pages load correctly
            assert self._test_endpoint_accessibility(base_url), "One or more endpoints are not accessible."
            
            # Step 3: Check if core features are working with benign payloads
            # This is crucial to prevent teams from breaking the service to "patch" it.
            assert self._test_feature_functionality(base_url), "Core feature functionality test failed."
            
            self.logger.info("LFS Challenge check passed successfully!")
            return True

        except Exception as e:
            self.logger.error(f'LFS Challenge check failed: {e}')
            return False

