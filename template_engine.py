from typing import Union, Mapping

from models import LeadDetails


def generate_reply(details: Union[LeadDetails, Mapping[str, str]]):
    if isinstance(details, dict):
        # Backward compatibility if called with the old dict structure
        name = details.get("name", "Client") or "Client"
        zip_code = details.get("zip", "Unknown") or "Unknown"
        when = details.get("when", "Unknown") or "Unknown"
        move_type = details.get("type", "moving") or "moving"
    else:
        name = details.safe_name
        zip_code = details.safe_zip
        when = details.safe_when
        move_type = details.move_type or "moving"

    missing = []
    if zip_code == "Unknown":
        missing.append("ZIP code")
    if when == "Unknown":
        missing.append("date/time window")

    missing_block = ""
    if missing:
        missing_block = "\nNote: I didn't see your " + ", ".join(missing) + ". Please include it if possible."

    return f"""Hi {name},

Thanks for reaching out to Beezee Movers!

To provide an accurate quote for your {move_type} request in ZIP code {zip_code} ({when}), could you please let us know:
- Number of rooms or estimated item volume?
- Any heavy items (like safes, pianos)?
- Stairs or elevator access at pickup and delivery?{missing_block}

We can also do a quick phone call if easier.

Best,
Artem from Beezee Movers"""
