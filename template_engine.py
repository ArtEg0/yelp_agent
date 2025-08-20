def generate_reply(details):
    name = details.get("name", "Client") or "Client"
    zip_code = details.get("zip", "Unknown") or "Unknown"
    when = details.get("when", "Unknown") or "Unknown"
    move_type = details.get("type", "moving") or "moving"

    return f"""Hi {name},

Thanks for reaching out to Beezee Movers!

To provide an accurate quote for your {move_type} request in ZIP code {zip_code} ({when}), could you please let us know:
- Number of rooms or estimated item volume?
- Any heavy items (like safes, pianos)?
- Stairs or elevator access at pickup and delivery?

We can also do a quick phone call if easier.

Best,
Artem from Beezee Movers"""
