from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, func
from app.database import Base


class CustomerServiceMessage(Base):
    __tablename__ = "customer_service_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    sender_role = Column(String(16), default="user")  # user / merchant
    content = Column(Text, default="")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
