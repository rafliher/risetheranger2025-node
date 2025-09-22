#!/usr/bin/env python3
"""
Checker for the Notes website.

Usage:
    python3 notes_checker.py check http://host:5000

Exit codes:
    0 = OK (service up and functional)
    1 = FAIL (unexpected behaviour or service down)
"""

import sys
import requests
import random
import string

USER_AGENT = "notes-checker/1.0"

def randstr(n=8):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(n))

def check(base_url: str) -> int:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})

    # Step 1: create note
    note_name = "note_" + randstr()
    note_body = "body_" + randstr(12)

    try:
        r = s.post(base_url.rstrip('/') + "/create", data={"name": note_name, "body": note_body}, timeout=8)
    except Exception as e:
        print(f"ERROR: cannot connect to /create: {e}", file=sys.stderr)
        return 1

    try:
        data = r.json()
    except Exception:
        print("ERROR: /create did not return JSON", file=sys.stderr)
        return 1

    if data.get("error"):
        print(f"ERROR: /create failed: {data.get('message')}", file=sys.stderr)
        return 1

    # Step 2: read back note
    try:
        r2 = s.get(base_url.rstrip('/') + "/read", params={"name": note_name}, timeout=8)
    except Exception as e:
        print(f"ERROR: cannot connect to /read: {e}", file=sys.stderr)
        return 1

    if note_body not in r2.text:
        print("ERROR: note body mismatch in /read", file=sys.stderr)
        return 1

    # Step 3: confirm note appears in /list
    try:
        r3 = s.get(base_url.rstrip('/') + "/list", timeout=8)
    except Exception as e:
        print(f"ERROR: cannot connect to /list: {e}", file=sys.stderr)
        return 1

    try:
        data3 = r3.json()
    except Exception:
        print("ERROR: /list did not return JSON", file=sys.stderr)
        return 1

    notes = data3.get("notes", [])
    if note_name not in notes:
        print("ERROR: note not found in /list", file=sys.stderr)
        return 1

    print("OK: service is up and functional")
    return 0

def usage():
    print("Usage: python3 notes_checker.py check <base_url>")
    sys.exit(2)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        usage()
    cmd = sys.argv[1].lower()
    base = sys.argv[2]
    if cmd != "check":
        usage()
    sys.exit(check(base))
