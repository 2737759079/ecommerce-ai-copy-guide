from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, func, JSON
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    display_id = Column(String(16), unique=True, index=True, default="")
    name = Column(String(255), nullable=False)
    category = Column(String(64), default="")
    description = Column(Text, default="")
    price = Column(Float, default=0.0)
    stock = Column(Integer, default=0)
    status = Column(String(16), default="off")  # on / off / deleted
    specs = Column(JSON, default=list)
    images = Column(JSON, default=list)
    video_url = Column(String(512), default="")
    ai_title = Column(String(255), default="")
    ai_selling_points = Column(Text, default="")
    ai_detail = Column(Text, default="")
    ai_slogan = Column(String(512), default="")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
