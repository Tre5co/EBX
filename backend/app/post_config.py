"""Post taxonomy & rules — the single source of truth for the discussion model.

Two-tier taxonomy (settled 2026-07-19):

    CATEGORY (supercategory)  →  TYPE (subcategory)
    ─────────────────────────────────────────────────────────────
    budgeting        →  service · supply · support
    mission_support  →  context · investigation · analysis
    review           →  case · evaluation

Everything that used to be scattered across `create_post`, `react_to_post`,
the reward split in `distribute_*`, and the frontend vote widgets is described
declaratively here instead. Backend enforcement and the frontend both read
from this table so the rules live in exactly one place.

IMPORTANT — vote semantics are single-implementation:
    The backend keeps ONE reaction enum (helpful · neutral · harmful) and ONE
    `react_to_post` path for every post. A post type does NOT get its own vote
    code — it only declares which reactions the *frontend* exposes and how they
    are *labelled*. "Upvote-only", "fair/unfair", and "up/down/neutral" are all
    the same three columns with different subsets shown.

This module is inert: importing it changes no behaviour. Wiring it into
`create_post` / `react_to_post` / the payout split is staged in
docs/INSTRUCTIONS.md. Until then it is the spec that those changes implement.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Canonical reaction enum — unchanged backend storage (PostVote.value).
# A type exposes a SUBSET of these, optionally relabelled for the UI.
# ---------------------------------------------------------------------------
REACTIONS = ("helpful", "neutral", "harmful")

# Reward slices (fractions of the 32nds pool split). The three MISSION_SUPPORT
# types are the rewarded post types now — one reward each, replacing the old
# best_case / context_or_analysis / comments slices.
REWARD_FRACTION = 1 / 32


@dataclass(frozen=True)
class PostType:
    """A subcategory — the leaf a benefactor actually posts under."""

    key: str                          # stored on Post.type
    label: str                        # UI label
    category: str                     # parent supercategory key
    # How many of THIS type a benefactor may hold in one mission.
    #   "one"          — exactly one, editable forever.
    #   "one_rolling"  — one open at a time; a new slot opens only when the
    #                    current one RESOLVES (budgeting: resolves = paid out).
    limit_rule: str
    # Which reactions the frontend shows. Backend still accepts only these
    # three values total; the rest are simply never offered for this type and
    # their stored counts stay 0.
    reactions: tuple[str, ...]
    # Optional UI relabelling, e.g. review shows helpful->"Fair", harmful->"Unfair".
    reaction_labels: dict[str, str] = field(default_factory=dict)
    # Is this type judged for a cash reward? When it wins, when it pays.
    rewarded: bool = False
    reward_note: str = ""
    # Membership rule (settled 2026-07-19): you must be a member — or have
    # *agreed to become one* by committing a phase-1 stake — to POST any
    # benefactor category at all. Winning is therefore a subset of posting, so
    # every author of a rewarded post is already a member. See
    # `crud.can_post_mission`. Kept per-type for documentation.
    win_requires_membership: bool = False
    # Edit policy. "full" — any field, versioned. "partial" — versioned, but the
    # fields in `locked_fields` freeze once set. Every edit is kept as history
    # (edits are UPDATES: prior versions remain viewable).
    edit_policy: str = "full"
    locked_fields: tuple[str, ...] = ()
    # For rolling/rewarded types: the event that closes the slot / picks a winner.
    resolves_when: Optional[str] = None
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
# BUDGETING — service / supply / support. One post PER TYPE (up to 3), each
# on a rolling slot. Upvote-only: neutral & harmful are never shown and their
# counts stay 0 (a downvote would only hurt mission productivity). A budget
# item is never revoked — its slot frees only when the money is actually paid
# out. Some fields (the committed cost line, once adopted) cannot be edited.
# ===========================================================================
#
# §2a (2026-08-08): a budgeting post is a SUGGESTION the mission may adopt, so
# it is not a suggestion until it is costed. Every one of the three types
# requires two estimates — `est_setup_days` (how long to stand it up) and
# `est_cost_usd` (what it costs) — enforced in `crud.create_post`.
# ===========================================================================
_BUDGETING_TYPES = (
    PostType(
        key="service", label="Service", category="budgeting",
        limit_rule="one_rolling", reactions=("helpful",),
        edit_policy="partial", locked_fields=("committed_cost",),
        resolves_when="paid_out",
        notes="Something we can send people to DO. Carried by orgs.",
    ),
    PostType(
        key="supply", label="Supply", category="budgeting",
        limit_rule="one_rolling", reactions=("helpful",),
        edit_policy="partial", locked_fields=("committed_cost",),
        resolves_when="paid_out",
        notes="What those people need to do it. Carried by bens.",
    ),
    PostType(
        key="support", label="Support", category="budgeting",
        limit_rule="one_rolling", reactions=("helpful",),
        edit_policy="partial", locked_fields=("committed_cost",),
        resolves_when="paid_out",
        notes="How we ensure the issue is resolved honestly. Carried by ebx.",
    ),
)

# ===========================================================================
# MISSION_SUPPORT — context / investigation / analysis. One post EACH. Full
# up/neutral/harmful reactions (incentivises the best possible support; neutral
# signals "read, no strong feeling" — engagement without commitment). These are
# the three REWARDED post types now, one reward each. Rewards are tax-deductible
# for members, which is why winning requires membership.
# ===========================================================================
_MISSION_SUPPORT_TYPES = (
    PostType(
        key="context", label="Context", category="mission_support",
        limit_rule="one", reactions=REACTIONS,
        rewarded=True, reward_note="reward released WITH THE ADVANCES",
        win_requires_membership=True, resolves_when="advances_release",
        notes="Background teaching voters about the initiatives and related news.",
    ),
    PostType(
        key="investigation", label="Investigation", category="mission_support",
        limit_rule="one", reactions=REACTIONS,
        rewarded=True, reward_note="winner decided at the END OF PHASE 3",
        win_requires_membership=True, resolves_when="phase3_end",
        notes="Digging into the org actually running the mission — leadership, "
              "proposal quality, credibility.",
    ),
    PostType(
        key="analysis", label="Analysis", category="mission_support",
        limit_rule="one", reactions=REACTIONS,
        rewarded=True, reward_note="winner decided LATER (post-phase-3)",
        win_requires_membership=True, resolves_when="post_phase3",
        notes="Research backing / independent assessment of financials, track "
              "record, or method. Never cost-based.",
    ),
)

# ===========================================================================
# REVIEW — case / evaluation. One EACH. Rated fair / unfair only (no neutral;
# neutral_count stays 0). Both the fair (=helpful) and unfair (=harmful) counts
# are displayed. Winner = most FAIR votes (for now). The winner of each gets a
# direct line to Earthbux and the org — a perk, so winning requires membership.
# ===========================================================================
_REVIEW_REACTIONS = ("helpful", "harmful")
_REVIEW_LABELS = {"helpful": "Fair", "harmful": "Unfair"}
_REVIEW_TYPES = (
    PostType(
        key="case", label="Case", category="review",
        limit_rule="one", reactions=_REVIEW_REACTIONS, reaction_labels=_REVIEW_LABELS,
        win_requires_membership=True, resolves_when="phase1_close",
        notes="Pitches the initiative the benefactor supports. Winner (most fair) "
              "earns a direct line to Earthbux + the org.",
    ),
    PostType(
        key="evaluation", label="Evaluation", category="review",
        limit_rule="one", reactions=_REVIEW_REACTIONS, reaction_labels=_REVIEW_LABELS,
        win_requires_membership=True, resolves_when="phase3",
        notes="Reviews the organization's effort on the mission. Winner (most fair) "
              "earns a direct line to Earthbux + the org.",
    ),
)

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
TYPES: dict[str, PostType] = {
    t.key: t for t in (*_BUDGETING_TYPES, *_MISSION_SUPPORT_TYPES, *_REVIEW_TYPES)
}

CATEGORIES: dict[str, PostCategory] = {
    "budgeting": PostCategory(
        "budgeting", "Budgeting", tuple(t.key for t in _BUDGETING_TYPES), "ben",
        notes="One post per type (up to 3); rolling slots; upvote-only.",
    ),
    "mission_support": PostCategory(
        "mission_support", "Mission Support",
        tuple(t.key for t in _MISSION_SUPPORT_TYPES), "ben",
        notes="One post per type; full reactions; the three rewarded types.",
    ),
    "review": PostCategory(
        "review", "Review", tuple(t.key for t in _REVIEW_TYPES), "ben",
        notes="Case + evaluation; fair/unfair; winner = most fair.",
    ),
}

# Benefactor-authored categories carry the 1-post-per-type limits. Org- and
# staff-authored posts (org_update, mission_update, testimonial, editorial,
# headline) are unlimited and live outside this table — they are not part of
# the per-benefactor allowance and are not rewarded through the 32nds split.
STAFF_OR_ORG_CATEGORIES = ("org_update", "mission_update", "testimonial",
                           "editorial", "headline")

# The rewarded post types, in payout order. Replaces the old
# best_case / context_or_analysis / comments slices — one 1/32 slice each.
REWARDED_TYPES = tuple(k for k, t in TYPES.items() if t.rewarded)

# Benefactor categories require mission membership (or a phase-1 "agreement to
# become a member" = a committed stake) to POST. Enforced in crud.create_post
# via can_post_mission. Org/staff categories are exempt.
BENEFACTOR_CATEGORIES = ("budgeting", "mission_support", "review")
POST_REQUIRES_MEMBERSHIP = frozenset(BENEFACTOR_CATEGORIES)


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
# Only org-tagged post types are rated — case, investigation and evaluation are
# the three that name an organization. Everything else is unrated (`None` on
# the wire, stored green so the column can stay NOT NULL).
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
    """True if authoring in this category requires mission membership."""
    return category_key in POST_REQUIRES_MEMBERSHIP


def is_benefactor_type(type_key: str) -> bool:
    """True if `type_key` is one of the benefactor subcategories in this table."""
    return type_key in TYPES


# ---------------------------------------------------------------------------
# Helpers (what enforcement will call)
# ---------------------------------------------------------------------------
def allowed_reactions(type_key: str) -> tuple[str, ...]:
    """Reactions the frontend should show for a post type. Backend still stores
    only helpful/neutral/harmful; anything not returned here is never offered."""
    return TYPES[type_key].reactions


def reaction_label(type_key: str, reaction: str) -> str:
    """UI label for a reaction on a given type (e.g. 'Fair' for review helpful)."""
    return TYPES[type_key].reaction_labels.get(reaction, reaction.capitalize())


def is_reaction_allowed(type_key: str, reaction: str) -> bool:
    return reaction in TYPES[type_key].reactions


def category_of(type_key: str) -> str:
    return TYPES[type_key].category


def is_rewarded(type_key: str) -> bool:
    return TYPES[type_key].rewarded


def win_requires_membership(type_key: str) -> bool:
    return TYPES[type_key].win_requires_membership


def _validate() -> None:
    """Fail fast on an internally inconsistent table (run at import)."""
    for key, t in TYPES.items():
        assert t.key == key, f"type key mismatch: {key} vs {t.key}"
        assert t.category in CATEGORIES, f"{key}: unknown category {t.category}"
        assert set(t.reactions) <= set(REACTIONS), f"{key}: bad reactions {t.reactions}"
        assert t.reactions, f"{key}: must expose at least one reaction"
        assert set(t.reaction_labels) <= set(t.reactions), f"{key}: label for hidden reaction"
        assert t.limit_rule in ("one", "one_rolling"), f"{key}: bad limit_rule {t.limit_rule}"
        assert t.edit_policy in ("full", "partial", "none"), f"{key}: bad edit_policy"
        if t.edit_policy == "partial":
            assert t.locked_fields, f"{key}: partial edit needs locked_fields"
    for key, c in CATEGORIES.items():
        assert c.key == key
        for tk in c.type_keys:
            assert tk in TYPES and TYPES[tk].category == key, f"{key}: bad member {tk}"
    # Exactly the three mission-support types are rewarded.
    assert REWARDED_TYPES == ("context", "investigation", "analysis"), REWARDED_TYPES
    # Every org-tagged type must exist in the taxonomy, and the classifier must
    # only ever return a real flag.
    for tk in ORG_TAGGED_TYPES:
        assert tk in TYPES, f"org-tagged type {tk} is not in the taxonomy"
    assert classify_flag() in FLAGS
    assert set(FLAG_MEANING) == set(FLAGS)


_validate()
