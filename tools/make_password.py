#!/usr/bin/env python3
"""Create a SHA-256 password hash for login.json.

Usage:
    python tools/make_password.py            # asks for the password (hidden)
    python tools/make_password.py "my-pass"  # or pass it as an argument

Copy the printed hash into the "password" field of login.json.
"""
import getpass
import hashlib
import sys

pw = sys.argv[1] if len(sys.argv) > 1 else getpass.getpass("Password: ")
print(hashlib.sha256(pw.encode("utf-8")).hexdigest())
