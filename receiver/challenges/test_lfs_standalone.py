#!/usr/bin/env python3
"""
Standalone test script for LFS service - simplified version
Run this directly to test if the LFS service is working properly
"""

import requests
import os
import subprocess


def check():
    """Main check function that runs all tests - matches Lfs.py logic exactly"""
    try:
        base_url = 'http://localhost:13000'
        payload_base_dir = 'payloads/lfs'
        
        # Step 1: Check if the website is up at all
        print(f"Pinging service at {base_url}...")
        response = requests.get(base_url, timeout=5)
        assert response.status_code == 200, f"Website is down or not responding. Status code: {response.status_code}"
        print("Website is online.")
        
        # Step 2: Check endpoint accessibility
        endpoints = ['/', '/disk', '/pdf', '/png']
        print("Checking web page accessibility...")
        for endpoint in endpoints:
            url = base_url + endpoint
            response = requests.get(url, timeout=5)
            assert response.status_code == 200, f"Endpoint {endpoint} returned status {response.status_code}"
            assert "</html>" in response.text.lower(), f"Endpoint {endpoint} did not return valid HTML"
            print(f"  - Endpoint {endpoint}: OK")
        print("All web pages are accessible.")
        
        # Step 3: Check feature functionality
        print("Checking feature functionality...")
        
        # Test 1: Disk Analyzer
        disk_url = base_url + '/analyze/disk'
        disk_payload_path = os.path.join(payload_base_dir, 'disk', 'benign.dd')
        
        with open(disk_payload_path, 'rb') as f:
            files = {'disk_image': (os.path.basename(disk_payload_path), f, 'application/octet-stream')}
            response = requests.post(disk_url, files=files, timeout=25)

        assert response.status_code == 200, f"Disk analyzer returned status {response.status_code}"
        assert "Partition Information" in response.text, "Disk analyzer response missing key text"
        print("  - Disk analyzer functionality: OK")

        # Test 2: PDF Analyzer
        pdf_url = base_url + '/analyze/pdf'
        pdf_payload_path = os.path.join(payload_base_dir, 'pdf', 'benign.pdf')

        with open(pdf_payload_path, 'rb') as f:
            files = {'pdf_file': (os.path.basename(pdf_payload_path), f, 'application/pdf')}
            response = requests.post(pdf_url, files=files, timeout=15)
        
        assert response.status_code == 200, f"PDF analyzer returned status {response.status_code}"
        assert "exif_data" in response.text, "PDF analyzer HTML response missing 'exif_data' key"
        print("  - PDF analyzer functionality: OK")

        # Test 3: PNG Analyzer
        png_url = base_url + '/analyze/png'
        png_payload_path = os.path.join(payload_base_dir, 'png', 'benign.png')

        with open(png_payload_path, 'rb') as f:
            files = {'png_file': (os.path.basename(png_payload_path), f, 'image/png')}
            response = requests.post(png_url, files=files, timeout=15)

        assert response.status_code == 200, f"PNG analyzer returned status {response.status_code}"
        assert "pngcheck_data" in response.text, "PNG analyzer HTML response missing 'pngcheck_data' key"
        print("  - PNG analyzer functionality: OK")
        
        print("All feature functionality checks passed.")

        # Step 4: Check if the flag still exists and matches the one in the container
        with open('flags/lfs.txt', 'r') as f:
            host_flag = f.read().strip()

        container_flag = subprocess.run(
            ["docker", "exec", "lfs_container", "cat", "/flag.txt"],
            capture_output=True,
            text=True
        ).stdout.strip()
        
        assert host_flag == container_flag, 'Flag mismatch between host and container'

        print('Check passed for LFS')
        return True

    except Exception as e:
        print(f'Could not check LFS: {e}')
        return False


if __name__ == "__main__":
    success = check()
    if success:
        print("SUCCESS")
    else:
        print("FAILED")
    exit(0 if success else 1)