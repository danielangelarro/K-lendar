from enum import Enum as TypeEnum

from sqlalchemy import Enum
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import Integer
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from app.domain.models.enum import UserRole
from app.domain.models.enum import EventType
from app.domain.models.enum import EventStatus


Base = declarative_base()


class TablesNames(TypeEnum):
    USER = "users"
    GROUP = "groups"
    GROUP_MEMBER = "group_members"
    EVENT = "events"
    EVENT_INVITATION = "event_invitations"


class SQLAlchemyBaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id})>"


class User(SQLAlchemyBaseModel):
    __tablename__ = TablesNames.USER.value

    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    
    events = relationship("Event", back_populates="creator")
    group_memberships = relationship("GroupMember", back_populates="user")
    event_invitations = relationship("EventInvitation", back_populates="user")


class Group(SQLAlchemyBaseModel):
    __tablename__ = TablesNames.GROUP.value

    name = Column(String)
    description = Column(String)
    is_hierarchical = Column(Boolean, default=False)
    
    members = relationship("GroupMember", back_populates="group")
    events = relationship("Event", back_populates="group")


class GroupMember(SQLAlchemyBaseModel):
    __tablename__ = TablesNames.GROUP_MEMBER.value

    group_id = Column(Integer, ForeignKey("groups.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String)
    
    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="group_memberships")


class Event(SQLAlchemyBaseModel):
    __tablename__ = TablesNames.EVENT.value

    title = Column(String)
    description = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    event_type = Column(Enum(EventType))
    status = Column(Enum(EventStatus), default=EventStatus.PENDING)
    
    creator_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    
    creator = relationship("User", back_populates="events")
    group = relationship("Group", back_populates="events")
    invitations = relationship("EventInvitation", back_populates="event")


class EventInvitation(SQLAlchemyBaseModel):
    __tablename__ = TablesNames.EVENT_INVITATION.value

    event_id = Column(Integer, ForeignKey("events.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(EventStatus), default=EventStatus.PENDING)
    
    event = relationship("Event", back_populates="invitations")
    user = relationship("User", back_populates="event_invitations")
