import os
import shutil
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.user import User
from app.models.order import Order

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")


def ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_DIR, "images"), exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_DIR, "videos"), exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_DIR, "avatars"), exist_ok=True)


def save_upload_file(file: UploadFile, subfolder: str) -> str:
    ensure_upload_dir()
    ext = os.path.splitext(file.filename or "")[1].lower()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    filename = f"{timestamp}{ext}"
    path = os.path.join(UPLOAD_DIR, subfolder, filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return f"/uploads/{subfolder}/{filename}"


def generate_product_display_id(db: Session) -> str:
    count = db.query(Product).count()
    return f"{count + 1:05d}"


def generate_user_display_id(db: Session) -> str:
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(User).filter(User.display_id.like(f"{today}%")).count()
    return f"{today}{count + 1:07d}"


def generate_order_no(db: Session, product_id: int) -> str:
    now = datetime.now()
    product = db.query(Product).filter(Product.id == product_id).first()
    product_display = product.display_id if product and product.display_id else f"{product_id:05d}"
    seq = db.query(Order).filter(Order.order_no.like(f"{now.strftime('%Y%m%d%H%M%S')}{product_display}%")).count() + 1
    return f"{now.strftime('%Y%m%d%H%M%S')}{product_display}{seq:05d}"
