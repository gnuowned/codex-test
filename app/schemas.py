from dataclasses import dataclass, field
from typing import Optional


def _validate_length(value: Optional[str], max_length: int, field_name: str) -> Optional[str]:
    if value is None:
        return None
    if len(value) > max_length:
        raise ValueError(f"{field_name} exceeds {max_length} characters")
    return value


def _validate_email(email: str) -> str:
    if "@" not in email or email.startswith("@"):
        raise ValueError("email must contain '@' and a local part")
    return email


@dataclass
class CustomerCreate:
    name: str
    email: str
    phone: Optional[str] = None
    status: str = "active"
    notes: Optional[str] = None

    def validate(self) -> "CustomerCreate":
        self.name = _validate_length(self.name, 200, "name") or self.name
        self.email = _validate_email(self.email)
        self.phone = _validate_length(self.phone, 50, "phone") or self.phone
        self.status = _validate_length(self.status, 50, "status") or self.status
        self.notes = _validate_length(self.notes, 500, "notes") or self.notes
        return self


@dataclass
class CustomerUpdate:
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

    def validate(self) -> "CustomerUpdate":
        self.name = _validate_length(self.name, 200, "name") or self.name
        if self.email is not None:
            self.email = _validate_email(self.email)
        self.phone = _validate_length(self.phone, 50, "phone") or self.phone
        self.status = _validate_length(self.status, 50, "status") or self.status
        self.notes = _validate_length(self.notes, 500, "notes") or self.notes
        if not any([self.name, self.email, self.phone, self.status, self.notes]):
            raise ValueError("no fields provided for update")
        return self


@dataclass
class Customer:
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    status: str = "active"
    notes: Optional[str] = None

    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "status": self.status,
            "notes": self.notes,
        }
