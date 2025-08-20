from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class LeadDetails:
    name: str = "Client"
    zip_code: Optional[str] = None
    when: Optional[str] = None
    move_type: str = "moving"  # e.g., "in-state", "local", etc.

    @property
    def safe_name(self) -> str:
        return self.name or "Client"

    @property
    def safe_zip(self) -> str:
        return self.zip_code or "Unknown"

    @property
    def safe_when(self) -> str:
        return self.when or "Unknown"

