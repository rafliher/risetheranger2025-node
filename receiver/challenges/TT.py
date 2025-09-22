#!/usr/bin/env python3
"""
simple_checker.py

Usage:
    python3 simple_checker.py check <base_url>

Checks:
 - POST /login with a letters-only username
 - ensures a 'jwt' cookie is set
 - GET / and ensure it contains "Welcome <username>!"
Exits 0 on success, 1 on failure.
"""
import sys
import random
import string
import requests

USER_AGENT = "simple-checker/1.0"

def make_username():
    return "checker" + ''.join(random.choice(string.ascii_lowercase) for _ in range(6))

def check(base_url: str) -> int:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    login_url = base_url.rstrip('/') + '/login'
    home_url = base_url.rstrip('/') + '/'

    username = make_username()
    try:
        r = s.post(login_url, data={"username": username}, timeout=8, allow_redirects=True)
    except Exception as e:
        print(f"ERROR: cannot connect to {login_url}: {e}", file=sys.stderr)
        return 1

    # Look for jwt cookie in session
    jwt_cookie = None
    for ck in s.cookies:
        if ck.name == 'jwt':
            jwt_cookie = ck.value
            break

    if not jwt_cookie:
        print("ERROR: 'jwt' cookie not set after login", file=sys.stderr)
        return 1

    # GET home and verify welcome text
    try:
        r2 = s.get(home_url, timeout=8)
    except Exception as e:
        print(f"ERROR: cannot GET {home_url}: {e}", file=sys.stderr)
        return 1

    expected = f"Welcome {username}!"
    if expected in r2.text:
        print("OK: service is up and responding")
        return 0
    else:
        print("ERROR: unexpected home page content (welcome text not found)", file=sys.stderr)
        return 1

def usage():
    print("Usage: python3 simple_checker.py check <base_url>")
    sys.exit(2)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        usage()
    cmd = sys.argv[1].lower()
    base = sys.argv[2].rstrip('/')
    if cmd != "check":
        usage()
    code = check(base)
    sys.exit(code)
