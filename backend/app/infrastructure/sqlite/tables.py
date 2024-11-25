from enum import Enum as TypeEnum

from sqlalchemy import Enum
from sqlalchemy import Column
from sqlalchemy import String
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
    EVENT = "events"
    GROUP = "groups"
    USER_EVENT = "user_event"
    MEMBER = "member"
    NOTIFICATION = "notification"


class SQLAlchemyBaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id})>"


class User(SQLAlchemyBaseModel):
    __tablename__ = TablesNames.USER.value
    
    username = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    password = Column(String(255), comment='Encrypted')

    created_events = relationship('Event', back_populates='creator_rel', foreign_keys='Event.creator')
    participations = relationship('UserEvent', back_populates='user_rel')
    sent_notifications = relationship('Notification', back_populates='sender_rel', foreign_keys='Notification.sender')
    received_notifications = relationship('Notification', back_populates='recipient_rel', foreign_keys='Notification.recipient')
    memberships = relationship('Member', back_populates='user_rel')


class Event(SQLAlchemyBaseModel):
    __tablename__ = TablesNames.EVENT.value
    
    title = Column(String(255), nullable=False)
    description = Column(String)
    start_datetime = Column(DateTime(timezone=True))
    end_datetime = Column(DateTime(timezone=True))
    creator = Column(Integer, ForeignKey('users.id'), nullable=False)

    creator_rel = relationship('User', back_populates='created_events')
    participations = relationship('UserEvent', back_populates='event_rel')
    notifications = relationship('Notification', back_populates='event_rel')


class Group(SQLAlchemyBaseModel):
    __tablename__ = TablesNames.GROUP.value
    
    group_name = Column(String(255))
    parent_group = Column(Integer, ForeignKey('groups.id'))

    subgroups = relationship('Group', backref='parent_group_rel', remote_side=[id])
    members = relationship('Member', back_populates='group_rel')


class UserEvent(SQLAlchemyBaseModel):
    __tablename__ = TablesNames.USER_EVENT.value
    
    user_id = Column(Integer, ForeignKey('users.id'))
    event_id = Column(Integer, ForeignKey('events.id'))
    status = Column(Enum('Accepted', 'Pending', 'Cancelled', name="status_enum"), default=EventStatus.PENDING)

    user_rel = relationship('User', back_populates='participations')
    event_rel = relationship('Event', back_populates='participations')


class Member(SQLAlchemyBaseModel):
    __tablename__ = TablesNames.MEMBER.value
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)

    user_rel = relationship('User', back_populates='memberships')
    group_rel = relationship('Group', back_populates='members')


class Notification(SQLAlchemyBaseModel):
    __tablename__ = TablesNames.NOTIFICATION.value
    
    recipient = Column(Integer, ForeignKey('users.id'), nullable=False)
    sender = Column(Integer, ForeignKey('users.id'), nullable=False)
    event = Column(Integer, ForeignKey('events.id'), nullable=False)

    recipient_rel = relationship('User', foreign_keys=[recipient], back_populates='received_notifications')
    sender_rel = relationship('User', foreign_keys=[sender], back_populates='sent_notifications')
    event_rel = relationship('Event', back_populates='notifications')
