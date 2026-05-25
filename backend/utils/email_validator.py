"""
utils/email_validator.py
─────────────────────────
Two-layer email validation:
  1. Blocks disposable/temporary email domains (instant, no network)
  2. Checks MX records — verifies the domain actually has mail servers (DNS lookup)

Used before sending OTP so we never waste an SMTP call on fake emails.
"""

import re
import asyncio

# ── Disposable email domain blocklist ─────────────────────────────────────────
# Most commonly used throwaway email services

BLOCKED_DOMAINS = {
    # Classic disposable
    "mailinator.com", "guerrillamail.com", "guerrillamail.net", "guerrillamail.org",
    "tempmail.com", "temp-mail.org", "temp-mail.io", "throwaway.email",
    "10minutemail.com", "10minutemail.net", "10minutemail.org",
    "yopmail.com", "yopmail.fr", "cool.fr.nf", "jetable.fr.nf",
    "maildrop.cc", "mailnull.com", "mailnesia.com", "mailnew.com",
    "spamgourmet.com", "spamgourmet.net", "spamgourmet.org",
    "trashmail.com", "trashmail.me", "trashmail.net", "trashmail.at",
    "trashmail.io", "trashmail.xyz", "trashcanmail.com",
    "dispostable.com", "disposableaddress.com", "discard.email",
    "sharklasers.com", "guerrillamailblock.com", "grr.la",
    "spam4.me", "spamherelots.com", "spamhereplease.com",
    "fakeinbox.com", "fakemailgenerator.com", "fakemail.fr",
    "getnada.com", "getairmail.com", "filzmail.com",
    "armyspy.com", "cuvox.de", "dayrep.com", "einrot.com",
    "fleckens.hu", "gustr.com", "jourrapide.com", "rhyta.com",
    "superrito.com", "teleworm.us", "spambog.com",
    "mailexpire.com", "spamex.com", "spam.la",
    # Indian-context throwaway services
    "moakt.com", "mohmal.com", "tempinbox.com",
    "inboxbear.com", "disbox.org", "disbox.net",
    # Common test/fake patterns
    "example.com", "test.com", "invalid.com", "nowhere.com",
    "noemail.com", "nospam.com", "nomail.com", "noreply.com",
}


def is_valid_email_format(email: str) -> bool:
    """Basic RFC 5322 format check."""
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def is_disposable_email(email: str) -> bool:
    """Returns True if the email domain is a known disposable service."""
    domain = email.strip().lower().split("@")[-1]
    return domain in BLOCKED_DOMAINS


async def has_mx_records(domain: str) -> bool:
    """
    Checks if the domain has MX (mail exchange) records via DNS.
    If no MX records exist, the domain cannot receive email — it's fake.

    Returns True if valid mail servers exist, False otherwise.
    Uses asyncio to avoid blocking the event loop.
    """
    try:
        import dns.resolver
        loop    = asyncio.get_event_loop()
        records = await loop.run_in_executor(
            None,
            lambda: dns.resolver.resolve(domain, 'MX', lifetime=5)
        )
        return len(records) > 0
    except Exception:
        return False


async def validate_email_fully(email: str) -> dict:
    """
    Full validation pipeline. Returns dict with:
      valid: bool
      reason: str (why it failed, empty if valid)
    """
    email = email.strip().lower()

    # 1. Format check
    if not is_valid_email_format(email):
        return {"valid": False, "reason": "Invalid email format."}

    # 2. Disposable domain check (instant)
    if is_disposable_email(email):
        return {"valid": False, "reason": "Temporary or disposable email addresses are not allowed. Please use your real email."}

    # 3. MX record check (DNS lookup — ~1-2 seconds)
    domain = email.split("@")[-1]
    if not await has_mx_records(domain):
        return {"valid": False, "reason": f"The email domain '{domain}' does not appear to accept emails. Please use a real email address."}

    return {"valid": True, "reason": ""}