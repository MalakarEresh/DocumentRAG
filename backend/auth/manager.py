from fastapi_users import BaseUserManager, UUIDIDMixin
from auth.database import User
from config import settings
import uuid

SECRET = settings.JWT_SECRET_KEY  

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

async def get_user_manager():
    yield UserManager()

