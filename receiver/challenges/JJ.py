#!/usr/bin/env python3
"""
Standalone checker for the Go service (routes: /, /airforce, /marine, /image.jpg).

Usage:
  python checker.py            # defaults host=localhost port=33201
  python checker.py --host 127.0.0.1 --port 8080
"""

import requests
import argparse
import sys
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("airforce-checker")


class AirforceServiceChecker:
    def __init__(self, host="localhost", port=33201, timeout=5):
        self.host = host
        self.port = int(port)
        self.base = f"http://{self.host}:{self.port}"
        self.timeout = timeout
        self.session = requests.Session()

    def distribute(self, flag: str, path: str = None):
        """
        Placeholder to mimic a CTF engine writing a flag for the service.
        For this Go service the flag is provided by environment FLAG at container start,
        so this function is just a convenience to write to disk if you want.
        """
        if not path:
            logger.info("distribute: no path provided, skipping local write (service gets FLAG via env)")
            return True
        try:
            with open(path, "w") as f:
                f.write(flag)
            logger.info("distribute: wrote flag to %s", path)
            return True
        except Exception as e:
            logger.error("distribute failed: %s", e)
            return False

    def _request_ok(self, method, url, **kwargs):
        try:
            r = method(url, timeout=self.timeout, **kwargs)
            return r
        except Exception as e:
            logger.error("HTTP request failed: %s %s -> %s", method.__name__.upper(), url, e)
            return None

    def test_endpoints(self):
        """
        Check that '/', '/marine' and '/image.jpg' return 200.
        '/airforce' is POST-only so it's covered in feature test.
        """
        endpoints = ["/", "/marine", "/image.jpg"]
        logger.info("Checking endpoint accessibility on %s ...", self.base)
        for ep in endpoints:
            url = self.base + ep
            r = self._request_ok(self.session.get, url)
            if r is None:
                logger.error("Endpoint %s not reachable", ep)
                return False
            if r.status_code != 200:
                logger.error("Endpoint %s returned status %d", ep, r.status_code)
                return False
            logger.info("  - %s OK (200)", ep)
        logger.info("All endpoint accessibility checks passed.")
        return True

    def test_feature_functionality(self):
        """
        Tests the flow:
          1) GET / to be assigned a cookie (marine)
          2) POST to /airforce with form fields 'Jalesveva' and 'Jayamahe'
          3) GET /marine and verify the posted key/value appears
          4) GET /image.jpg and ensure it returns bytes
        """
        logger.info("Testing core functionality...")

        # 1) Initialize cookie via GET /
        url_idx = self.base + "/"
        r = self._request_ok(self.session.get, url_idx)
        if r is None or r.status_code != 200:
            logger.error("Failed to fetch index page for cookie init")
            return False
        logger.info("Index page fetched; session cookies: %s", self.session.cookies.get_dict())

        # 2) POST some data to /airforce
        post_url = self.base + "/airforce"
        key = f"TestKey-{int(time.time())}"
        value = "TestValue"
        payload = {"Jalesveva": key, "Jayamahe": value}
        r = self._request_ok(self.session.post, post_url, data=payload, allow_redirects=True)
        if r is None:
            logger.error("POST to /airforce failed (no response)")
            return False
        # After redirect it may return 200 on index (app uses redirect to "/")
        if r.status_code not in (200, 302):
            logger.error("POST to /airforce returned bad status %d", r.status_code)
            return False
        logger.info("POST to /airforce succeeded (status %d).", r.status_code)

        # 3) GET /marine and check for stored data
        show_url = self.base + "/marine"
        r = self._request_ok(self.session.get, show_url)
        if r is None or r.status_code != 200:
            logger.error("Failed to fetch /marine")
            return False
        body = r.text
        if key not in body or value not in body:
            # provide helpful debug output
            logger.error("Posted key-value not found on /marine. Searching for key or value in response...")
            logger.debug("Response body snippet: %s", body[:1000])
            return False
        logger.info("Posted key-value found on /marine: %s => %s", key, value)

        # 4) GET /image.jpg
        img_url = self.base + "/image.jpg"
        r = self._request_ok(self.session.get, img_url)
        if r is None or r.status_code != 200:
            logger.error("Failed to fetch /image.jpg")
            return False
        if len(r.content) == 0:
            logger.error("/image.jpg returned empty content")
            return False
        logger.info("/image.jpg served correctly (bytes=%d).", len(r.content))

        logger.info("All feature functionality checks passed.")
        return True

    def check(self):
        """
        Full check: site up + endpoints + features.
        """
        try:
            # quick ping root
            ping = self._request_ok(self.session.get, self.base + "/")
            if ping is None or ping.status_code != 200:
                logger.error("Service unavailable at %s (status=%s)", self.base, getattr(ping, "status_code", None))
                return False
            logger.info("Service reachable at %s", self.base)

            if not self.test_endpoints():
                logger.error("Endpoint accessibility checks failed")
                return False

            if not self.test_feature_functionality():
                logger.error("Feature functionality checks failed")
                return False

            logger.info("Service check PASSED")
            return True

        except Exception as e:
            logger.exception("Unexpected error during check: %s", e)
            return False


def main():
    parser = argparse.ArgumentParser(description="Airforce service checker (standalone)")
    parser.add_argument("--host", default="localhost", help="target host (default localhost)")
    parser.add_argument("--port", default="33201", help="target port (default 33201 per your docker-compose)")
    parser.add_argument("--flag-write", default=None, help="optional local path to write flag (distribute simulation)")
    parser.add_argument("--flag", default=None, help="flag string to write when --flag-write used")
    args = parser.parse_args()

    checker = AirforceServiceChecker(host=args.host, port=args.port)
    if args.flag_write and args.flag:
        checker.distribute(args.flag, args.flag_write)

    ok = checker.check()
    if ok:
        logger.info("CHECKER: SUCCESS")
        sys.exit(0)
    else:
        logger.error("CHECKER: FAILED")
        sys.exit(2)


if __name__ == "__main__":
    main()
