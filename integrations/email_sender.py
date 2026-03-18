from dotenv import load_dotenv
load_dotenv()
import os
import ssl
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import date

logger = logging.getLogger(__name__)

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
SMTP_HOST = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com")
SMTP_SSL_PORT = int(os.getenv("EMAIL_SMTP_SSL_PORT", "465"))
SMTP_STARTTLS_PORT = int(os.getenv("EMAIL_SMTP_STARTTLS_PORT", "587"))
SMTP_TIMEOUT_SECONDS = int(os.getenv("EMAIL_SMTP_TIMEOUT_SECONDS", "25"))


def _send_message(msg: MIMEMultipart) -> None:
    """Send email using SSL first, then fallback to STARTTLS."""
    last_error = None

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_SSL_PORT, timeout=SMTP_TIMEOUT_SECONDS) as server:
            server.login(EMAIL_FROM, EMAIL_APP_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
            return
    except Exception as e:
        last_error = e
        logger.warning(f"Email SSL send failed, trying STARTTLS fallback: {e}")

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_STARTTLS_PORT, timeout=SMTP_TIMEOUT_SECONDS) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(EMAIL_FROM, EMAIL_APP_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
            return
    except Exception as e:
        last_error = e

    raise RuntimeError(str(last_error) if last_error else "Unknown SMTP error")


def send_daily_posts_email(posts: dict) -> dict:
    """
    Send all platform posts in one email.
    posts = {
        "linkedin": "post text",
        "reddit": "post text", 
        "twitter": "post text",
        "indie_hackers": "post text"
    }
    """
    if not all([EMAIL_FROM, EMAIL_TO, EMAIL_APP_PASSWORD]):
        return {"status": "failed", "error": "Email credentials missing"}

    try:
        today = date.today().strftime("%B %d, %Y")
        subject = f"SkillVector Daily Posts — {today}"

        msg = MIMEMultipart("related")
        msg["Subject"] = subject
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO

        logo_tag = ""
        if os.path.exists(LOGO_PATH):
            logo_tag = '<img src="cid:logo" width="60" height="60" style="border-radius: 10px;"/><br/>'

        def post_block(platform, color, icon, link, content):
            if not content:
                return ""
            return f"""
            <div style="margin-bottom: 20px;">
                <div style="background: {color}22; border-left: 3px solid {color}; 
                            padding: 8px 12px; border-radius: 4px 4px 0 0;
                            display: flex; align-items: center;">
                    <span style="color: {color}; font-weight: bold; font-size: 13px;">{icon} {platform}</span>
                    <a href="{link}" style="margin-left: auto; background: {color}; color: #000; 
                       padding: 4px 12px; border-radius: 4px; text-decoration: none; 
                       font-size: 11px; font-weight: bold;">Open {platform} →</a>
                </div>
                <div style="background: #141b24; padding: 16px; border-radius: 0 0 4px 4px;">
                    <p style="color: #e8edf5; white-space: pre-wrap; font-size: 13px; 
                               line-height: 1.6; margin: 0;">{content}</p>
                </div>
            </div>
            """

        linkedin_block = post_block(
            "LinkedIn", "#0077b5", "💼",
            "https://www.linkedin.com/feed/",
            posts.get("linkedin", "")
        )
        reddit_block = post_block(
            "Reddit", "#ff4500", "🔴",
            "https://www.reddit.com/r/MachineLearning/submit",
            posts.get("reddit", "")
        )
        twitter_block = post_block(
            "Twitter/X", "#1da1f2", "🐦",
            "https://twitter.com/intent/tweet",
            posts.get("twitter", "")
        )
        indie_block = post_block(
            "Indie Hackers", "#0ea5e9", "🚀",
            "https://www.indiehackers.com/post/new",
            posts.get("indie_hackers", "")
        )

        html = f"""
        <html><body style="font-family: Arial; max-width: 620px; margin: 0 auto; 
                           padding: 20px; background: #f5f5f5;">
        <div style="background: #080b10; padding: 20px; border-radius: 12px 12px 0 0; text-align: center;">
            {logo_tag}
            <h2 style="color: #00e5a0; margin: 8px 0 0 0;">SkillVector</h2>
            <p style="color: #5a6478; margin: 4px 0 0 0; font-size: 11px; letter-spacing: 2px;">
                DAILY POSTS — {today}
            </p>
        </div>
        <div style="background: #0d1117; padding: 20px;">
            <p style="color: #5a6478; font-size: 12px; margin: 0 0 20px 0;">
                Your posts are ready. Click the button next to each platform to open it, 
                then copy and paste the post. Takes 2 minutes total.
            </p>
            {linkedin_block}
            {reddit_block}
            {twitter_block}
            {indie_block}
        </div>
        <div style="background: #080b10; padding: 12px; border-radius: 0 0 12px 12px; text-align: center;">
            <p style="color: #5a6478; font-size: 11px; margin: 0;">
                Sent by Atlas · <a href="https://skill-vector.com" style="color: #00e5a0;">skill-vector.com</a>
            </p>
        </div>
        </body></html>
        """

        msg.attach(MIMEText(html, "html"))

        if os.path.exists(LOGO_PATH):
            with open(LOGO_PATH, "rb") as f:
                logo_data = f.read()
            logo_img = MIMEImage(logo_data)
            logo_img.add_header("Content-ID", "<logo>")
            logo_img.add_header("Content-Disposition", "inline")
            msg.attach(logo_img)

        _send_message(msg)

        logger.info(f"Daily posts email sent to {EMAIL_TO}")
        return {"status": "success", "sent_to": EMAIL_TO}

    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return {"status": "failed", "error": str(e)}


# Keep old function for backwards compatibility
def send_daily_post_email(post_content: str) -> dict:
    return send_daily_posts_email({"linkedin": post_content})
