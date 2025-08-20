from gmail_reader import fetch_latest_email
from yelp_parser import extract_details
from template_engine import generate_reply
from logger import get_logger

logger = get_logger(__name__)

def main():
    logger.info("Reading latest Yelp email...")
    email_body = None
    # Try IMAP first
    try:
        email_body = fetch_latest_email()
    except Exception as error:
        logger.exception("Reader crashed: %s", error)

    if email_body is None:
        # Fallback: if last_email.txt exists (saved earlier or provided manually), use it
        try:
            with open("last_email.txt", "r", encoding="utf-8") as fh:
                email_body = fh.read()
            logger.info("Loaded email content from last_email.txt fallback.")
        except Exception:
            logger.warning("Email not found or no matching content.")
            return

    try:
        preview = email_body[:1500] if isinstance(email_body, str) else str(email_body)
        logger.debug("Email preview: %s", preview)
    except Exception as error:
        logger.exception("Failed to preview email body: %s", error)
        return

    logger.info("Extracting details...")
    details = extract_details(email_body)

    logger.info("Generating reply...")
    reply = generate_reply(details)

    print("\nSuggested reply:\n")
    print(reply)

if __name__ == "__main__":
    main()
