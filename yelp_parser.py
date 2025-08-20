import re

def extract_details(text):
    if not text or not isinstance(text, str):
        return {
            "name": "Client",
            "zip": "Unknown",
            "when": "Unknown",
            "type": "moving"
        }

    try:
        name_match = re.search(r"([A-Z][a-z]+)\sM\.\srequested", text)
        zip_match = re.search(r"ZIP Code:\s*(\d{5})", text)
        when_match = re.search(r"Availability:\s*([A-Za-z]+)", text)
        move_type = "in-state" if "In-state moving" in text else "moving"

        return {
            "name": name_match.group(1) if name_match else "Client",
            "zip": zip_match.group(1) if zip_match else "Unknown",
            "when": when_match.group(1) if when_match else "Unknown",
            "type": move_type
        }
    except Exception as e:
        print("❗ Ошибка в парсинге письма:", e)
        return {
            "name": "Client",
            "zip": "Unknown",
            "when": "Unknown",
            "type": "moving"
        }
