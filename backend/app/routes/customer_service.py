from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.customer_service import CustomerServiceMessage
from app.schemas import CustomerServiceMessageCreate, CustomerServiceMessageOut, CustomerServiceThreadOut
from app.utils.security import get_current_user, require_merchant

router = APIRouter()


def _message_to_dict(msg: CustomerServiceMessage, user_map: dict = None, product_map: dict = None) -> dict:
    user = (user_map or {}).get(msg.user_id)
    product = (product_map or {}).get(msg.product_id) if msg.product_id else None
    return {
        "id": msg.id,
        "user_id": msg.user_id,
        "product_id": msg.product_id,
        "sender_role": msg.sender_role,
        "content": msg.content,
        "is_read": msg.is_read,
        "created_at": msg.created_at,
        "user_nickname": user.nickname if user else "",
        "user_display_id": user.display_id if user else "",
        "user_avatar_url": user.avatar_url if user else "",
        "product_name": product.name if product else "",
        "product_display_id": product.display_id if product else "",
    }


@router.post("/messages", response_model=CustomerServiceMessageOut)
def create_message(
    payload: CustomerServiceMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.product_id:
        product = db.query(Product).filter(Product.id == payload.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="商品不存在")
    msg = CustomerServiceMessage(
        user_id=current_user.id,
        product_id=payload.product_id,
        sender_role="user",
        content=payload.content.strip(),
        is_read=False,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return _message_to_dict(msg, {current_user.id: current_user})


@router.get("/messages/my", response_model=List[CustomerServiceMessageOut])
def my_messages(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    messages = (
        db.query(CustomerServiceMessage)
        .filter(CustomerServiceMessage.user_id == current_user.id)
        .order_by(CustomerServiceMessage.created_at)
        .all()
    )
    product_ids = {m.product_id for m in messages if m.product_id}
    product_map = {p.id: p for p in db.query(Product).filter(Product.id.in_(product_ids)).all()}
    return [_message_to_dict(m, {current_user.id: current_user}, product_map) for m in messages]


@router.get("/merchant/threads", response_model=List[CustomerServiceThreadOut])
def merchant_threads(db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    subquery = (
        db.query(
            CustomerServiceMessage.user_id,
            func.max(CustomerServiceMessage.created_at).label("last_time"),
        )
        .group_by(CustomerServiceMessage.user_id)
        .subquery()
    )
    latest = (
        db.query(CustomerServiceMessage)
        .join(
            subquery,
            (CustomerServiceMessage.user_id == subquery.c.user_id)
            & (CustomerServiceMessage.created_at == subquery.c.last_time),
        )
        .order_by(desc(CustomerServiceMessage.created_at))
        .all()
    )
    user_ids = {m.user_id for m in latest}
    users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()}
    result = []
    for msg in latest:
        user = users.get(msg.user_id)
        if not user:
            continue
        unread_count = (
            db.query(CustomerServiceMessage)
            .filter(
                CustomerServiceMessage.user_id == msg.user_id,
                CustomerServiceMessage.sender_role == "user",
                CustomerServiceMessage.is_read == False,
            )
            .count()
        )
        result.append({
            "user_id": msg.user_id,
            "user_nickname": user.nickname,
            "user_display_id": user.display_id,
            "user_avatar_url": user.avatar_url or "",
            "last_message": msg.content,
            "last_time": msg.created_at,
            "unread_count": unread_count,
            "product_id": msg.product_id,
        })
    return result


@router.get("/merchant/threads/{user_id}", response_model=List[CustomerServiceMessageOut])
def merchant_thread_detail(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    messages = (
        db.query(CustomerServiceMessage)
        .filter(CustomerServiceMessage.user_id == user_id)
        .order_by(CustomerServiceMessage.created_at)
        .all()
    )
    user = db.query(User).filter(User.id == user_id).first()
    user_map = {user_id: user} if user else {}
    product_ids = {m.product_id for m in messages if m.product_id}
    product_map = {p.id: p for p in db.query(Product).filter(Product.id.in_(product_ids)).all()}
    return [_message_to_dict(m, user_map, product_map) for m in messages]


@router.post("/merchant/threads/{user_id}/reply", response_model=CustomerServiceMessageOut)
def merchant_reply(
    user_id: int,
    payload: CustomerServiceMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_merchant),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    latest = (
        db.query(CustomerServiceMessage)
        .filter(CustomerServiceMessage.user_id == user_id)
        .order_by(desc(CustomerServiceMessage.created_at))
        .first()
    )
    product_id = payload.product_id or (latest.product_id if latest else None)
    msg = CustomerServiceMessage(
        user_id=user_id,
        product_id=product_id,
        sender_role="merchant",
        content=payload.content.strip(),
        is_read=True,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    product_map = {}
    if product_id:
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            product_map[product_id] = product
    return _message_to_dict(msg, {user_id: user}, product_map)


@router.patch("/messages/{message_id}/read")
def mark_read(message_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    msg = db.query(CustomerServiceMessage).filter(CustomerServiceMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="消息不存在")
    if current_user.role == "user" and msg.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作")
    msg.is_read = True
    db.commit()
    return {"ok": True}


@router.get("/merchant/unread-count")
def merchant_unread_count(db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    count = db.query(CustomerServiceMessage).filter(
        CustomerServiceMessage.sender_role == "user",
        CustomerServiceMessage.is_read == False,
    ).count()
    return {"count": count}
