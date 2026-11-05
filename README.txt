VOLTEX – web edition (vl.web.zip)
=================================

What is inside
--------------
index.html, styles.css, app.js      The app (UI, login, navigation, install button)
engine.worker.js                    Runs the Python engine in a background worker
engine/voltex-engine.zip            Python calculation engine (TG.VL, TG.VX, TG.WX)
pyodide/                            Python runtime (Pyodide) – makes Python run in the browser
sw.js, manifest.webmanifest         Offline support and "Install app" support
login.json                          User accounts (login only, no sign-up)
tools/make_password.py              Helper to create SHA-256 password hashes
fonts/, icons/                      Vazirmatn (Persian/Latin) font and app icons
source/                             Python source of the engine

Run it
------
The app must be served over HTTPS (or http://localhost for testing).
Any static host works: GitHub Pages, Netlify, Cloudflare Pages, Nginx, Apache, IIS.
For a quick local test:
    cd vl
    python -m http.server 8080
then open http://localhost:8080

Install on a phone
------------------
Open the site, press "Download app" (دانلود برنامه) at the top, and confirm.
Android/Chrome: install prompt or ⋮ → "Install app".
iPhone/Safari: Share → "Add to Home Screen".
After the first visit the app works offline.

Accounts (login.json)
---------------------
There is no sign-up. Only accounts in login.json can sign in.
Each account has:
    "username"  – the user name
    "password"  – SHA-256 hash (recommended) or plain text
    "name"      – display name
Add as many users as you like to the "users" list.
To create a hash:
    python tools/make_password.py
The default account is admin / voltex123 – CHANGE IT before publishing.

Security note: login.json is a static file, so it is downloadable by anyone who
knows its address. Use hashed passwords and strong passwords, and treat this as a
convenience gate, not as protection for sensitive data.

Languages: English (default) and Persian (فارسی), switch with the top-right button.
