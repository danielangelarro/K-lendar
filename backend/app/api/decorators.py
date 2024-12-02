import inject
from fastapi import Request
from fastapi import HTTPException
from functools import wraps
from app.infrastructure.services.auth_service import AuthService


def require_authentication(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get('request') or args[0]        
        token = request.headers.get("Authorization")

        if token is None:
            raise HTTPException(status_code=401, detail="Not authenticated")

        token = token.split(" ")[1]
        auth_service: AuthService = inject.instance(AuthService)
        current_user = await auth_service.get_current_user_dependency(token)
        request.state.current_user = current_user

        return await func(*args, **kwargs)

    return wrapper
