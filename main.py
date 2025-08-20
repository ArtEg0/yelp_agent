from gmail_reader import fetch_latest_email
from yelp_parser import extract_details
from template_engine import generate_reply

def main():
    print("\nReading latest Yelp email...")

    email_body = fetch_latest_email()

    if email_body is None:
        print("⚠️ Email не найден или не содержит подходящего контента.")
        return

    print("\n--- Raw Email Content ---\n")

    # Добавим защиту от None и покажем первые символы
    try:
        preview = email_body[:3000] if isinstance(email_body, str) else str(email_body)
        print(preview)
    except Exception as e:
        print(f"❗ Ошибка при выводе email_body: {e}")
        return

    print("\n-------------------------\n")

    print("Extracting details...")
    details = extract_details(email_body)

    print("Generating reply...")
    reply = generate_reply(details)

    print("\nSuggested reply:\n")
    print(reply)

if __name__ == "__main__":
    main()
