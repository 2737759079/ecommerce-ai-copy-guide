from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, func, JSON
from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    rating = Column(Integer, default=5)
    content = Column(Text, default="")
    sentiment = Column(String(16), default="neutral")  # positive / neutral / negative
    source = Column(String(16), default="user")  # user / merchant
    images = Column(JSON, default=list)
    video_url = Column(String(512), default="")
    created_at = Column(DateTime, server_default=func.now())
