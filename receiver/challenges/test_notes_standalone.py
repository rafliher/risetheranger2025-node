import requests
import logging


class NotesChecker:
    def __init__(self, port=8080):
        self.port = port
        self.logger = logging.getLogger("NotesChecker")
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def _test_endpoint_accessibility(self, base_url, session):
        """Just check endpoints respond 200, not content correctness."""
        endpoints = ['/', '/list']
        self.logger.info("Checking web page accessibility...")
        for endpoint in endpoints:
            url = base_url + endpoint
            try:
                response = session.get(url, timeout=5)
                assert response.status_code == 200, f"Endpoint {endpoint} returned {response.status_code}"
                self.logger.info(f"  - Endpoint {endpoint}: OK")
            except Exception as e:
                self.logger.error(f"Failed to access endpoint {endpoint}: {e}")
                return False
        self.logger.info("All web pages are accessible.")
        return True

    def _test_core_functionality(self, base_url, session):
        """Create, read, and list note within same session (uuid)."""
        self.logger.info("Checking core functionality...")

        test_note_name = "slatestnote"
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

    def check(self):
        try:
            base_url = f"http://localhost:{self.port}"
            session = requests.Session()

            # Step 1: Website up
            self.logger.info(f"Pinging service at {base_url}...")
            response = session.get(base_url, timeout=5)
            assert response.status_code == 200, f"Website down: {response.status_code}"
            self.logger.info("Website is online.")

            # Step 2: Endpoint accessibility (only check status)
            assert self._test_endpoint_accessibility(base_url, session), "Endpoint check failed."

            # Step 3: Core functionality (create→read→list with same session)
            assert self._test_core_functionality(base_url, session), "Core functionality check failed."

            self.logger.info("Notes Challenge check passed successfully!")
            return True

        except Exception as e:
            self.logger.error(f"Notes Challenge check failed: {e}")
            return False


if __name__ == "__main__":
    checker = NotesChecker(port=10000)
    success = checker.check()
    print("Result:", "PASS" if success else "FAIL")
