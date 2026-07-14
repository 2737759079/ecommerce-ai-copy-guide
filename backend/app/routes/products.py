from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import json
import io
import pandas as pd
from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.favorite import Favorite
from app.models.browse_history import BrowseHistory
from app.schemas import ProductCreate, ProductUpdate, ProductOut, FavoriteOut
from app.utils.security import get_current_user, require_merchant
from app.utils.helpers import save_upload_file, generate_product_display_id
from app.services import rag_service

router = APIRouter()


@router.get("", response_model=List[ProductOut])
def list_products(
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    status: Optional[str] = "on",
    include_deleted: bool = False,
    db: Session = Depends(get_db),
):
    q = db.query(Product)
    if status:
        q = q.filter(Product.status == status)
    if not include_deleted:
        q = q.filter(Product.status != "deleted")
    if category:
        q = q.filter(Product.category == category)
    if keyword:
        q = q.filter(Product.name.contains(keyword))
    return q.order_by(desc(Product.created_at)).all()


@router.get("/categories/list")
def categories(db: Session = Depends(get_db)):
    rows = db.query(Product.category).distinct().all()
    return [r[0] for r in rows if r[0]]


@router.get("/my/favorites")
def my_favorites(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = (
        db.query(Favorite, Product)
        .join(Product, Favorite.product_id == Product.id)
        .filter(Favorite.user_id == current_user.id)
        .order_by(desc(Favorite.created_at))
        .all()
    )
    return [{"id": f.id, "product_id": f.product_id, "product": p, "created_at": f.created_at} for f, p in rows]


@router.get("/my/browse-history")
def browse_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = (
        db.query(BrowseHistory, Product)
        .join(Product, BrowseHistory.product_id == Product.id)
        .filter(BrowseHistory.user_id == current_user.id)
        .order_by(desc(BrowseHistory.created_at))
        .limit(50)
        .all()
    )
    return [{"id": h.id, "product": p, "created_at": h.created_at} for h, p in rows]


@router.get("/template/download")
def download_template(_: User = Depends(require_merchant)):
    df = pd.DataFrame([{
        "name": "示例商品",
        "category": "分类",
        "description": "商品描述",
        "price": 99.0,
        "stock": 100,
        "status": "on",
        "specs": "规格1,规格2",
        "images": "图片URL1,图片URL2",
        "video_url": "视频URL",
    }])
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=product_template.xlsx"})


@router.post("/import")
def import_products(file: UploadFile = File(...), db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    ext = file.filename.split(".")[-1].lower()
    content = file.file.read()
    if ext == "json":
        data = json.loads(content)
    elif ext in ("xlsx", "xls"):
        df = pd.read_excel(io.BytesIO(content))
        data = df.to_dict(orient="records")
    else:
        raise HTTPException(status_code=400, detail="仅支持json/xlsx")
    count = 0
    for item in data:
        specs = item.get("specs", "")
        if isinstance(specs, str):
            specs = [s.strip() for s in specs.split(",") if s.strip()]
        images = item.get("images", "")
        if isinstance(images, str):
            images = [s.strip() for s in images.split(",") if s.strip()]
        product = Product(
            display_id=generate_product_display_id(db),
            name=item.get("name", ""),
            category=item.get("category", ""),
            description=item.get("description", ""),
            price=float(item.get("price", 0) or 0),
            stock=int(item.get("stock", 0) or 0),
            status=item.get("status", "off"),
            specs=specs,
            images=images,
            video_url=item.get("video_url", ""),
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        count += 1
    return {"ok": True, "count": count}


@router.get("/export/data")
def export_products(db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    products = db.query(Product).all()
    data = [
        {
            "display_id": p.display_id,
            "name": p.name,
            "category": p.category,
            "description": p.description,
            "price": p.price,
            "stock": p.stock,
            "status": p.status,
            "specs": ",".join(p.specs) if p.specs else "",
            "images": ",".join(p.images) if p.images else "",
            "video_url": p.video_url,
            "ai_title": p.ai_title,
            "ai_slogan": p.ai_slogan,
        }
        for p in products
    ]
    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=products.xlsx"})


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="商品不存在")
    return p


@router.post("", response_model=ProductOut)
def create_product(
    name: str = Form(...),
    category: Optional[str] = Form(""),
    description: Optional[str] = Form(""),
    price: float = Form(0.0),
    stock: int = Form(0),
    status: Optional[str] = Form("off"),
    specs: Optional[str] = Form(""),
    images: List[UploadFile] = File(default=[]),
    video: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_merchant),
):
    image_urls = []
    for img in images:
        if img.filename:
            image_urls.append(save_upload_file(img, "images"))
    video_url = ""
    if video and video.filename:
        video_url = save_upload_file(video, "videos")
    product = Product(
        display_id=generate_product_display_id(db),
        name=name,
        category=category,
        description=description,
        price=price,
        stock=stock,
        status=status,
        specs=[s.strip() for s in specs.split(",") if s.strip()] if specs else [],
        images=image_urls,
        video_url=video_url,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    name: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    stock: Optional[int] = Form(None),
    status: Optional[str] = Form(None),
    specs: Optional[str] = Form(None),
    keep_images: Optional[str] = Form(""),
    images: List[UploadFile] = File(default=[]),
    video: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_merchant),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    if name is not None:
        product.name = name
    if category is not None:
        product.category = category
    if description is not None:
        product.description = description
    if price is not None:
        product.price = price
    if stock is not None:
        product.stock = stock
    if status is not None:
        product.status = status
    if specs is not None:
        product.specs = [s.strip() for s in specs.split(",") if s.strip()]

    retained = [u.strip() for u in keep_images.split(",") if u.strip()]
    image_urls = list(retained)
    for img in images:
        if img.filename:
            image_urls.append(save_upload_file(img, "images"))
    product.images = image_urls

    if video and video.filename:
        product.video_url = save_upload_file(video, "videos")

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    product.status = "deleted"
    db.commit()
    return {"ok": True}


@router.post("/{product_id}/favorite")
def toggle_favorite(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    fav = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.product_id == product_id).first()
    if fav:
        db.delete(fav)
        db.commit()
        return {"ok": True, "favorited": False}
    db.add(Favorite(user_id=current_user.id, product_id=product_id))
    db.commit()
    return {"ok": True, "favorited": True}


@router.post("/{product_id}/browse")
def record_browse(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.add(BrowseHistory(user_id=current_user.id, product_id=product_id))
    db.commit()
    return {"ok": True}
