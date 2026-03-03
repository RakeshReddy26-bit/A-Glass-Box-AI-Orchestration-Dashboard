from dotenv import load_dotenv
load_dotenv()
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date

logger = logging.getLogger(__name__)

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")


def send_daily_post_email(post_content: str) -> dict:
    if not all([EMAIL_FROM, EMAIL_TO, EMAIL_APP_PASSWORD]):
        return {"status": "failed", "error": "Email credentials missing from .env"}

    try:
        today = date.today().strftime("%B %d, %Y")
        subject = f"SkillVector LinkedIn Post — {today}"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO

        html = f"""
        <html><body style="font-family: Arial; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #00e5a0; padding: 16px; border-radius: 8px 8px 0 0;">
            <h2 style="color: #080b10; margin: 0;">SkillVector Daily Post</h2>
            <p style="color: #080b10; margin: 4px 0 0 0;">{today}</p>
        </div>
        <div style="background: #0d1117; padding: 20px; border-radius: 0 0 8px 8px;">
            <p style="color: #5a6478; font-size: 13px;">Your LinkedIn post is ready. Copy and paste to LinkedIn:</p>
            <div style="background: #141b24; border-left: 3px solid #00e5a0; padding: 16px; border-radius: 4px; margin: 16px 0;">
                <p style="color: #e8edf5; white-space: pre-wrap; font-size: 14px; line-height: 1.6;">{post_content}</p>
            </div>
            <a href="https://www.linkedin.com/feed/" 
               style="background: #00e5a0; color: #080b10; padding: 12px 24px; 
                      border-radius: 6px; text-decoration: none; font-weight: bold;
                      display: inline-block; margin-top: 8px;">
                Open LinkedIn
            </a>
            <p style="color: #5a6478; font-size: 11px; margin-top: 20px;">
                Sent by Atlas — SkillVector AI Automation
            </p>
        </div>
        </body></html>
        """

        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_FROM, EMAIL_APP_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

        logger.info(f"Daily post email sent to {EMAIL_TO}")
        return {"status": "success", "sent_to": EMAIL_TO}

    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return {"status": "failed", "error": str(e)}
