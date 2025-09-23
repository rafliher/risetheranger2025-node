from .Challenge import Challenge
import requests
import secrets


class Notes(Challenge):
    """
    SLA Checker for the Notes challenge.
    This checker verifies:
    1. Service is online and responds at main endpoints.
    2. Core functionality works: create → read → list notes (same session).
    """

    def check(self):
        base_url = f"http://localhost:{self.port}"
        session = requests.Session()

        # Step 1: Website up
        self.logger.info(f"Pinging service at {base_url}...")
        try:
            r = session.get(base_url, timeout=5)
            assert r.status_code == 200, f"Website down: {r.status_code}"
            self.logger.info("Website is online.")
        except Exception as e:
            self.logger.error(f"Website not reachable: {e}")
            return False

        # Step 2: Endpoint accessibility
        endpoints = ["/", "/list"]
        self.logger.info("Checking web page accessibility...")
        for ep in endpoints:
            try:
                r = session.get(base_url + ep, timeout=5)
                assert r.status_code == 200, f"Endpoint {ep} returned {r.status_code}"
                self.logger.info(f"  - Endpoint {ep}: OK")
            except Exception as e:
                self.logger.error(f"Failed to access endpoint {ep}: {e}")
                return False
        self.logger.info("All web pages are accessible.")

        # Step 3: Core functionality
        self.logger.info("Checking core functionality...")

        # Generate unique note name each run
        test_note_name = "sla" + secrets.token_hex(4)
        test_note_body = "hello_from_checker"

        # --- Create ---
        try:
            r = session.post(base_url + "/create", data={
                "name": test_note_name,
                "body": test_note_body
            }, timeout=5)
            j = r.json()
            assert r.status_code == 200, f"Create returned {r.status_code}"
            assert not j.get("error", True), f"Create failed: {j}"
            self.logger.info("  - Create note: OK")
        except Exception as e:
            self.logger.error(f"Create note failed: {e}")
            return False

        # --- Read ---
        try:
            r = session.get(base_url + "/read", params={"name": test_note_name}, timeout=5)
            assert r.status_code == 200, f"Read returned {r.status_code}"
            assert test_note_body in r.text, f"Read content mismatch: {r.text}"
            self.logger.info("  - Read note: OK")
        except Exception as e:
            self.logger.error(f"Read note failed: {e}")
            return False

        # --- List ---
        try:
            r = session.get(base_url + "/list", timeout=5)
            j = r.json()
            assert r.status_code == 200, f"List returned {r.status_code}"
            assert test_note_name in j.get("notes", []), f"Test note not found in list: {j}"
            self.logger.info("  - List notes: OK")
        except Exception as e:
            self.logger.error(f"List notes failed: {e}")
            return False

        self.logger.info("All core functionality checks passed.")
        return True
