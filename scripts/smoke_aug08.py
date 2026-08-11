"""End-to-end smoke test for the 2026-08-08 pass (§7).

Run the API, seed a staff account, then:  python scripts/smoke_aug08.py

Runs against a THROWAWAY copy of the db in /tmp — never the live one.
Checks, in order:
  1. the app boots and auto-migrates (posts.flag / est_* exist)
  2. a budgeting post WITHOUT estimates is rejected (400)
  3. a budgeting post WITH estimates is accepted and rated green
  4. an org-tagged review post lands in the mission's post-support layer
  5. a staff flag override moves it to orange and the layer counts follow
"""
import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"
MISSION = "atm0"          # in `budget` phase, org-001 elected
ORG = "org-001"


def call(method, path, body=None, token=None):
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data, timeout=20) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw.decode()[:300]


fails = []


def check(name, cond, detail=""):
    print(("  PASS  " if cond else "  FAIL  ") + name + ("" if cond else "  <- " + str(detail)))
    if not cond:
        fails.append(name)


def login(user, pw):
    import urllib.parse
    req = urllib.request.Request(BASE + "/auth/login", method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    body = urllib.parse.urlencode({"username": user, "password": pw}).encode()
    try:
        with urllib.request.urlopen(req, body, timeout=20) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]


st, tok = login("smoke@test.local", "smoke-pass-123")
check("1. staff login", st == 200 and tok and tok.get("access_token"), (st, tok))
token = (tok or {}).get("access_token")

st, r = call("POST", "/posts", {
    "id": "smoke-nobudget", "category": "budgeting", "type": "service",
    "body": "Ship water filters", "author_type": "ben", "mission_id": MISSION,
}, token)
check("2. budgeting post without estimates is rejected", st == 400, (st, r))
check("2b. and the message names both estimates",
      st == 400 and "setup time" in str(r).lower() and "cost" in str(r).lower(), r)

st, r = call("POST", "/posts", {
    "id": "smoke-budget", "category": "budgeting", "type": "service",
    "body": "Ship water filters to the delta villages", "author_type": "ben",
    "mission_id": MISSION, "est_setup_days": 14, "est_cost_usd": 12500,
}, token)
check("3. budgeting post with estimates is accepted", st == 201, (st, r))
check("3b. estimates round-trip", st == 201 and r.get("est_setup_days") == 14
      and r.get("est_cost_usd") == 12500, r)
check("3c. rated green on the way in", st == 201 and r.get("flag") == "green", r)

st, r = call("POST", "/posts", {
    "id": "smoke-case", "category": "review", "type": "case",
    "body": "This org has run three comparable programmes.", "author_type": "ben",
    "mission_id": MISSION, "org_id": ORG,
}, token)
check("4. org-tagged review post created", st == 201, (st, r))

st, layer = call("GET", "/missions/%s/post-support" % MISSION)
check("4b. post-support layer reachable", st == 200, (st, layer))
check("4c. the case is in the layer", st == 200 and layer.get("total", 0) >= 1, layer)
check("4d. grouped under its organization",
      st == 200 and any(o.get("org_id") == ORG for o in layer.get("orgs", [])), layer)
check("4e. everything reads green",
      st == 200 and layer["counts"]["green"] == layer["total"], layer.get("counts"))
check("4f. only org-tagged types are rated (the budgeting post is not)",
      st == 200 and all(t["type"] in ("case", "investigation", "evaluation")
                        for o in layer.get("orgs", []) for t in o["threads"]), layer)

st, r = call("POST", "/posts/smoke-case/flag",
             {"flag": "orange", "reason": "Critical but sourced"}, token)
check("5. staff flag override accepted", st == 200 and r.get("flag") == "orange", (st, r))

st, r = call("POST", "/posts/smoke-case/flag", {"flag": "chartreuse"}, token)
check("5b. an unknown flag is rejected", st == 400, (st, r))

st, layer = call("GET", "/missions/%s/post-support" % MISSION)
check("5c. the layer follows the override",
      st == 200 and layer["counts"]["orange"] >= 1, layer.get("counts"))

print()
print("FAILED: " + ", ".join(fails) if fails else "ALL PASS")
sys.exit(1 if fails else 0)
