import os
import smtplib
from email.message import EmailMessage

DEFAULT_REPORT_RECIPIENT = "kranthiksg@gmail.com"

def send_daily_report_email(subject, body, recipient=DEFAULT_REPORT_RECIPIENT):
    sender = os.getenv("GCSE_REPORT_EMAIL")
    password = os.getenv("GCSE_REPORT_APP_PASSWORD")

    if not sender or not password:
        raise RuntimeError(
            "Email is not configured. Set GCSE_REPORT_EMAIL and GCSE_REPORT_APP_PASSWORD, then restart PyCharm."
        )

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)
