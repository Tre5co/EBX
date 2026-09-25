"""Outgoing mail — the smallest thing that works (2026-09-25, Contact us).

Standard-library SMTP with STARTTLS. Configured by SMTP_HOST / SMTP_PORT /
SMTP_USER / SMTP_PASSWORD / SMTP_FROM (config.py). With no SMTP_HOST it sends
nothing and returns False, and callers keep the message in the database, so a
missing mailbox never loses a message. The full mail transport (P6/c1) replaces
this; its callers only need `send`.
"""
from __future__ import annotations

import smtplib
from email.message import EmailMessage
from typing import Optional

from .config import get_settings


def configured() -> bool:
    return bool(get_settings().smtp_host)


def send(to: str, subject: str, body: str, reply_to: Optional[str] = None) -> bool:
    s = get_settings()
    if not s.smtp_host:
        return False
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
        print(f"[mailer] send to {to} failed: {e}")
        return False
