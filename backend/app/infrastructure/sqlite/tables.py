from enum import Enum as TypeEnum

from app.infrastructure.sqlite.utils import generate_uuid
from sqlalchemy import Enum
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from app.domain.models.enum import EventStatus


Base = declarative_base()


class TablesNames(TypeEnum):
    USER = "users"
    EVENT = "events"
    GROUP_HIERARCHY = "group_hierarchy"
    GROUP = "groups"
    USER_EVENT = "user_event"
    MEMBER = "member"
    NOTIFICATION = "notification"


class SQLAlchemyBaseModel(Base):
    __abstract__ = True

    id = Column(String(36), primary_key=True, index=True, default=lambda: generate_uuid())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id})>"

class User(SQLAlchemyBaseModel):
    __tablename__ = TablesNames.USER.value

    username = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    password = Column(String(255), comment="Encrypted")

    created_events = relationship(
        "Event",
        back_populates="creator_rel",
        foreign_keys="Event.creator",
        cascade="all, delete-orphan",
    )
    participations = relationship(
        "UserEvent", back_populates="user_rel", cascade="all, delete-orphan"
    )
    sent_notifications = relationship(
        "Notification",
        back_populates="sender_rel",
        foreign_keys="Notification.sender",
        cascade="all, delete-orphan",
    )
    received_notifications = relationship(
        "Notification",
        back_populates="recipient_rel",
        foreign_keys="Notification.recipient",
        cascade="all, delete-orphan",
    )
    memberships = relationship(
        "Member", back_populates="user_rel", cascade="all, delete-orphan"
    )
    owned_groups = relationship(
        "Group", back_populates="owner", cascade="all, delete-orphan"
    )


class Event(SQLAlchemyBaseModel):
    __tablename__ = TablesNames.EVENT.value

    title = Column(String(255), nullable=False)
    description = Column(String)
    start_datetime = Column(DateTime(timezone=True))
    end_datetime = Column(DateTime(timezone=True))
    event_type = Column(
        Enum("personal", "group", "hierarchical", name="event_type"), default="personal"
    )
    creator = Column(String(36), ForeignKey("users.id"), nullable=False)

    creator_rel = relationship("User", back_populates="created_events")
    participations = relationship(
        "UserEvent", back_populates="event_rel", cascade="all, delete-orphan"
    )
    notifications = relationship(
        "Notification", back_populates="event_rel", cascade="all, delete-orphan"
    )


class GroupHierarchy(SQLAlchemyBaseModel):
    __tablename__ = TablesNames.GROUP_HIERARCHY.value

    parent_group_id = Column(String(36), ForeignKey("groups.id"), primary_key=True)
    child_group_id = Column(String(36), ForeignKey("groups.id"), primary_key=True)

    parent_group = relationship(
        "Group",
        foreign_keys=[parent_group_id],
        back_populates="parent_hierarchies",
        cascade="all, delete-orphan",
        single_parent=True,
    )
    child_group = relationship(
        "Group",
        foreign_keys=[child_group_id],
        back_populates="child_hierarchies",
        cascade="all, delete-orphan",
        single_parent=True,
    )


class Group(SQLAlchemyBaseModel):
    __tablename__ = TablesNames.GROUP.value

    group_name = Column(String(255))
    description = Column(String(500))
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="owned_groups")
    members = relationship(
        "Member", back_populates="group_rel", cascade="all, delete-orphan"
    )
    user_events = relationship(
        "UserEvent", back_populates="group_rel", cascade="all, delete-orphan"
    )
    parent_hierarchies = relationship(
        "GroupHierarchy",
        foreign_keys=[GroupHierarchy.parent_group_id],
        back_populates="parent_group",
        cascade="all, delete-orphan",
    )
    child_hierarchies = relationship(
        "GroupHierarchy",
        foreign_keys=[GroupHierarchy.child_group_id],
        back_populates="child_group",
        cascade="all, delete-orphan",
    )


class UserEvent(SQLAlchemyBaseModel):
    __tablename__ = TablesNames.USER_EVENT.value

    user_id = Column(String(36), ForeignKey("users.id"))
    event_id = Column(String(36), ForeignKey("events.id"))
    group_id = Column(String(36), ForeignKey("groups.id"))

    status = Column(
        Enum("confirmed", "pending", "cancelled", name="status_enum"),
        default=EventStatus.PENDING,
    )

    user_rel = relationship("User", back_populates="participations")
    event_rel = relationship("Event", back_populates="participations")
    group_rel = relationship("Group", back_populates="user_events")


class Member(SQLAlchemyBaseModel):
    __tablename__ = TablesNames.MEMBER.value

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    group_id = Column(String(36), ForeignKey("groups.id"), nullable=False)

    user_rel = relationship("User", back_populates="memberships")
    group_rel = relationship("Group", back_populates="members")


class Notification(SQLAlchemyBaseModel):
    __tablename__ = TablesNames.NOTIFICATION.value

    recipient = Column(String(36), ForeignKey("users.id"), nullable=False)
    sender = Column(String(36), ForeignKey("users.id"), nullable=False)
    event = Column(String(36), ForeignKey("events.id"))
    message = Column(String(500), default="")
    is_read = Column(Boolean, default=False)
    priority = Column(Boolean, default=True)
    title = Column(String(36), default="Info")

    recipient_rel = relationship(
        "User", foreign_keys=[recipient], back_populates="received_notifications"
    )
    sender_rel = relationship(
        "User", foreign_keys=[sender], back_populates="sent_notifications"
    )
    event_rel = relationship("Event", back_populates="notifications")
