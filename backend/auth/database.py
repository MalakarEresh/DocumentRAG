from sqlalchemy import String, Column
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from database.models import Base 

class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    
    name = Column(String, nullable=False)