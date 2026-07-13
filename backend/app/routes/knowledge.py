from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
import io
import pandas as pd
from fastapi.responses import StreamingResponse
from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.knowledge import KnowledgeItem
from app.schemas import KnowledgeItemCreate, KnowledgeItemOut
from app.utils.security import require_merchant
from app.services import rag_service

router = APIRouter()


@router.get("", response_model=List[KnowledgeItemOut])
def list_items(product_id: int = None, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    q = db.query(KnowledgeItem)
    if product_id:
        q = q.filter(KnowledgeItem.product_id == product_id)
    return q.order_by(desc(KnowledgeItem.created_at)).all()


@router.get("/template/download")
def download_template(_: User = Depends(require_merchant)):
    df = pd.DataFrame([{
        "product_name": "示例商品名称（留空表示通用）",
        "category": "common",
        "question": "问题内容",
        "answer": "回答内容",
    }])
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=knowledge_template.xlsx"})


@router.get("/export")
def export_knowledge(product_id: int = None, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    q = db.query(KnowledgeItem)
    if product_id:
        q = q.filter(KnowledgeItem.product_id == product_id)
    items = q.order_by(desc(KnowledgeItem.created_at)).all()
    product_map = {p.id: p.name for p in db.query(Product).all()}
    data = [
        {
            "id": item.id,
            "product_name": product_map.get(item.product_id, "通用"),
            "category": item.category,
            "question": item.question,
            "answer": item.answer,
            "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else "",
        }
        for item in items
    ]
    df = pd.DataFrame(data, columns=["id", "product_name", "category", "question", "answer", "created_at"])
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=knowledge_export.xlsx"})


@router.post("/import")
def import_knowledge(file: UploadFile = File(...), db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    ext = file.filename.split(".")[-1].lower()
    if ext not in ("xlsx", "xls"):
        raise HTTPException(status_code=400, detail="仅支持xlsx/xls")
    df = pd.read_excel(io.BytesIO(file.file.read()))
    rows = df.to_dict(orient="records")
    count = 0
    products = {p.name: p.id for p in db.query(Product).all()}
    for row in rows:
        product_name = str(row.get("product_name", "") or "").strip()
        product_id = products.get(product_name)
        category = str(row.get("category", "common") or "common").strip()
        question = str(row.get("question", "") or "").strip()
        answer = str(row.get("answer", "") or "").strip()
        if not question or not answer:
            continue
        item = KnowledgeItem(product_id=product_id, category=category, question=question, answer=answer)
        db.add(item)
        db.commit()
        db.refresh(item)
        text = f"问题：{item.question}\n回答：{item.answer}"
        eid = rag_service.add_knowledge(text, {
            "product_id": item.product_id,
            "question": item.question,
            "category": item.category,
        })
        item.embedding_id = eid
        db.commit()
        count += 1
    return {"ok": True, "count": count}


@router.post("", response_model=KnowledgeItemOut)
def create_item(payload: KnowledgeItemCreate, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    item = KnowledgeItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    text = f"问题：{item.question}\n回答：{item.answer}"
    eid = rag_service.add_knowledge(text, {
        "product_id": item.product_id,
        "question": item.question,
        "category": item.category,
    })
    item.embedding_id = eid
    db.commit()
    db.refresh(item)
    return item


@router.post("/sync/{product_id}")
def sync_product_knowledge(product_id: int, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    items = db.query(KnowledgeItem).filter(KnowledgeItem.product_id == product_id).all()
    data = {
        "id": product.id,
        "name": product.name,
        "category": product.category,
        "description": product.description,
        "price": product.price,
        "specs": product.specs or [],
        "knowledge_items": [{"question": i.question, "answer": i.answer} for i in items],
    }
    pairs = rag_service.sync_product_knowledge(data)
    for text, meta in pairs:
        rag_service.add_knowledge(text, meta)
    return {"ok": True, "count": len(pairs)}


@router.put("/{item_id}", response_model=KnowledgeItemOut)
def update_item(item_id: int, payload: KnowledgeItemCreate, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="知识条目不存在")
    for k, v in payload.model_dump().items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    if item.embedding_id:
        rag_service.delete_knowledge(item.embedding_id)
    text = f"问题：{item.question}\n回答：{item.answer}"
    item.embedding_id = rag_service.add_knowledge(text, {
        "product_id": item.product_id,
        "question": item.question,
        "category": item.category,
    })
    db.commit()
    return item


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="知识条目不存在")
    if item.embedding_id:
        rag_service.delete_knowledge(item.embedding_id)
    db.delete(item)
    db.commit()
    return {"ok": True}
