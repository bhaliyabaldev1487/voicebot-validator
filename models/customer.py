from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Customer:
    site_user_id: int
    first_name: str
    last_name: str
    email: Optional[str]
    phone_no: Optional[str]
    mobile: Optional[str]

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def to_dict(self) -> dict:
        return {
            "site_user_id": self.site_user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "email": self.email,
            "phone_no": self.phone_no,
            "mobile": self.mobile,
        }