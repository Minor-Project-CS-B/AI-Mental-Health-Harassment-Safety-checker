# services/email_service.py
# ─────────────────────────────────────────────────────────────────────────────
# Email sending via Resend API (primary) with Gmail SMTP as fallback.
#
# WHY: Render free tier blocks outbound SMTP ports (587, 465, 25).
#      Resend uses HTTPS (port 443) which is always open on Render.
#      Gmail SMTP is kept as a fallback for local development.
# ─────────────────────────────────────────────────────────────────────────────

import httpx
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from database.connection import get_settings


# ── Resend API (Primary — works on Render free tier) ──────────────────────────

async def _send_via_resend(to_email: str, subject: str, html_body: str, text_body: str) -> bool:
    """
    Sends email via Resend API over HTTPS (port 443).
    This works on Render free tier where SMTP ports are blocked.
    Requires RESEND_API_KEY env variable.
    """
    settings = get_settings()

    if not settings.resend_api_key:
        print("[RESEND] No RESEND_API_KEY set, skipping Resend.")
        return False

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.resend_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": f"{settings.app_name} <{settings.resend_from_email}>",
                    "to": [to_email],
                    "subject": subject,
                    "html": html_body,
                    "text": text_body,
                },
            )
            if resp.status_code in (200, 201):
                print(f"[RESEND] Email sent to {to_email} ✓")
                return True
            else:
                print(f"[RESEND ERROR] Status {resp.status_code}: {resp.text}")
                return False
    except Exception as e:
        print(f"[RESEND ERROR] {e}")
        return False


# ── Gmail SMTP (Fallback — for local development only) ────────────────────────

async def _send_via_smtp(to_email: str, subject: str, html_body: str, text_body: str) -> bool:
    """
    Sends email via Gmail SMTP.
    NOTE: This WILL FAIL on Render free tier (SMTP ports are blocked).
    Only use this as a local dev fallback.
    """
    settings = get_settings()

    if not settings.gmail_user or not settings.gmail_app_password:
        print("[SMTP] No Gmail credentials set, skipping SMTP.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{settings.app_name} <{settings.gmail_user}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username=settings.gmail_user,
            password=settings.gmail_app_password,
            timeout=10,
        )
        print(f"[SMTP] Email sent to {to_email} ✓")
        return True
    except Exception as e:
        print(f"[SMTP ERROR] Failed to send to {to_email}: {e}")
        return False


# ── Unified send — tries Resend first, falls back to SMTP ─────────────────────

async def _send_email(to_email: str, subject: str, html_body: str, text_body: str) -> bool:
    """
    Tries Resend first (works on Render), then falls back to Gmail SMTP (local dev).
    """
    # Try Resend first
    sent = await _send_via_resend(to_email, subject, html_body, text_body)
    if sent:
        return True

    # Fallback to SMTP (works locally, fails on Render free tier)
    print(f"[EMAIL] Resend failed, trying SMTP fallback for {to_email}...")
    sent = await _send_via_smtp(to_email, subject, html_body, text_body)
    return sent


# ── Public API ─────────────────────────────────────────────────────────────────

async def send_magic_link_email(to_email: str, name: str, magic_url: str) -> bool:
    """
    Sends the authentication magic link email.
    Returns True on success, False on failure.
    """
    settings = get_settings()
    subject   = f"Your {settings.app_name} login link"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; background: #f4f4f4; padding: 40px;">
      <div style="max-width: 480px; margin: auto; background: #fff;
                  border-radius: 12px; padding: 40px; box-shadow: 0 2px 12px rgba(0,0,0,0.08);">

        <h2 style="color: #2d2d2d; margin-bottom: 8px;">Hello, {name} 👋</h2>
        <p style="color: #555; font-size: 15px; line-height: 1.6;">
          Click the button below to securely log in to <strong>{settings.app_name}</strong>.
          This link expires in <strong>30 minutes</strong>.
        </p>

        <div style="text-align: center; margin: 32px 0;">
          <a href="{magic_url}"
             style="background: #3B8BD4; color: #fff; text-decoration: none;
                    padding: 14px 32px; border-radius: 8px; font-size: 15px;
                    font-weight: bold; display: inline-block;">
            Log in to {settings.app_name}
          </a>
        </div>

        <p style="color: #999; font-size: 13px;">
          If you didn't request this, you can safely ignore this email.
          Never share this link with anyone.
        </p>

        <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
        <p style="color: #bbb; font-size: 12px; text-align: center;">
          {settings.app_name} · AI-powered Mental Health &amp; Safety Support
        </p>
      </div>
    </body>
    </html>
    """

    text_body = (
        f"Hello {name},\n\n"
        f"Click the link below to log in to {settings.app_name}:\n\n"
        f"{magic_url}\n\n"
        f"This link expires in 30 minutes. Do not share it with anyone.\n\n"
        f"— The {settings.app_name} Team"
    )

    return await _send_email(to_email, subject, html_body, text_body)


async def send_otp_email(to_email: str, name: str, otp: str) -> bool:
    """
    Sends a 6-digit OTP to verify the email address during registration.
    OTP expires in 10 minutes.
    """
    settings = get_settings()
    subject   = f"Your {settings.app_name} verification code"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; background: #f4f4f4; padding: 40px;">
      <div style="max-width: 480px; margin: auto; background: #fff;
                  border-radius: 12px; padding: 40px; box-shadow: 0 2px 12px rgba(0,0,0,0.08);">

        <h2 style="color: #2d2d2d; margin-bottom: 8px;">Verify your email 📧</h2>
        <p style="color: #555; font-size: 15px; line-height: 1.6;">
          Hi <strong>{name}</strong>, enter this code to complete your
          <strong>{settings.app_name}</strong> registration.
          It expires in <strong>10 minutes</strong>.
        </p>

        <div style="text-align: center; margin: 32px 0;">
          <div style="background: #f0fdfe; border: 2px solid #06b6d4;
                      border-radius: 12px; padding: 24px; display: inline-block;">
            <span style="font-size: 42px; font-weight: 900; letter-spacing: 12px;
                         color: #0891b2; font-family: monospace;">{otp}</span>
          </div>
        </div>

        <p style="color: #999; font-size: 13px;">
          If you didn't request this code, ignore this email — your inbox is safe.
          Never share this code with anyone.
        </p>

        <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
        <p style="color: #bbb; font-size: 12px; text-align: center;">
          {settings.app_name} · AI-powered Mental Health &amp; Safety Support
        </p>
      </div>
    </body>
    </html>
    """

    text_body = (
        f"Hi {name},\n\n"
        f"Your {settings.app_name} verification code is: {otp}\n\n"
        f"This code expires in 10 minutes. Do not share it with anyone.\n\n"
        f"— The {settings.app_name} Team"
    )

    return await _send_email(to_email, subject, html_body, text_body)