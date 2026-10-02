import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Tuple, Set
from config.settings import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    SENDER_NAME,
    SEND_MODE
)

def validate_email_address(email: str) -> bool:
    if not email or email == "Not Found" or "@" not in email:
        return False
    parts = email.split("@")
    return len(parts) == 2 and "." in parts[1]

def can_send_email(email: str, sent_history: Set[str]) -> Tuple[bool, str]:
    if not validate_email_address(email):
        return False, "Invalid or missing email address (marked Not Found)"
    if email.lower() in sent_history:
        return False, f"Duplicate prevented: {email} was already contacted"
    return True, "Ready to send"

def send_smtp_email(to_email: str, subject: str, body: str) -> Tuple[bool, str]:
    if not SMTP_USER or not SMTP_PASSWORD:
        return False, "SMTP credentials not configured"
    
    try:
        msg = MIMEMultipart()
        msg["From"] = f"{SENDER_NAME} <{SMTP_USER}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return True, "Sent successfully via SMTP"
    except Exception as exc:
        return False, f"SMTP Error: {str(exc)}"

def simulate_send_email(to_email: str, subject: str) -> Tuple[bool, str]:
    return True, f"Simulated delivery to {to_email} (Sandbox mode)"

def dispatch_email_outreach(
    message_item: Dict[str, Any],
    sent_emails_set: Set[str],
    force_simulation: bool = False
) -> Dict[str, Any]:
    email = message_item.get("email", "")
    can_send, reason = can_send_email(email, sent_emails_set)
    
    if not can_send:
        return {
            "influencer": message_item.get("influencer_name"),
            "email": email,
            "channel": "Email",
            "sent": "No",
            "status": f"SKIPPED: {reason}",
            "error_reason": reason
        }

    use_simulation = force_simulation or (SEND_MODE.lower() == "simulation")
    if use_simulation or not SMTP_USER:
        success, info = simulate_send_email(email, message_item.get("email_subject", ""))
        status_label = "SIMULATED_SUCCESS" if success else "FAILED"
    else:
        success, info = send_smtp_email(
            email,
            message_item.get("email_subject", ""),
            message_item.get("email_body", "")
        )
        status_label = "SENT_SUCCESS" if success else "FAILED"

    return {
        "influencer": message_item.get("influencer_name"),
        "email": email,
        "channel": "Email",
        "sent": "Yes" if success else "No",
        "status": status_label,
        "detail": info
    }
