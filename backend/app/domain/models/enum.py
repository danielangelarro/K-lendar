from enum import Enum as PyEnum


class UserRole(PyEnum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class EventType(PyEnum):
    PERSONAL = "personal"
    GROUP = "group"
    HIERARCHICAL = "hierarchical"


class EventStatus(PyEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
