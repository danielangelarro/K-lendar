import os
import socket
from pydantic import BaseSettings
from app.infrastructure.services.chord_service import ChordService


def configure(binder):    
    from app.application.services.user_service import IUserService
    from app.application.services.auth_service import IAuthService
    from app.application.services.event_service import IEventService
    from app.application.services.group_service import IGroupService
    from app.application.services.member_service import IMemberService
    from app.application.services.agenda_service import IAgendaService
    from app.application.services.invitation_service import IInvitationService
    from app.application.services.notification_service import INotificationService

    from app.application.repositories.user_repository import IUserRepository
    from app.application.repositories.event_repository import IEventRepository
    from app.application.repositories.group_repository import IGroupRepository
    from app.application.repositories.member_repository import IMemberRepository
    from app.application.repositories.agenda_repository import IAgendaRepository
    from app.application.repositories.invitation_repository import IInvitationRepository
    from app.application.repositories.notification_repository import INotificationRepository
    
    from app.infrastructure.services.user_service import UserService
    from app.infrastructure.services.auth_service import AuthService
    from app.infrastructure.services.event_service import EventService
    from app.infrastructure.services.group_service import GroupService
    from app.infrastructure.services.member_service import MemberService
    from app.infrastructure.services.agenda_service import AgendaService
    from app.infrastructure.services.invitation_service import InvitationService
    from app.infrastructure.services.notification_service import NotificationService
    
    from app.infrastructure.repositories.user_repository import UserRepository
    from app.infrastructure.repositories.event_repository import EventRepository
    from app.infrastructure.repositories.group_repository import GroupRepository
    from app.infrastructure.repositories.member_repository import MemberRepository
    from app.infrastructure.repositories.agenda_repository import AgendaRepository
    from app.infrastructure.repositories.invitation_repository import InvitationRepository
    from app.infrastructure.repositories.notification_repository import NotificationRepository


    # Services
    binder.bind(IUserService, UserService())
    binder.bind(IAuthService, AuthService())
    binder.bind(IEventService, EventService())
    binder.bind(IGroupService, GroupService())
    binder.bind(IMemberService, MemberService())
    binder.bind(IAgendaService, AgendaService())
    binder.bind(IInvitationService, InvitationService())
    binder.bind(INotificationService, NotificationService())

    # Repositories
    binder.bind(IUserRepository, UserRepository())
    binder.bind(IEventRepository, EventRepository())
    binder.bind(IGroupRepository, GroupRepository())
    binder.bind(IMemberRepository, MemberRepository())
    binder.bind(IAgendaRepository, AgendaRepository())
    binder.bind(IInvitationRepository, InvitationRepository())
    binder.bind(INotificationRepository, NotificationRepository())


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./database.sqlite")
    SECRET_KEY = os.getenv("SECRET_KEY", "tu_clave_secreta")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    IP = socket.gethostbyname(socket.gethostname())
    
    class Config:
        env_file = ".env"
    
    @property
    def chord_service(self):
        return ChordService(self.IP)

    @property
    def node(self):
        return self.chord_service.get_node()


settings = Settings()
