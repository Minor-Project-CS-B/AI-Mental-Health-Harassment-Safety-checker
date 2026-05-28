"""
utils/email_validator.py
─────────────────────────
Two-layer email validation:
  1. Blocks disposable/temporary email domains (instant, no network)
  2. Checks MX records — verifies the domain actually has mail servers (DNS lookup)

CHANGES vs original:
  - MX lookup has a hard 3-second asyncio timeout (was unbounded on Render)
  - On DNS failure/timeout we return True (allow) instead of False (block)
    because blocking valid emails due to a DNS hiccup is worse than
    occasionally letting a fake email through (SMTP will reject it anyway).
"""

import re
import asyncio

# ── Disposable email domain blocklist ─────────────────────────────────────────

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

    IMPORTANT CHANGE: On Render (and many cloud environments), DNS lookups
    can be slow or fail unpredictably. We now:
      1. Use a hard 3-second asyncio timeout (not just a dns library timeout)
      2. Return True on any failure/timeout — better to allow a possibly
         valid email than to block real users due to a cloud DNS hiccup.
         The actual SMTP send will fail if the email is truly invalid.

    Returns True if valid mail servers found OR if check could not complete.
    Returns False only if DNS definitively returns no MX records.
    """
    try:
        import dns.resolver
        loop = asyncio.get_event_loop()

        # Hard asyncio timeout — prevents hanging requests on Render
        records = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: dns.resolver.resolve(domain, 'MX', lifetime=3)
            ),
            timeout=3.0
        )
        return len(records) > 0

    except asyncio.TimeoutError:
        # DNS took too long (common on Render) — allow the email
        print(f"[EMAIL VALIDATOR] MX lookup timed out for {domain}, allowing.")
        return True

    except Exception:
        # Any other DNS error — allow the email, don't block registration
        return True


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

    # 2. Disposable domain check (instant, no network)
    if is_disposable_email(email):
        return {
            "valid": False,
            "reason": "Temporary or disposable email addresses are not allowed. Please use your real email.",
        }

    # 3. MX record check (DNS lookup with timeout)
    #    Note: returns True on timeout/error to avoid blocking real users
    domain = email.split("@")[-1]
    if not await has_mx_records(domain):
        return {
            "valid": False,
            "reason": f"The email domain '{domain}' does not appear to accept emails. Please use a real email address.",
        }

    return {"valid": True, "reason": ""}