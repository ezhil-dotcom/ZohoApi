import os
import sys
import logging
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import requests

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "daily_sync.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
    force=True,
)

from zoho_analytics import get_view_data
from sql_loader import push_rows


def send_email(subject: str, body: str):
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "465"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    to = os.getenv("NOTIFY_TO")

    if not (host and user and password and to):
        logging.warning("Email not configured, skipping notification")
        return

    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL(host, port, timeout=30) as server:
            server.login(user, password)
            server.send_message(msg)
        logging.info("Notification email sent to %s", to)
    except Exception:
        logging.exception("Could not send notification email")
def send_webhook(text: str):
    url = os.getenv("NOTIFY_WEBHOOK_URL")
    if not url:
        return
    try:
        requests.post(url, json={"text": text}, timeout=30)
        logging.info("Webhook notification sent")
    except Exception:
        logging.exception("Could not send webhook notification")

def main():
    logging.info("Daily sync started")

    org_id = os.getenv("ZOHO_ORG_ID")
    workspace_id = os.getenv("ZOHO_WORKSPACE_ID")
    view_id = os.getenv("ZOHO_VIEW_ID")
    table_name = os.getenv("SQL_TABLE_NAME", "Bently_VJ")

    if not (org_id and workspace_id and view_id):
        raise Exception("ZOHO_ORG_ID, ZOHO_WORKSPACE_ID or ZOHO_VIEW_ID is missing in .env")

    result = get_view_data(org_id, workspace_id, view_id, max_wait=600)
    rows = result.get("data", [])
    if not isinstance(rows, list):
        raise Exception(f"Unexpected data shape: {type(rows)}")

    info = push_rows(table_name, rows)   # adds only rows with a new ID
    logging.info(
        "Done: received %s, inserted %s, skipped %s",
        info["received"], info["inserted"], info["skipped"],
    )
    return info


if __name__ == "__main__":
    try:
        info = main()
        # if os.getenv("NOTIFY_ON_SUCCESS", "true").lower() == "true":
            # send_email(
            #     f"Bently sync OK: {info['inserted']} new rows",
            #     f"The daily Zoho to SQL sync finished.\n\n"
            #     f"Received from Zoho: {info['received']}\n"
            #     f"New rows added to SQL: {info['inserted']}\n"
            #     f"Already existed (skipped): {info['skipped']}\n",
            # )
    except Exception as e:
        logging.exception("Daily sync FAILED: %s", e)
        send_email("Bently sync FAILED", f"The daily Zoho to SQL sync failed.\n\nError:\n{e}")
        sys.exit(1)