from .Challenge import Challenge
import requests

class NotesChecker(Challenge):
    """
    SLA Checker for the 'Notes' challenge.
    This checker verifies:
    1. The web service is online and pages are accessible.
    2. Core functionality works: create, read, and list notes.
    """

    def _test_endpoint_accessibility(self, base_url):
        """Checks if all required web pages are accessible via GET requests."""
        endpoints = ['/', '/list']
        self.logger.info("Checking web page accessibility...")
        for endpoint in endpoints:
            url = base_url + endpoint
            try:
                response = requests.get(url, timeout=5)
                assert response.status_code == 200, f"Endpoint {endpoint} returned {response.status_code}"
                self.logger.info(f"  - Endpoint {endpoint}: OK")
            except Exception as e:
                self.logger.error(f"Failed to access endpoint {endpoint}: {e}")
                return False
        self.logger.info("All web pages are accessible.")
        return True

    def _test_core_functionality(self, base_url):
        """
        Tests create, read, and list functionality with a benign note.
        Uses a session to persist cookies across requests.
        """
        self.logger.info("Checking core functionality...")
        session = requests.Session()

        test_note_name = "sla_test_note"
        test_note_body = "hello_from_checker"

        # --- Test Create ---
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

        # --- Test Read ---
        try:
            r = session.get(base_url + "/read", params={"name": test_note_name}, timeout=5)
            assert r.status_code == 200, f"Read returned {r.status_code}"
            assert test_note_body in r.text, f"Read content mismatch: {r.text}"
            self.logger.info("  - Read note: OK")
        except Exception as e:
            self.logger.error(f"Read note failed: {e}")
            return False

        # --- Test List ---
        try:
            r = session.get(base_url + "/list", timeout=5)
            j = r.json()
            assert r.status_code == 200, f"List returned {r.status_code}"
            assert test_note_name in j.get("notes", []), "Test note not found in list"
            self.logger.info("  - List notes: OK")
        except Exception as e:
            self.logger.error(f"List notes failed: {e}")
            return False

        self.logger.info("All core functionality checks passed.")
        return True

    def check(self):
        """
        Main SLA check function. Called periodically by the game engine.
        """
        try:
            base_url = f"http://localhost:{self.port}"

            # Step 1: Check if the website is up
            self.logger.info(f"Pinging service at {base_url}...")
            response = requests.get(base_url, timeout=5)
            assert response.status_code == 200, f"Website down: {response.status_code}"
            self.logger.info("Website is online.")

            # Step 2: Endpoint accessibility
            assert self._test_endpoint_accessibility(base_url), "Endpoint check failed."

            # Step 3: Core functionality
            assert self._test_core_functionality(base_url), "Core functionality check failed."

            self.logger.info("Notes Challenge check passed successfully!")
            return True

        except Exception as e:
            self.logger.error(f"Notes Challenge check failed: {e}")
            return False
