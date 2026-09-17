#!/usr/bin/env python3
"""ebx_bots — AI benefactor bots for Earthbux.

Built 2026-09-16 (INSTRUCTIONS build-seq §1), rebuilt the same day for
build-seq §2 ("Bots deep"). Each bot is an ordinary benefactor account with a
personality (`personas.json`) that drives the REAL HTTP API, exactly as the
pages do. Standard library only: Python 3.9+ on any machine, from a terminal, a
Cowork session, or a scheduled task.

    python scripts/bots/ebx_bots.py --base https://earthbux.net plan
    python scripts/bots/ebx_bots.py --base https://earthbux.net initiatives   --content week.json
    python scripts/bots/ebx_bots.py --base https://earthbux.net organizations --content week.json
    python scripts/bots/ebx_bots.py --base https://earthbux.net budget        --content week.json
    python scripts/bots/ebx_bots.py --base https://earthbux.net research      --content week.json
    python scripts/bots/ebx_bots.py --base https://earthbux.net exchange      --content week.json

ONE TASK PER RUN, EVERY BOT AT ONCE
-----------------------------------
Each command is one task. Every bot runs it at the same time (one thread per
bot, each with its own session).

    plan           read-only JSON of the week, plus each bot's own stakes and
                   posts. An AI reads this before writing a content file.
    initiatives    1. vote in every open initiative election (a whole-
                   percentage split), propose initiatives, argue a case for or
                   against one, reply to other posts, rate cases fair/unfair.
    organizations  2. commit to the organization election closing this week,
                   nominate organizations, argue a case for or against one,
                   reply, rate cases.
    budget         3. suggest budget items (service · supply · support, with
                   costed rows) in missions the bot has a stake in, and upvote
                   other people's.
    research       4. create or update the bot's research posts (context ·
                   investigation · analysis) for any mission it has a stake in.
    exchange       5. move stakes between open organization races, and withdraw
                   part of a stake as cash after an election (the non-final
                   part, until budget day).

    sync           (staff) add the local version's initiatives and organizations
                   to the site: bots for open elections, the staff account for
                   windows that have passed. Pilot rows are skipped.
    backfill       (staff) elect an organization in every past organization
                   election that never got one.

2026-09-17: `initiatives` votes in EVERY open initiative election — tokens in
the upcoming one, a 0-token preference elsewhere — and `organizations` votes
only in this week's race plus races whose initiative election the bot backed.

WHERE THE WORDS COME FROM
-------------------------
* `--content week.json` — a file keyed by bot handle, then task (see
  `content.example.json`). This is the Cowork path: Claude runs `plan`, searches
  the web, writes the file in each bot's voice, then runs the task.
* `--ai` — each bot asks Claude itself (web search on), in its own personality.
  Needs `ANTHROPIC_API_KEY` and `EBX_BOT_MODEL` in the environment. This is the
  unattended / scheduled path.
* Neither — the bots still vote, rate, upvote and exchange, leaning toward the
  causes in their `cause_affinity`, but write nothing.

THE BOT SIGNATURE
-----------------
Set `EBX_BOT_KEY` (the same value as the server's) and new bot accounts are
created with `is_test = true`, which keeps them out of the public member counts
and is how they are found and removed before real money is used. Existing
accounts can be marked by staff: `POST /admin/accounts/{id}/test`.

ACCOUNTS
--------
Personas live in `scripts/bots/personas.json` (committed — no secrets). Passwords
are generated once into `scripts/bots/bots.local.json` (git-ignored). Keep that
file, or the bots cannot log back in. Use `--accounts other.json` per site.

SAFETY
------
* `--dry-run` prints every write instead of sending it.
* Proposed initiatives and nominated organizations enter UNAPPROVED; staff
  approval is still the gate. Nominations name real organizations publicly —
  check what an AI found before posting it.
* Bot votes are real votes. Remove bot accounts before real money is used.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import secrets
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_ACCOUNTS = HERE / "bots.local.json"
DEFAULT_PERSONAS = HERE / "personas.json"
CT_PER_TOKEN = 100
TASKS = ("initiatives", "organizations", "budget", "research", "exchange")
ADMIN_TASKS = ("sync", "backfill")
_print_lock = threading.Lock()


def say(handle: str, msg: str) -> None:
    with _print_lock:
        print(f"  {handle:>10}: {msg}", flush=True)


# ---------------------------------------------------------------------------
# HTTP — how --base works: every call is BASE + PATH
# ---------------------------------------------------------------------------
class ApiError(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


class Api:
    """One benefactor's session with one site.

    `base` is the ORIGIN — scheme + host (+ port): `https://earthbux.net`,
    `http://localhost:8000`. Every request is that origin followed by an API
    path, so the same bot code talks to the live site or a local copy.
    """

    def __init__(self, base: str, dry_run: bool = False, pause: float = 0.2,
                 bot_key: str | None = None):
        self.base = base.rstrip("/")
        self.dry_run = dry_run
        self.pause = pause
        self.bot_key = bot_key
        self.token: str | None = None

    def _req(self, method, path, body=None, form=None, write=False, headers=None):
        if write and self.dry_run:
            return {"dry_run": True, "method": method, "path": path, "body": body}
        h = {"Accept": "application/json", "User-Agent": "ebx-bots/2"}
        h.update(headers or {})
        data = None
        if form is not None:
            data = urllib.parse.urlencode(form).encode()
            h["Content-Type"] = "application/x-www-form-urlencoded"
        elif body is not None:
            data = json.dumps(body).encode()
            h["Content-Type"] = "application/json"
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        req = urllib.request.Request(self.base + path, data=data, method=method, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
            if write:
                time.sleep(self.pause)
            return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:300]
            raise ApiError(e.code, f"{method} {path}: {detail}") from None

    def get(self, path, **params):
        q = {k: v for k, v in params.items() if v is not None}
        return self._req("GET", path + (("?" + urllib.parse.urlencode(q)) if q else ""))

    def post(self, path, body):
        return self._req("POST", path, body=body, write=True)

    def put(self, path, body):
        return self._req("PUT", path, body=body, write=True)


# ---------------------------------------------------------------------------
# Accounts
# ---------------------------------------------------------------------------
def load_bots(personas_path: Path, accounts_path: Path) -> list[dict]:
    personas = json.loads(personas_path.read_text())
    secrets_by_handle = json.loads(accounts_path.read_text()) if accounts_path.exists() else {}
    if isinstance(secrets_by_handle, list):          # the 2026-09-16a format
        secrets_by_handle = {}
    changed = False
    for p in personas:
        if p["handle"] not in secrets_by_handle:
            secrets_by_handle[p["handle"]] = secrets.token_urlsafe(18)
            changed = True
        p["password"] = secrets_by_handle[p["handle"]]
    if changed:
        accounts_path.write_text(json.dumps(secrets_by_handle, indent=2))
        print(f"credentials written: {accounts_path}")
    return personas


def sign_in(api: Api, bot: dict) -> dict | None:
    """Log in, signing up first if needed. Returns /auth/me, or None in a dry run
    for an account that does not exist yet."""
    login = {"username": bot["handle"], "password": bot["password"]}
    try:
        tok = api._req("POST", "/auth/login", form=login)
    except ApiError as e:
        if e.code != 401:
            raise
        if api.dry_run:
            say(bot["handle"], "[dry-run] would sign up")
            return None
        hdr = {"X-EBX-Bot-Key": api.bot_key} if api.bot_key else None
        api._req("POST", "/auth/signup", headers=hdr,
                 body={"email": bot["email"], "handle": bot["handle"], "password": bot["password"]})
        tok = api._req("POST", "/auth/login", form=login)
    api.token = tok["access_token"]
    return api.get("/auth/me")


# ---------------------------------------------------------------------------
# Reading the week
# ---------------------------------------------------------------------------
def slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:48] + "-" + secrets.token_hex(3)


def read_week(api: Api) -> dict:
    causes = api.get("/causes") or []
    slate = api.get("/causes/slate") or {}
    active = next((c for c in causes if c.get("index") == slate.get("active_index")), None)
    missions = api.get("/missions") or []
    # 2026-09-17 (build-seq §1): every cause's UPCOMING initiative election — the
    # lowest undecided cycle, not the newest. The old sort took the newest cycle
    # of the active cause only, which is why every bot voted in the latest
    # possible election and nowhere else.
    def upcoming_me(cause_id):
        ms = sorted([m for m in missions if m["cause_id"] == cause_id
                     and not m.get("winning_tiv_id")
                     and m.get("current_phase") in ("pre", "initiative")],
                    key=lambda m: int(m.get("cycle_num") or 0))
        return ms[0] if ms else None
    me = upcoming_me(active["id"]) if active else None
    elections = []
    for c in causes:
        m = upcoming_me(c["id"])
        if not m:
            continue
        elections.append({
            "mission_id": m["id"], "cause_id": c["id"], "cause": c.get("name"),
            "is_upcoming": bool(active and c["id"] == active["id"]),
            "initiatives": [{"id": t["id"], "title": t["title"],
                             "description": (t.get("description") or "")[:300],
                             "committed_tokens": t.get("ebx_committed", 0)}
                            for t in (api.get("/initiatives", mission_id=m["id"]) or [])
                            if t.get("mission_id") == m["id"]]})
    elections.sort(key=lambda e: (not e["is_upcoming"], e["cause_id"]))
    orgs = {o["id"]: o.get("name") for o in (api.get("/organizations") or [])}
    races = []
    for r in api.get("/wallet/rows") or []:
        cands = api.get("/candidacies", mission_id=r["mission_id"]) or []
        races.append({"mission_id": r["mission_id"], "cause_id": r["cause_id"],
                      "initiative": r.get("tiv_title"), "vote_date": r.get("vote_date"),
                      "is_active_race": r.get("is_active_race"),
                      "candidates": [{"org_id": c["org_id"], "name": orgs.get(c["org_id"])}
                                     for c in cands]})
    framing = [{"mission_id": m["id"], "cause_id": m["cause_id"]}
               for m in missions if m.get("winning_org_id") and m.get("current_phase") == "budget"]

    def posts_for(mid):
        return [{"id": p["id"], "category": p.get("category"), "type": p.get("type"),
                 "stance": p.get("stance"), "tiv_id": p.get("tiv_id"), "org_id": p.get("org_id"),
                 "title": p.get("title"), "body": (p.get("body") or "")[:400],
                 "ben_author_id": p.get("ben_author_id")}
                for p in (api.get("/posts", mission_id=mid, roots_only="true", limit=40) or [])]

    watched = [e["mission_id"] for e in elections] + [r["mission_id"] for r in races]
    return {
        "active_cause": active and {"id": active["id"], "name": active.get("name"),
                                    "description": active.get("description")},
        "initiative_election": next((e for e in elections if e["is_upcoming"]), None),
        "initiative_elections": elections,
        "organization_races": races,
        "framing_missions": framing,
        "posts_by_mission": {mid: posts_for(mid) for mid in watched},
    }


def read_me(api: Api, me: dict) -> dict:
    w = api.get("/wallet")
    rows = [r for r in w.get("rows", []) if int(r.get("my_stake_ct") or 0) > 0]
    mine = api.get("/posts", ben_author_id=me["id"], limit=100) or []
    return {"id": me["id"], "free_tokens": int(w["wallet"]["free_ct"]) / CT_PER_TOKEN,
            "cash_ct": w["wallet"].get("cash_ct"),
            "stakes": [{"mission_id": r["mission_id"], "initiative": r.get("tiv_title"),
                        "stake_tokens": r["my_stake_ct"] / CT_PER_TOKEN,
                        "final_tokens": (r.get("my_final_ct") or 0) / CT_PER_TOKEN,
                        "org_id": r.get("my_org_id"), "movable": r.get("movable")} for r in rows],
            # 2026-09-17: the organization races this bot may vote in — this
            # week's, plus any whose initiative election it backed.
            "open_races": [r["mission_id"] for r in w.get("rows", []) if r.get("can_take_part")],
            "my_posts": [{"id": p["id"], "mission_id": p.get("mission_id"), "type": p.get("type"),
                          "title": p.get("title"), "parent_id": p.get("parent_id")} for p in mine]}


# ---------------------------------------------------------------------------
# AI (optional) — each bot drafts its own content, in its own voice
# ---------------------------------------------------------------------------
SCHEMAS = {
    "initiatives": '{"propose":[{"title","description","emoji"}], "votes":{"<mission id>":{"<initiative id>": <whole percent>}}, '
                   '"case":{"tiv_id","stance":"for|against","title","body"}, '
                   '"replies":[{"parent_id","body"}], "ratings":[{"post_id","fair":true|false}]}',
    "organizations": '{"nominate":[{"mission_id","name","website_link","description","mission_statement"}], '
                     '"vote":{"org_id"}, "votes":{"<mission id>":"<org id>"}, "case":{"org_id","stance":"for|against","title","body"}, '
                     '"replies":[{"parent_id","body"}], "ratings":[{"post_id","fair":true|false}]}',
    "budget": '{"items":[{"mission_id","type":"service|supply|support","title","body",'
              '"line_items":[service {"job","hourly_rate","days_needed"} | supply {"item","supplier","cost"} | support {"item"}]}], '
              '"upvote":["<post id>"]}',
    "research": '{"posts":[{"mission_id","type":"context|investigation|analysis","title","body"}]}',
    "exchange": '{"moves":[{"from_mission_id","to_mission_id","tokens","org_id"}], '
                '"withdraw":[{"mission_id","tokens"}]}',
}
BRIEFS = {
    "initiatives": "Vote in EVERY open initiative election listed under initiative_elections (whole percentages "
                   "summing to 100 across 1-3 initiatives each), focusing on the one marked is_upcoming — your tokens "
                   "go there; the others are preferences. "
                   "propose 0-1 new real, specific initiative for the active cause that is not already listed, "
                   "write ONE case for or against one initiative, reply to 0-2 posts, and rate 0-3 cases.",
    "organizations": "Pick one candidate organization to back in the race marked is_active_race (and, if you "
                     "have one, in each race listed under your open_races), nominate 0-1 "
                     "real organization (verify it exists; include its website) for a race, write ONE case for "
                     "or against one candidate in the race you back, reply to 0-2 posts, rate 0-3 cases.",
    "budget": "Suggest 1-2 costed budget items only in missions listed under your stakes, with realistic costs, "
              "and upvote 0-3 other people's budget posts.",
    "research": "Write or rewrite your research posts (at most one per type per mission) only for missions "
                "listed under your stakes. Cite sources inline. If you already have that post, it will be updated.",
    "exchange": "Decide whether to move part of a movable stake to another open organization race (you must name "
                "an org_id from that race's candidates) and whether to withdraw a small part of a stake as cash. "
                "Stay in character: withdraw little if you are committed, more if you are skeptical.",
}


def ai_content(bot: dict, task: str, week: dict, mine: dict) -> dict:
    key, model = os.environ.get("ANTHROPIC_API_KEY"), os.environ.get("EBX_BOT_MODEL")
    if not key or not model:
        raise SystemExit("--ai needs ANTHROPIC_API_KEY and EBX_BOT_MODEL in the environment")
    system = (f"You are {bot['handle']}, a benefactor on Earthbux, a weekly charity pool elected by its "
              f"community. Personality: {bot['personality']} Write in that voice, stay factual, never "
              f"invent organizations or statistics, and keep posts under 180 words.")
    prompt = (f"TASK: {BRIEFS[task]}\n\nReturn ONLY a JSON object shaped like:\n{SCHEMAS[task]}\n"
              f"Omit any key you have nothing for. Use only ids that appear below.\n\n"
              f"THE WEEK:\n{json.dumps(week)[:40000]}\n\nYOU:\n{json.dumps(mine)[:8000]}")
    body = {"model": model, "max_tokens": 3000, "system": system,
            "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}],
            "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request("https://api.anthropic.com/v1/messages",
                                 data=json.dumps(body).encode(), method="POST",
                                 headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                                          "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=240) as r:
        out = json.loads(r.read())
    text = "".join(b.get("text", "") for b in out.get("content", []) if b.get("type") == "text")
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0)) if m else {}


# ---------------------------------------------------------------------------
# The five tasks
# ---------------------------------------------------------------------------
def _try(bot, what, fn):
    try:
        res = fn()
        say(bot["handle"], ("[dry-run] " if isinstance(res, dict) and res.get("dry_run") else "") + what)
        return res
    except ApiError as e:
        say(bot["handle"], f"refused — {what}: {e}")
        return None


def _reply_and_rate(api, bot, c, week):
    known = {p["id"]: (mid, p) for mid, ps in week["posts_by_mission"].items() for p in ps}
    for r in c.get("replies", []):
        mid, parent = known.get(r.get("parent_id"), (None, None))
        if not parent:
            continue
        _try(bot, f"replied to {r['parent_id']}", lambda: api.post("/posts", {
            "id": "p-" + secrets.token_hex(6), "author_type": "ben", "category": parent["category"],
            "type": parent["type"], "mission_id": mid, "parent_id": r["parent_id"], "body": r["body"]}))
    for r in c.get("ratings", []):
        if r.get("post_id") in known and known[r["post_id"]][1].get("ben_author_id") != c.get("_me"):
            value = "helpful" if r.get("fair", True) else "harmful"
            _try(bot, f"rated {r['post_id']} {'fair' if value == 'helpful' else 'unfair'}",
                 lambda: api.post(f"/posts/{r['post_id']}/react", {"value": value}))


def _auto_ratings(bot, week, mission_ids, rng, my_id=None):
    out = []
    for mid in mission_ids:
        for p in week["posts_by_mission"].get(mid, []):
            if p["type"] == "case" and p.get("ben_author_id") != my_id and rng.random() < 0.5:
                out.append({"post_id": p["id"], "fair": rng.random() < 0.7})
    return out


def _whole_pct(shares: dict) -> dict:
    """Whole percentages summing to 100, at least 1 each (largest remainder)."""
    shares = {k: float(v) for k, v in shares.items() if float(v) > 0}
    total = sum(shares.values())
    if not total:
        return {}
    raw = {k: 100 * v / total for k, v in shares.items()}
    out = {k: max(1, int(x)) for k, x in raw.items()}
    for k in sorted(raw, key=lambda k: raw[k] - int(raw[k]), reverse=True):
        if sum(out.values()) >= 100:
            break
        out[k] += 1
    while sum(out.values()) > 100:
        k = max(out, key=out.get)
        out[k] -= 1
    return out


def task_initiatives(api, bot, week, mine, c, rng):
    """2026-09-17 (build-seq §1): vote in EVERY open initiative election, with the
    bot's tokens in the upcoming one (the week's cause — the only one a granted
    token may enter) and a standing preference, 0 tokens, in the rest."""
    elections = week.get("initiative_elections") or []
    if not elections:
        say(bot["handle"], "no open initiative election")
        return
    votes = dict(c.get("votes") or {})
    upcoming = next((e for e in elections if e["is_upcoming"]), None)
    if c.get("vote") and upcoming:                       # the older single-election shape
        votes.setdefault(upcoming["mission_id"], c["vote"])
    aff_of = bot.get("cause_affinity", {})
    for e in elections:
        tivs = {t["id"]: t for t in e["initiatives"]}
        if not tivs:
            continue
        shares = {k: v for k, v in (votes.get(e["mission_id"]) or {}).items() if k in tivs and v > 0}
        if not shares:
            # Spread: the upcoming election always, the rest in proportion to how
            # much the persona cares about that cause.
            if not e["is_upcoming"] and rng.random() > 0.25 + 0.15 * aff_of.get(e["cause_id"], 2):
                continue
            picks = rng.sample(list(tivs), k=min(len(tivs), rng.randint(1, 3)))
            shares = {p: rng.randint(1, 10) for p in picks}
        pct = _whole_pct(shares)
        tokens = 0
        if e["is_upcoming"]:
            # More of the grant into a cause it cares about (affinity 1-5 → 40-80%);
            # the rest waits for this week's organization election.
            aff = aff_of.get(e["cause_id"], 3)
            tokens = int(mine["free_tokens"] * min(0.8, 0.3 + 0.1 * aff)) or int(mine["free_tokens"])
        label = ", ".join(f"{tivs[k]['title'][:22]} {v}%" for k, v in pct.items())
        _try(bot, f"ME {e['mission_id']} · {tokens} tokens · {label}",
             lambda e=e, pct=pct, tokens=tokens: api.put(
                 f"/missions/{e['mission_id']}/p1/votes",
                 {"mission_id": e["mission_id"], "ebx": tokens,
                  "shares": {k: v / 100 for k, v in pct.items()}}))
    me = upcoming or elections[0]
    tivs = {t["id"]: t for t in me["initiatives"]}
    for t in c.get("propose", []):
        _try(bot, f"proposed initiative '{t['title']}'", lambda t=t: api.post("/initiatives", {
            "id": slug(t["title"]), "title": t["title"], "description": t.get("description"),
            "emoji": t.get("emoji"), "cause_id": t.get("cause_id") or week["active_cause"]["id"]}))
    case = c.get("case")
    all_tivs = {t["id"]: (e["mission_id"], t) for e in elections for t in e["initiatives"]}
    if case and case.get("tiv_id") in all_tivs:
        mid, t = all_tivs[case["tiv_id"]]
        _try(bot, f"case {case.get('stance', 'for')} '{t['title'][:30]}'",
             lambda: api.post("/posts", {
                 "id": "p-" + secrets.token_hex(6), "author_type": "ben", "category": "review",
                 "type": "case", "mission_id": mid, "tiv_id": case["tiv_id"],
                 "stance": case.get("stance", "for"), "title": case.get("title"), "body": case["body"]}))
    c = dict(c, _me=mine["id"])
    c.setdefault("ratings", _auto_ratings(bot, week, [me["mission_id"]], rng, mine["id"]))
    _reply_and_rate(api, bot, c, week)


def task_organizations(api, bot, week, mine, c, rng):
    race = next((r for r in week["organization_races"] if r["is_active_race"]), None)
    for n in c.get("nominate", []):
        body = {"name": n["name"], "description": n.get("description"),
                "website_link": n.get("website_link"), "kind": "nomination",
                "mission_id": n.get("mission_id"), "mission_statement": n.get("mission_statement")}
        res = _try(bot, f"nominated '{n['name']}' for {n.get('mission_id')}",
                   lambda: api.post("/organizations/register", body))
        if res and not res.get("dry_run") and not res.get("created") and res.get("matches"):
            body["org_id"] = res["matches"][0]["org_id"]
            _try(bot, f"…matched existing '{res['matches'][0]['name']}', nominated that",
                 lambda: api.post("/organizations/register", body))
    if not race:
        say(bot["handle"], "no organization race closes this week")
        return
    cands = {x["org_id"]: x for x in race["candidates"]}
    org = (c.get("vote") or {}).get("org_id")
    if org not in cands and cands:
        org = rng.choice(list(cands))
    free_ct = int(mine["free_tokens"] * CT_PER_TOKEN)
    if org and free_ct > 0:
        _try(bot, f"OE commit {free_ct / CT_PER_TOKEN:g} tokens → {cands[org]['name'] or org} ({race['initiative']})",
             lambda: api.post("/wallet/commit", {"mission_id": race["mission_id"],
                                                 "target_ct": free_ct, "org_id": org}))
    elif not cands:
        say(bot["handle"], f"no organization is running in this week's race ({race['mission_id']}) — nominate one")
    elif org:
        # Everyone gets a vote in this week's race, tokens or not (0 tokens = 1 vote).
        _try(bot, f"OE vote → {cands[org]['name'] or org} ({race['initiative']})",
             lambda: api.put("/wallet/org", {"mission_id": race["mission_id"], "org_id": org}))
    # 2026-09-17 (build-seq §1): the other races only where the bot backed the
    # initiative election — never a race it has no stake in.
    chosen = dict(c.get("votes") or {})
    for r in week["organization_races"]:
        if r["is_active_race"] or r["mission_id"] not in set(mine.get("open_races") or []):
            continue
        rc = {x["org_id"]: x for x in r["candidates"]}
        pick = chosen.get(r["mission_id"])
        if pick not in rc:
            if not rc or rng.random() < 0.3:
                continue
            pick = rng.choice(list(rc))
        _try(bot, f"OE vote → {rc[pick]['name'] or pick} ({r['initiative']})",
             lambda r=r, pick=pick: api.put("/wallet/org", {"mission_id": r["mission_id"], "org_id": pick}))
    case = c.get("case")
    if case and case.get("org_id") in cands:
        _try(bot, f"case {case.get('stance', 'for')} '{cands[case['org_id']]['name']}'",
             lambda: api.post("/posts", {
                 "id": "p-" + secrets.token_hex(6), "author_type": "ben", "category": "review",
                 "type": "case", "mission_id": race["mission_id"], "org_id": case["org_id"],
                 "stance": case.get("stance", "for"), "title": case.get("title"), "body": case["body"]}))
    c = dict(c, _me=mine["id"])
    c.setdefault("ratings", _auto_ratings(bot, week, [race["mission_id"]], rng, mine["id"]))
    _reply_and_rate(api, bot, c, week)


def task_budget(api, bot, week, mine, c, rng):
    staked = {s["mission_id"] for s in mine["stakes"]}
    for it in c.get("items", []):
        if it.get("mission_id") not in staked:
            say(bot["handle"], f"skipped budget item in {it.get('mission_id')} (no stake there)")
            continue
        _try(bot, f"budget {it['type']} '{(it.get('title') or '')[:30]}' in {it['mission_id']}",
             lambda: api.post("/posts", {
                 "id": "p-" + secrets.token_hex(6), "author_type": "ben", "category": "budgeting",
                 "type": it["type"], "mission_id": it["mission_id"], "title": it.get("title"),
                 "body": it.get("body") or it.get("title"), "line_items": it.get("line_items")}))
    ups = c.get("upvote")
    if ups is None:
        mine_ids = {p["id"] for p in mine["my_posts"]}
        ups = [p["id"] for mid in staked for p in week["posts_by_mission"].get(mid, [])
               if p["category"] == "budgeting" and p["id"] not in mine_ids and rng.random() < 0.6]
    for pid in ups:
        _try(bot, f"upvoted budget item {pid}", lambda: api.post(f"/posts/{pid}/react", {"value": "helpful"}))


def task_research(api, bot, week, mine, c, rng):
    staked = {s["mission_id"] for s in mine["stakes"]}
    if week["initiative_election"]:
        staked.add(week["initiative_election"]["mission_id"])   # a committed ME stake counts too
    existing = {(p["mission_id"], p["type"]): p["id"] for p in mine["my_posts"] if not p["parent_id"]}
    for rp in c.get("posts", []):
        mid, typ = rp.get("mission_id"), rp.get("type")
        if typ not in ("context", "investigation", "analysis"):
            continue
        pid = existing.get((mid, typ))
        if pid:
            _try(bot, f"updated {typ} in {mid}", lambda: api.put(f"/posts/{pid}",
                                                                {"title": rp.get("title"), "body": rp["body"]}))
        elif mid in staked:
            _try(bot, f"wrote {typ} in {mid}", lambda: api.post("/posts", {
                "id": "p-" + secrets.token_hex(6), "author_type": "ben", "category": "mission_support",
                "type": typ, "mission_id": mid, "title": rp.get("title"), "body": rp["body"]}))
        else:
            say(bot["handle"], f"skipped {typ} in {mid} (no stake there)")


def task_exchange(api, bot, week, mine, c, rng):
    races = {r["mission_id"]: r for r in week["organization_races"]}
    moves, withdraws = c.get("moves"), c.get("withdraw")
    if moves is None:
        moves = []
        movable = [s for s in mine["stakes"] if s["movable"] and s["mission_id"] in races]
        if movable and len(races) > 1 and rng.random() < 0.5:
            src = rng.choice(movable)
            options = [r for r in races.values()
                       if r["mission_id"] != src["mission_id"] and r["candidates"]]
            weights = [bot.get("cause_affinity", {}).get(r["cause_id"], 1) for r in options]
            dst = rng.choices(options, weights=weights)[0] if options else None
            if dst:
                moves.append({"from_mission_id": src["mission_id"], "to_mission_id": dst["mission_id"],
                              "tokens": max(1, int(src["stake_tokens"] * rng.uniform(0.2, 0.5))),
                              "org_id": rng.choice(dst["candidates"])["org_id"]})
    if withdraws is None:
        withdraws = []
        for s in mine["stakes"]:
            open_tokens = s["stake_tokens"] - s["final_tokens"]
            take = round(open_tokens * bot.get("withdraw_appetite", 0.1), 2)
            if take >= 0.01 and rng.random() < 0.5:
                withdraws.append({"mission_id": s["mission_id"], "tokens": take})
    for mv in moves:
        ct = int(round(float(mv["tokens"]) * CT_PER_TOKEN))
        _try(bot, f"moved {mv['tokens']} tokens {mv['from_mission_id']} → {mv['to_mission_id']}",
             lambda: api.post("/wallet/move", {"from_mission_id": mv["from_mission_id"],
                                               "to_mission_id": mv["to_mission_id"],
                                               "ct": ct, "org_id": mv["org_id"]}))
    for wd in withdraws:
        ct = int(round(float(wd["tokens"]) * CT_PER_TOKEN))
        _try(bot, f"withdrew {wd['tokens']} tokens as cash from {wd['mission_id']}",
             lambda: api.post("/wallet/withdraw-stake", {"mission_id": wd["mission_id"], "ct": ct}))


# ---------------------------------------------------------------------------
# Admin tasks — sync the local version to a site, and backfill past races
# ---------------------------------------------------------------------------
# INSTRUCTIONS build-seq §1 (2026-09-17): "Use our bots to add the initiatives
# and organizations from the local version to the website. (If their time is
# passed, just use my gamemaster account)" and "A few of the previous missions on
# the website did not get an organization. Backfill them."
#
# Both are dry runs unless `--dry-run` is left off, and both print their list
# first. Staff credentials come from `--staff-handle` plus the EBX_STAFF_PASSWORD
# environment variable (or a prompt) and are never written anywhere.

# Pilot and seed rows that must never reach the live site.
PILOT_ID = re.compile(r"^(init-\d+|[A-Z][a-z]{2}-\d{4}|org-\d+|ebx-internal|founding-bonus-init|a-[a-z0-9]{5}|pilot.*)$")


def read_local(db_path: Path) -> dict:
    """Initiatives, organizations and candidacies from a local earthbucks.db
    (sqlite, read-only)."""
    import sqlite3
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    q = lambda sql: [dict(r) for r in con.execute(sql)]
    missions = {m["id"]: m for m in q("SELECT id, cause_id, cycle_num, current_phase, winning_tiv_id, winning_org_id FROM missions")}
    tivs = q("SELECT id, title, description, emoji, cause_id, mission_id, status FROM initiatives")
    orgs = {o["id"]: o for o in q("SELECT id, name, description, website_link FROM organizations")}
    cands = q("SELECT mission_id, org_id, mission_statement, status FROM mission_candidacies")
    con.close()
    return {"missions": missions, "initiatives": tivs, "organizations": orgs, "candidacies": cands}


def staff_session(args) -> Api:
    import getpass
    if not args.staff_handle:
        raise SystemExit("this task needs --staff-handle (your gamemaster account)")
    pw = os.environ.get("EBX_STAFF_PASSWORD") or getpass.getpass(f"password for {args.staff_handle}: ")
    api = Api(args.base, dry_run=args.dry_run)
    tok = api._req("POST", "/auth/login", form={"username": args.staff_handle, "password": pw})
    api.token = tok["access_token"]
    return api


def _norm(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def task_sync(args, bots) -> int:
    """Add the local version's initiatives and organizations to the site.

    Open elections: a bot proposes / nominates (the one that cares most about
    the cause). Past windows (the local mission is decided, or the site has no
    open election for it): the staff account adds it instead."""
    local = read_local(args.from_db)
    site = Api(args.base)
    live_tivs = site.get("/initiatives") or []
    live_ids = {t["id"] for t in live_tivs}
    live_titles = {_norm(t["title"]) for t in live_tivs}
    live_orgs = site.get("/organizations") or []
    live_org_names = {_norm(o["name"]) for o in live_orgs}
    live_missions = {m["id"]: m for m in (site.get("/missions") or [])}
    open_me = {}
    for m in sorted(live_missions.values(), key=lambda m: int(m.get("cycle_num") or 0)):
        if not m.get("winning_tiv_id") and m.get("current_phase") in ("pre", "initiative"):
            open_me.setdefault(m["cause_id"], m["id"])
    open_races = {r["mission_id"] for r in (site.get("/wallet/rows") or [])}

    plan = []
    for t in local["initiatives"]:
        if PILOT_ID.match(t["id"]) or t["id"] in live_ids or _norm(t["title"]) in live_titles:
            continue
        lm = local["missions"].get(t["mission_id"] or "") or {}
        passed = bool(lm.get("winning_tiv_id")) or t["cause_id"] not in open_me
        plan.append(("initiative", t, passed))
    for c in local["candidacies"]:
        o = local["organizations"].get(c["org_id"])
        if not o or PILOT_ID.match(o["id"]) or _norm(o["name"]) in live_org_names:
            continue
        passed = c["mission_id"] not in open_races
        plan.append(("organization", dict(o, mission_id=c["mission_id"],
                                          mission_statement=c["mission_statement"]), passed))
        live_org_names.add(_norm(o["name"]))       # one nomination per organization

    print(f"== sync · {args.from_db} → {args.base}" + (" · DRY RUN" if args.dry_run else ""))
    if not plan:
        print("  nothing to add — the site already has every non-pilot initiative and organization")
        return 0
    for kind, row, passed in plan:
        print(f"  {'staff' if passed else 'bot  '} {kind:<12} {row.get('title') or row.get('name')}"
              + (f"  ({row.get('mission_id')})" if row.get("mission_id") else ""))

    staff = None
    if any(p for _, _, p in plan):
        if args.staff_handle:
            staff = staff_session(args)
        else:
            print("  (rows marked staff are skipped — pass --staff-handle to add them)")
    sessions = {}

    def bot_for(cause_id):
        b = max(bots, key=lambda b: b.get("cause_affinity", {}).get(cause_id, 0))
        if b["handle"] not in sessions:
            api = Api(args.base, dry_run=args.dry_run, bot_key=args.bot_key)
            sign_in(api, b)
            sessions[b["handle"]] = api
        return b, sessions[b["handle"]]

    for kind, row, passed in plan:
        if passed and staff is None:
            continue
        try:
            if kind == "initiative":
                body = {"id": row["id"], "title": row["title"][:120], "description": row.get("description"),
                        "emoji": row.get("emoji"), "cause_id": row["cause_id"]}
                if passed:
                    if row.get("mission_id") in live_missions:
                        body["mission_id"] = row["mission_id"]
                    res = staff.post("/initiatives", body)
                    who = args.staff_handle
                else:
                    b, api = bot_for(row["cause_id"])
                    res = api.post("/initiatives", body)
                    who = b["handle"]
            else:
                cause = (live_missions.get(row["mission_id"]) or {}).get("cause_id")
                body = {"name": row["name"], "description": row.get("description"),
                        "website_link": row.get("website_link"), "kind": "nomination",
                        "mission_id": row["mission_id"] if row["mission_id"] in live_missions else None,
                        "mission_statement": row.get("mission_statement"), "force": True}
                if passed:
                    res, who = staff.post("/organizations/register", body), args.staff_handle
                else:
                    b, api = bot_for(cause)
                    res, who = api.post("/organizations/register", body), b["handle"]
            say(who, ("[dry-run] " if isinstance(res, dict) and res.get("dry_run") else "")
                + f"added {kind} '{row.get('title') or row.get('name')}'")
        except ApiError as e:
            say("sync", f"refused — {kind} '{row.get('title') or row.get('name')}': {e}")
    return 0


def task_backfill(args, content) -> int:
    """Elect an organization in every past race that never got one.

    For each race, in order: an organization named in the content file
    (`{"backfill": {"<mission id>": {"name", "website_link", "description",
    "mission_statement"}}}` — nominated first), else the best-placed candidate
    already running. Staff casts the free vote and the race finalizes normally."""
    staff = staff_session(args)
    races = staff.get("/admin/elections/unelected-orgs") or []
    print(f"== backfill · {len(races)} past race(s) with no organization · {args.base}"
          + (" · DRY RUN" if args.dry_run else ""))
    wanted = (content or {}).get("backfill") or {}
    for r in races:
        mid = r["mission_id"]
        pick = wanted.get(mid) or {}
        org_id = pick.get("org_id")
        try:
            if pick.get("name") and not org_id:
                res = staff.post("/organizations/register", {
                    "name": pick["name"], "description": pick.get("description"),
                    "website_link": pick.get("website_link"), "kind": "nomination",
                    "mission_id": mid, "mission_statement": pick.get("mission_statement"), "force": True})
                org_id = ((res or {}).get("org") or {}).get("id")
            if not org_id and not r["candidates"]:
                say("backfill", f"{mid}: no candidate — add one under backfill.{mid} in the content file")
                continue
            res = staff.post(f"/admin/missions/{mid}/backfill-org",
                             {"org_id": org_id, "mission_statement": pick.get("mission_statement")})
            say("backfill", ("[dry-run] " if res and res.get("dry_run") else "")
                + f"{mid}: " + (f"elected {res.get('winning_org_id')}" if res and not res.get("dry_run") else "would elect"))
        except ApiError as e:
            say("backfill", f"refused — {mid}: {e}")
    return 0


RUNNERS = {"initiatives": task_initiatives, "organizations": task_organizations,
           "budget": task_budget, "research": task_research, "exchange": task_exchange}


def run_bot(args, bot, task, week, content, seed):
    api = Api(args.base, dry_run=args.dry_run, bot_key=args.bot_key)
    rng = random.Random(None if seed is None else f"{seed}-{bot['handle']}")
    try:
        me = sign_in(api, bot)
        if me is None:
            return
        mine = read_me(api, me)
        c = (content.get(bot["handle"]) or {}).get(task) or {}
        if args.ai and not c:
            c = ai_content(bot, task, week, mine)
        RUNNERS[task](api, bot, week, mine, c, rng)
    except ApiError as e:
        say(bot["handle"], f"error — {e}")
    except urllib.error.URLError as e:
        say(bot["handle"], f"cannot reach {args.base} — {e.reason}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Earthbux AI benefactor bots")
    ap.add_argument("command", choices=("plan",) + TASKS + ADMIN_TASKS)
    ap.add_argument("--base", default=os.environ.get("EBX_BASE", "http://localhost:8000"),
                    help="the site's origin, e.g. https://earthbux.net (env EBX_BASE)")
    ap.add_argument("--personas", type=Path, default=DEFAULT_PERSONAS)
    ap.add_argument("--accounts", type=Path, default=DEFAULT_ACCOUNTS)
    ap.add_argument("--only", help="comma-separated handles to run (default: every persona)")
    ap.add_argument("--content", type=Path, help="JSON keyed by handle, then task")
    ap.add_argument("--ai", action="store_true", help="each bot drafts its own content with Claude")
    ap.add_argument("--bot-key", default=os.environ.get("EBX_BOT_KEY"),
                    help="the server's EBX_BOT_KEY, so new bot accounts are marked is_test")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--from-db", type=Path, default=HERE.parent.parent / "backend" / "earthbucks.db",
                    help="sync: the local database to copy initiatives and organizations from")
    ap.add_argument("--staff-handle", default=os.environ.get("EBX_STAFF_HANDLE"),
                    help="sync/backfill: the staff (gamemaster) login; password from EBX_STAFF_PASSWORD or a prompt")
    ap.add_argument("--seed", default=None)
    args = ap.parse_args(argv)

    bots = load_bots(args.personas, args.accounts)
    if args.only:
        keep = {h.strip().lower() for h in args.only.split(",")}
        bots = [b for b in bots if b["handle"].lower() in keep]

    try:
        week = read_week(Api(args.base))
    except urllib.error.URLError as e:
        print(f"cannot reach {args.base} — {e.reason}")
        return 2

    if args.command == "plan":
        out = {"week": week, "bots": {}}
        for b in bots:
            api = Api(args.base, dry_run=True, bot_key=args.bot_key)
            try:
                me = sign_in(api, b)
                out["bots"][b["handle"]] = ({"personality": b["personality"], **read_me(api, me)}
                                            if me else {"personality": b["personality"],
                                                        "note": "account not created yet"})
            except ApiError as e:
                out["bots"][b["handle"]] = {"error": str(e)}
        print(json.dumps(out, indent=2))
        return 0

    content = json.loads(args.content.read_text()) if args.content else {}
    if args.command == "sync":
        return task_sync(args, bots)
    if args.command == "backfill":
        return task_backfill(args, content)
    print(f"== {args.command} · {len(bots)} bots at once · {args.base}"
          + (" · DRY RUN" if args.dry_run else ""))
    with ThreadPoolExecutor(max_workers=max(1, len(bots))) as pool:
        futures = {pool.submit(run_bot, args, b, args.command, week, content, args.seed): b
                   for b in bots}
    for f, b in futures.items():
        exc = f.exception()
        if exc is not None:
            say(b["handle"], f"crashed — {exc!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
