import os
import imaplib
import email
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from email.header import decode_header

load_dotenv()

EMAIL = os.getenv("EMAIL_ADDRESS")
APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
IMAP_SERVER = os.getenv("EMAIL_IMAP_SERVER", "imap.gmail.com")
IMAP_PORT = int(os.getenv("EMAIL_IMAP_PORT", 993))
PROCESSED_FILE = "processed_emails.txt"

# 🔍 Декодируем тему письма корректно
def decode_mime_words(s):
    if not s:
        return ""
    decoded_fragments = decode_header(s)
    return ''.join([
        fragment.decode(encoding or "utf-8") if isinstance(fragment, bytes) else fragment
        for fragment, encoding in decoded_fragments
    ])

# Проверка, обрабатывали ли мы это письмо
def is_processed(message_id):
    if not message_id:
        return False
    if not os.path.exists(PROCESSED_FILE):
        return False
    with open(PROCESSED_FILE, "r") as f:
        return message_id in f.read()

# Отметить письмо как обработанное
def mark_as_processed(message_id):
    if not message_id:
        return
    with open(PROCESSED_FILE, "a") as f:
        f.write(message_id + "\n")

# 📬 Главная функция — получить последнее письмо от Yelp
def fetch_latest_email():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL, APP_PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, '(FROM "@r.yelp.com" SUBJECT "New Lead: Reply to")')
        email_ids = messages[0].split()

        if not email_ids:
            print("📭 Нет новых писем по фильтру.")
            return None

        for email_id in reversed(email_ids):
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject_raw = msg.get("Subject", "[NO SUBJECT]")
            subject = decode_mime_words(subject_raw)

            message_id = msg.get("Message-ID")
            if not message_id:
                message_id = f"NO-ID-{email_id.decode('utf-8')}"

            print("📩 Обработка письма:")
            print("• Subject:", subject)
            print("• Message-ID:", message_id)

            if is_processed(message_id):
                print("🔁 Уже обработано, пропускаем.")
                continue

            if not subject.startswith("New Lead: Reply to"):
                print("⚠️ Тема не соответствует: ", subject)
                continue

            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                print("🔍 Контент:", content_type)

                if content_type == "text/html" and "attachment" not in content_disposition:
                    try:
                        payload = part.get_payload(decode=True)
                        if not payload:
                            print("⚠️ Пустой HTML payload.")
                            continue
                        html_body = payload.decode(errors="ignore")
                        soup = BeautifulSoup(html_body, "html.parser")
                        text = soup.get_text(separator="\n")
                        if text and len(text.strip()) > 0:
                            mark_as_processed(message_id)
                            return text
                        else:
                            print("⚠️ HTML распаршен, но текст пуст.")
                    except Exception as e:
                        print("❌ Ошибка при разборе HTML:", e)

        return None

    except Exception as e:
        print("❗ Ошибка при получении письма:", e)
        return None
