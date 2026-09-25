"""research_gate_check — the 2026-09-25 posting rules, against a live API.

    python3 scripts/research_gate_check.py [http://127.0.0.1:8000]

Research (Background · Vetting · Analysis) is open to anyone signed in, with no
stake; budgeting and review stay gated; a new vetting post must name an
organization that exists. Signs up a throwaway account on the target — run it
against a local server, not the live site.
"""
import json, secrets, sys, urllib.request, urllib.error, urllib.parse

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
bad = n = 0


def ok(c, what, detail=""):
    global bad, n
    n += 1; bad += (not c)
    print(("  ok    " if c else "  FAIL  ") + what + ("  " + str(detail) if detail else ""))


def call(method, path, body=None, token=None, form=False):
    data = None; h = {}
    if body is not None:
        data = (urllib.parse.urlencode(body) if form else json.dumps(body)).encode()
        h["Content-Type"] = "application/x-www-form-urlencoded" if form else "application/json"
    if token: h["Authorization"] = "Bearer " + token
    req = urllib.request.Request(BASE + path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req) as r: return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null")


handle = "gate" + secrets.token_hex(3)
call("POST", "/auth/signup", {"email": handle + "@example.com", "handle": handle, "password": "pw-" + handle})
_, t = call("POST", "/auth/login", {"username": handle, "password": "pw-" + handle}, form=True)
tok = t["access_token"]
missions = call("GET", "/missions")[1]
m = next(x for x in missions if x.get("winning_org_id"))
base = {"author_type": "ben", "mission_id": m["id"], "cause_id": m["cause_id"], "body": "gate check"}
pid = lambda: "p-" + secrets.token_hex(6)

print("\n=== research is open (no stake)")
s, r = call("POST", "/posts", dict(base, id=pid(), category="mission_support", type="context"), tok)
ok(s == 201, "a Background post with no stake", s)
s, r = call("POST", "/posts", dict(base, id=pid(), category="mission_support", type="investigation"), tok)
ok(s == 400 and "organization" in json.dumps(r), "a Vetting post with no organization is refused", r)
s, r = call("POST", "/posts", dict(base, id=pid(), category="mission_support", type="investigation", org_id="no-such-org-x"), tok)
ok(s == 400 and "not found" in json.dumps(r), "…and one naming an organization that does not exist", r)
s, r = call("POST", "/posts", dict(base, id=pid(), category="mission_support", type="investigation", org_id=m["winning_org_id"]), tok)
ok(s == 201 and r.get("org_id") == m["winning_org_id"], "a Vetting post naming the elected organization", s)
s, r = call("POST", "/posts", dict(base, id=pid(), category="mission_support", type="investigation", org_id=m["winning_org_id"]), tok)
ok(s == 400 and "one investigation" in json.dumps(r), "still one of each per person per mission", s)

print("\n=== budgeting and review stay gated")
s, r = call("POST", "/posts", dict(base, id=pid(), category="budgeting", type="support", est_cost_usd=0, est_setup_days=0), tok)
ok(s == 403, "a budget item with no stake is refused", s)
s, r = call("POST", "/posts", dict(base, id=pid(), category="review", type="case", stance="for"), tok)
ok(s == 403, "a case with no stake is refused", s)

print("\n" + (f"FAILED {bad}/{n}" if bad else f"all {n} checks passed"))
sys.exit(1 if bad else 0)
