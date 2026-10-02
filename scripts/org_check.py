"""org_check — P2b · Organization experience, against a throwaway copy of the db.

    python3 scripts/org_check.py [path/to/earthbucks.db]

Copies the database, points the app at the copy (migrating it to head), and
drives the API in-process with FastAPI's TestClient. Nothing it does is kept.

What it holds P2b to (INSTRUCTIONS › P2b › Done when):
  * the application form is served, and an incomplete one is refused rule by rule;
  * applying makes a PENDING organization login that cannot sign in until staff approve;
  * an organization token is refused by every vote, wallet and benefactor-post route;
  * the three tabs answer (Home · Initiatives · Profile) and each campaign has a page;
  * the public profile, claimed and UNCLAIMED (the shared D30 panel);
  * an administrator creates a member's login; a member cannot;
  * Run for this creates a candidacy; a campaign page's five sections;
  * the four organization post kinds, and an answer refused off its own ground;
  * a claimed organization cannot be claimed twice.
"""
import os
import secrets
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "backend", "earthbucks.db")
tmp = tempfile.mkdtemp(prefix="org_check_")
DB = os.path.join(tmp, "earthbucks.db")
shutil.copy(SRC, DB)
os.environ["DATABASE_URL"] = "sqlite:///" + DB
sys.path.insert(0, os.path.join(HERE, "..", "backend"))
os.chdir(os.path.join(HERE, "..", "backend"))

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from app import models, org_config  # noqa: E402
from app.auth import create_access_token, hash_password  # noqa: E402
from app.database import SessionLocal  # noqa: E402

bad = n = 0


def ok(cond, what):
    global bad, n
    n += 1
    if not cond:
        bad += 1
    print(("  ok   " if cond else "  FAIL ") + what)


def full_answers(name):
    a = {}
    for q in org_config.all_questions():
        k = q["kind"]
        a[q["key"]] = (True if k == "checkbox" else [q["options"][0]] if k == "multiselect"
                       else q["options"][0] if k == "select" else 2001 if k == "number"
                       else "https://example.org" if k == "url" else f"{name} {q['key']}")
    a["legal_name"] = name
    a["public_name"] = name
    return a


with TestClient(app) as c:
    db = SessionLocal()
    staff = models.BenefactorAccount(email=f"st{secrets.token_hex(3)}@x.test",
                                     handle="st" + secrets.token_hex(3),
                                     pass_hash=hash_password("password123"), role="admin")
    ben = models.BenefactorAccount(email=f"bn{secrets.token_hex(3)}@x.test",
                                   handle="bn" + secrets.token_hex(3),
                                   pass_hash=hash_password("password123"))
    db.add_all([staff, ben]); db.commit()
    S = {"Authorization": "Bearer " + create_access_token(staff.id)}
    B = {"Authorization": "Bearer " + create_access_token(ben.id)}

    print("· the form")
    f = c.get("/org/application").json()
    ok(len(f["sections"]) >= 4 and f["payable_later"] and f["unclaimed_panel"]["title"] == "UNCLAIMED",
       "GET /org/application serves sections, the stage-2 list and the UNCLAIMED panel")
    r = c.post("/org/apply", json={"answers": {"legal_name": "X"}, "email": "a@x.test",
                                   "handle": "ax", "password": "password123"})
    ok(r.status_code == 400 and "Required" in r.text, "an incomplete application is refused, rule by rule")

    print("· applying (a new organization)")
    name = "Check Org " + secrets.token_hex(3)
    h = "chk" + secrets.token_hex(3)
    r = c.post("/org/apply", json={"answers": full_answers(name), "email": h + "@x.test",
                                   "handle": h, "password": "password123"})
    ok(r.status_code == 201 and r.json()["created_org"], "apply creates the organization and the application")
    app_id, oid = r.json()["application_id"], r.json()["org_id"]
    r = c.post("/org/login", data={"username": h, "password": "password123"})
    ok(r.status_code == 403, "a pending login cannot sign in")
    pub = c.get(f"/organizations/{oid}/public").json()
    ok(pub["claimed"] is False and pub["unclaimed_panel"], "before approval the profile is UNCLAIMED")
    ok(c.get("/org/applications", headers=B).status_code == 403, "a benefactor cannot see the review queue")
    q = c.get("/org/applications", headers=S).json()
    ok(any(a["id"] == app_id for a in q), "staff see the application")
    ok(c.post(f"/org/applications/{app_id}/approve", headers=S, json={}).status_code == 200, "staff approve")
    r = c.post("/org/login", data={"username": h, "password": "password123"})
    ok(r.status_code == 200, "the approved administrator signs in")
    O = {"Authorization": "Bearer " + r.json()["access_token"]}
    me = c.get("/org/me", headers=O).json()
    ok(me["account"]["role"] == "admin" and me["org"]["claimed"], "/org/me: admin of a claimed organization")

    print("· no voting")
    refused = [
        ("PUT", "/missions/atm0/p1/votes", {"votes": {}}),
        ("PUT", "/missions/atm0/p2/vote", {"org_id": oid}),
        ("POST", "/missions/atm0/p2/commit", {}),
        ("GET", "/wallet", None),
        ("POST", "/wallet/commit", {}),
        ("POST", "/wallet/withdraw", {}),
        ("POST", "/posts", {"id": "x" + secrets.token_hex(3), "body": "hi", "category": "general"}),
        ("GET", "/auth/me", None),
        ("GET", "/benefactors/me/watchlist", None),
    ]
    for m, p, body in refused:
        r = c.request(m, p, headers=O, json=body)
        ok(r.status_code == 403 and "Organization accounts" in r.text, f"{m} {p} refuses an organization token")
    ok(c.get("/org/me", headers=B).status_code == 401, "a benefactor token is not an organization login")

    print("· the three tabs")
    hm = c.get("/org/home", headers=O).json()
    ok({"campaigns", "activity", "about_you", "earthbux"} <= set(hm), "Home: campaigns · activity · about you · Earthbux")
    ini = c.get("/org/initiatives", headers=O).json()
    ok("initiative_elections" in ini and "organization_elections" in ini, "Initiatives: steps 2–3")
    r = c.put("/org/profile", headers=O, json={"description": "We check things.", "website_link": "https://chk.test"})
    ok(r.status_code == 200 and r.json()["description"] == "We check things.", "Profile: edits the outward-facing fields")

    print("· members (D29)")
    mh = "mem" + secrets.token_hex(3)
    r = c.post("/org/members", headers=O, json={"email": mh + "@x.test", "handle": mh,
                                                "password": "password123", "display_name": "M"})
    ok(r.status_code == 201, "the administrator creates a member's login")
    r = c.post("/org/login", data={"username": mh, "password": "password123"})
    M = {"Authorization": "Bearer " + r.json()["access_token"]}
    r = c.post("/org/members", headers=M, json={"email": "z" + mh + "@x.test", "handle": "z" + mh,
                                                "password": "password123"})
    ok(r.status_code == 403, "a member cannot create logins")

    print("· campaigns")
    target = next((m for m in ini["organization_elections"] if not m["running"]), None) or \
        next((m for m in ini["initiative_elections"] if not m["running"]), None)
    if target is None:
        ok(False, "an open election to run in")
    else:
        r = c.post("/org/candidacies", headers=O, json={"mission_id": target["id"], "mission_statement": ""})
        ok(r.status_code == 400, "Run for this needs a mission statement")
        r = c.post("/org/candidacies", headers=O, json={"mission_id": target["id"],
                                                        "mission_statement": "We will do it well."})
        ok(r.status_code == 201, f"Run for this creates a candidacy ({target['id']})")
        mid = target["id"]
        ok(any(x["id"] == mid for x in c.get("/org/home", headers=O).json()["campaigns"]),
           "the campaign appears on Home (and so gets a tab)")
        ok(c.put(f"/org/campaigns/{mid}", headers=O, json={"mission_statement": "Revised promise."}).status_code == 200,
           "a campaign tab edits the promise")
        r = c.post("/org/posts", headers=O, json={"kind": "plan", "mission_id": mid, "title": "Plan",
                                                   "body": "Week 1: hire. Week 2: plant."})
        ok(r.status_code == 201 and r.json()["author_type"] == "org", "a plan post, authored by the organization")
        r = c.post("/org/posts", headers=O, json={"kind": "update", "body": "Hello benefactors."})
        ok(r.status_code == 201, "an update post")
        # A benefactor asks; the organization answers.
        db.refresh(ben)
        qid = "q" + secrets.token_hex(4)
        r = c.post("/posts", headers=B, json={"id": qid, "category": "general", "type": "general",
                                              "body": "How will you measure it?", "target_kind": "organization",
                                              "target_id": oid})
        ok(r.status_code == 201, "a benefactor posts about the organization")
        r = c.post("/org/posts", headers=O, json={"kind": "answer", "parent_id": qid, "body": "Quarterly counts."})
        ok(r.status_code == 201, "the organization answers it")
        other = db.query(models.Post).filter(models.Post.org_id.is_(None), models.Post.mission_id.is_(None),
                                             models.Post.parent_id.is_(None)).first()
        if other:
            r = c.post("/org/posts", headers=O, json={"kind": "answer", "parent_id": other.id, "body": "x"})
            ok(r.status_code == 403, "an answer off its own ground is refused")
        cp = c.get(f"/organizations/{oid}/campaigns/{mid}").json()
        ok({"plan", "receipts", "slate", "qa", "promise"} <= set(cp), "campaign page: the five sections")
        ok(cp["promise"] == "Revised promise." and cp["plan"]["org_plan"], "promise and plan read back")
        ok(any(q["id"] == qid and q["org_answers"] for q in cp["qa"]), "Q&A pulls in the post and its answer")
        ok(cp["receipts"]["first_receipt"], "receipts carry the application's past outcome")

    tiv = db.query(models.Initiative).join(models.Mission, models.Initiative.mission_id == models.Mission.id) \
        .filter(models.Mission.current_phase == "initiative", models.Mission.winning_tiv_id.is_(None)).first()
    if tiv:
        r = c.post("/org/posts", headers=O, json={"kind": "suggestion", "tiv_id": tiv.id, "body": "We could run this."})
        ok(r.status_code == 201 and "suggestion" in r.json()["tags"], "Suggest us on an initiative that has not won")

    print("· the public profile")
    pub = c.get(f"/organizations/{oid}/public").json()
    ok(pub["claimed"] and pub["unclaimed_panel"] is None and pub["updates"], "claimed: updates, no UNCLAIMED panel")
    ok(any(m["display_name"] == "M" for m in pub["members"]), "members listed by name")
    un = db.query(models.Organization).filter(~models.Organization.id.in_(
        db.query(models.OrgAccount.org_id))).first()
    if un:
        p2 = c.get(f"/organizations/{un.id}/public").json()
        ok(not p2["claimed"] and p2["unclaimed_panel"]["you_can"], f"unclaimed ({un.id}): the shared panel")
    ok(c.get("/o/" + oid).status_code == 200 and c.get(f"/o/{oid}/x").status_code == 200
       and c.get("/org").status_code == 200, "the pages are served: /org, /o/<org>, /o/<org>/<mission>")

    print("· claiming twice")
    h2 = "dup" + secrets.token_hex(3)
    r = c.post("/org/apply", json={"org_id": oid, "answers": full_answers(name), "email": h2 + "@x.test",
                                   "handle": h2, "password": "password123"})
    ok(r.status_code == 403 and "already claimed" in r.text, "a claimed organization cannot be claimed again")
    db.close()

shutil.rmtree(tmp, ignore_errors=True)
print(f"\n{n - bad}/{n} passed" + ("" if not bad else f" — {bad} FAILED"))
sys.exit(1 if bad else 0)
