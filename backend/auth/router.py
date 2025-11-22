from fastapi import APIRouter
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport, JWTStrategy, AuthenticationBackend
from auth.database import User
from auth.manager import get_user_manager
from auth.schemas import UserRead, UserCreate
import uuid

# Cookie + JWT auth
cookie_transport = CookieTransport(
    cookie_name="rag_auth",
    cookie_max_age=3600 * 24 * 30,  
    cookie_secure=False, 
    cookie_httponly=True,
    cookie_samesite="lax"
)

def get_jwt_strategy() -> JWTStrategy:
    from config import settings
    return JWTStrategy(secret=settings.JWT_SECRET_KEY, lifetime_seconds=3600*24*30)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

auth_router = APIRouter(prefix="/auth", tags=["auth"])

# Register, login, logout routes
auth_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt"
)
auth_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate)
)


auth_router.include_router(
    fastapi_users.get_users_router(UserRead, UserRead),
    prefix="/users",
    tags=["users"]
)


current_active_user = fastapi_users.current_user(active=True)