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
        payload_base_dir = '../payloads/lfs'
        
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
        disk_payload_dir = os.path.join(payload_base_dir, 'disk')
        print(f"  - Testing Disk analyzer with payloads from {disk_payload_dir}...")
        for filename in os.listdir(disk_payload_dir):
            disk_payload_path = os.path.join(disk_payload_dir, filename)
            if not os.path.isfile(disk_payload_path):
                continue
            
            print(f"    - Uploading {filename}...")
            with open(disk_payload_path, 'rb') as f:
                files = {'disk_image': (filename, f, 'application/octet-stream')}
                response = requests.post(disk_url, files=files, timeout=25)

            assert response.status_code == 200, f"Disk analyzer returned status {response.status_code} for file {filename}"
            assert "</html>" in response.text.lower(), f"Disk analyzer response for {filename} did not return valid HTML"
            assert "blacklisted" not in response.text.lower(), f"Disk analyzer response for {filename} contains error message"
        print("  - Disk analyzer functionality: OK")

        # Test 2: PDF Analyzer
        pdf_url = base_url + '/analyze/pdf'
        pdf_payload_dir = os.path.join(payload_base_dir, 'pdf')
        print(f"  - Testing PDF analyzer with payloads from {pdf_payload_dir}...")
        for filename in os.listdir(pdf_payload_dir):
            pdf_payload_path = os.path.join(pdf_payload_dir, filename)
            if not os.path.isfile(pdf_payload_path):
                continue
            
            print(f"    - Uploading {filename}...")
            with open(pdf_payload_path, 'rb') as f:
                files = {'pdf_file': (filename, f, 'application/pdf')}
                response = requests.post(pdf_url, files=files, timeout=15)
        
            assert response.status_code == 200, f"PDF analyzer returned status {response.status_code} for file {filename}"
            assert "</html>" in response.text.lower(), f"PDF analyzer response for {filename} did not return valid HTML"
        print("  - PDF analyzer functionality: OK")

        # Test 3: PNG Analyzer
        png_url = base_url + '/analyze/png'
        png_payload_dir = os.path.join(payload_base_dir, 'png')
        print(f"  - Testing PNG analyzer with payloads from {png_payload_dir}...")
        for filename in os.listdir(png_payload_dir):
            png_payload_path = os.path.join(png_payload_dir, filename)
            if not os.path.isfile(png_payload_path):
                continue

            print(f"    - Uploading {filename}...")
            with open(png_payload_path, 'rb') as f:
                files = {'png_file': (filename, f, 'image/png')}
                response = requests.post(png_url, files=files, timeout=15)

            assert response.status_code == 200, f"PNG analyzer returned status {response.status_code} for file {filename}"
            assert "</html>" in response.text.lower(), f"PNG analyzer response for {filename} did not return valid HTML"
        print("  - PNG analyzer functionality: OK")
        
        print("All feature functionality checks passed.")

        # Step 4: Check if the flag still exists and matches the one in the container
        with open('../flags/lfs.txt', 'r') as f:
            host_flag = f.read().strip()

        container_flag = subprocess.run(
            ["docker", "exec", "lfs_container", "cat", "/flag.txt"],
            capture_output=True,
            text=True
        ).stdout.strip()

        print(f"Host flag: {host_flag}")
        print(f"Container flag: {container_flag}")
        
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