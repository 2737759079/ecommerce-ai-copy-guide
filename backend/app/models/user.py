from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    display_id = Column(String(32), unique=True, index=True, default="")
    username = Column(String(64), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(64), unique=True, index=True, default="")
    avatar_url = Column(String(512), default="")
    role = Column(String(16), default="user")  # user / merchant
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
