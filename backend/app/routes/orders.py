from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_
from typing import List, Dict
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.schemas import OrderCreate, OrderOut
from app.utils.security import get_current_user, require_merchant
from app.utils.helpers import generate_order_no

router = APIRouter()


def _serialize_order(order: Order, user_map: Dict[int, User] = None, product_map: Dict[int, Product] = None) -> dict:
    user = (user_map or {}).get(order.user_id)
    product_map = product_map or {}
    return {
        "id": order.id,
        "order_no": order.order_no,
        "user_id": order.user_id,
        "user_display_id": user.display_id if user else "",
        "user_nickname": user.nickname if user else "",
        "status": order.status,
        "total_amount": order.total_amount,
        "address": order.address,
        "recipient_name": order.recipient_name,
        "recipient_phone": order.recipient_phone,
        "recipient_address": order.recipient_address,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "items": [
            {
                "id": i.id,
                "product_id": i.product_id,
                "quantity": i.quantity,
                "price": i.price,
                "spec": i.spec,
                "product_name": product_map.get(i.product_id, Product(name="")).name,
                "product_display_id": product_map.get(i.product_id, Product(display_id="")).display_id,
            }
            for i in order.items
        ],
    }


def _apply_shipping(order: Order, name: str, phone: str, address: str):
    order.recipient_name = name or ""
    order.recipient_phone = phone or ""
    order.recipient_address = address or ""
    parts = [p for p in [name, phone, address] if p]
    order.address = " ".join(parts)


def _auto_cancel_expired_orders(db: Session):
    deadline = datetime.now() - timedelta(minutes=15)
    expired = db.query(Order).filter(Order.status == "pending", Order.created_at < deadline).all()
    for order in expired:
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock += item.quantity
        order.status = "cancelled"
    if expired:
        db.commit()


@router.post("/checkout", response_model=OrderOut)
def checkout(payload: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    has_structured = payload.address_name or payload.address_phone or payload.address_detail
    if not payload.address.strip() and not has_structured:
        raise HTTPException(status_code=400, detail="请先填写收货地址")
    total = 0.0
    order = Order(user_id=current_user.id, status="pending", total_amount=0.0, address=payload.address)
    db.add(order)
    db.flush()
    first_product_id = None
    product_map = {}
    for item in payload.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product or product.status != "on":
            raise HTTPException(status_code=400, detail=f"商品不存在或已下架: {item.product_id}")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"库存不足: {product.name}")
        product.stock -= item.quantity
        db.add(OrderItem(order_id=order.id, product_id=item.product_id, quantity=item.quantity, price=product.price, spec=item.spec or ""))
        total += product.price * item.quantity
        product_map[product.id] = product
        if first_product_id is None:
            first_product_id = item.product_id
    order.total_amount = total
    order.order_no = generate_order_no(db, first_product_id)
    if has_structured:
        _apply_shipping(order, payload.address_name or "", payload.address_phone or "", payload.address_detail or "")
    db.commit()
    db.refresh(order)
    return _serialize_order(order, {current_user.id: current_user}, product_map)


@router.get("/my", response_model=List[OrderOut])
def my_orders(status: str = None, keyword: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _auto_cancel_expired_orders(db)
    q = db.query(Order).filter(Order.user_id == current_user.id)
    if status:
        q = q.filter(Order.status == status)
    if keyword:
        q = q.outerjoin(OrderItem, OrderItem.order_id == Order.id) \
              .outerjoin(Product, Product.id == OrderItem.product_id) \
              .filter(or_(
                  Order.order_no.contains(keyword),
                  Product.name.contains(keyword),
                  Order.recipient_name.contains(keyword),
                  Order.recipient_phone.contains(keyword),
                  Order.recipient_address.contains(keyword),
                  Order.address.contains(keyword),
              )) \
              .distinct()
    orders = q.order_by(desc(Order.created_at)).all()
    product_ids = {i.product_id for o in orders for i in o.items}
    product_map = {p.id: p for p in db.query(Product).filter(Product.id.in_(product_ids)).all()}
    user_map = {current_user.id: current_user}
    return [_serialize_order(o, user_map, product_map) for o in orders]


@router.get("/all/list", response_model=List[OrderOut])
def all_orders(keyword: str = None, status: str = None, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    _auto_cancel_expired_orders(db)
    q = db.query(Order)
    if keyword:
        q = q.filter(Order.order_no.contains(keyword))
    if status:
        q = q.filter(Order.status == status)
    orders = q.order_by(desc(Order.created_at)).all()
    user_ids = {o.user_id for o in orders}
    product_ids = {i.product_id for o in orders for i in o.items}
    user_map = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()}
    product_map = {p.id: p for p in db.query(Product).filter(Product.id.in_(product_ids)).all()}
    return [_serialize_order(o, user_map, product_map) for o in orders]


@router.get("/dashboard")
def dashboard(date_str: str = None, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    _auto_cancel_expired_orders(db)
    if date_str:
        selected = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        selected = datetime.now().date()
    month_str = selected.strftime("%Y-%m")
    paid_statuses = ("paid", "shipped", "completed", "refunded")

    daily_orders = db.query(Order).filter(func.date(Order.created_at) == selected, Order.status.in_(paid_statuses)).all()
    monthly_orders = db.query(Order).filter(func.strftime("%Y-%m", Order.created_at) == month_str, Order.status.in_(paid_statuses)).all()
    return_orders = db.query(Order).filter(func.date(Order.updated_at) == selected, Order.status == "refunded").count()
    cancel_orders = db.query(Order).filter(func.date(Order.updated_at) == selected, Order.status == "cancelled").count()
    recent = db.query(Order).filter(func.date(Order.created_at) == selected).order_by(desc(Order.created_at)).all()

    user_ids = {o.user_id for o in recent}
    product_ids = {i.product_id for o in recent for i in o.items}
    user_map = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()}
    product_map = {p.id: p for p in db.query(Product).filter(Product.id.in_(product_ids)).all()}

    return {
        "date": selected.isoformat(),
        "daily_amount": round(sum(o.total_amount for o in daily_orders), 2),
        "monthly_amount": round(sum(o.total_amount for o in monthly_orders), 2),
        "daily_orders": len(daily_orders),
        "return_orders": return_orders,
        "cancel_orders": cancel_orders,
        "recent_orders": [_serialize_order(o, user_map, product_map) for o in recent],
    }


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _auto_cancel_expired_orders(db)
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.user_id != current_user.id and current_user.role != "merchant":
        raise HTTPException(status_code=403, detail="无权查看")
    user_map = {current_user.id: current_user}
    if current_user.role == "merchant" and order.user_id != current_user.id:
        user = db.query(User).filter(User.id == order.user_id).first()
        if user:
            user_map[order.user_id] = user
    product_ids = {i.product_id for i in order.items}
    product_map = {p.id: p for p in db.query(Product).filter(Product.id.in_(product_ids)).all()}
    return _serialize_order(order, user_map, product_map)


@router.post("/{order_id}/pay")
def pay_order(order_id: int, method: str = "wechat", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _auto_cancel_expired_orders(db)
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="订单状态不可支付")
    order.status = "paid"
    db.commit()
    return {"ok": True, "status": order.status, "method": method}


@router.post("/{order_id}/ship")
def ship_order(order_id: int, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != "paid":
        raise HTTPException(status_code=400, detail="订单状态不可发货")
    order.status = "shipped"
    db.commit()
    return {"ok": True, "status": order.status}


@router.post("/{order_id}/complete")
def complete_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.user_id != current_user.id and current_user.role != "merchant":
        raise HTTPException(status_code=403, detail="无权操作")
    if order.status != "shipped":
        raise HTTPException(status_code=400, detail="订单状态不可完成")
    order.status = "completed"
    db.commit()
    return {"ok": True, "status": order.status}


@router.post("/{order_id}/cancel")
def cancel_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作")
    if order.status not in ("pending", "paid"):
        raise HTTPException(status_code=400, detail="当前状态不可取消")
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock += item.quantity
    if order.status == "paid":
        order.status = "refunded"
    else:
        order.status = "cancelled"
    db.commit()
    return {"ok": True, "status": order.status}


@router.put("/{order_id}/shipping")
def update_shipping(
    order_id: int,
    name: str,
    phone: str,
    address: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作")
    if order.status not in ("pending", "paid"):
        raise HTTPException(status_code=400, detail="只有待支付或已支付订单可修改收货信息")
    _apply_shipping(order, name, phone, address)
    db.commit()
    return {"ok": True}


@router.put("/{order_id}/address")
def update_address(order_id: int, name: str, phone: str, address: str, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    _apply_shipping(order, name, phone, address)
    db.commit()
    return {"ok": True}


@router.put("/{order_id}/status")
def update_status(order_id: int, status: str, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    order.status = status
    db.commit()
    return {"ok": True, "status": order.status}


@router.delete("/{order_id}")
def delete_order(order_id: int, refund: bool = True, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if refund and order.status == "paid":
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock += item.quantity
    db.delete(order)
    db.commit()
    return {"ok": True}
