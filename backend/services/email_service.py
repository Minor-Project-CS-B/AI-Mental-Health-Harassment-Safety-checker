import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from database.connection import get_settings


async def send_magic_link_email(to_email: str, name: str, magic_url: str) -> bool:
    """
    Sends the authentication magic link email via Gmail SMTP.
    Returns True on success, False on failure.
    """
    settings = get_settings()

    subject = f"Your {settings.app_name} login link"

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
          {settings.app_name} · AI-powered Mental Health & Safety Support
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
        )
        print(f"[EMAIL] Magic link sent to {to_email}")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send to {to_email}: {e}")
        return False