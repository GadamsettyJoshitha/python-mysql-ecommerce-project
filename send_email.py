import smtplib
from email.message import EmailMessage
from getpass import getpass
from mimetypes import guess_type
from pathlib import Path

from dynamic_table import read_ecommerce_excel
from generate_report import generate_customer_report
from config.config import EMAIL_CONFIG, REPORT_OUTPUT


DEFAULT_SUBJECT = "Your E-Commerce Order Report"
DEFAULT_BODY = """Hello,

Please find your personal e-commerce order report attached.

Regards,
E-Commerce Reporting System"""

EMAIL_COLUMN_CANDIDATES = ("customer_email", "email", "mail", "receiver_email")


def value_or_default(value, default):
    return value.strip() if value and value.strip() else default


def create_email_message(sender, receiver, subject, body, attachment_path=None):
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = receiver
    message.set_content(body)

    if attachment_path:
        attachment_path = Path(attachment_path)
        if attachment_path.exists():
            content_type, _ = guess_type(attachment_path)
            maintype, subtype = (content_type or "application/octet-stream").split("/", 1)
            message.add_attachment(
                attachment_path.read_bytes(),
                maintype=maintype,
                subtype=subtype,
                filename=attachment_path.name,
            )

    return message


def send_email(
    sender=None,
    receiver=None,
    password=None,
    subject=DEFAULT_SUBJECT,
    body=DEFAULT_BODY,
    attachment_path=None,
    smtp_host=None,
    smtp_port=None,
):
    sender = value_or_default(sender, EMAIL_CONFIG["sender"])
    receiver = value_or_default(receiver, EMAIL_CONFIG["receiver"])
    password = value_or_default(password, EMAIL_CONFIG["password"])
    smtp_host = value_or_default(smtp_host, EMAIL_CONFIG["smtp_host"])
    smtp_port = int(smtp_port or EMAIL_CONFIG["smtp_port"])
    smtp_timeout = int(EMAIL_CONFIG["smtp_timeout"])

    if not sender or not receiver or not password:
        return False

    message = create_email_message(
        sender=sender,
        receiver=receiver,
        subject=subject,
        body=body,
        attachment_path=attachment_path,
    )

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=smtp_timeout) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(message)
    except (smtplib.SMTPException, OSError) as exc:
        print(f"Email skipped. SMTP error: {exc}")
        return False

    return True


def send_report_email(report_path=REPORT_OUTPUT):
    return send_email(attachment_path=report_path)


def get_customer_email_addresses():
    df = read_ecommerce_excel()
    email_column = next(
        (column for column in EMAIL_COLUMN_CANDIDATES if column in df.columns),
        None,
    )

    if not email_column:
        return []

    emails = []
    seen = set()
    for value in df[email_column].dropna():
        email = str(value).strip()
        if "@" in email and email not in seen:
            emails.append(email)
            seen.add(email)

    return emails


def send_customer_report_emails(report_path=REPORT_OUTPUT):
    receivers = get_customer_email_addresses()

    if not receivers:
        print(
            "Customer emails skipped. Add a Customer_Email column in the Excel file "
            "to send individual customer emails."
        )
        return 0

    sent_count = 0
    sender = EMAIL_CONFIG["sender"].strip()
    password = EMAIL_CONFIG["password"].strip()
    smtp_host = EMAIL_CONFIG["smtp_host"].strip()
    smtp_port = int(EMAIL_CONFIG["smtp_port"])
    smtp_timeout = int(EMAIL_CONFIG["smtp_timeout"])

    if not sender or not password:
        return 0

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=smtp_timeout) as server:
            server.starttls()
            server.login(sender, password)

            for receiver in receivers:
                customer_report_path = generate_customer_report(receiver)
                if not customer_report_path:
                    print(f"Email skipped for {receiver}. No customer data found.", flush=True)
                    continue

                message = create_email_message(
                    sender=sender,
                    receiver=receiver,
                    subject=DEFAULT_SUBJECT,
                    body=DEFAULT_BODY,
                    attachment_path=customer_report_path,
                )
                server.send_message(message)
                sent_count += 1
                print(f"Customer report sent to {receiver}", flush=True)
    except (smtplib.SMTPException, OSError) as exc:
        print(f"Customer emails skipped. SMTP error: {exc}", flush=True)

    return sent_count


def ask_multiline_body():
    print("Enter email body. Press Enter on an empty line to finish.")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines) if lines else DEFAULT_BODY


def send_dynamic_email():
    print("Dynamic SMTP Email Sender")
    print("Leave any field blank to use value from .env/config where available.")

    sender = input("Sender email: ")
    password = getpass("App password: ") if sender else ""
    receiver = input("Receiver email: ")
    subject = value_or_default(input("Subject: "), DEFAULT_SUBJECT)
    body = ask_multiline_body()
    attachment = value_or_default(input(f"Attachment path [{REPORT_OUTPUT}]: "), str(REPORT_OUTPUT))

    sent = send_email(
        sender=sender,
        receiver=receiver,
        password=password,
        subject=subject,
        body=body,
        attachment_path=attachment,
    )

    print("Email sent successfully." if sent else "Email skipped. Missing SMTP credentials.")


if __name__ == "__main__":
    send_dynamic_email()
