"""org_config — the organization experience's words and rules (P2b, 2026-10-02).

The same pattern as `post_config.py`: the application form, the shared
UNCLAIMED panel (D30) and the organization post kinds live here, and the pages
render them from `GET /org/application`, so the words ARE the rules.

THE APPLICATION IS THE CLAIM (P2b › Accounts). One form makes three things at
once: the organization (if it is new), a PENDING organization account for the
person applying (its first administrator, D29), and the application staff
approve. Nothing is public until staff approve it.

TWO STAGES, because of `mission_model.md` §6 (the three gates):
  * STAGE 1 — this form. Enough to be *electable* and to be contacted: who you
    are, who is applying, what you would do, and the promises every campaign
    makes. Short on purpose — "no organization should have to write a budget for
    money it has a one-in-eight chance of receiving."
  * STAGE 2 — *payable* (P6, not built). Asked only of an organization that wins:
    registration documents, the payee, the representative's authority, bank
    details. Listed below (`PAYABLE_QUESTIONS`) so the form can say what comes
    later, and so P6 starts from a list instead of a blank page.

Question kinds: text · textarea · email · url · tel · number · select ·
multiselect · checkbox (a promise: required means it must be ticked).
"""
from __future__ import annotations

ATTESTATION_VERSION = "org-application-2026-10"

CAUSES = [
    ("atmosphere", "Atmosphere"), ("oceans", "Oceans"), ("land", "Land"),
    ("forests", "Forests"), ("wildlife", "Wildlife"),
    ("human-rights", "Human Rights"), ("human-progress", "Human Progress"),
]

# ── Stage 1: the application ────────────────────────────────────────────────
APPLICATION_SECTIONS: list[dict] = [
    {
        "key": "org",
        "title": "The organization",
        "intro": "Who you are. If your organization is already on Earthbux (someone may "
                 "have nominated it), pick it — you are claiming that page, not making a second one.",
        "questions": [
            {"key": "legal_name", "label": "Legal name", "kind": "text", "required": True,
             "help": "As registered. The name benefactors see can differ (next question)."},
            {"key": "public_name", "label": "Name you go by, if different", "kind": "text"},
            {"key": "legal_form", "label": "What kind of organization is it?", "kind": "select",
             "required": True,
             "options": ["US 501(c)(3) public charity", "US 501(c)(3) private foundation",
                         "Registered charity outside the US", "Other nonprofit / NGO",
                         "Social enterprise / B Corp", "Government or public body",
                         "University or research group", "Informal / community group",
                         "Not sure"]},
            {"key": "country", "label": "Country of registration", "kind": "text", "required": True},
            {"key": "registration_number", "label": "Registration number (EIN or equivalent)",
             "kind": "text",
             "help": "Optional now. Required before any money moves (stage 2)."},
            {"key": "founded_year", "label": "Year founded", "kind": "number"},
            {"key": "website", "label": "Website", "kind": "url",
             "help": "Optional — someone can add it later."},
            {"key": "public_contact", "label": "Public contact — an email or phone benefactors can use",
             "kind": "text", "required": True},
            {"key": "one_line", "label": "Your mission, in one sentence", "kind": "text",
             "required": True, "max": 200},
            {"key": "causes", "label": "Which of the seven causes do you work in?",
             "kind": "multiselect", "required": True, "options": [c[1] for c in CAUSES]},
            {"key": "regions", "label": "Where do you work?", "kind": "text", "required": True,
             "help": "Countries, regions or cities."},
            {"key": "budget_band", "label": "Annual budget", "kind": "select", "required": True,
             "options": ["Under $50k", "$50k – $250k", "$250k – $1M", "$1M – $10M",
                         "Over $10M", "Prefer not to say"]},
            {"key": "staff_band", "label": "Paid staff", "kind": "select", "required": True,
             "options": ["None (volunteer-run)", "1 – 5", "6 – 25", "26 – 100", "Over 100"]},
        ],
    },
    {
        "key": "person",
        "title": "You",
        "intro": "The person applying becomes the organization account's first administrator "
                 "and creates everyone else's logins.",
        "questions": [
            {"key": "full_name", "label": "Your full name", "kind": "text", "required": True},
            {"key": "position", "label": "Your position", "kind": "text", "required": True},
            {"key": "proof_of_role", "label": "How can we confirm you work there?", "kind": "textarea",
             "required": True,
             "help": "A staff page that lists you, an email on the organization's domain, a "
                     "LinkedIn profile — anything we can check."},
            {"key": "authority", "label": "Can you make commitments on the organization's behalf?",
             "kind": "select", "required": True,
             "options": ["Yes", "No — I will name who can", "Not sure"]},
            {"key": "authority_name", "label": "If not, who can? (name and position)", "kind": "text"},
        ],
    },
    {
        "key": "fit",
        "title": "What you would do",
        "intro": "Credentials and a short statement — not a plan. The plan comes only if you win.",
        "questions": [
            {"key": "brought_by", "label": "Which initiative or mission brings you here?",
             "kind": "text", "help": "Optional. Leave blank if you are just getting set up."},
            {"key": "pitch", "label": "If benefactors chose you, what would you do with a week's pool?",
             "kind": "textarea", "required": True, "max": 1200},
            {"key": "receipt", "label": "One past outcome you are proud of — with a number in it",
             "kind": "textarea", "required": True,
             "help": "Trees planted, people served, tons removed, cases won. This becomes your "
                     "first receipt on your profile."},
            {"key": "reporting_today", "label": "How do you report to donors today?",
             "kind": "textarea",
             "help": "Annual report, impact dashboard, audited accounts — link it if public."},
        ],
    },
    {
        "key": "integrity",
        "title": "Integrity",
        "intro": "Answered privately, reviewed by Earthbux staff. A 'yes' is not a refusal — "
                 "hiding one is.",
        "questions": [
            {"key": "conflicts", "label": "Any relationship with Earthbux staff, or a plan to "
                                          "ask people to vote for you in exchange for anything?",
             "kind": "select", "required": True, "options": ["No", "Yes — explained below"]},
            {"key": "legal_issues", "label": "Any open investigations, sanctions or lawsuits?",
             "kind": "select", "required": True, "options": ["No", "Yes — explained below"]},
            {"key": "partisan", "label": "Does the organization campaign for or against "
                                         "political candidates?",
             "kind": "select", "required": True, "options": ["No", "Yes — explained below"]},
            {"key": "integrity_notes", "label": "Anything you answered 'yes' to", "kind": "textarea"},
        ],
    },
    {
        "key": "promises",
        "title": "What every campaign promises",
        "intro": "These are the terms of being on the ballot.",
        "questions": [
            {"key": "will_answer", "kind": "checkbox", "required": True,
             "label": "We will answer benefactors' questions on Earthbux. Silence is shown on our page."},
            {"key": "will_report", "kind": "checkbox", "required": True,
             "label": "If we win, we will publish progress reports for the mission."},
            {"key": "accept_coverage", "kind": "checkbox", "required": True,
             "label": "We accept that Earthbux News supervises and reports on missions we run, "
                      "including critical coverage."},
            {"key": "accept_vetting", "kind": "checkbox", "required": True,
             "label": "We understand no money moves until stage 2 (identity, payee, nonprofit "
                      "status) is verified, and that a failed verification is published."},
            {"key": "attest", "kind": "checkbox", "required": True,
             "label": "Everything above is true, and I am applying for this organization with its knowledge."},
        ],
    },
]

# ── Stage 2: payable (P6 — listed, not asked) ───────────────────────────────
PAYABLE_QUESTIONS: list[str] = [
    "Registration documents (certificate of incorporation, IRS determination letter or equivalent)",
    "Registered address",
    "The payee — the legal name a check is made out to, matched to the registration",
    "Bank details for the payee (or a mailing address for a check)",
    "The representative's authority to bind the organization (board letter or officer signature)",
    "An executive and a representative named (the representative edits the mission, "
    "the executive holds the account)",
    "A start estimate for the mission: the date you can begin, and what has to be true first",
    "Most recent annual accounts or Form 990",
]

# ── D30: the shared UNCLAIMED panel ─────────────────────────────────────────
UNCLAIMED_PANEL = {
    "title": "UNCLAIMED",
    "body": (
        "Nobody from this organization runs this page yet. Benefactors named it, and "
        "Earthbux keeps its page so the discussion has a home. When an organization is "
        "nominated or reaches an organization election, Earthbux contacts it with what "
        "benefactors are saying and how to claim the page. An unclaimed organization can "
        "still be elected — the mission runs, Earthbux News reports on it, and the "
        "organization receives a smaller guaranteed donation until it claims."
    ),
    "you_can": [
        "Post about it — questions and evidence here are what we forward to them.",
        "Tell them: if you know someone there, send them this page.",
        "Work there? Claim it — the application takes about ten minutes.",
    ],
}

# ── Organization post kinds (category `org_update`) ─────────────────────────
# update      general content on the organization's profile (target: itself)
# plan        a campaign's plan (target: the mission it runs for)
# answer      a reply to a benefactor's post (Q&A) — parent_id required
# suggestion  "Suggest us" on an initiative that has not won (target: initiative)
ORG_POST_KINDS = ("update", "plan", "answer", "suggestion")

MEMBER_ROLES = ("admin", "member")


def all_questions() -> list[dict]:
    return [q for s in APPLICATION_SECTIONS for q in s["questions"]]


def validate_answers(answers: dict) -> list[str]:
    """Every rule broken, in words — an empty list means the form is complete."""
    answers = answers or {}
    errs: list[str] = []
    for q in all_questions():
        v = answers.get(q["key"])
        empty = v in (None, "", [], False)
        if q.get("required") and empty:
            errs.append(("Tick: " if q["kind"] == "checkbox" else "Required: ") + q["label"])
            continue
        if empty:
            continue
        if q["kind"] in ("select",) and v not in q["options"]:
            errs.append(f"Choose one of the options for: {q['label']}")
        if q["kind"] == "multiselect":
            if not isinstance(v, list) or any(x not in q["options"] for x in v):
                errs.append(f"Choose from the list for: {q['label']}")
        if q.get("max") and isinstance(v, str) and len(v) > q["max"]:
            errs.append(f"Too long ({len(v)}/{q['max']}): {q['label']}")
    return errs


def public_form() -> dict:
    return {
        "attestation_version": ATTESTATION_VERSION,
        "sections": APPLICATION_SECTIONS,
        "payable_later": PAYABLE_QUESTIONS,
        "unclaimed_panel": UNCLAIMED_PANEL,
    }
