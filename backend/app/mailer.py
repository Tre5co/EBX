"""Outgoing mail — the smallest thing that works (2026-09-25, Contact us).

Two routes, tried in this order:

1. **Resend** (HTTPS API) when RESEND_API_KEY is set — the one that works on
   Railway's Hobby plan, where outbound SMTP is blocked (2026-09-26). Sends
   from MAIL_FROM, which must be on a domain verified in Resend
   (send.earthbux.net — a subdomain, so it cannot disturb the Google Workspace
   mail on earthbux.net itself).
2. **SMTP** (STARTTLS) when SMTP_HOST is set — for a Pro plan or another host.

With neither configured it sends nothing and returns False; callers keep the
message in the database, so a missing mail route never loses a message. The
full mail transport (P6/c1) replaces this; its callers only need `send`.
"""
from __future__ import annotations

import json
import smtplib
import urllib.error
import urllib.request
from email.message import EmailMessage
from typing import Optional

from .config import get_settings

RESEND_URL = "https://api.resend.com/emails"


def configured() -> bool:
    s = get_settings()
    return bool(s.resend_api_key or s.smtp_host)


def _send_resend(to: str, subject: str, body: str, reply_to: Optional[str]) -> bool:
    s = get_settings()
    payload = {"from": s.mail_from, "to": [to], "subject": subject, "text": body}
    if reply_to:
        payload["reply_to"] = reply_to
    req = urllib.request.Request(
        RESEND_URL, data=json.dumps(payload).encode(), method="POST",
        headers={"Authorization": "Bearer " + s.resend_api_key,
                 "Content-Type": "application/json", "User-Agent": "earthbux-mailer/1"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return 200 <= r.status < 300
    except urllib.error.HTTPError as e:
        # Resend explains itself in the body (unverified domain, bad key, …).
        print(f"[mailer] resend refused ({e.code}): {e.read()[:300]!r}")
    except (urllib.error.URLError, OSError) as e:
        print(f"[mailer] resend unreachable: {e}")
    return False


def _send_smtp(to: str, subject: str, body: str, reply_to: Optional[str]) -> bool:
    s = get_settings()
    msg = EmailMessage()
    msg["From"] = s.smtp_from or s.smtp_user
    msg["To"] = to
    msg["Subject"] = subject
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.set_content(body)
    try:
        with smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=15) as smtp:
            smtp.starttls()
            if s.smtp_user:
                smtp.login(s.smtp_user, s.smtp_password)
            smtp.send_message(msg)
        return True
    except (smtplib.SMTPException, OSError) as e:
        print(f"[mailer] smtp send to {to} failed: {e}")
        return False


def send(to: str, subject: str, body: str, reply_to: Optional[str] = None) -> bool:
    s = get_settings()
    if s.resend_api_key and _send_resend(to, subject, body, reply_to):
        return True
    if s.smtp_host:
        return _send_smtp(to, subject, body, reply_to)
    return False
