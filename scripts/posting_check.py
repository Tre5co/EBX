"""posting_check — P3 · Posting, against a live API, then the clock-bound rules
against a throwaway copy of the database.

    python3 scripts/posting_check.py [http://127.0.0.1:8000] [path/to/earthbucks.db]

Part 1 (live API) signs up throwaway accounts — run it against a local server,
never the live site. Part 2 copies the database file and moves the clock
forward inside the copy (pins, rolls, leads), so nothing it does is kept.

What it holds P3 to (INSTRUCTIONS › P3 · Posting › Done when):
  * the gates are gone — a brand-new account posts every type and replies;
  * each type's target and limit (Background → cause, one per cause;
    Investigation → organization, one per organization; Analysis → mission,
    one per mission, open T+8 → T+15; budget → initiative, one open per type;
    general → anything or nothing, unlimited, tags);
  * the Review lane is gone — a case arrives as a general post tagged `case`;
  * the Analysis composer's reference rules (12 + 12, the two leading
    attached and not removable);
  * versions — every edit is a new version, the version a mission kept is
    locked, edits go forward; pulling an old post restarts its votes;
  * the guide — every creatable type carries purpose, target, limit, earns and
    steps, and the three vote names exist;
  * the feed framework — every strategy answers, ties are stable.
"""
import json
import os
import secrets
import shutil
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
HERE = os.path.dirname(os.path.abspath(__file__))
DB = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "backend", "earthbucks.db")
bad = n = 0


def ok(c, what, detail=""):
    global bad, n
    n += 1
    bad += (not c)
    print(("  ok    " if c else "  FAIL  ") + what + ("  " + str(detail)[:200] if (detail and not c) else ""))


def section(t):
    print("\n=== " + t)


def call(method, path, body=None, token=None, form=False):
    data, h = None, {}
    if body is not None:
        data = (urllib.parse.urlencode(body) if form else json.dumps(body)).encode()
        h["Content-Type"] = "application/x-www-form-urlencoded" if form else "application/json"
    if token:
        h["Authorization"] = "Bearer " + token
    req = urllib.request.Request(BASE + path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        raw = e.read() or b"null"
        try:
            return e.code, json.loads(raw)
        except ValueError:
            return e.code, raw.decode(errors="replace")


def account():
    h = "pc" + secrets.token_hex(3)
    call("POST", "/auth/signup", {"email": h + "@posting-check.example.com", "handle": h, "password": "pw-" + h})
    _, t = call("POST", "/auth/login", {"username": h, "password": "pw-" + h}, form=True)
    return t["access_token"], h


pid = lambda: "pc-" + secrets.token_hex(6)


def post(tok, **kw):
    kw.setdefault("id", pid())
    kw.setdefault("author_type", "ben")
    kw.setdefault("body", "posting_check")
    return call("POST", "/posts", kw, tok)


# ════════════════════════════════════════════════════════════════════════
section("the guide — one table for the composer, the How-to and the outline")
s, g = call("GET", "/posts/guide")
ok(s == 200, "GET /posts/guide answers", s)
types = {t["key"]: t for t in g["types"]}
ok(set(types) == {"general", "context", "investigation", "analysis", "service", "supply", "support"},
   "seven creatable types: general · Background · Investigation · Analysis · Service · Supply · Support", list(types))
ok(all(t["guide"] and all(t["guide"][k] for k in ("purpose", "points_at", "limit", "earns", "steps"))
       for t in types.values()), "every type carries purpose · points at · limit · earns · steps")
ok([c["label"] for c in g["categories"]] == ["General", "Research", "Budget"], "three kinds of post",
   [c["label"] for c in g["categories"]])
ok({v["name"] for v in g["votes"]} >= {"Election vote", "Research vote", "Analysis vote"},
   "the three vote names", [v["name"] for v in g["votes"]])
ok(types["context"]["vote_name"] == "Research vote" and types["analysis"]["vote_name"] == "Analysis vote",
   "a vote on a Background is a Research vote; on an Analysis, an Analysis vote")
ok(not any(t["key"] in ("case", "evaluation") for t in g["types"]) and
   {"case", "evaluation"} <= {t["key"] for t in g["general_tags"]},
   "Case and Evaluation are tags, not types (D8)")

# ════════════════════════════════════════════════════════════════════════
section("the gates are gone — a brand-new account, no stake")
tok, handle = account()
tok2, handle2 = account()
missions = call("GET", "/missions")[1]
causes = call("GET", "/causes")[1]
orgs = call("GET", "/organizations")[1]
cause = causes[0]["id"]
tivs = call("GET", "/initiatives")[1]
tiv = next(t for t in tivs if t.get("mission_id"))
org = orgs[0]["id"]

s, r = post(tok, category="general", type="general", body="a plain post about nothing")
ok(s == 201 and r["target_kind"] == "none", "a general post with no target", (s, r))
s, r2 = post(tok, category="general", tags=["opinion", "tiv:" + tiv["id"], "tiv:no-such-x"],
             target_kind="initiative", target_id=tiv["id"], body="an opinion on an initiative")
ok(s == 201 and r2["target_kind"] == "initiative" and r2["target_label"] == tiv["title"],
   "a general post on an initiative carries its target and its name", (s, r2))
ok(s == 201 and r2["tags"] == ["opinion", "tiv:" + tiv["id"]], "tags kept; an entity tag for nothing dropped",
   r2.get("tags") if isinstance(r2, dict) else r2)
s, r = post(tok, category="general", tags=["opinion"], body="a second general post")
ok(s == 201, "general posts are unlimited", s)
s, r = post(tok, category="general", tags=["response"], body="in response to nothing")
ok(s == 400 and "response" in json.dumps(r).lower(), "a Response must target a post", (s, r))
s, r = post(tok, category="general", tags=["response"], target_kind="post", target_id=r2["id"],
            body="in response to that opinion")
ok(s == 201 and r["target_label"], "…and does, when it names one", (s, r))

s, r = post(tok, category="review", type="case", stance="for", tiv_id=tiv["id"], body="the case for it")
ok(s == 201 and r["category"] == "general" and "case" in r["tags"],
   "a Review-lane case arrives as a general post tagged `case` (D8)", (s, r))

s, reply = post(tok2, parent_id=r2["id"], body="a reply from someone else", category="general")
ok(s == 201 and reply["target_kind"] == "post", "anyone can reply", (s, reply))
s, c = call("GET", f"/posts/{r2['id']}/comments")
ok(s == 200 and any(x["id"] == reply["id"] for x in c), "the reply is in the thread")
s, lst = call("GET", f"/posts?ben_author_id=0&limit=1")

# ── Background ──────────────────────────────────────────────────────────
section("Background → a cause, one per person per cause (D19)")
s, bg = post(tok, category="mission_support", type="context", target_kind="cause", target_id=cause,
             tags=["tiv:" + tiv["id"]], title="What voters should know", body="background v1")
ok(s == 201 and bg["cause_id"] == cause and bg["target_kind"] == "cause", "a Background points at its cause", (s, bg))
ok(s == 201 and bg["mission_id"], "…and lands in the cause's open initiative election", bg.get("mission_id"))
s, r = post(tok, category="mission_support", type="context", target_kind="cause", target_id=cause, body="again")
ok(s == 400 and "one background" in json.dumps(r).lower(), "a second Background for the same cause is refused", (s, r))
s, r = post(tok, category="mission_support", type="context", body="no cause")
ok(s == 400 and "cause" in json.dumps(r).lower(), "a Background with no cause is refused", (s, r))
s, lst = call("GET", f"/posts?tiv_id={tiv['id']}&type=context")
ok(s == 200 and any(x["id"] == bg["id"] for x in lst), "it previews under each initiative it tags")

# ── Investigation ───────────────────────────────────────────────────────
section("Investigation → an organization, one per person per organization")
s, inv = post(tok, category="mission_support", type="investigation", target_kind="organization",
              target_id=org, body="what I found")
ok(s == 201 and inv["org_id"] == org and inv["target_label"], "an Investigation names its organization", (s, inv))
s, r = post(tok, category="mission_support", type="investigation", target_kind="organization",
            target_id=org, body="again")
ok(s == 400 and "one investigation" in json.dumps(r).lower(), "a second one of the same organization is refused", (s, r))
s, r = post(tok, category="mission_support", type="investigation", body="no org")
ok(s == 400 and "organization" in json.dumps(r).lower(), "an Investigation with no organization is refused", (s, r))
s, r = post(tok, category="mission_support", type="investigation", target_kind="organization",
            target_id="no-such-org-x", body="x")
ok(s == 400 and "not found" in json.dumps(r), "…or one naming an organization that does not exist", (s, r))

# ── Budget ──────────────────────────────────────────────────────────────
section("Budget item → an initiative, any time, one open per type")
s, b = post(tok, category="budgeting", type="supply", target_kind="initiative", target_id=tiv["id"],
            line_items=[{"item": "40 sensors", "supplier": "Acme", "cost": 1200}], body="sensors")
ok(s == 201 and b["tiv_id"] == tiv["id"] and b["est_cost_usd"] == 1200, "a supply item on an initiative, no stake", (s, b))
s, r = post(tok, category="budgeting", type="supply", target_kind="initiative", target_id=tiv["id"],
            line_items=[{"item": "more", "supplier": "Acme", "cost": 1}], body="more")
ok(s == 400 and "open supply" in json.dumps(r).lower(), "a second open Supply on the same initiative is refused", (s, r))
s, r = post(tok, category="budgeting", type="support", target_kind="initiative", target_id=tiv["id"],
            line_items=[{"item": "a permit"}], body="a permit")
ok(s == 201, "a Support item (no cost line) beside it", (s, r))
s, r = post(tok, category="budgeting", type="service", target_kind="initiative", target_id=tiv["id"], body="uncosted")
ok(s == 400 and "cost" in json.dumps(r).lower(), "an uncosted Service is refused", (s, r))

# ── Analysis ────────────────────────────────────────────────────────────
section("Analysis → a mission, T+8 → T+15, the two leading posts attached")
now = datetime.utcnow()


def _d(x):
    return datetime.fromisoformat(str(x).replace("Z", ""))


kits = [(m, call("GET", "/posts/analysis-kit?mission_id=" + m["id"])[1]) for m in missions]
open_kit = next(((m, k) for m, k in kits if k.get("open")), None)
shut_kit = next(((m, k) for m, k in kits if not k.get("open") and _d(k["opens_at"]) > now), None)
if shut_kit:
    s, r = post(tok, category="mission_support", type="analysis", target_kind="mission",
                target_id=shut_kit[0]["id"], body="too early")
    ok(s == 400 and "organization election closes" in json.dumps(r), "an Analysis before T+8 is refused", (s, r))
if open_kit:
    m, kit = open_kit
    ok("leads" in kit and "backgrounds" in kit and kit["max_backgrounds"] == 12, "the kit offers leads and research")
    bgs = [x["id"] for x in kit["backgrounds"]][:13]
    invs = [x["id"] for x in kit["investigations"]][:13]
    if len(bgs) > 12:
        s, r = post(tok2, category="mission_support", type="analysis", target_kind="mission", target_id=m["id"],
                    references=[{"kind": "post", "post_id": x} for x in bgs], body="too many")
        ok(s == 400 and "at most 12" in json.dumps(r), "13 Backgrounds is refused", (s, r))
    refs = [{"kind": "post", "post_id": x} for x in (bgs[:3] + invs[:3])] + \
           [{"kind": "link", "url": "https://example.org/report", "label": "A report"}]
    s, an = post(tok2, category="mission_support", type="analysis", target_kind="mission", target_id=m["id"],
                 references=refs, body="the analysis")
    ok(s == 201 and an["target_kind"] == "mission", "an Analysis on an open mission, no stake", (s, an))
    if s == 201:
        s, full = call("GET", "/posts/" + an["id"])
        autos = [x["post_id"] for x in full["references"] if x.get("auto")]
        lead = kit["leads"]
        want = [x for x in (lead.get("background_id"), lead.get("investigation_id")) if x]
        ok(sorted(autos) == sorted(want), "the leading Background and Investigation are attached", (autos, want))
        ok(any(x["kind"] == "link" for x in full["references"]), "an outside link is a reference too")
        # try to drop the leads by editing the references
        s, ed = call("PUT", "/posts/" + an["id"], {"references": [{"kind": "link", "url": "https://example.org"}]}, tok2)
        s, full2 = call("GET", "/posts/" + an["id"])
        ok(sorted(x["post_id"] for x in full2["references"] if x.get("auto")) == sorted(want),
           "…and an edit cannot remove them")
        s, r = post(tok2, category="mission_support", type="analysis", target_kind="mission", target_id=m["id"], body="2")
        ok(s == 400 and "one per person per mission" in json.dumps(r), "one Analysis per person per mission", (s, r))
else:
    print("  (no mission with an open Analysis window in this database — skipped)")

# ── Versions ────────────────────────────────────────────────────────────
section("versions (D21) — every edit is a new version")
s, e1 = call("PUT", "/posts/" + bg["id"], {"body": "background v2"}, tok)
ok(s == 200 and e1["version"] == 2, "an edit makes version 2", (s, e1))
s, v1 = call("GET", f"/posts/{bg['id']}/versions/1")
ok(s == 200 and v1["body"] == "background v1", "version 1 is exactly as it was")
s, r = call("PUT", "/posts/" + bg["id"], {"body": "hijack"}, tok2)
ok(s == 403, "only the author edits", s)
s, full = call("GET", "/posts/" + bg["id"])
ok(s == 200 and [v["version"] for v in full["versions"]] == [1, 2], "the full view lists every version")

# ── Votes per mission, and pull ──────────────────────────────────────────
section("votes count per mission; a pulled post starts from zero (D21)")
s, r = call("POST", f"/posts/{r2['id']}/react", {"value": "helpful"}, tok2)
ok(s == 200 and r["helpful_count"] == 1, "an upvote counts", (s, r))
s, r = call("POST", f"/posts/{r2['id']}/react", {"value": "harmful"}, tok2)
ok(s == 400, "a general post is upvote-only", s)
other = next((m for m in missions if m["id"] != r2.get("mission_id")), None)
s, pulled = call("POST", f"/posts/{r2['id']}/pull", {"mission_id": other["id"]}, tok)
ok(s == 200 and pulled["helpful_count"] == 0 and pulled["mission_id"] == other["id"],
   "pulled into another mission, its votes start from zero there", (s, pulled))
s, lst = call("GET", f"/posts?mission_id={other['id']}&limit=500")
ok(any(x["id"] == r2["id"] for x in lst), "…and it lists in that mission")
if r2.get("mission_id"):
    s, lst = call("GET", f"/posts?mission_id={r2['mission_id']}&limit=500")
    row = next((x for x in lst if x["id"] == r2["id"]), None)
    ok(row is not None and row["helpful_count"] == 1, "the old mission keeps it, with its vote", row and row.get("helpful_count"))
s, r = call("POST", f"/posts/{r2['id']}/pull", {"mission_id": other["id"]}, tok2)
ok(s == 403, "only the author pulls", s)

# ── The feed framework ───────────────────────────────────────────────────
section("the feed framework — named strategies, stable ties")
s, st = call("GET", "/posts/strategies")
keys = [x["key"] for x in st if "label" in x]
ok(s == 200 and {"latest", "hot", "trending", "research", "missions"} <= set(keys), "five strategies", keys)
for k in keys:
    s1, a = call("GET", f"/posts?sort={k}&limit=40&roots_only=true")
    s2, b2 = call("GET", f"/posts?sort={k}&limit=40&roots_only=true")
    ok(s1 == 200 and [x["id"] for x in a] == [x["id"] for x in b2], f"sort={k} answers, and twice the same")
s, r = call("GET", "/posts?sort=research&limit=50")
ok(s == 200 and all(x["type"] in ("context", "investigation", "analysis") for x in r), "research is research only")
s, r = call("GET", "/posts?sort=nonsense")
ok(s == 400, "an unknown order is refused", s)

# ════════════════════════════════════════════════════════════════════════
section("the clock — pins, rolls and leads, on a throwaway copy of the database")
tmp = tempfile.mkdtemp()
shutil.copy2(DB, os.path.join(tmp, "copy.db"))
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tmp, "copy.db")
sys.path.insert(0, os.path.join(HERE, "..", "backend"))
from app import models, posting  # noqa: E402
from app.database import SessionLocal  # noqa: E402

db = SessionLocal()
# A mission with a later, still-open initiative election in the same cause,
# so the roll has somewhere to go.
_all = db.query(models.Mission).all()
m = next((x for x in sorted(_all, key=lambda x: x.started_at, reverse=True)
          if any(y.cause_id == x.cause_id and not y.winning_tiv_id and
                 posting.me_close(y) > posting.me_close(x) + timedelta(days=1) for y in _all)), _all[-1])
has_bg = {b for (b,) in db.query(models.Post.ben_author_id).filter(
    models.Post.type == "context", models.Post.cause_id == m.cause_id).all()}
ben = next(b for b in db.query(models.BenefactorAccount).all() if b.id not in has_bg)
t0 = posting.me_close(m) - timedelta(days=3)
p = models.Post(id=pid(), category="mission_support", type="context", body="v1", author_type="ben",
                ben_author_id=ben.id)
refs = posting.prepare_new(db, p, target_kind="cause", target_id=m.cause_id, tags=[], references=None,
                           author=ben, now=t0)
db.add(p); db.flush()
p.created_at = t0
posting.after_create(db, p, refs)
db.query(models.PostVersion).filter_by(post_id=p.id).update({"created_at": t0})
p.mission_id = m.id
posting.link_mission(db, p.id, m.id, "origin")
db.flush()
ok(posting.pin_due(db, p, t0) == [], "before the initiative election closes, nothing is pinned")
after = posting.me_close(m) + timedelta(days=1)
posting.new_version(db, p, {"body": "v2, written after the close"}, now=after)
row = db.query(models.PostMission).filter_by(post_id=p.id, mission_id=m.id).one()
ok(row.pinned_version == 1, "the closed election keeps version 1 — the one standing at T", row.pinned_version)
ok(1 in posting.locked_versions(db, p.id), "…and version 1 is locked for good")
ok(p.version == 2, "the author edited forward, to version 2")
nxt = posting.open_initiative_mission(db, m.cause_id, after)
if nxt is not None and nxt.id != m.id:
    ok(p.mission_id == nxt.id, "the Background rolled into the cause's next initiative election", (p.mission_id, nxt.id))
    ok(p.helpful_count == 0, "…where its votes start from zero")
else:
    print("  (no later mission of this cause in the copy — the roll is not exercised)")
lead = posting.leads(db, m, after)
ok(lead["background_fixed"], "the leading Background is fixed once T has passed (D20)")
lead2 = posting.leads(db, m, after + timedelta(days=30))
ok(lead2["background_id"] == lead["background_id"], "…and stays fixed")
db.rollback()
db.close()
shutil.rmtree(tmp, ignore_errors=True)

print(f"\n{n - bad}/{n} ok" + ("" if not bad else f" — {bad} FAILED"))
sys.exit(1 if bad else 0)
