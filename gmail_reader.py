import os
import imaplib
import email
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from email.header import decode_header
from typing import Optional

from logger import get_logger

load_dotenv()
logger = get_logger(__name__)

EMAIL = os.getenv("EMAIL_ADDRESS")
APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
IMAP_SERVER = os.getenv("EMAIL_IMAP_SERVER", "imap.gmail.com")
IMAP_PORT = int(os.getenv("EMAIL_IMAP_PORT", 993))
PROCESSED_FILE = os.getenv("PROCESSED_FILE", "processed_emails.txt")
SAVE_LAST_EMAIL = os.getenv("SAVE_LAST_EMAIL", "false").lower() in {"1", "true", "yes", "y"}

# 🔍 Декодируем тему письма корректно
def decode_mime_words(subject_value: Optional[str]) -> str:
    if not subject_value:
        return ""
    decoded_fragments = decode_header(subject_value)
    return ''.join([
        fragment.decode(encoding or "utf-8", errors="ignore") if isinstance(fragment, bytes) else str(fragment)
        for fragment, encoding in decoded_fragments
    ])

# Проверка, обрабатывали ли мы это письмо
def is_processed(message_id: Optional[str]) -> bool:
    if not message_id:
        return False
    if not os.path.exists(PROCESSED_FILE):
        return False
    try:
        with open(PROCESSED_FILE, "r", encoding="utf-8") as file_handle:
            existing = {line.strip() for line in file_handle if line.strip()}
            return message_id in existing
    except Exception as error:
        logger.warning("Failed to read processed file: %s", error)
        return False

# Отметить письмо как обработанное
def mark_as_processed(message_id: Optional[str]) -> None:
    if not message_id:
        return
    try:
        with open(PROCESSED_FILE, "a", encoding="utf-8") as file_handle:
            file_handle.write(message_id + "\n")
    except Exception as error:
        logger.warning("Failed to write processed message id: %s", error)

# 📬 Главная функция — получить последнее письмо от Yelp
def fetch_latest_email() -> Optional[str]:
    mail = None
    try:
        # Validate credentials early to avoid NoneType errors inside imaplib
        if not EMAIL or not APP_PASSWORD:
            logger.warning("EMAIL_ADDRESS or EMAIL_APP_PASSWORD is not set in environment. Skipping IMAP fetch.")
            return None
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL, APP_PASSWORD)
        mail.select("inbox")

        search_criteria = '(FROM "@r.yelp.com" SUBJECT "New Lead: Reply to")'
        status, messages = mail.search(None, search_criteria)
        if status != "OK":
            logger.info("Search returned status %s. No messages.", status)
            return None

        email_ids = messages[0].split() if messages and messages[0] else []

        if not email_ids:
            logger.info("No new messages by filter.")
            return None

        for email_id in reversed(email_ids):
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            if status != "OK" or not msg_data:
                logger.warning("Failed to fetch message %s: %s", email_id, status)
                continue

            raw_email = msg_data[0][1]
            if not raw_email:
                logger.warning("Empty raw email for id %s", email_id)
                continue

            msg = email.message_from_bytes(raw_email)

            subject_raw = msg.get("Subject", "[NO SUBJECT]")
            subject = decode_mime_words(subject_raw)

            message_id = msg.get("Message-ID") or f"NO-ID-{email_id.decode('utf-8', errors='ignore')}"

            logger.info("Processing message | Subject='%s' | Message-ID=%s", subject, message_id)

            if is_processed(message_id):
                logger.info("Already processed. Skipping.")
                continue

            if not subject.startswith("New Lead: Reply to"):
                logger.info("Subject does not match expected lead pattern: %s", subject)
                continue

            # Try HTML first, then plain text fallback
            extracted_text = None
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                logger.debug("Part content-type=%s disposition=%s", content_type, content_disposition)

                if content_type in ("text/html", "text/plain") and "attachment" not in content_disposition:
                    try:
                        payload = part.get_payload(decode=True)
                        if not payload:
                            logger.debug("Empty payload for part type=%s", content_type)
                            continue
                        body = payload.decode(errors="ignore")
                        if content_type == "text/html":
                            soup = BeautifulSoup(body, "html.parser")
                            text = soup.get_text(separator="\n")
                        else:
                            text = body
                        if text and text.strip():
                            extracted_text = text
                            break
                    except Exception as error:
                        logger.exception("Error while parsing message part: %s", error)
                        continue

            if extracted_text and extracted_text.strip():
                if SAVE_LAST_EMAIL:
                    try:
                        with open("last_email.txt", "w", encoding="utf-8") as fh:
                            fh.write(extracted_text)
                    except Exception as save_error:
                        logger.debug("Failed to save last email text: %s", save_error)
                mark_as_processed(message_id)
                return extracted_text
            else:
                logger.info("Parsed message but text is empty. Skipping message %s", message_id)

        return None

    except Exception as error:
        logger.exception("Error while fetching emails: %s", error)
        return None
    finally:
        try:
            if mail is not None:
                mail.logout()
        except Exception:
            pass
