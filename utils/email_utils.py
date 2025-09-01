import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

def get_env_variable(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None:
        raise EnvironmentError(f"Missing required environment variable: {var_name}")
    return value

def debug_env():
    expected_vars = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS"]
    print("---- ENV DEBUG ----")
    for var in expected_vars:
        value = os.getenv(var)
        if value is None:
            print(f"{var}: MISSING")
        else:
            to_print = value if var != "SMTP_PASS" else ("*" * len(value))
            print(f"{var}: {to_print}")
    print("-------------------\n")

    SMTP_HOST = get_env_variable("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = get_env_variable("SMTP_USER")
    SMTP_PASS = get_env_variable("SMTP_PASS")


def send_email(to_email: str, subject: str, body: str):
    """Send plain text email via SMTP"""
    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [to_email], msg.as_string())
        print(f"[EMAIL] Sent to {to_email}")
    except smtplib.SMTPAuthenticationError:
        print("[EMAIL ERROR] Authentication failed. Check your SMTP_USER and SMTP_PASS (App Password for Gmail).")
    except smtplib.SMTPConnectError:
        print("[EMAIL ERROR] Could not connect to SMTP server. Check SMTP_HOST/PORT.")
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")