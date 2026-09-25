"""contact_check — the footer's Contact us, against a live API (2026-09-25).

    python3 scripts/contact_check.py [http://127.0.0.1:8000]

Run it against a LOCAL server: it posts real messages. Checks that a message is
stored, that bad input is refused, that the honeypot keeps nothing, and that
reading messages is staff-only. Also greps ebx_shared.js for the dialog and
every page for the footer mount.
"""
import json, re, sys, urllib.error, urllib.request
from pathlib import Path

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
ROOT = Path(__file__).resolve().parents[1]
bad = n = 0


def ok(c, what, detail=""):
    global bad, n
    n += 1; bad += (not c)
    print(("  ok    " if c else "  FAIL  ") + what + ("  " + str(detail) if detail else ""))


def call(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"} if body is not None else {})
    try:
        with urllib.request.urlopen(req) as r: return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null")


good = {"name": "Check", "email": "check@example.com", "topic": "general", "body": "contact_check message", "page": "/check"}
print("\n=== POST /contact")
s, r = call("POST", "/contact", good)
ok(s == 201 and r.get("ok") and isinstance(r.get("id"), int), "a message is stored", r)
ok(call("POST", "/contact", dict(good, email="not-an-email"))[0] == 422, "a bad email is refused")
ok(call("POST", "/contact", dict(good, body="hi"))[0] == 422, "an empty message is refused")
ok(call("POST", "/contact", dict(good, topic="nope"))[0] == 400, "an unknown topic is refused")
s, r = call("POST", "/contact", dict(good, website="http://spam"))
ok(s == 201 and r.get("id") is None, "the honeypot is accepted and kept nowhere", r)

print("\n=== staff only")
ok(call("GET", "/admin/contact")[0] in (401, 403), "GET /admin/contact needs a staff sign-in")

print("\n=== the dialog and the footer")
js = (ROOT / "resources/js/ebx_shared.js").read_text(encoding="utf8")
ok("contact(opts)" in js and '"/contact"' in js, "EBX.Dialogs.contact posts /contact")
ok("data-ebx-contact" in js and '"#contact"' in js, "footer buttons and #contact open it")
ok('document.body.appendChild(mount)' in js, "a page without a footer mount still gets the footer")
for page in ("index.html", "about.html", "mission.html", "cause.html", "profile.html"):
    ok("ebx_shared.js" in (ROOT / page).read_text(encoding="utf8"), page + " loads the shared footer")

print("\n" + (f"FAILED {bad}/{n}" if bad else f"all {n} checks passed"))
sys.exit(1 if bad else 0)
