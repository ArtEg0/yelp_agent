import re
from typing import Optional

from logger import get_logger
from models import LeadDetails

logger = get_logger(__name__)


def _extract_name(text: str) -> Optional[str]:
    # Try several patterns that appear across various Yelp formats
    patterns = [
        r"^([A-Z][a-zA-Z\-']+)\s+[A-Z][a-zA-Z\-']+\srequested",  # "John M requested"
        r"^([A-Z][a-zA-Z\-']+)\srequested",  # "John requested"
        r"Name:\s*([A-Za-z][A-Za-z\-']+)",
        r"^From:\s*([A-Za-z][A-Za-z\-']+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.MULTILINE)
        if match:
            return match.group(1)
    return None


def _extract_zip(text: str) -> Optional[str]:
    match = re.search(r"\b(?:ZIP|Zip|Postal)\s*Code:?\s*(\d{5})(?:-\d{4})?\b", text)
    if match:
        return match.group(1)
    # Try common pattern like "Los Angeles, CA 90012"
    match = re.search(r"\bCA\s*(\d{5})\b", text)
    return match.group(1) if match else None


def _extract_when(text: str) -> Optional[str]:
    # Look for natural words like Today/Tomorrow/This weekend, or a date
    match = re.search(r"Availability:?\s*([A-Za-z]+(?:\s+[A-Za-z]+)?)", text)
    if match:
        return match.group(1)
    match = re.search(r"Preferred\s*date:?\s*([A-Za-z0-9,\-/ ]+)", text)
    if match:
        return match.group(1).strip()
    return None


def _extract_move_type(text: str) -> str:
    if re.search(r"In-?state\s*moving", text, flags=re.IGNORECASE):
        return "in-state"
    if re.search(r"Local\s*moving", text, flags=re.IGNORECASE):
        return "local"
    if re.search(r"Long\s*distance", text, flags=re.IGNORECASE):
        return "long-distance"
    return "moving"


def extract_details(text: Optional[str]) -> LeadDetails:
    if not text or not isinstance(text, str):
        return LeadDetails()

    try:
        name = _extract_name(text) or "Client"
        zip_code = _extract_zip(text)
        when = _extract_when(text)
        move_type = _extract_move_type(text)

        return LeadDetails(name=name, zip_code=zip_code, when=when, move_type=move_type)
    except Exception as error:
        logger.exception("Parsing error: %s", error)
        return LeadDetails()
