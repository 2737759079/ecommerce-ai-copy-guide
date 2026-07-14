from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.chat_history import ChatHistory
from app.models.knowledge import KnowledgeItem
from app.schemas import ChatMessage, ChatOut
from app.utils.security import get_current_user, require_merchant
from app.services import rag_service, ai_service

router = APIRouter()


def _build_product_context(products: list) -> str:
    parts = []
    for p in products:
        if not p:
            continue
        specs = ", ".join(p.specs) if p.specs else "无"
        parts.append(
            f"商品名称：{p.name}\n分类：{p.category or '未分类'}\n价格：¥{p.price}\n"
            f"库存：{p.stock}\n规格：{specs}\n描述：{p.description or '暂无描述'}"
        )
    return "\n\n".join(parts)


@router.post("/ask")
def ask(payload: ChatMessage, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    products = []
    if payload.product_id:
        product = db.query(Product).filter(Product.id == payload.product_id, Product.status == "on").first()
        if product:
            products.append(product)
    else:
        keyword = payload.message.strip()
        products = db.query(Product).filter(
            Product.status == "on",
            or_(
                Product.name.contains(keyword),
                Product.category.contains(keyword),
                Product.description.contains(keyword),
            )
        ).order_by(desc(Product.created_at)).limit(5).all()

    product_context = _build_product_context(products)

    docs = rag_service.search_knowledge(payload.message, top_k=5, product_id=payload.product_id)
    rag_context = "\n\n".join([f"Q: {d['metadata'].get('question', '')}\nA: {d['document']}" for d in docs])

    context_parts = []
    if product_context:
        context_parts.append(f"【店铺当前在售商品信息】\n{product_context}")
    if rag_context:
        context_parts.append(f"【知识库参考】\n{rag_context}")
    full_context = "\n\n".join(context_parts)

    messages = [{"role": "user", "content": payload.message}]
    answer = ai_service.chat_with_context(messages, full_context)

    record = ChatHistory(
        user_id=current_user.id,
        product_id=payload.product_id,
        role="user",
        message=payload.message,
        response=answer,
    )
    db.add(record)
    db.commit()
    return {"answer": answer, "references": docs}


@router.get("/history", response_model=List[ChatOut])
def history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).order_by(desc(ChatHistory.created_at)).limit(50).all()


@router.get("/merchant/history")
def merchant_history(db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    rows = (
        db.query(ChatHistory.message, func.count(ChatHistory.id).label("count"))
        .group_by(ChatHistory.message)
        .order_by(desc("count"))
        .limit(30)
        .all()
    )
    return [{"message": m, "count": c} for m, c in rows]
