"""inbox_check — P4 · Event log + Inbox, against a throwaway copy of the db.

    python3 scripts/inbox_check.py [path/to/earthbucks.db]

Copies the database, points the app at the copy (migrating it to head), and
drives the API in-process with FastAPI's TestClient. Nothing it does is kept.

What it holds P4 to (INSTRUCTIONS › P4 › Done when — "event creation for each
notifying type, per-user fan-out, and the weekly-update assembly"):
  * reply · reaction (thresholds, once each) · cited_update · org_nominated ·
    tiv_elected · org_elected · weekly_update each create an event and reach the
    right people, never the actor;
  * win / lose / followed per voter, and what comes next;
  * read / unread and the nav summary;
  * the weekly update: assembled sections, published once, YOUR part, public latest;
  * messages: members of a shared mission only, read state, search by name and
    mission, the report button, staff hiding a message;
  * an organization token is refused; removing an account clears its inbox.
"""
import os
import secrets
import shutil
import sys
import tempfile
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "backend", "earthbucks.db")
tmp = tempfile.mkdtemp(prefix="inbox_check_")
DB = os.path.join(tmp, "earthbucks.db")
shutil.copy(SRC, DB)
os.environ["DATABASE_URL"] = "sqlite:///" + DB
sys.path.insert(0, os.path.join(HERE, "..", "backend"))
os.chdir(os.path.join(HERE, "..", "backend"))

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import select, func  # noqa: E402
from app.main import app  # noqa: E402
from app import crud, events, models, posting  # noqa: E402
from app.auth import create_access_token, create_org_token, hash_password  # noqa: E402
from app.database import SessionLocal  # noqa: E402

bad = n = 0


def ok(cond, what):
    global bad, n
    n += 1
    if not cond:
        bad += 1
    print(("  ok   " if cond else "  FAIL ") + what)


def ben(db, tag, role="benefactor"):
    h = tag + secrets.token_hex(3)
    b = models.BenefactorAccount(email=h + "@x.test", handle=h, pass_hash=hash_password("password123"), role=role)
    db.add(b)
    db.commit()
    return b


def H(b):
    return {"Authorization": "Bearer " + create_access_token(b.id)}


def notes(db, b, kind=None):
    q = select(models.Notification).join(models.Event).where(models.Notification.ben_id == b.id)
    if kind:
        q = q.where(models.Event.kind == kind)
    return db.scalars(q).all()


with TestClient(app) as c:
    db = SessionLocal()
    print("· the tables")
    from sqlalchemy import inspect
    names = set(inspect(db.get_bind()).get_table_names())
    ok({"events", "notifications", "message_threads", "messages", "message_reports"} <= names,
       "migration b8d2f6a4c1e9 made the five tables")

    staff = ben(db, "st", "admin")
    A, B, Cc, D, W = (ben(db, t) for t in ("aa", "bb", "cc", "dd", "ww"))
    voters = [ben(db, "v") for _ in range(5)]

    print("· reply")
    pid = "ic-" + secrets.token_hex(4)
    r = c.post("/posts", headers=H(A), json={"id": pid, "category": "general", "type": "general", "author_type": "ben",
                                             "title": "A's post", "body": "Something to reply to."})
    ok(r.status_code == 201, "A posts")
    rid = "ic-" + secrets.token_hex(4)
    r = c.post("/posts", headers=H(B), json={"id": rid, "category": "general", "type": "general", "author_type": "ben",
                                             "body": "B replies.", "parent_id": pid})
    ok(r.status_code == 201, "B replies")
    db.expire_all()
    na = notes(db, A, "reply")
    ok(len(na) == 1 and na[0].event.actor_ben_id == B.id, "A is notified of the reply, B is the actor")
    ok(not notes(db, B, "reply"), "the replier is not notified of their own reply")
    c.post("/posts", headers=H(A), json={"id": "ic-" + secrets.token_hex(4), "category": "general",
                                         "type": "general", "author_type": "ben", "body": "A replies to self.", "parent_id": pid})
    db.expire_all()
    ok(len(notes(db, A, "reply")) == 1, "replying to your own post notifies no one")

    print("· reaction thresholds")
    r = c.post(f"/posts/{pid}/react", headers=H(B), json={"value": "helpful"})
    ok(r.status_code == 200, "B upvotes A's post")
    db.expire_all()
    ok(len(notes(db, A, "reaction")) == 1, "the first vote notifies (threshold 1)")
    c.post(f"/posts/{pid}/react", headers=H(B), json={"value": "helpful"})   # toggle off
    c.post(f"/posts/{pid}/react", headers=H(B), json={"value": "helpful"})   # and on again
    db.expire_all()
    ok(len(notes(db, A, "reaction")) == 1, "taking a vote back and recasting it does not notify twice")
    for v in voters[:4]:
        c.post(f"/posts/{pid}/react", headers=H(v), json={"value": "helpful"})
    db.expire_all()
    rs = notes(db, A, "reaction")
    ok(len(rs) == 2 and rs[-1].event.data["count"] == 5, "the fifth vote notifies (threshold 5)")
    c.post(f"/posts/{pid}/react", headers=H(A), json={"value": "helpful"})
    db.expire_all()
    ok(len(notes(db, A, "reaction")) == 2, "your own vote on your post does not notify you")

    print("· cited_update")
    cid = "ic-" + secrets.token_hex(4)
    r = c.post("/posts", headers=H(Cc), json={"id": cid, "category": "general", "type": "general", "author_type": "ben",
                                              "body": "C cites A.", "references": [{"kind": "post", "post_id": pid}]})
    ok(r.status_code == 201, "C posts citing A's post")
    db.expire_all()
    ref = db.scalar(select(models.PostRef).where(models.PostRef.post_id == cid, models.PostRef.ref_post_id == pid))
    if ref is None:     # the composer's rules may not keep a general post's citation; record it directly
        db.add(models.PostRef(post_id=cid, kind="post", ref_post_id=pid, ref_version=1))
        db.commit()
    r = c.put(f"/posts/{pid}", headers=H(A), json={"body": "Something to reply to — edited."})
    ok(r.status_code == 200 and r.json()["version"] == 2, "A edits: version 2")
    db.expire_all()
    cu = notes(db, Cc, "cited_update")
    ok(len(cu) == 1 and cu[0].detail.get("cited_version") == 1, "C hears the post they cite changed (cited v1 · now v2)")
    ok(not notes(db, A, "cited_update"), "the editor is not notified")

    print("· a mission to elect in (synthetic, cycle 99)")
    now = datetime.utcnow()
    m = models.Mission(id="zzt99", cause_id="oceans", cycle_num=99, current_phase="initiative",
                       started_at=now - timedelta(weeks=7, days=1))
    db.add(m)
    X = models.Initiative(id="tiv-x-" + secrets.token_hex(3), title="Check initiative X", cause_id="oceans",
                          mission_id="zzt99", proposer_ben_id=A.id, status="suggested")
    Y = models.Initiative(id="tiv-y-" + secrets.token_hex(3), title="Check initiative Y", cause_id="oceans",
                          mission_id="zzt99", status="suggested")
    db.add_all([X, Y])
    db.commit()
    W.watched_tiv_ids = '["%s"]' % X.id
    db.add_all([models.VoteP1(ben_id=A.id, mission_id="zzt99", tiv_id=X.id, share=1.0, committed=True),
                models.VoteP1(ben_id=B.id, mission_id="zzt99", tiv_id=Y.id, share=1.0, committed=True),
                models.VoteP1(ben_id=Cc.id, mission_id="zzt99", tiv_id=X.id, share=1.0, committed=True)])
    db.commit()

    print("· tiv_elected")
    m = db.get(models.Mission, "zzt99")
    crud._elect_tiv(db, m, X.id)
    db.expire_all()
    ev = db.scalar(select(models.Event).where(models.Event.dedupe == "tiv_elected:zzt99"))
    ok(ev is not None and ev.data["next"]["label"].startswith("Organization election"),
       "the initiative election makes one event, with what comes next")
    out = {nn.ben_id: nn.detail["outcome"] for nn in db.scalars(select(models.Notification).where(
        models.Notification.event_id == (ev.id if ev else -1))).all()}
    ok(out.get(A.id) == "won" and out.get(Cc.id) == "won" and out.get(B.id) == "lost",
       "per voter: A and C won, B lost")
    ok(D.id not in out, "a non-voter is not notified")
    ok(events.on_tiv_elected(db, "zzt99", X.id, {}) is None, "the same election never notifies twice")

    print("· org_nominated")
    org1 = models.Organization(id="org-ic1-" + secrets.token_hex(2), name="Check Org One", verified=False)
    org2 = models.Organization(id="org-ic2-" + secrets.token_hex(2), name="Check Org Two", verified=False)
    db.add_all([org1, org2])
    db.commit()
    r = c.post("/candidacies", headers=H(D), json={"mission_id": "zzt99", "org_id": org1.id,
                                                    "mission_statement": "We will run X."})
    ok(r.status_code == 201, "D nominates Check Org One into X's organization election")
    db.expire_all()
    on = db.scalar(select(models.Event).where(models.Event.kind == "org_nominated",
                                              models.Event.org_id == org1.id))
    got = {nn.ben_id for nn in db.scalars(select(models.Notification).where(
        models.Notification.event_id == (on.id if on else -1))).all()}
    ok(on is not None and A.id in got and W.id in got, "X's proposer (A) and its watcher (W) are notified")
    ok(D.id not in got, "the nominator is not notified")
    # the organization side: Run for this
    oa = models.OrgAccount(org_id=org2.id, email="o" + secrets.token_hex(3) + "@x.test",
                           handle="o" + secrets.token_hex(3), pass_hash=hash_password("password123"),
                           role="admin", is_active=True)
    db.add(oa)
    db.commit()
    O = {"Authorization": "Bearer " + create_org_token(oa.id)}
    r = c.post("/org/candidacies", headers=O, json={"mission_id": "zzt99", "mission_statement": "We run X too."})
    ok(r.status_code == 201, "Check Org Two runs for X (organization account)")
    db.expire_all()
    ok(any(nn.event.data.get("how") == "running" for nn in notes(db, A, "org_nominated")),
       "A hears an organization is running for their initiative")
    ok(c.get("/inbox/summary", headers=O).status_code == 403, "an organization token is refused by the inbox")

    print("· org_elected")
    for cand in db.scalars(select(models.MissionCandidacy).where(models.MissionCandidacy.mission_id == "zzt99")).all():
        cand.status = "approved"
    db.add_all([models.VoteP2(ben_id=A.id, mission_id="zzt99", org_id=org1.id, votes=1, valence="helpful",
                              committed=True, stake_ct=100, origin_mission_id="zzt99"),
                models.VoteP2(ben_id=B.id, mission_id="zzt99", org_id=org2.id, votes=1, valence="helpful",
                              committed=True, stake_ct=100, origin_mission_id="zzt99"),
                models.VoteP2(ben_id=voters[0].id, mission_id="zzt99", org_id=org1.id, votes=1, valence="helpful",
                              committed=True, stake_ct=100, origin_mission_id="zzt99"),
                models.VoteP2(ben_id=Cc.id, mission_id="zzt99", org_id=None, votes=1, valence="helpful",
                              committed=True, stake_ct=100, origin_mission_id="zzt99")])
    db.commit()
    won = crud.finalize_p2(db, "zzt99")
    ok(won == org1.id, "finalize_p2 elects Check Org One")
    db.expire_all()
    ev = db.scalar(select(models.Event).where(models.Event.dedupe == "org_elected:zzt99"))
    out = {nn.ben_id: nn.detail["outcome"] for nn in db.scalars(select(models.Notification).where(
        models.Notification.event_id == (ev.id if ev else -1))).all()}
    ok(ev is not None and "Budget day" in ev.data["next"]["label"], "the organization election makes one event, with what comes next")
    ok(out.get(A.id) == "won" and out.get(B.id) == "lost" and out.get(Cc.id) == "followed",
       "per voter: A won, B lost, C's unnamed stake followed the winner")

    print("· the stream, read / unread")
    r = c.get("/inbox/notifications", headers=H(A)).json()
    kinds = {x["kind"] for x in r["items"]}
    ok({"reply", "reaction", "tiv_elected", "org_nominated", "org_elected"} <= kinds, "A's stream carries every kind A was sent")
    ok(all(x["title"] and x["link"] is not None for x in r["items"]), "every item has words and a link")
    s = c.get("/inbox/summary", headers=H(A)).json()
    ok(s["unread_notifications"] == len(r["items"]), "the summary counts the unread")
    first = r["items"][0]["id"]
    c.post("/inbox/notifications/read", headers=H(A), json={"ids": [first]})
    ok(c.get("/inbox/summary", headers=H(A)).json()["unread_notifications"] == len(r["items"]) - 1, "marking one read")
    ok(len(c.get("/inbox/notifications?unread=1", headers=H(A)).json()["items"]) == len(r["items"]) - 1, "?unread=1 filters")
    c.post("/inbox/notifications/read", headers=H(A), json={"all": True})
    ok(c.get("/inbox/summary", headers=H(A)).json()["unread_notifications"] == 0, "marking all read")
    r = c.post("/inbox/notifications/read", headers=H(B), json={"ids": [first]}).json()
    db.expire_all()
    ok(db.get(models.Notification, first).ben_id == A.id and r["marked"] == 0, "nobody marks another person's notification")

    print("· the weekly update")
    w = events.week_of(now)
    ed = events.assemble_weekly(db, w, now + timedelta(days=8))
    db.rollback()
    ok({"new_initiatives", "new_organizations", "entered_exchange", "prep", "next_week", "headline"} <= set(ed),
       "assembled: new initiative · new organization · exchange · prep · next week")
    # the synthetic mission's T fell a day ago; place the week on it
    tw = events.week_of(posting.me_close(db.get(models.Mission, "zzt99")))
    ed = events.assemble_weekly(db, tw, now)
    db.rollback()
    ok(any(x["mission_id"] == "zzt99" for x in ed["new_initiatives"]), "the week's new initiative is in its edition")
    ok(c.get("/inbox/weekly/preview", headers=H(A)).status_code == 403, "only staff preview an edition")
    r = c.post(f"/inbox/weekly/publish?week={tw}", headers=H(staff))
    ok(r.status_code == 200 and r.json()["week"] == tw, "staff publish the edition")
    ok(c.post(f"/inbox/weekly/publish?week={tw}", headers=H(staff)).status_code == 409, "an edition publishes once")
    db.expire_all()
    ev = events.published_week(db, tw)
    reached = db.scalar(select(func.count()).select_from(models.Notification).where(models.Notification.event_id == ev.id))
    live = db.scalar(select(func.count()).select_from(models.BenefactorAccount).where(
        models.BenefactorAccount.is_active.is_(True), models.BenefactorAccount.is_test.is_(False)))
    ok(reached == live, f"fanned out to every active benefactor ({reached})")
    r = c.get(f"/inbox/weekly?week={tw}", headers=H(A)).json()
    ok("you" in r and isinstance(r["you"]["results"], list), "YOUR part is added for the reader")
    r = c.get("/inbox/weekly/latest").json()
    ok(r and "you" not in r, "the latest edition is public (Home, News), without anyone's part")
    ok(events.publish_due(db, events.week_bounds(tw + 1)[0] + timedelta(hours=1)) is None,
       "the scheduler does not republish a published week")

    print("· messages (D10)")
    r = c.get("/inbox/people", headers=H(A)).json()
    ok(any(p["id"] == B.id for p in r) and not any(p["id"] == D.id for p in r),
       "people: members of my missions, and only them")
    r = c.post("/inbox/threads", headers=H(A), json={"to_id": D.id})
    ok(r.status_code == 403, "no thread with someone who shares no mission")
    r = c.post("/inbox/threads", headers=H(A), json={"to_id": B.id, "mission_id": "zzt99"})
    ok(r.status_code == 201, "A opens a thread with B in their shared mission")
    tid = r.json()["id"]
    ok(c.post("/inbox/threads", headers=H(B), json={"to_id": A.id}).json()["id"] == tid, "one thread per pair")
    ok(c.get(f"/inbox/threads/{tid}", headers=H(D)).status_code == 404, "an outsider cannot read it")
    r = c.post(f"/inbox/threads/{tid}/messages", headers=H(A), json={"body": "Hello from the mission."})
    ok(r.status_code == 201, "A sends a message")
    ok(c.get("/inbox/summary", headers=H(B)).json()["unread_threads"] == 1, "B has an unread thread")
    ok(c.get("/inbox/summary", headers=H(A)).json()["unread_threads"] == 0, "the sender's own message is not unread")
    t = c.get(f"/inbox/threads/{tid}", headers=H(B)).json()
    ok(t["messages"][0]["body"] == "Hello from the mission." and "No campaigning" in t["rule"],
       "B reads it, with the no-campaigning rule")
    ok(c.get("/inbox/summary", headers=H(B)).json()["unread_threads"] == 0, "reading clears it")
    ok(len(c.get(f"/inbox/threads?q={A.handle[:4]}", headers=H(B)).json()["items"]) == 1, "search by name")
    ok(len(c.get("/inbox/threads?q=zzt99", headers=H(B)).json()["items"]) == 1, "search by mission")
    ok(len(c.get("/inbox/threads?q=nomatchzz", headers=H(B)).json()["items"]) == 0, "a search that matches nothing")
    mid = t["messages"][0]["id"]
    ok(c.post(f"/inbox/messages/{mid}/report", headers=H(A), json={}).status_code == 400, "you cannot report your own message")
    r = c.post(f"/inbox/messages/{mid}/report", headers=H(B), json={"reason": "campaigning"})
    ok(r.status_code == 201, "B reports it")
    ok(c.get("/inbox/reports", headers=H(B)).status_code == 403, "only staff read reports")
    reps = c.get("/inbox/reports", headers=H(staff)).json()
    rep = next((x for x in reps if x["message"]["id"] == mid), None)
    ok(rep is not None and rep["reason"] == "campaigning", "staff see the report")
    c.post(f"/inbox/reports/{rep['id']}", headers=H(staff), json={"uphold": True})
    t = c.get(f"/inbox/threads/{tid}", headers=H(B)).json()
    ok(t["messages"][0]["hidden"], "upheld: the message is hidden")

    print("· removing an account")
    db.expire_all()
    crud.remove_account(db, A.id, db.get(models.BenefactorAccount, staff.id))
    db.expire_all()
    ok(db.scalar(select(func.count()).select_from(models.Notification).where(models.Notification.ben_id == A.id)) == 0,
       "their notifications go with them")
    ok(db.get(models.MessageThread, tid) is None, "and their threads")

    print("· the page")
    ok(c.get("/inbox").status_code == 200 and "inbox" in c.get("/inbox.html").text.lower(), "/inbox is served")
    db.close()

print(f"\n{n - bad}/{n} passed")
shutil.rmtree(tmp, ignore_errors=True)
sys.exit(1 if bad else 0)
