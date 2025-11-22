from fastapi_users.schemas import PYDANTIC_V2
from pydantic import BaseModel, Field

if PYDANTIC_V2:
    from pydantic import ConfigDict

class UserRead(BaseModel):
    if PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True
            
    id: str
    email: str
    name: str
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(BaseModel):
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., min_length=6)
    name: str = Field(..., example="John Doe")