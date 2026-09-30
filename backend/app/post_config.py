"""Post taxonomy & rules — the single source of truth for the discussion model.

P3 · Posting (2026-09-29; INSTRUCTIONS › P3, D8 + D19–D21). One stable post
object, three kinds of post:

    CATEGORY (stored)   LABEL      TYPE (stored)   LABEL           TARGET
    ─────────────────────────────────────────────────────────────────────────
    general             General    general         Post            anything, or nothing
    mission_support     Research   context         Background      a cause
                                   investigation   Investigation   an organization
                                   analysis        Analysis        a mission
    budgeting           Budget     service         Service         an initiative
                                   supply          Supply          an initiative
                                   support         Support         an initiative

The stored keys are the old ones (`context` is Background since 2026-09-24,
`investigation` was "Vetting" 2026-09-25 → "Investigation" in the P3 model);
renaming a stored key would orphan every row already written.

A GENERAL post's subtype is a TAG (Opinion · Idea · Experience · Justification ·
Prediction · Question · Observation · Criticism · Proposal · Update · Response),
and so are Case and Evaluation, which were the Review lane until P3 (D8: "Case
and evaluation will now be optional tags on the all-purpose posts … The review
lane is gone."). Tags are strings; an ENTITY tag carries a prefix —
`cause:<id>` · `tiv:<id>` · `org:<id>` · `mission:<id>` · `post:<id>` — and a
citation is a tag too.

Everything the composer, the How-to section (about.html#posting) and each
mission's outline say about a type is its `guide` here, beside the rule it
describes, so the words cannot drift from the rules.

IMPORTANT — vote semantics are single-implementation:
    The backend keeps ONE reaction enum (helpful · neutral · harmful) and ONE
    `react_to_post` path for every post. A post type does NOT get its own vote
    code — it only declares which reactions the *frontend* exposes, how they are
    *labelled*, and what that kind of vote is CALLED (`VOTE_NAMES`).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Canonical reaction enum — unchanged backend storage (PostVote.value).
# A type exposes a SUBSET of these, optionally relabelled for the UI.
# ---------------------------------------------------------------------------
REACTIONS = ("helpful", "neutral", "harmful")

# Reward slices (fractions of the 32nds pool split). The research pot and how
# it splits is P5 (D22); this is the size of one slice as the model stands.
REWARD_FRACTION = 1 / 32

# ---------------------------------------------------------------------------
# The three names a vote can have (inbox 2026-09-29: "Votes each need distinct
# names — Research, Analysis, and Election"). An ELECTION vote is a ballot —
# cause, initiative, organization; it is not a post reaction and never passes
# through `react_to_post`. The other two are reactions on research posts.
# Everything else (general posts, budget items) is a plain upvote.
# ---------------------------------------------------------------------------
VOTE_NAMES = {
    "election": "Election vote",
    "research": "Research vote",
    "analysis": "Analysis vote",
    "upvote": "Upvote",
}
VOTE_MEANING = {
    "election": "Your ballot in a cause, initiative or organization election — it moves money.",
    "research": "Your vote on a Background or an Investigation — it decides which one leads, and how the research prize splits.",
    "analysis": "Your vote on an Analysis — the most-voted Analysis on budget day is elected.",
    "upvote": "An upvote on a general post or a budget item — it ranks it, nothing more.",
}

# Targets a post can point at. `none` is a general post about nothing on the
# platform (a news story unrelated to any mission).
TARGET_KINDS = ("cause", "initiative", "organization", "mission", "post", "budget", "none")


@dataclass(frozen=True)
class Guide:
    """The user-facing guide for one type — what the composer shows beside it,
    what the How-to card says, and what a mission's outline lists."""

    purpose: str          # what it is for
    points_at: str        # what it points at
    limit: str            # the per-person limit, in words
    earns: str            # what it can earn
    steps: tuple[str, ...]


@dataclass(frozen=True)
class PostType:
    """A subcategory — the leaf a benefactor actually posts under."""

    key: str                          # stored on Post.type
    label: str                        # UI label
    category: str                     # parent supercategory key
    # How many of THIS type a benefactor may hold, and per WHAT (`limit_scope`):
    #   "none"         — unlimited.
    #   "one"          — exactly one per scope, edited forward (new versions).
    #   "one_rolling"  — one OPEN at a time per scope; a new slot opens when the
    #                    current one RESOLVES (budget: resolves = paid out).
    limit_rule: str
    reactions: tuple[str, ...]
    reaction_labels: dict[str, str] = field(default_factory=dict)
    # cause | organization | mission | initiative | none — what one-per counts.
    limit_scope: str = "none"
    # What it must (or may) point at.
    target: str = "none"              # cause|organization|mission|initiative|any
    target_required: bool = False
    # Which kind of vote a reaction on it is (VOTE_NAMES).
    vote_kind: str = "upvote"
    # Is this type judged for a cash reward? When it wins, when it pays.
    rewarded: bool = False
    reward_note: str = ""
    # Winning a reward still requires membership (2026-07-19); POSTING does
    # not since P3 ("All posting gates removed").
    win_requires_membership: bool = False
    # Versioning (D21): every edit is a new version; the version an election or
    # an Analysis used is locked for good. "full" — any field; "partial" — the
    # `locked_fields` freeze once set.
    edit_policy: str = "full"
    locked_fields: tuple[str, ...] = ()
    # The moment a mission fixes this type's version: me_close (T), oe_close
    # (T+8), budget_day (T+15), or None (never pinned by an election).
    pins_at: Optional[str] = None
    resolves_when: Optional[str] = None
    guide: Optional[Guide] = None
    notes: str = ""


@dataclass(frozen=True)
class PostCategory:
    """A supercategory — the umbrella grouping shown in the composer."""

    key: str
    label: str
    type_keys: tuple[str, ...]
    author: str          # who may author: "ben" | "org" | "staff"
    notes: str = ""


# ===========================================================================
# GENERAL — the all-purpose post. Unlimited, target optional (but suggested),
# subtype by tag. Upvote only.
# ===========================================================================
GENERAL_TAGS = (
    "opinion", "idea", "experience", "justification", "prediction", "question",
    "observation", "criticism", "proposal", "update", "response",
    # the Review lane's two types, folded in as tags (D8)
    "case", "evaluation",
)
GENERAL_TAG_LABELS = {t: t.capitalize() for t in GENERAL_TAGS}
GENERAL_TAG_HINTS = {
    "opinion": "What you think, and why.",
    "idea": "Something the mission could try.",
    "experience": "What you saw or did, first-hand.",
    "justification": "Why this initiative or organization should win — the default when you nominate one.",
    "prediction": "What you expect to happen, so it can be checked later.",
    "question": "Something you want answered.",
    "observation": "A fact you noticed, without a verdict.",
    "criticism": "What is wrong, and what would fix it.",
    "proposal": "A concrete change, stated so people can vote on it.",
    "update": "News on something already posted.",
    "response": "A reply lifted into its own post — 'in response to' another post.",
    "case": "The case for (or against) an initiative or an organization.",
    "evaluation": "How the organization is doing on the mission.",
}
# The tag a nomination defaults to (P3 › Nominations).
NOMINATION_DEFAULT_TAG = "justification"

_GENERAL_TYPES = (
    PostType(
        key="general", label="Post", category="general",
        limit_rule="none", reactions=("helpful",),
        reaction_labels={"helpful": "Upvote"},
        target="any", target_required=False, vote_kind="upvote",
        guide=Guide(
            purpose="Anything relevant to your thoughts, interests, experiences, questions, ideas or reactions — under the platform's general rules.",
            points_at="Optional, but suggested: a cause, an initiative, an organization, a mission, a budget item or another post. Or nothing at all — a news story unrelated to any mission.",
            limit="No limit.",
            earns="Nothing but upvotes — it ranks the post, it moves no money.",
            steps=("Pick what it is about, if anything.",
                   "Tag what kind of post it is — Opinion, Question, Case …",
                   "Write it, cite what you lean on, and post."),
        ),
    ),
)

# ===========================================================================
# RESEARCH — Background (cause) · Investigation (organization) · Analysis
# (mission). One each per scope, versioned, rewarded (the split is P5, D22).
# ===========================================================================
_RESEARCH_TYPES = (
    PostType(
        key="context", label="Background", category="mission_support",
        limit_rule="one", limit_scope="cause", reactions=REACTIONS,
        target="cause", target_required=True, vote_kind="research",
        rewarded=True, reward_note="paid when an Analysis that cites it is elected (D22, P5)",
        win_requires_membership=True, pins_at="me_close", resolves_when="budget_day",
        guide=Guide(
            purpose="Teach voters about the cause and the news around it, so the initiative election is an informed one.",
            points_at="A cause. Tag as many of its initiatives as it covers, or none — it previews under each one you tag.",
            limit="One per person per cause. It lives: edit it forward, never start a second.",
            earns="The most-voted Background when the initiative election closes leads — every Analysis of that mission cites it — and cited Backgrounds share a third of the research prize (P5).",
            steps=("Pick the cause, and tag the initiatives it covers.",
                   "Write what a voter needs to know; cite your sources.",
                   "Post — it is electable in this week's initiative election at once. Edits after election day carry into the cause's next mission; the version standing at the close stays with this one."),
        ),
        notes="Stored key `context` (renamed Background 2026-09-24).",
    ),
    PostType(
        key="investigation", label="Investigation", category="mission_support",
        limit_rule="one", limit_scope="organization", reactions=REACTIONS,
        target="organization", target_required=True, vote_kind="research",
        rewarded=True, reward_note="paid when an Analysis that cites it is elected (D22, P5)",
        win_requires_membership=True, pins_at="oe_close", resolves_when="budget_day",
        guide=Guide(
            purpose="Dig into an organization — its leadership, its record, its proposal, its credibility.",
            points_at="An organization, whether or not it is running. You may tag causes and initiatives.",
            limit="One per person per organization, edited forward.",
            earns="The most-voted Investigation on any of a mission's candidate organizations when its organization election closes leads that mission's Analyses — a critical one on an organization that lost can lead — and cited Investigations share a third of the research prize (P5).",
            steps=("Name the organization.",
                   "Say what you found and where you found it.",
                   "Post — the version standing when an organization election it is in closes stays with that mission."),
        ),
        notes="Stored key `investigation` (\"Vetting\" 2026-09-25 → \"Investigation\" in the P3 model).",
    ),
    PostType(
        key="analysis", label="Analysis", category="mission_support",
        limit_rule="one", limit_scope="mission", reactions=REACTIONS,
        target="mission", target_required=True, vote_kind="analysis",
        rewarded=True, reward_note="elected on budget day; pays 1/3 to its author (D22, P5)",
        win_requires_membership=True, pins_at="budget_day", resolves_when="budget_day",
        guide=Guide(
            purpose="Put the initiative and the organization together into one assessment of the mission — built from the research before it.",
            points_at="A mission. It opens when the organization election closes (T+8) and is elected on budget day (T+15).",
            limit="One per person per mission.",
            earns="The Analysis elected on budget day pays a third of the research prize to its author, and a third each to the Backgrounds and Investigations it cites (P5).",
            steps=("The leading Background and the leading Investigation are attached for you.",
                   "Cite up to 12 Backgrounds and 12 Investigations in all — from any mission, of any age — and any budget items.",
                   "Write the assessment and post it before budget day."),
        ),
    ),
)

# ===========================================================================
# BUDGET — service / supply / support → an initiative, any time. One OPEN per
# type per person per initiative (rolling: a slot frees when it is paid out).
# Upvote-only (a downvote would only hurt mission productivity).
# ===========================================================================
_BUDGET_STEPS_TAIL = "Post — any time, before the initiative is elected or after budget day. It carries into the mission when the initiative wins."
_BUDGETING_TYPES = (
    PostType(
        key="service", label="Service", category="budgeting",
        limit_rule="one_rolling", limit_scope="initiative", reactions=("helpful",),
        reaction_labels={"helpful": "Upvote"},
        target="initiative", target_required=True, vote_kind="upvote",
        edit_policy="partial", locked_fields=("committed_cost",),
        resolves_when="paid_out",
        guide=Guide(
            purpose="Labor the mission needs — something we can send people to do.",
            points_at="An initiative.",
            limit="One open Service per person per initiative; a new one opens when yours is paid out.",
            earns="Upvotes rank it into the budget. Nothing is paid for suggesting it.",
            steps=("Name the job.", "Give the hourly rate and the days it takes.", _BUDGET_STEPS_TAIL),
        ),
    ),
    PostType(
        key="supply", label="Supply", category="budgeting",
        limit_rule="one_rolling", limit_scope="initiative", reactions=("helpful",),
        reaction_labels={"helpful": "Upvote"},
        target="initiative", target_required=True, vote_kind="upvote",
        edit_policy="partial", locked_fields=("committed_cost",),
        resolves_when="paid_out",
        guide=Guide(
            purpose="What the people doing the work need — commodities, equipment.",
            points_at="An initiative.",
            limit="One open Supply per person per initiative; a new one opens when yours is paid out.",
            earns="Upvotes rank it into the budget. Nothing is paid for suggesting it.",
            steps=("Name the item and the supplier.", "Give what it costs.", _BUDGET_STEPS_TAIL),
        ),
    ),
    PostType(
        key="support", label="Support", category="budgeting",
        limit_rule="one_rolling", limit_scope="initiative", reactions=("helpful",),
        reaction_labels={"helpful": "Upvote"},
        target="initiative", target_required=True, vote_kind="upvote",
        edit_policy="partial", locked_fields=("committed_cost",),
        resolves_when="paid_out",
        guide=Guide(
            purpose="A connection — an approval from a government or community, professional or legal help. No cost line, on purpose.",
            points_at="An initiative.",
            limit="One open Support per person per initiative; a new one opens when yours resolves.",
            earns="Upvotes rank it into the budget. Nothing is paid for suggesting it.",
            steps=("Say what is needed and from whom.", "Say why the mission cannot run without it.", _BUDGET_STEPS_TAIL),
        ),
    ),
)

# ===========================================================================
# LEGACY — the Review lane (case · evaluation), retired by P3 (D8). Readable,
# never created: a request for one is rewritten as a general post carrying
# the tag (`normalize_legacy`), and the migration converted the stored rows.
# ===========================================================================
_REVIEW_REACTIONS = ("helpful", "harmful")
_REVIEW_LABELS = {"helpful": "Fair", "harmful": "Unfair"}
LEGACY_TYPES: dict[str, PostType] = {
    t.key: t for t in (
        PostType(key="case", label="Case", category="review", limit_rule="none",
                 reactions=_REVIEW_REACTIONS, reaction_labels=_REVIEW_LABELS),
        PostType(key="evaluation", label="Evaluation", category="review", limit_rule="none",
                 reactions=_REVIEW_REACTIONS, reaction_labels=_REVIEW_LABELS),
    )
}

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
TYPES: dict[str, PostType] = {
    t.key: t for t in (*_GENERAL_TYPES, *_RESEARCH_TYPES, *_BUDGETING_TYPES)
}

CATEGORIES: dict[str, PostCategory] = {
    "general": PostCategory(
        "general", "General", tuple(t.key for t in _GENERAL_TYPES), "ben",
        notes="The all-purpose post; subtypes are tags; unlimited; target optional.",
    ),
    "mission_support": PostCategory(
        "mission_support", "Research",
        tuple(t.key for t in _RESEARCH_TYPES), "ben",
        notes="Background · Investigation · Analysis; one each per scope; versioned; rewarded.",
    ),
    "budgeting": PostCategory(
        "budgeting", "Budget", tuple(t.key for t in _BUDGETING_TYPES), "ben",
        notes="Service · Supply · Support → an initiative; rolling slots; upvote-only.",
    ),
}

# Org- and staff-authored posts are unlimited and live outside this table.
STAFF_OR_ORG_CATEGORIES = ("org_update", "mission_update", "testimonial",
                           "editorial", "headline")

REWARDED_TYPES = tuple(k for k, t in TYPES.items() if t.rewarded)

BENEFACTOR_CATEGORIES = tuple(CATEGORIES)
# P3 (2026-09-29): "All posting gates removed — everyone can post, everyone can
# reply." Nothing requires membership to POST; winning a research reward still
# does (`win_requires_membership`). Kept as names so a caller that asks gets
# the honest answer.
POST_REQUIRES_MEMBERSHIP: frozenset = frozenset()
OPEN_POSTING_CATEGORIES = frozenset(BENEFACTOR_CATEGORIES)

# The research types that must name the organization they are about.
TYPES_REQUIRING_ORG = frozenset({"investigation"})

# The Analysis composer's reference rules (P3 › The Analysis composer).
ANALYSIS_MAX_BACKGROUNDS = 12
ANALYSIS_MAX_INVESTIGATIONS = 12

# How the three research types are stored — handy for callers.
BACKGROUND, INVESTIGATION, ANALYSIS = "context", "investigation", "analysis"
BUDGET_TYPES = tuple(t.key for t in _BUDGETING_TYPES)

# The words a composer link may use for a type (post.html?type=…).
TYPE_ALIASES = {
    "background": "context", "context": "context",
    "investigation": "investigation", "vetting": "investigation",
    "analysis": "analysis",
    "service": "service", "supply": "supply", "support": "support",
    "general": "general", "post": "general",
    **{t: "general" for t in GENERAL_TAGS},
}


def resolve_type(word: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """(type key, default tag) for a composer link's `type=` word."""
    if not word:
        return None, None
    w = str(word).strip().lower()
    key = TYPE_ALIASES.get(w)
    return key, (w if w in GENERAL_TAGS else None)


def normalize_legacy(category: Optional[str], type_key: Optional[str]) -> tuple[str, str, Optional[str]]:
    """A request in the retired Review lane becomes a general post with a tag.

    Returns (category, type, tag-or-None). Anything else passes through."""
    if category == "review" or (type_key in LEGACY_TYPES):
        return "general", "general", (type_key if type_key in LEGACY_TYPES else None)
    if category == "general" and not type_key:
        return "general", "general", None
    return category or "general", type_key or "", None


def clean_tags(tags) -> list[str]:
    """Normalise a tag list: strings, lower-case words, entity tags kept as
    `kind:id`, no duplicates, at most 24."""
    out: list[str] = []
    for t in (tags or []):
        if not isinstance(t, str):
            continue
        t = t.strip()
        if not t:
            continue
        if ":" in t:
            kind, _, ident = t.partition(":")
            kind = kind.strip().lower()
            if kind not in ("cause", "tiv", "org", "mission", "post", "budget") or not ident.strip():
                continue
            t = kind + ":" + ident.strip()
        else:
            t = t.lower()[:32]
        if t not in out:
            out.append(t)
    return out[:24]


def guide_payload() -> dict:
    """The whole taxonomy as the composer, the How-to and the mission outline
    read it (GET /posts/guide)."""
    def t_out(t: PostType) -> dict:
        g = t.guide
        return {
            "key": t.key, "label": t.label, "category": t.category,
            "category_label": CATEGORIES[t.category].label,
            "target": t.target, "target_required": t.target_required,
            "limit_rule": t.limit_rule, "limit_scope": t.limit_scope,
            "reactions": [{"value": r, "label": t.reaction_labels.get(r, r.capitalize())}
                          for r in t.reactions],
            "vote_kind": t.vote_kind, "vote_name": VOTE_NAMES[t.vote_kind],
            "rewarded": t.rewarded, "pins_at": t.pins_at,
            "guide": None if g is None else {
                "purpose": g.purpose, "points_at": g.points_at, "limit": g.limit,
                "earns": g.earns, "steps": list(g.steps)},
        }
    return {
        "categories": [{"key": c.key, "label": c.label, "types": list(c.type_keys)}
                       for c in CATEGORIES.values()],
        "types": [t_out(t) for t in TYPES.values()],
        "general_tags": [{"key": k, "label": GENERAL_TAG_LABELS[k], "hint": GENERAL_TAG_HINTS[k]}
                         for k in GENERAL_TAGS],
        "votes": [{"key": k, "name": VOTE_NAMES[k], "meaning": VOTE_MEANING[k]} for k in VOTE_NAMES],
        "analysis": {"max_backgrounds": ANALYSIS_MAX_BACKGROUNDS,
                     "max_investigations": ANALYSIS_MAX_INVESTIGATIONS},
        "target_kinds": list(TARGET_KINDS),
    }


# ---------------------------------------------------------------------------
# §2a — budgeting estimates. A service/supply/support post is a costed
# suggestion; without both numbers the budget builder has nothing to rank.
# ---------------------------------------------------------------------------
ESTIMATE_CATEGORIES = ("budgeting",)
ESTIMATE_FIELDS = ("est_setup_days", "est_cost_usd")


def requires_estimates(category_key: str) -> bool:
    """True if a post in this category must carry setup-time + cost estimates."""
    return category_key in ESTIMATE_CATEGORIES


# ---------------------------------------------------------------------------
# §1 (2026-08-12) — THE COSTED LIST. A budgeting suggestion is a list of rows,
# and the row's shape is the kind of thing being asked for:
#
#   service  🛠 Labor required        job    · hourly_rate · days_needed
#   supply   📦 Commodities required  item   · supplier    · cost
#   support  🤝 Connections required  item
#
# Support carries no money on purpose: it is a CONNECTION — an approval from a
# government or community, professional help, legal help in a conflict — and
# pricing it would invite a bill for something nobody is buying.
# ---------------------------------------------------------------------------
LINE_ITEM_FIELDS: dict[str, tuple[str, ...]] = {
    "service": ("job", "hourly_rate", "days_needed"),
    "supply": ("item", "supplier", "cost"),
    "support": ("item",),
}
LINE_ITEM_LABEL = {
    "service": ("🛠", "Labor required"),
    "supply": ("📦", "Commodities required"),
    "support": ("🤝", "Connections required"),
}
# A working day, for turning an hourly rate into a cost. Named rather than
# inlined because it is an assumption, not a fact about the world.
HOURS_PER_DAY = 8.0


def invalid_line_items(type_key: str | None, rows) -> str:
    """'' if every row is complete for this type, else why the first bad one is."""
    if not rows:
        return ""
    fields = LINE_ITEM_FIELDS.get(type_key or "")
    if fields is None:
        return f"'{type_key}' does not take line items"
    for i, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            return f"row {i} is not a row"
        for f in fields:
            v = row.get(f)
            if v is None or (isinstance(v, str) and not v.strip()):
                return f"row {i} is missing {f}"
            if f in ("hourly_rate", "days_needed", "cost"):
                try:
                    if float(v) < 0:
                        return f"row {i} has a negative {f}"
                except (TypeError, ValueError):
                    return f"row {i} has a non-numeric {f}"
    return ""


def estimates_from_line_items(type_key: str | None, rows) -> dict[str, float]:
    """Derive (est_setup_days, est_cost_usd) from a costed list.

    service — days = Σ days_needed, cost = Σ rate × days × HOURS_PER_DAY
    supply  — cost = Σ cost, days = 0 (a purchase has no setup of its own)
    support — both 0: a connection costs nothing to ask for.
    Returns only the fields it can actually compute.
    """
    if not rows or type_key not in LINE_ITEM_FIELDS:
        return {}
    num = lambda v: float(v or 0)
    try:
        if type_key == "service":
            days = sum(num(r.get("days_needed")) for r in rows)
            cost = sum(num(r.get("hourly_rate")) * num(r.get("days_needed")) * HOURS_PER_DAY
                       for r in rows)
            return {"est_setup_days": days, "est_cost_usd": cost}
        if type_key == "supply":
            return {"est_setup_days": 0.0, "est_cost_usd": sum(num(r.get("cost")) for r in rows)}
        return {"est_setup_days": 0.0, "est_cost_usd": 0.0}
    except (TypeError, ValueError, AttributeError):
        return {}


# ===========================================================================
# POST-SUPPORT LAYER — the first layer of the mission annulus.
#
# Philanthropies are sent a weekly digest of what the community wrote about
# them, so every thread that carries an ORGANIZATION tag is flagged first:
#
#   green  — Useful.
#   orange — CRITICAL, but helpful.
#   red    — spam, scams, or unsupported slander. We apologise for these and
#            tell the organization we are working to keep them off the platform.
#
# Only org-tagged post types are rated — investigation names an organization,
# and so did the retired case / evaluation rows (now general posts carrying the
# tag). Everything else is unrated (`None` on the wire, stored green so the
# column can stay NOT NULL).
#
# `classify_flag` is deliberately a STUB: it rates everything green. The real
# filter is a content classifier and is not built. Staff override through
# POST /posts/{id}/flag, which is how a red ever appears today.
# ===========================================================================
FLAGS = ("green", "orange", "red")
FLAG_MEANING = {
    "green": "Useful.",
    "orange": "Critical, but helpful.",
    "red": "Spam, scams, or unsupported slander — we are working to keep it off the platform.",
}
# The org-tagged types: these are the posts that name an organization, and the
# only ones the post-support layer rates. (structure.md, mission.html annulus.)
ORG_TAGGED_TYPES = ("case", "investigation", "evaluation")


def is_org_tagged(type_key: Optional[str]) -> bool:
    """True if this post type carries an organization tag, i.e. it is rated."""
    return type_key in ORG_TAGGED_TYPES


def is_flag(value: str) -> bool:
    return value in FLAGS


def classify_flag(type_key: Optional[str] = None, body: str = "",
                  title: Optional[str] = None) -> str:
    """Rate a post for the post-support layer.

    STUB — rates everything **green**. Kept as the single call site so the real
    classifier drops in here and every surface picks it up at once.
    """
    return "green"


def category_requires_membership(category_key: str) -> bool:
    """True if authoring in this category requires mission membership.
    Nothing does since P3 — kept so a caller that asks gets the honest answer."""
    return category_key in POST_REQUIRES_MEMBERSHIP


def is_benefactor_type(type_key: str) -> bool:
    """True if `type_key` is one of the benefactor types — current or legacy."""
    return type_key in TYPES or type_key in LEGACY_TYPES


def _type(type_key: str) -> PostType:
    return TYPES.get(type_key) or LEGACY_TYPES[type_key]


# ---------------------------------------------------------------------------
# Helpers (what enforcement calls)
# ---------------------------------------------------------------------------
def allowed_reactions(type_key: str) -> tuple[str, ...]:
    """Reactions the frontend should show for a post type."""
    return _type(type_key).reactions


def reaction_label(type_key: str, reaction: str) -> str:
    return _type(type_key).reaction_labels.get(reaction, reaction.capitalize())


def is_reaction_allowed(type_key: str, reaction: str) -> bool:
    return reaction in _type(type_key).reactions


def vote_name(type_key: Optional[str]) -> str:
    """What a reaction on this type is called (VOTE_NAMES)."""
    t = TYPES.get(type_key or "")
    return VOTE_NAMES[t.vote_kind if t else "upvote"]


def category_of(type_key: str) -> str:
    return _type(type_key).category


def is_rewarded(type_key: str) -> bool:
    return TYPES.get(type_key) is not None and TYPES[type_key].rewarded


def win_requires_membership(type_key: str) -> bool:
    return TYPES.get(type_key) is not None and TYPES[type_key].win_requires_membership


def _validate() -> None:
    """Fail fast on an internally inconsistent table (run at import)."""
    for key, t in {**TYPES, **LEGACY_TYPES}.items():
        assert t.key == key, f"type key mismatch: {key} vs {t.key}"
        assert set(t.reactions) <= set(REACTIONS), f"{key}: bad reactions {t.reactions}"
        assert t.reactions, f"{key}: must expose at least one reaction"
        assert set(t.reaction_labels) <= set(t.reactions), f"{key}: label for hidden reaction"
        assert t.limit_rule in ("none", "one", "one_rolling"), f"{key}: bad limit_rule {t.limit_rule}"
        assert t.edit_policy in ("full", "partial", "none"), f"{key}: bad edit_policy"
        if t.edit_policy == "partial":
            assert t.locked_fields, f"{key}: partial edit needs locked_fields"
    for key, t in TYPES.items():
        assert t.category in CATEGORIES, f"{key}: unknown category {t.category}"
        assert t.guide is not None, f"{key}: every creatable type carries its guide"
        assert t.vote_kind in VOTE_NAMES, f"{key}: unknown vote kind"
        assert t.limit_scope in ("none", "cause", "organization", "mission", "initiative"), key
        assert (t.limit_rule == "none") == (t.limit_scope == "none"), f"{key}: limit rule/scope disagree"
        assert t.pins_at in (None, "me_close", "oe_close", "budget_day"), key
    for key, c in CATEGORIES.items():
        assert c.key == key
        for tk in c.type_keys:
            assert tk in TYPES and TYPES[tk].category == key, f"{key}: bad member {tk}"
    assert REWARDED_TYPES == ("context", "investigation", "analysis"), REWARDED_TYPES
    for tk in ORG_TAGGED_TYPES:
        assert tk in TYPES or tk in LEGACY_TYPES, f"org-tagged type {tk} is not in the taxonomy"
    assert classify_flag() in FLAGS
    assert set(FLAG_MEANING) == set(FLAGS)
    assert set(TYPE_ALIASES.values()) <= set(TYPES)


_validate()
